import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.config import get_settings

settings = get_settings()
DB_PATH = settings.database_url.replace("sqlite:///", "")


class CacheService:
    def __init__(self):
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                adjustflag TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(index_code, date)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_meta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stock_data_code_date 
            ON stock_data(index_code, date)
        """)
        
        conn.commit()
        conn.close()
    
    def get_last_update(self, index_code: str) -> Optional[str]:
        """获取最后更新时间"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT updated_at FROM cache_meta WHERE key = ?",
            (f"last_update_{index_code}",)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def set_last_update(self, index_code: str, update_time: str):
        """设置最后更新时间"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO cache_meta (key, value, updated_at) 
               VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET 
               value = excluded.value, updated_at = excluded.updated_at""",
            (f"last_update_{index_code}", update_time, update_time)
        )
        conn.commit()
        conn.close()
    
    def save_stock_data(self, index_code: str, data: List[Dict[str, Any]]):
        """保存股票数据"""
        if not data:
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for row in data:
            # 将 Timestamp 转为字符串
            date_val = row.get("date")
            if hasattr(date_val, 'strftime'):
                date_val = date_val.strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO stock_data 
                (index_code, date, open, high, low, close, volume, amount, adjustflag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(index_code, date) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume,
                amount = excluded.amount,
                adjustflag = excluded.adjustflag
            """, (
                index_code,
                date_val,
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("volume"),
                row.get("amount"),
                row.get("adjustflag")
            ))
        
        conn.commit()
        conn.close()
    
    def get_stock_data(self, index_code: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取股票数据"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM stock_data WHERE index_code = ?"
        params = [index_code]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def is_cache_valid(self, index_code: str) -> bool:
        """检查缓存是否有效"""
        last_update = self.get_last_update(index_code)
        if not last_update:
            return False
        
        try:
            last_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
            ttl = timedelta(hours=settings.cache_ttl_hours)
            return datetime.now() - last_dt < ttl
        except:
            return False
    
    def get_date_range(self, index_code: str) -> tuple:
        """获取数据日期范围"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(date), MAX(date) FROM stock_data WHERE index_code = ?",
            (index_code,)
        )
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, None)


cache_service = CacheService()
