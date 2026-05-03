<template>
  <div class="dashboard">
    <!-- 头部 -->
    <header class="dashboard-header">
      <div class="header-content">
        <h1 class="header-title">国证A股指数五年之锚</h1>
        <TimeRangeSelector
          v-model="chartStore.selectedRange"
          v-model:customStart="chartStore.customStartDate"
          v-model:customEnd="chartStore.customEndDate"
          :loading="chartStore.loading"
          @change="handleRangeChange"
          @refresh="handleRefresh"
        />
      </div>
    </header>

    <!-- 主内容 -->
    <main class="dashboard-main">
      <div class="charts-container">
        <!-- 主图 -->
        <div class="chart-section main-chart-section">
          <LoadingOverlay :loading="chartStore.loading" />
          <MainChart :data="chartStore.data" />
        </div>

        <!-- RSI 图 -->
        <div class="chart-section">
          <LoadingOverlay :loading="chartStore.loading" />
          <RsiChart :data="chartStore.data" />
        </div>

        <!-- 回撤图 -->
        <div class="chart-section">
          <LoadingOverlay :loading="chartStore.loading" />
          <DrawdownChart :data="chartStore.data" />
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="dashboard-footer">
      <div class="footer-content">
        <p class="footer-text">
          数据来源: baostock | 
          更新时间: {{ chartStore.data?.last_update || '--' }}
        </p>
      </div>
    </footer>

    <!-- 错误提示 -->
    <div v-if="chartStore.error" class="error-toast">
      <span>{{ chartStore.error }}</span>
      <button class="error-close" @click="chartStore.error = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useChartStore } from '@/stores/chartStore'
import type { TimeRangeOption } from '@/types/chart'

import MainChart from '@/components/MainChart.vue'
import RsiChart from '@/components/RsiChart.vue'
import DrawdownChart from '@/components/DrawdownChart.vue'
import TimeRangeSelector from '@/components/TimeRangeSelector.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const chartStore = useChartStore()

function handleRangeChange(range: TimeRangeOption) {
  chartStore.fetchData(range)
}

function handleRefresh() {
  chartStore.refreshData()
}

onMounted(() => {
  chartStore.fetchData('all')
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

/* 头部 */
.dashboard-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
  white-space: nowrap;
}

/* 主内容 */
.dashboard-main {
  flex: 1;
  padding: 24px;
}

.charts-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-section {
  position: relative;
}

.main-chart-section {
  min-height: 450px;
}

/* 底部 */
.dashboard-footer {
  background: white;
  border-top: 1px solid #e0e0e0;
  padding: 12px 24px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-text {
  font-size: 12px;
  color: #999;
  margin: 0;
  text-align: center;
}

/* 错误提示 */
.error-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: #ff4444;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  animation: slideUp 0.3s ease;
}

.error-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .dashboard-header {
    padding: 12px 12px;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-title {
    font-size: 18px;
    text-align: center;
  }

  .dashboard-main {
    padding: 8px;
  }

  .charts-container {
    gap: 8px;
  }

  .main-chart-section {
    min-height: 300px;
  }

  .dashboard-footer {
    padding: 8px 12px;
  }
}
</style>
