from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

from app.models.schemas import ChartDataResponse, HealthResponse, TimeRangeRequest
from app.services.baostock_service import baostock_service
from app.services.indicator_service import indicator_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chart", tags=["chart"])

DEFAULT_INDEX_CODE = "sz.399317"


@router.get("/data", response_model=ChartDataResponse)
async def get_chart_data(
    index_code: str = Query(default=DEFAULT_INDEX_CODE, description="指数代码"),
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD")
):
    """
    获取图表数据

    包含：
    - 国证A股指数走势
    - SMA1210 及上下通道
    - 周线 RSI14
    - 滚动 5 年最大回撤
    """
    try:
        # 获取数据
        df = baostock_service.update_data(index_code)

        if df.empty:
            raise HTTPException(status_code=404, detail="未获取到数据")

        # 日期过滤
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]

        if df.empty:
            raise HTTPException(status_code=404, detail="指定日期范围内无数据")

        # 计算指标
        chart_data = indicator_service.prepare_chart_data(df)

        return ChartDataResponse(**chart_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图表数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    try:
        last_update = cache_service.get_last_update(DEFAULT_INDEX_CODE)
        return HealthResponse(
            status="ok",
            last_update=last_update,
            message="服务运行正常"
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            last_update=None,
            message=f"服务异常: {str(e)}"
        )


@router.post("/refresh")
async def refresh_data(index_code: str = DEFAULT_INDEX_CODE):
    """
    手动刷新数据

    强制从 baostock 获取最新数据
    """
    try:
        df = baostock_service.fetch_history_data(index_code)

        if df.empty:
            raise HTTPException(status_code=404, detail="未获取到数据")

        # 保存到缓存
        records = df.to_dict('records')
        cache_service.save_stock_data(index_code, records)
        cache_service.set_last_update(
            index_code,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return {
            "message": "数据刷新成功",
            "records_count": len(records),
            "date_range": {
                "start": df['date'].min().strftime("%Y-%m-%d"),
                "end": df['date'].max().strftime("%Y-%m-%d")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新数据失败: {str(e)}")
