<script setup>
import { ref, reactive } from 'vue'
import { submitAnalysisStream } from '../api/analysis.js'

const emit = defineEmits(['result', 'error', 'update:loading'])

defineProps({
  loading: Boolean,
})

const resumeText = ref('')
const jdText = ref('')

// 进度步骤列表 — 定义全部可能的步骤及其顺序
const STEP_ORDER = [
  '解析文档',
  '并行分析',
  '综合评分',
]
const STEP_LABELS = {
  '解析文档': '文档解析智能体',
  '并行分析': '技能匹配 + 文化匹配智能体',
  '综合评分': '综合评分智能体（含邮件）',
}

const progress = reactive({
  active: false,
  currentStep: '',
  completedSteps: [],
})

async function handleSubmit() {
  if (!resumeText.value.trim()) {
    emit('error', '请粘贴简历内容')
    return
  }
  if (!jdText.value.trim() || jdText.value.trim().length < 50) {
    emit('error', '职位描述至少 50 个字符')
    return
  }

  emit('update:loading', true)
  emit('error', '')

  // 重置进度
  progress.active = true
  progress.currentStep = ''
  progress.completedSteps = []

  try {
    await submitAnalysisStream(
      resumeText.value.trim(),
      jdText.value.trim(),
      // onProgress
      (event) => {
        progress.currentStep = event.step
        // 标记已完成的步骤
        const idx = STEP_ORDER.indexOf(event.step)
        if (idx > 0) {
          progress.completedSteps = STEP_ORDER.slice(0, idx)
        }
      },
      // onResult
      (data) => {
        progress.active = false
        emit('result', { success: true, data })
      },
      // onError
      (msg) => {
        progress.active = false
        emit('error', msg)
      },
    )
  } catch (err) {
    progress.active = false
    const msg = err.message || '请求失败，请检查服务是否启动'
    emit('error', msg)
  } finally {
    emit('update:loading', false)
  }
}

function handleClear() {
  resumeText.value = ''
  jdText.value = ''
}
</script>

<template>
  <div class="input-panel">
    <!-- 进度指示器 -->
    <transition name="fade">
      <div v-if="progress.active" class="progress-bar">
        <div class="progress-steps">
          <div
            v-for="step in STEP_ORDER"
            :key="step"
            class="progress-step"
            :class="{
              done: progress.completedSteps.includes(step),
              current: progress.currentStep === step,
            }"
          >
            <span class="progress-dot">
              <span v-if="progress.completedSteps.includes(step)" class="dot-check">&#10003;</span>
              <span v-else-if="progress.currentStep === step" class="dot-pulse"></span>
              <span v-else class="dot-empty"></span>
            </span>
            <span class="progress-label">
              {{ STEP_LABELS[step] || step }}
            </span>
          </div>
        </div>
      </div>
    </transition>

    <div class="input-grid">
      <!-- 简历 — 01 -->
      <div class="input-group">
        <div class="input-head">
          <span class="section-num">01</span>
          <label class="input-label">简历内容</label>
        </div>
        <el-input
          v-model="resumeText"
          type="textarea"
          :rows="15"
          placeholder="粘贴简历全文……

张三 · 高级工程师 · 138-0000-0000 · email@example.com

技能
Python, FastAPI, PostgreSQL, Docker, Kubernetes

工作经历
高级工程师  |  某科技公司  |  2021 — 至今
负责核心系统架构设计与开发……"
        />
        <span class="char-count">{{ resumeText.length }} 字符</span>
      </div>

      <!-- JD — 02 -->
      <div class="input-group">
        <div class="input-head">
          <span class="section-num">02</span>
          <label class="input-label">职位描述</label>
        </div>
        <el-input
          v-model="jdText"
          type="textarea"
          :rows="15"
          placeholder="粘贴职位描述全文……

高级工程师

公司: 某科技  |  地点: 北京

岗位职责
负责公司核心产品的后端架构设计和开发

任职要求
5 年以上开发经验，熟悉主流框架"
        />
        <span class="char-count">{{ jdText.length }} 字符</span>
      </div>
    </div>

    <!-- 操作区域 -->
    <div class="action-row">
      <button
        class="submit-btn"
        :class="{ loading: progress.active }"
        :disabled="!resumeText.trim() || !jdText.trim() || progress.active"
        @click="handleSubmit"
      >
        <span class="submit-btn-text">{{ progress.active ? '分析中' : '开始匹配' }}</span>
        <span v-if="!progress.active" class="submit-btn-arrow">&rarr;</span>
        <span v-else class="submit-btn-dot"></span>
      </button>
      <button
        class="clear-btn"
        @click="handleClear"
        :disabled="!resumeText && !jdText"
      >
        清空全部
      </button>
    </div>
  </div>
</template>

<style scoped>
.input-panel {
  margin-bottom: 32px;
}

/* ── Progress Bar ── */
.progress-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.progress-steps {
  display: flex;
  align-items: center;
  gap: 40px;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.35;
  transition: opacity 0.3s;
}

.progress-step.current {
  opacity: 1;
}

.progress-step.done {
  opacity: 0.6;
}

.progress-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.dot-empty {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border);
  display: block;
}

.dot-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  display: block;
  animation: dot-pulse 0.8s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.3); opacity: 1; }
}

.dot-check {
  font-size: 11px;
  color: var(--success);
  font-weight: 700;
}

.progress-label {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* ── Grid ── */
.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* ── Section Header ── */
.input-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
}

.section-num {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  font-style: italic;
  color: var(--accent);
  line-height: 1;
  opacity: 0.7;
}

.input-label {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

/* ── Char Count ── */
.char-count {
  text-align: right;
  font-family: var(--font-body);
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 6px;
  letter-spacing: 0.03em;
  font-variant-numeric: tabular-nums;
}

/* ── Action Row ── */
.action-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
}

/* ── Submit Button ── */
.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--text);
  color: var(--surface);
  border: none;
  padding: 12px 28px;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.01em;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #3d3428;
  box-shadow: 0 4px 20px rgba(44, 36, 22, 0.15);
  transform: translateY(-1px);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.submit-btn.loading {
  background: var(--accent);
}

.submit-btn-text {
  z-index: 1;
}

.submit-btn-arrow {
  font-family: var(--font-display);
  font-size: 18px;
  transition: transform 0.2s;
  z-index: 1;
}

.submit-btn:hover:not(:disabled) .submit-btn-arrow {
  transform: translateX(3px);
}

.submit-btn-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--surface);
  animation: pulse 0.8s ease-in-out infinite;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* ── Clear Button ── */
.clear-btn {
  background: none;
  border: none;
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  letter-spacing: 0.02em;
  transition: color 0.2s;
  padding: 4px 0;
}

.clear-btn:hover:not(:disabled) {
  color: var(--text-secondary);
}

.clear-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

/* ── Transitions ── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ── Responsive ── */
@media (max-width: 680px) {
  .input-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .progress-steps {
    flex-wrap: wrap;
    gap: 16px;
    justify-content: center;
  }
}
</style>
