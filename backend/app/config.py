from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "ETF Chart API"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据配置
    database_url: str = "sqlite:///./etf_data.db"
    cache_ttl_hours: int = 24
    
    # baostock 配置
    bs_username: str = ""
    bs_password: str = ""
    
    # 定时任务配置
    data_update_hour: int = 20
    data_update_minute: int = 0
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
