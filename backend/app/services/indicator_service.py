import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IndicatorService:
    @staticmethod
    def calculate_sma(data: pd.DataFrame, window: int = 1210) -> pd.DataFrame:
        """计算简单移动平均线"""
        df = data.copy()
        df[f'sma{window}'] = df['close'].rolling(window=window).mean()
        return df
    
    @staticmethod
    def calculate_envelope_bands(data: pd.DataFrame, window: int = 1210,
                                  percent: float = 0.15) -> pd.DataFrame:
        """
        计算SMA包络线（基于SMA的百分比通道）
        
        Args:
            data: 包含 close 列的 DataFrame
            window: 移动平均窗口
            percent: 包络线百分比，默认 15%
        """
        df = data.copy()
        sma = df['close'].rolling(window=window).mean()

        df['upper_band'] = sma * (1 + percent)
        df['lower_band'] = sma * (1 - percent)
        df['sma'] = sma

        return df
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算 RSI 指标 (Wilder EMA 平滑算法)

        Args:
            data: 包含 close 列的 DataFrame
            period: RSI 周期
        """
        df = data.copy()
        delta = df['close'].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = pd.Series(np.nan, index=df.index)
        avg_loss = pd.Series(np.nan, index=df.index)

        first_gain = gain.iloc[:period].mean()
        first_loss = loss.iloc[:period].mean()
        avg_gain.iloc[period - 1] = first_gain
        avg_loss.iloc[period - 1] = first_loss

        factor = period - 1
        for i in range(period, len(df)):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * factor + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * factor + loss.iloc[i]) / period

        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))

        return df
    
    @staticmethod
    def calculate_weekly_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算周线 RSI
        
        先将日线数据转为周线，再计算 RSI
        """
        df = data[['date', 'close']].copy()
        df.set_index('date', inplace=True)
        
        # 重采样为周线（取每周最后一个交易日）
        weekly = df.resample('W').last().dropna()
        
        # 计算周线 RSI
        weekly = IndicatorService.calculate_rsi(weekly, period)
        
        weekly.reset_index(inplace=True)
        return weekly[['date', 'rsi']].dropna()
    
    @staticmethod
    def calculate_rolling_drawdown(data: pd.DataFrame, 
                                    window: int = 1260) -> pd.DataFrame:
        """
        计算滚动最大回撤
        
        Args:
            data: 包含 close 列的 DataFrame
            window: 滚动窗口（交易日），约 5 年 = 252 * 5 = 1260
        """
        df = data.copy()
        
        # 滚动窗口内的最大值
        rolling_max = df['close'].rolling(window=window, min_periods=1).max()
        
        # 回撤 = (当前值 - 滚动最大值) / 滚动最大值 * 100
        df['drawdown'] = ((df['close'] - rolling_max) / rolling_max * 100)
        
        return df
    
    @staticmethod
    def calculate_deviation_rate(data: pd.DataFrame, 
                                  sma_column: str = 'sma1210') -> Optional[float]:
        """
        计算当前乖离率
        
        乖离率 = (当前价格 - SMA) / SMA * 100
        """
        if data.empty or sma_column not in data.columns:
            return None
        
        latest = data.iloc[-1]
        if pd.isna(latest[sma_column]) or latest[sma_column] == 0:
            return None
        
        deviation = (latest['close'] - latest[sma_column]) / latest[sma_column] * 100
        return round(deviation, 2)
    
    @staticmethod
    def prepare_chart_data(data: pd.DataFrame) -> Dict:
        """
        准备图表所需的所有数据
        
        Returns:
            Dict 包含所有图表数据
        """
        if data.empty:
            return {
                "dates": [],
                "index_values": [],
                "sma1210": [],
                "upper_band": [],
                "lower_band": [],
                "deviation_rate": None,
                "rsi_dates": [],
                "rsi14": [],
                "current_rsi": None,
                "drawdown_5y": [],
                "min_drawdown": None,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        df = data.copy()
        
        # 1. 计算 SMA1210 和包络线（±15%）
        df = IndicatorService.calculate_sma(df, 1210)
        df = IndicatorService.calculate_envelope_bands(df, 1210, 0.15)
        
        # 2. 计算周线 RSI14
        weekly_rsi = IndicatorService.calculate_weekly_rsi(df, 14)
        
        # 3. 计算滚动 5 年最大回撤
        df = IndicatorService.calculate_rolling_drawdown(df, 1260)
        
        # 4. 计算乖离率
        deviation_rate = IndicatorService.calculate_deviation_rate(df, 'sma1210')
        
        # 5. 提取数据
        dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
        index_values = df['close'].tolist()
        sma1210 = [round(v, 2) if not pd.isna(v) else None for v in df['sma1210'].tolist()]
        upper_band = [round(v, 2) if not pd.isna(v) else None for v in df['upper_band'].tolist()]
        lower_band = [round(v, 2) if not pd.isna(v) else None for v in df['lower_band'].tolist()]
        
        rsi_dates = weekly_rsi['date'].dt.strftime('%Y-%m-%d').tolist()
        rsi_values = [round(v, 2) if not pd.isna(v) else None for v in weekly_rsi['rsi'].tolist()]
        current_rsi = rsi_values[-1] if rsi_values else None
        
        rsi_daily = [None] * len(dates)
        rsi_idx = 0
        j = 0
        while rsi_idx < len(rsi_dates) and j < len(dates):
            w_date_str = rsi_dates[rsi_idx]
            while j + 1 < len(dates) and dates[j + 1] <= w_date_str:
                j += 1
            rsi_daily[j] = rsi_values[rsi_idx]
            rsi_idx += 1
        
        drawdown_values = [round(v, 2) if not pd.isna(v) else None for v in df['drawdown'].tolist()]
        min_drawdown = round(df['drawdown'].min(), 2) if not df['drawdown'].isna().all() else None
        
        return {
            "dates": dates,
            "index_values": index_values,
            "sma1210": sma1210,
            "upper_band": upper_band,
            "lower_band": lower_band,
            "deviation_rate": deviation_rate,
            "rsi_dates": rsi_dates,
            "rsi14": rsi_values,
            "rsi_daily": rsi_daily,
            "current_rsi": current_rsi,
            "drawdown_5y": drawdown_values,
            "min_drawdown": min_drawdown,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


indicator_service = IndicatorService()
