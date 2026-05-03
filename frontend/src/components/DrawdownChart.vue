<template>
  <div class="chart-wrapper">
    <div class="chart-header">
      <h3 class="chart-title">滚动5年最大回撤</h3>
      <div v-if="minDrawdown !== null" class="drawdown-badge">
        最小值: {{ minDrawdown }}%
      </div>
    </div>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import type { ChartData } from '@/types/chart'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent
])

interface Props {
  data: ChartData | null
}

const props = defineProps<Props>()

const minDrawdown = computed(() => {
  return props.data?.min_drawdown ?? null
})

const chartOption = computed(() => {
  if (!props.data) return {}

  const { dates, drawdown_5y } = props.data

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: '#999',
          type: 'dashed'
        }
      },
      formatter: (params: any[]) => {
        const date = params[0]?.axisValue
        const value = params[0]?.value
        return `<div style="font-weight:600;margin-bottom:4px">${date}</div>
                <div>最大回撤: ${value?.toFixed(2) ?? '--'}%</div>`
      }
    },
    grid: {
      left: 60,
      right: 40,
      top: 30,
      bottom: 60
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: '#ddd' }
      },
      axisLabel: {
        color: '#666',
        fontSize: 11,
        interval: 500,
        formatter: (value: string) => {
          return value.substring(0, 4)
        }
      },
      axisTick: {
        show: true,
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      max: 0,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#666',
        fontSize: 11,
        formatter: (value: number) => `${value}%`
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        bottom: 10,
        handleSize: '80%',
        showDetail: false,
        borderColor: 'transparent',
        backgroundColor: '#f5f5f5',
        fillerColor: 'rgba(68, 114, 196, 0.1)',
        handleStyle: {
          color: '#4472C4'
        }
      }
    ],
    series: [
      {
        name: '滚动5年最大回撤',
        type: 'line',
        data: drawdown_5y,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: '#333333',
          width: 1.5
        }
      }
    ]
  }
})
</script>

<style scoped>
.chart-wrapper {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.drawdown-badge {
  background: #f0f0f0;
  color: #666;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.chart {
  width: 100%;
  height: 280px;
}

@media (max-width: 768px) {
  .chart {
    height: 220px;
  }
}
</style>
