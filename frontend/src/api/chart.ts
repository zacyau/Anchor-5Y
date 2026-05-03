import axios from 'axios'
import type { ChartData, HealthStatus } from '@/types/chart'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

const DEFAULT_INDEX_CODE = 'sz.399317'

export const chartApi = {
  async getChartData(
    indexCode: string = DEFAULT_INDEX_CODE,
    startDate?: string | null,
    endDate?: string | null
  ): Promise<ChartData> {
    const params: Record<string, string> = { index_code: indexCode }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.get('/chart/data', { params })
    return response.data
  },

  async getHealth(): Promise<HealthStatus> {
    const response = await api.get('/chart/health')
    return response.data
  },

  async refreshData(indexCode: string = DEFAULT_INDEX_CODE): Promise<{ message: string; records_count: number }> {
    const response = await api.post('/chart/refresh', null, {
      params: { index_code: indexCode }
    })
    return response.data
  }
}
