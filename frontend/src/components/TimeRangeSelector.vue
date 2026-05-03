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
    
    <button class="refresh-btn" @click="refresh" :disabled="loading">
      <span class="refresh-icon" :class="{ spinning: loading }">↻</span>
      刷新
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { TimeRangeOption } from '@/types/chart'

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

watch(() => props.customStart, (val) => { localStart.value = val })
watch(() => props.customEnd, (val) => { localEnd.value = val })

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

function refresh() {
  emit('refresh')
}
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
