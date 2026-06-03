<script setup>
import { ref } from 'vue'
import InputPanel from './components/InputPanel.vue'
import ResultPanel from './components/ResultPanel.vue'

const loading = ref(false)
const report = ref(null)
const error = ref('')

function handleResult(data) {
  if (data.success) {
    report.value = data.data
    error.value = ''
  } else {
    error.value = data.error || '分析失败'
    report.value = null
  }
}

function handleError(msg) {
  error.value = msg
  report.value = null
}

function handleReset() {
  report.value = null
  error.value = ''
}
</script>

<template>
  <div class="app-container">
    <!-- 头部 -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <el-icon :size="28"><Document /></el-icon>
          Precruit
        </h1>
        <span class="app-subtitle">简历与招聘JD智能匹配平台</span>
      </div>
    </header>

    <!-- 主体 -->
    <main class="app-main">
      <InputPanel
        :loading="loading"
        @result="handleResult"
        @error="handleError"
        @update:loading="loading = $event"
      />

      <!-- 错误信息 -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        closable
        class="error-alert"
        @close="error = ''"
      />

      <!-- 结果面板 -->
      <ResultPanel
        v-if="report"
        :report="report"
        @reset="handleReset"
      />
    </main>

    <!-- 底部 -->
    <footer class="app-footer">
      <span>Precruit © 2026 | Powered by LangChain + DeepSeek</span>
    </footer>
  </div>
</template>

<style>
/* ── 全局样式 ── */
:root {
  --primary: #409eff;
  --success: #67c23a;
  --warning: #e6a23c;
  --danger: #f56c6c;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Microsoft YaHei', sans-serif;
  background: #f0f2f5;
  color: #333;
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── 头部 ── */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-subtitle {
  font-size: 14px;
  opacity: 0.85;
}

/* ── 主体 ── */
.app-main {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 24px auto;
  padding: 0 24px;
}

.error-alert {
  margin-top: 16px;
}

/* ── 底部 ── */
.app-footer {
  text-align: center;
  padding: 16px;
  color: #999;
  font-size: 12px;
  border-top: 1px solid #e8e8e8;
}
</style>
