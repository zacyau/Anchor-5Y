import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chartApi } from '@/api/chart'
import type { ChartData, TimeRangeOption } from '@/types/chart'

export const useChartStore = defineStore('chart', () => {
  // State
  const data = ref<ChartData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedRange = ref<TimeRangeOption>('all')
  const customStartDate = ref<string | null>(null)
  const customEndDate = ref<string | null>(null)
  const lastUpdate = ref<string | null>(null)

  // Getters
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)
  const chartData = computed(() => data.value)

  // Actions
  async function fetchData(range: TimeRangeOption = selectedRange.value) {
    loading.value = true
    error.value = null

    try {
      const { startDate, endDate } = calculateDateRange(range)
      const response = await chartApi.getChartData('sz.399317', startDate, endDate)
      data.value = response
      lastUpdate.value = response.last_update
      selectedRange.value = range
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取数据失败'
      console.error('获取图表数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function refreshData() {
    loading.value = true
    error.value = null

    try {
      await chartApi.refreshData('sz.399317')
      await fetchData(selectedRange.value)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '刷新数据失败'
      console.error('刷新数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  function setCustomDateRange(start: string | null, end: string | null) {
    customStartDate.value = start
    customEndDate.value = end
    if (start || end) {
      selectedRange.value = 'custom'
    }
  }

  function calculateDateRange(range: TimeRangeOption): { startDate: string | null; endDate: string | null } {
    const now = new Date()
    const endDate = now.toISOString().split('T')[0]
    let startDate: string | null = null

    switch (range) {
      case '5y':
        startDate = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate()).toISOString().split('T')[0]
        break
      case '3y':
        startDate = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate()).toISOString().split('T')[0]
        break
      case '1y':
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()).toISOString().split('T')[0]
        break
      case 'custom':
        startDate = customStartDate.value
        break
      case 'all':
      default:
        startDate = null
    }

    return { startDate, endDate }
  }

  return {
    data,
    loading,
    error,
    selectedRange,
    customStartDate,
    customEndDate,
    lastUpdate,
    isLoading,
    hasError,
    chartData,
    fetchData,
    refreshData,
    setCustomDateRange,
    calculateDateRange
  }
})
