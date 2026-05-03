from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChartDataResponse(BaseModel):
    dates: List[str]
    index_values: List[float]
    sma1210: List[Optional[float]]
    upper_band: List[Optional[float]]
    lower_band: List[Optional[float]]
    deviation_rate: Optional[float]
    rsi_dates: List[str]
    rsi14: List[Optional[float]]
    rsi_daily: List[Optional[float]]
    current_rsi: Optional[float]
    drawdown_5y: List[Optional[float]]
    min_drawdown: Optional[float]
    last_update: str


class HealthResponse(BaseModel):
    status: str
    last_update: Optional[str]
    message: str


class TimeRangeRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    index_code: str = "sh.000001"
