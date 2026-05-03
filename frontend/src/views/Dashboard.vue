<template>
  <div class="dashboard">
    <!-- 头部 -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="header-title">国证A股指数五年之锚</h1>
          <button class="guide-btn" @click="showGuide = true" title="使用说明">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="guide-icon">
              <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.2"/>
              <path d="M8 4.5V4.51" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M8 7.5V11.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            <span class="guide-btn-text">使用说明</span>
          </button>
        </div>
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

    <!-- 使用说明弹窗 -->
    <UsageGuideModal :visible="showGuide" @close="showGuide = false" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useChartStore } from '@/stores/chartStore'
import type { TimeRangeOption } from '@/types/chart'

import MainChart from '@/components/MainChart.vue'
import RsiChart from '@/components/RsiChart.vue'
import DrawdownChart from '@/components/DrawdownChart.vue'
import TimeRangeSelector from '@/components/TimeRangeSelector.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import UsageGuideModal from '@/components/UsageGuideModal.vue'

const chartStore = useChartStore()
const showGuide = ref(false)

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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
  white-space: nowrap;
}

.guide-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  background: #fafafa;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.guide-btn:hover {
  background: #4472C4;
  border-color: #4472C4;
  color: white;
}

.guide-btn:active {
  transform: scale(0.97);
}

.guide-icon {
  flex-shrink: 0;
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

  .header-left {
    justify-content: center;
  }

  .header-title {
    font-size: 18px;
    text-align: center;
  }

  .guide-btn-text {
    display: none;
  }

  .guide-btn {
    padding: 5px 8px;
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
