<template>
  <div class="time-range-selector">
    <div class="range-buttons">
      <button
        v-for="option in rangeOptions"
        :key="option.value"
        :class="['range-btn', { active: modelValue === option.value }]"
        @click="selectRange(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div v-if="modelValue === 'custom'" class="custom-range">
      <input
        type="date"
        :value="customStart"
        @input="updateStartDate(($event.target as HTMLInputElement).value)"
        class="date-input"
      />
      <span class="range-separator">至</span>
      <input
        type="date"
        :value="customEnd"
        @input="updateEndDate(($event.target as HTMLInputElement).value)"
        class="date-input"
      />
      <button class="apply-btn" @click="applyCustomRange">应用</button>
    </div>

    <button class="refresh-btn" @click="openPasswordModal" :disabled="loading">
      <span class="refresh-icon" :class="{ spinning: loading }">↻</span>
      刷新
    </button>

    <!-- 密码验证弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showPasswordModal" class="pwd-backdrop" @click.self="cancelPassword">
          <div class="pwd-modal">
            <div class="pwd-header">
              <span class="pwd-title">请输入管理员密码</span>
              <button class="pwd-close" @click="cancelPassword">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M4 4L12 12M12 4L4 12" stroke="#666" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
            <div class="pwd-body">
              <input
                ref="passwordInputRef"
                v-model="passwordInput"
                type="password"
                class="pwd-input"
                placeholder="请输入密码"
                @keydown.enter="confirmPassword"
                @keydown.esc="cancelPassword"
              />
              <p v-if="pwdError" class="pwd-error">{{ pwdError }}</p>
            </div>
            <div class="pwd-footer">
              <button class="pwd-cancel-btn" @click="cancelPassword">取消</button>
              <button class="pwd-confirm-btn" @click="confirmPassword">确认</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import type { TimeRangeOption } from '@/types/chart'

const ADMIN_PASSWORD = 'admin123'

interface Props {
  modelValue: TimeRangeOption
  customStart: string | null
  customEnd: string | null
  loading: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: TimeRangeOption]
  'update:customStart': [value: string | null]
  'update:customEnd': [value: string | null]
  'change': [value: TimeRangeOption]
  'refresh': []
}>()

const rangeOptions = [
  { value: 'all' as TimeRangeOption, label: '全部' },
  { value: '5y' as TimeRangeOption, label: '5年' },
  { value: '3y' as TimeRangeOption, label: '3年' },
  { value: '1y' as TimeRangeOption, label: '1年' },
  { value: 'custom' as TimeRangeOption, label: '自定义' },
]

const localStart = ref(props.customStart)
const localEnd = ref(props.customEnd)

const showPasswordModal = ref(false)
const passwordInput = ref('')
const pwdError = ref('')
const passwordInputRef = ref<HTMLInputElement | null>(null)

function selectRange(value: TimeRangeOption) {
  emit('update:modelValue', value)
  if (value !== 'custom') {
    emit('change', value)
  }
}

function updateStartDate(value: string) {
  localStart.value = value || null
  emit('update:customStart', localStart.value)
}

function updateEndDate(value: string) {
  localEnd.value = value || null
  emit('update:customEnd', localEnd.value)
}

function applyCustomRange() {
  emit('change', 'custom')
}

async function openPasswordModal() {
  if (props.loading) return
  passwordInput.value = ''
  pwdError.value = ''
  showPasswordModal.value = true
  await nextTick()
  passwordInputRef.value?.focus()
}

function cancelPassword() {
  showPasswordModal.value = false
  passwordInput.value = ''
  pwdError.value = ''
}

function confirmPassword() {
  if (passwordInput.value === ADMIN_PASSWORD) {
    showPasswordModal.value = false
    passwordInput.value = ''
    pwdError.value = ''
    emit('refresh')
  } else {
    pwdError.value = '密码错误，请重新输入'
    passwordInput.value = ''
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && showPasswordModal.value) {
    cancelPassword()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.time-range-selector {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.range-buttons {
  display: flex;
  gap: 4px;
  background: #f0f0f0;
  padding: 4px;
  border-radius: 6px;
}

.range-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.range-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.range-btn.active {
  background: white;
  color: #333;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
}

.range-separator {
  color: #999;
  font-size: 13px;
}

.apply-btn {
  padding: 6px 12px;
  background: #4472C4;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.apply-btn:hover {
  background: #3a5fa8;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: auto;
}

.refresh-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #ccc;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  display: inline-block;
  font-size: 14px;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 密码弹窗 */
.pwd-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.pwd-modal {
  background: white;
  border-radius: 10px;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.pwd-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.pwd-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.pwd-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.pwd-close:hover {
  background: #f0f0f0;
}

.pwd-body {
  padding: 20px;
}

.pwd-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}

.pwd-input:focus {
  border-color: #4472C4;
}

.pwd-error {
  margin: 8px 0 0;
  font-size: 12px;
  color: #e54d42;
}

.pwd-footer {
  display: flex;
  gap: 10px;
  padding: 12px 20px 16px;
  justify-content: flex-end;
}

.pwd-cancel-btn {
  padding: 8px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.pwd-cancel-btn:hover {
  background: #f5f5f5;
}

.pwd-confirm-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  background: #4472C4;
  color: white;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.pwd-confirm-btn:hover {
  background: #3a5fa8;
}

/* 弹窗动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-active .pwd-modal,
.modal-fade-leave-active .pwd-modal {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .pwd-modal {
  transform: scale(0.95) translateY(-8px);
  opacity: 0;
}

.modal-fade-leave-to .pwd-modal {
  transform: scale(0.95) translateY(-8px);
  opacity: 0;
}

@media (max-width: 768px) {
  .time-range-selector {
    flex-direction: column;
    align-items: stretch;
  }

  .range-buttons {
    justify-content: center;
  }

  .custom-range {
    justify-content: center;
  }

  .refresh-btn {
    margin-left: 0;
    justify-content: center;
  }
}
</style>
