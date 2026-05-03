import baostock as bs
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import logging

from app.services.cache_service import cache_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaostockService:
    def __init__(self):
        self._logged_in = False
    
    def _ensure_login(self):
        """确保已登录"""
        if not self._logged_in:
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
        """登出"""
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def fetch_history_data(self, index_code: str = "sh.000001", 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          frequency: str = "d") -> pd.DataFrame:
        """
        获取历史K线数据
        
        Args:
            index_code: 指数代码，如 sh.000001
            start_date: 开始日期，格式 YYYY-MM-DD
            end_date: 结束日期，格式 YYYY-MM-DD
            frequency: 数据频率，d=日, w=周, m=月
        """
        self._ensure_login()
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*25)).strftime("%Y-%m-%d")
        
        logger.info(f"获取数据: {index_code}, {start_date} ~ {end_date}")
        
        # 复权类型: 3=不复权, 2=前复权, 1=后复权
        # 指数数据不需要复权
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
        """
        更新数据，优先从缓存读取，缓存无效或过期时从 baostock 获取
        
        Returns:
            pd.DataFrame: 完整的历史数据
        """
        # 检查缓存
        if cache_service.is_cache_valid(index_code):
            logger.info("使用缓存数据")
            cached_data = cache_service.get_stock_data(index_code)
            if cached_data:
                df = pd.DataFrame(cached_data)
                df['date'] = pd.to_datetime(df['date'])
                return df
        
        # 从 baostock 获取
        logger.info("从 baostock 获取数据")
        df = self.fetch_history_data(index_code)
        
        if not df.empty:
            # 保存到缓存
            records = df.to_dict('records')
            cache_service.save_stock_data(index_code, records)
            cache_service.set_last_update(
                index_code, 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        
        return df
    
    def get_index_name(self, index_code: str) -> str:
        """获取指数名称"""
        self._ensure_login()
        rs = bs.query_stock_basic(code=index_code)
        if rs.error_code == '0' and rs.next():
            return rs.get_row_data()[1]
        return index_code


baostock_service = BaostockService()
