<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="visible"
        class="modal-backdrop"
        @click.self="handleClose"
      >
        <div class="modal-container" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div class="modal-header">
            <h2 id="modal-title" class="modal-title">普通基民投资框架使用说明</h2>
            <button
              class="modal-close-btn"
              @click="handleClose"
              aria-label="关闭"
              title="关闭"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M5 5L15 15M15 5L5 15" stroke="#666" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="disclaimer-box">
              <strong>【声明】</strong>本内容仅作为投资策略参考，不构成任何具体的投资建议。投资者应根据自身风险承受能力、投资目标和财务状况做出独立的投资决策。
            </div>

            <section class="guide-section">
              <h3 class="section-title">
                <span class="section-number">一</span>
                定投策略执行规则
              </h3>
              <ol class="rule-list">
                <li>
                  当指数点位在五年均线的包络线上下轨<strong>之间</strong>时：执行<strong>正常定投</strong>计划，按预设标准金额进行定期投资
                </li>
                <li>
                  当指数点位<strong>高于</strong>五年均线+15%时：<strong>暂停定投</strong>或者<strong>根据自行情况减仓</strong>操作，将原定投资资金暂时配置于货币市场基金或短期债券型基金等低风险产品
                </li>
                <li>
                  当指数点位从高于五年均线+15%的状态<strong>回落至</strong>五年均线以内时：<strong>恢复正常</strong>定投计划
                </li>
                <li>
                  当指数点位<strong>低于</strong>五年均线-15%时：按预设标准金额执行<strong>加倍定投</strong>
                </li>
              </ol>
            </section>

            <section class="guide-section">
              <h3 class="section-title">
                <span class="section-number">二</span>
                资产配置与动态平衡策略
              </h3>
              <ol class="rule-list">
                <li>
                  <strong>固定周期再平衡</strong>，如一年一次、或半年一次
                </li>
                <li>
                  当指数点位<strong>显著高于</strong>五年均线+15%以上时：执行<strong>减仓</strong>操作，降低股票类资产配置比例，相应增加债券类资产配置，以降低整体权益风险敞口
                </li>
                <li>
                  当指数点位<strong>显著低于</strong>五年均线-15%以下时：执行<strong>加仓</strong>操作，提高股票类资产配置比例，相应减少债券类资产配置，以增加权益类资产仓位
                </li>
                <li>
                  当指数点位<strong>回归至</strong>五年均线附近（±5%区间内）时：执行一次<strong>完整的资产配置比例重置</strong>，将各类资产比例恢复至预设的目标配置比例
                </li>
              </ol>
            </section>

            <section class="guide-section">
              <h3 class="section-title">
                <span class="section-number">三</span>
                辅助判断工具
              </h3>
              <p class="section-text">
                在执行上述策略时，可结合 <strong>RSI</strong>（相对强弱指数）等技术指标的超买超卖信号进行综合判断，以提高策略执行的准确性和有效性。
              </p>
            </section>
          </div>

          <div class="modal-footer">
            <button class="modal-confirm-btn" @click="handleClose">
              我了解了
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

function handleClose() {
  emit('close')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.visible) {
    handleClose()
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 640px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.modal-close-btn:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
  -webkit-overflow-scrolling: touch;
}

.disclaimer-box {
  background: #fff8e6;
  border: 1px solid #f5d89a;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 13px;
  color: #7a5c10;
  line-height: 1.7;
  margin-bottom: 20px;
}

.disclaimer-box strong {
  color: #c17b00;
}

.guide-section {
  margin-bottom: 20px;
}

.guide-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #4472C4;
  color: white;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.section-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.section-list > li {
  font-size: 14px;
  color: #555;
  line-height: 1.75;
  padding: 6px 0;
  padding-left: 20px;
  position: relative;
}

.section-list > li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 13px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4472C4;
}

.section-list strong {
  color: #333;
}

.rule-list {
  counter-reset: rule-counter;
  list-style: none;
  padding: 0;
  margin: 0;
}

.rule-list > li {
  font-size: 14px;
  color: #555;
  line-height: 1.75;
  padding: 8px 0 8px 28px;
  position: relative;
  border-left: 2px solid #e8e8e8;
  padding-left: 28px;
}

.rule-list > li::before {
  counter-increment: rule-counter;
  content: counter(rule-counter);
  position: absolute;
  left: 0;
  top: 8px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4472C4;
  color: white;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.rule-list strong {
  color: #333;
}

.section-text {
  font-size: 14px;
  color: #555;
  line-height: 1.75;
  margin: 0;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.modal-confirm-btn {
  background: #4472C4;
  color: white;
  border: none;
  padding: 10px 40px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.modal-confirm-btn:hover {
  background: #3a62b0;
}

.modal-confirm-btn:active {
  transform: scale(0.97);
}

/* Transition */
.modal-fade-enter-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-active .modal-container {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-leave-active .modal-container {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-fade-enter-from {
  opacity: 0;
}

.modal-fade-enter-from .modal-container {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-leave-to .modal-container {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

/* 响应式 */
@media (max-width: 640px) {
  .modal-backdrop {
    padding: 0;
    align-items: flex-end;
  }

  .modal-container {
    max-width: 100%;
    max-height: 90vh;
    border-radius: 16px 16px 0 0;
  }

  .modal-header {
    padding: 16px 16px 12px;
  }

  .modal-title {
    font-size: 16px;
  }

  .modal-body {
    padding: 16px;
  }

  .modal-footer {
    padding: 12px 16px;
  }

  .modal-confirm-btn {
    width: 100%;
  }
}
</style>
