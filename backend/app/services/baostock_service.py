import baostock as bs
import pandas as pd
import threading
import signal
from contextlib import contextmanager
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.services.cache_service import cache_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_BAOSTOCK_TIMEOUT_SECONDS = 30


class TimeoutError(Exception):
    pass


@contextmanager
def timeout_context(seconds: int):
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def _raise_timeout(signum, frame):
        raise TimeoutError(f"操作超时 ({seconds}s)")

    old_handler = signal.signal(signal.SIGALRM, _raise_timeout)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


class BaostockService:
    def __init__(self):
        self._logged_in = False
        self._login_lock = threading.Lock()
        self._fetch_locks: dict[str, threading.Lock] = {}
        self._fetch_locks_lock = threading.Lock()

    def _get_fetch_lock(self, index_code: str) -> threading.Lock:
        with self._fetch_locks_lock:
            if index_code not in self._fetch_locks:
                self._fetch_locks[index_code] = threading.Lock()
            return self._fetch_locks[index_code]

    def _ensure_login(self):
        if self._logged_in:
            return
        with self._login_lock:
            if self._logged_in:
                return
            try:
                lg = bs.login()
                if lg.error_code != '0':
                    logger.error(f"baostock 登录失败: {lg.error_msg}")
                    raise Exception(f"baostock login failed: {lg.error_msg}")
                self._logged_in = True
                logger.info("baostock 登录成功")
            except Exception as e:
                logger.error(f"baostock 登录异常: {e}")
                raise

    def logout(self):
        with self._login_lock:
            if self._logged_in:
                bs.logout()
                self._logged_in = False

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

        rs = bs.query_history_k_data_plus(
            index_code,
            "date,open,high,low,close,volume,amount,adjustflag",
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag=adjustflag
        )

        if rs.error_code != '0':
            logger.error(f"获取数据失败: {rs.error_msg}")
            raise Exception(f"Fetch data failed: {rs.error_msg}")

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
                raise TimeoutError(f"等待 {index_code} 数据获取超时")
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
        rs = bs.query_stock_basic(code=index_code)
        if rs.error_code == '0' and rs.next():
            return rs.get_row_data()[1]
        return index_code


baostock_service = BaostockService()
