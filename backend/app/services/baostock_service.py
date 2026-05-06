import baostock as bs
import pandas as pd
import threading
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.services.cache_service import cache_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_BAOSTOCK_TIMEOUT_SECONDS = 30
_LOGIN_TTL_SECONDS = 4 * 3600


class BaostockError(Exception):
    pass


class BaostockService:
    def __init__(self):
        self._logged_in = False
        self._login_time: Optional[datetime] = None
        self._login_lock = threading.Lock()
        self._fetch_locks: dict[str, threading.Lock] = {}
        self._fetch_locks_lock = threading.Lock()

    def _get_fetch_lock(self, index_code: str) -> threading.Lock:
        with self._fetch_locks_lock:
            if index_code not in self._fetch_locks:
                self._fetch_locks[index_code] = threading.Lock()
            return self._fetch_locks[index_code]

    def _is_login_stale(self) -> bool:
        if not self._logged_in or self._login_time is None:
            return True
        return (datetime.now() - self._login_time).total_seconds() > _LOGIN_TTL_SECONDS

    def _ensure_login(self):
        if self._logged_in and not self._is_login_stale():
            return
        with self._login_lock:
            if self._logged_in and not self._is_login_stale():
                return
            if self._logged_in:
                try:
                    bs.logout()
                except Exception:
                    pass
                self._logged_in = False
                self._login_time = None

            try:
                lg = bs.login()
                if lg.error_code != '0':
                    logger.error(f"baostock 登录失败: {lg.error_msg}")
                    raise BaostockError(f"baostock login failed: {lg.error_msg}")
                self._logged_in = True
                self._login_time = datetime.now()
                logger.info("baostock 登录成功")
            except BaostockError:
                raise
            except Exception as e:
                logger.error(f"baostock 登录异常: {e}")
                self._logged_in = False
                self._login_time = None
                raise BaostockError(f"baostock login failed: {e}")

    def _force_reconnect(self):
        with self._login_lock:
            if self._logged_in:
                try:
                    bs.logout()
                except Exception:
                    pass
            self._logged_in = False
            self._login_time = None
            try:
                lg = bs.login()
                if lg.error_code != '0':
                    raise BaostockError(f"reconnect failed: {lg.error_msg}")
                self._logged_in = True
                self._login_time = datetime.now()
                logger.info("baostock 重连成功")
            except Exception:
                self._logged_in = False
                self._login_time = None
                raise

    def logout(self):
        with self._login_lock:
            if self._logged_in:
                try:
                    bs.logout()
                except Exception:
                    pass
                self._logged_in = False
                self._login_time = None

    def fetch_history_data(
        self,
        index_code: str = "sh.000001",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = "d"
    ) -> pd.DataFrame:
        self._ensure_login()

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365 * 25)).strftime("%Y-%m-%d")

        logger.info(f"获取数据: {index_code}, {start_date} ~ {end_date}")

        adjustflag = "3" if "sh." in index_code or "sz." in index_code else "2"

        for attempt in range(2):
            try:
                rs = bs.query_history_k_data_plus(
                    index_code,
                    "date,open,high,low,close,volume,amount,adjustflag",
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    adjustflag=adjustflag
                )

                if rs.error_code != '0':
                    error_msg = rs.error_msg if hasattr(rs, 'error_msg') else str(rs.error_code)
                    if attempt == 0:
                        logger.warning(f"查询失败 ({error_msg})，尝试重连后重试...")
                        self._force_reconnect()
                        continue
                    logger.error(f"获取数据失败: {error_msg}")
                    raise BaostockError(f"Fetch data failed: {error_msg}")

                data_list = []
                while (rs.error_code == '0') & rs.next():
                    row = rs.get_row_data()
                    data_list.append({
                        "date": row[0],
                        "open": float(row[1]) if row[1] else None,
                        "high": float(row[2]) if row[2] else None,
                        "low": float(row[3]) if row[3] else None,
                        "close": float(row[4]) if row[4] else None,
                        "volume": float(row[5]) if row[5] else None,
                        "amount": float(row[6]) if row[6] else None,
                        "adjustflag": row[7]
                    })

                df = pd.DataFrame(data_list)
                if df.empty:
                    logger.warning("获取到空数据")
                    return df

                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)

                logger.info(f"获取到 {len(df)} 条数据")
                return df

            except BaostockError:
                raise
            except Exception as e:
                if attempt == 0:
                    logger.warning(f"查询异常 ({e})，尝试重连后重试...")
                    self._force_reconnect()
                    continue
                logger.error(f"获取数据异常: {e}")
                raise BaostockError(f"Fetch data failed: {e}")

        raise BaostockError("获取数据失败，重试已耗尽")

    def update_data(self, index_code: str = "sh.000001") -> pd.DataFrame:
        if cache_service.is_cache_valid(index_code):
            logger.info("使用缓存数据")
            cached_data = cache_service.get_stock_data(index_code)
            if cached_data:
                df = pd.DataFrame(cached_data)
                df['date'] = pd.to_datetime(df['date'])
                return df

        fetch_lock = self._get_fetch_lock(index_code)
        if not fetch_lock.acquire(blocking=False):
            logger.info(f"已有其他请求正在获取 {index_code} 数据，等待中...")
            acquired = fetch_lock.acquire(timeout=_BAOSTOCK_TIMEOUT_SECONDS)
            if not acquired:
                raise RuntimeError(f"等待 {index_code} 数据获取超时")
            if cache_service.is_cache_valid(index_code):
                cached_data = cache_service.get_stock_data(index_code)
                if cached_data:
                    df = pd.DataFrame(cached_data)
                    df['date'] = pd.to_datetime(df['date'])
                    fetch_lock.release()
                    return df

        try:
            if cache_service.is_cache_valid(index_code):
                cached_data = cache_service.get_stock_data(index_code)
                if cached_data:
                    df = pd.DataFrame(cached_data)
                    df['date'] = pd.to_datetime(df['date'])
                    return df

            logger.info("从 baostock 获取数据")
            df = self.fetch_history_data(index_code)

            if not df.empty:
                records = df.to_dict('records')
                cache_service.save_stock_data(index_code, records)
                cache_service.set_last_update(
                    index_code,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

            return df
        finally:
            fetch_lock.release()

    def get_index_name(self, index_code: str) -> str:
        self._ensure_login()
        for attempt in range(2):
            try:
                rs = bs.query_stock_basic(code=index_code)
                if rs.error_code == '0' and rs.next():
                    return rs.get_row_data()[1]
                if rs.error_code != '0' and attempt == 0:
                    self._force_reconnect()
                    continue
                return index_code
            except Exception:
                if attempt == 0:
                    self._force_reconnect()
                    continue
                return index_code
        return index_code


baostock_service = BaostockService()
