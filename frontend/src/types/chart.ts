export interface ChartData {
  dates: string[]
  index_values: number[]
  sma1210: (number | null)[]
  upper_band: (number | null)[]
  lower_band: (number | null)[]
  deviation_rate: number | null
  rsi_dates: string[]
  rsi14: (number | null)[]
  rsi_daily: (number | null)[]
  current_rsi: number | null
  drawdown_5y: (number | null)[]
  min_drawdown: number | null
  last_update: string
}

export interface HealthStatus {
  status: string
  last_update: string | null
  message: string
}

export interface TimeRange {
  start_date: string | null
  end_date: string | null
  label: string
}

export type TimeRangeOption = 'all' | '5y' | '3y' | '1y' | 'custom'

export interface ChartState {
  data: ChartData | null
  loading: boolean
  error: string | null
  selectedRange: TimeRangeOption
  customStartDate: string | null
  customEndDate: string | null
}
