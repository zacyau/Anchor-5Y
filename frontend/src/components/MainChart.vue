<template>
  <div class="chart-wrapper">
    <div class="chart-header">
      <h3 class="chart-title">国证A股指数五年之锚</h3>
      <div v-if="deviationRate !== null" class="deviation-badge">
        乖离率: {{ deviationRate > 0 ? '+' : '' }}{{ deviationRate }}%
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
  LegendComponent,
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
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent
])

interface Props {
  data: ChartData | null
}

const props = defineProps<Props>()

const deviationRate = computed(() => {
  return props.data?.deviation_rate ?? null
})

function buildYearLabels(dates: string[]): { index: number, year: string }[] {
  const result: { index: number, year: string }[] = []
  let lastYear = ''
  for (let i = 0; i < dates.length; i++) {
    const year = dates[i].substring(0, 4)
    if (year !== lastYear) {
      result.push({ index: i, year })
      lastYear = year
    }
  }
  return result
}

const chartOption = computed(() => {
  if (!props.data) return {}

  const { dates, index_values, sma1210, upper_band, lower_band } = props.data
  const yearLabels = buildYearLabels(dates)

  // Calculate data range for y-axis
  const validValues = index_values.filter((v): v is number => v !== null && v !== undefined)
  const minVal = Math.min(...validValues)
  const maxVal = Math.max(...validValues)
  const padding = (maxVal - minVal) * 0.05

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      confine: true,
      appendToBody: true,
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: '#999',
          type: 'dashed'
        }
      },
      formatter: (params: any[]) => {
        const date = params[0]?.axisValue
        const dataIndex = params[0]?.dataIndex
        let html = `<div style="font-weight:600;margin-bottom:4px">${date}</div>`
        params.forEach(p => {
          if (p.seriesName && p.value !== undefined && p.value !== null) {
            const color = p.color
            const val = typeof p.value === 'number' ? p.value.toFixed(2) : p.value
            html += `<div style="display:flex;align-items:center;gap:6px">
              <span style="display:inline-block;width:10px;height:2px;background:${color}"></span>
              <span>${p.seriesName}: ${val}</span>
            </div>`
          }
        })
        const close = index_values[dataIndex]
        const sma = sma1210[dataIndex]
        if (close !== null && close !== undefined && sma !== null && sma !== undefined && sma !== 0) {
          const deviation = ((close - sma) / sma * 100).toFixed(2)
          const sign = +deviation > 0 ? '+' : ''
          html += `<div style="margin-top:6px;padding-top:6px;border-top:1px solid #eee;color:#333">
            乖离率: ${sign}${deviation}%
          </div>`
        }
        return html
      }
    },
    legend: {
      data: ['国证A股', 'SMA1210'],
      right: 20,
      top: 10,
      textStyle: {
        color: '#666',
        fontSize: 12
      }
    },
    grid: {
      left: 60,
      right: 40,
      top: 50,
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
      type: 'log',
      min: (value: { min: number }) => Math.floor(value.min * 0.8),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#666',
        fontSize: 11,
        formatter: (value: number) => {
          if (value >= 1000) return `${Math.round(value)}`
          return `${value}`
        }
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
        name: '包络上轨',
        type: 'line',
        data: upper_band,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: '#bbbbbb',
          width: 1
        },
        areaStyle: {
          color: 'rgba(200, 200, 200, 0.2)',
          origin: 'start'
        },
        z: 1
      },
      {
        name: '包络下轨',
        type: 'line',
        data: lower_band,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: '#bbbbbb',
          width: 1
        },
        areaStyle: {
          color: '#ffffff',
          origin: 'start'
        },
        z: 2
      },
      {
        name: 'SMA1210',
        type: 'line',
        data: sma1210,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: '#4472C4',
          width: 1.5
        },
        z: 3
      },
      {
        name: '国证A股',
        type: 'line',
        data: index_values,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: '#333333',
          width: 1.5
        },
        z: 4
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

.deviation-badge {
  background: #f0f0f0;
  color: #666;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.chart {
  width: 100%;
  height: 400px;
}

@media (max-width: 768px) {
  .chart {
    height: 280px;
  }

  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
