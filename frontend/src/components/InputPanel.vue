<script setup>
import { ref } from 'vue'
import { submitAnalysis } from '../api/analysis.js'

const emit = defineEmits(['result', 'error', 'update:loading'])

defineProps({
  loading: Boolean,
})

const resumeText = ref('')
const jdText = ref('')

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

  try {
    const data = await submitAnalysis(resumeText.value.trim(), jdText.value.trim())
    emit('result', data)
  } catch (err) {
    const msg = err.response?.data?.detail || err.message || '请求失败，请检查服务是否启动'
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
        :class="{ loading }"
        :disabled="!resumeText.trim() || !jdText.trim() || loading"
        @click="handleSubmit"
      >
        <span class="submit-btn-text">{{ loading ? '分析中' : '开始匹配' }}</span>
        <span v-if="!loading" class="submit-btn-arrow">&rarr;</span>
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

/* Loading dot pulse */
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

/* ── Responsive ── */
@media (max-width: 680px) {
  .input-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>
