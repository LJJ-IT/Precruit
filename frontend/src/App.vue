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
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <a href="/" class="app-logo">Precruit</a>
      <span class="app-tagline">智能简历匹配</span>
    </header>

    <main class="app-main">
      <!-- Hero 区域（无结果时显示） -->
      <section v-if="!report" class="hero-section">
        <h1 class="hero-title">
          找到<span class="hero-accent">对的人</span>，<br />从一份简历开始。
        </h1>
        <p class="hero-desc">
          粘贴简历和职位描述，AI 多智能体协作分析，从技能、文化、竞争力多维度评估匹配度。
        </p>
      </section>

      <InputPanel
        :loading="loading"
        @result="handleResult"
        @error="handleError"
        @update:loading="loading = $event"
      />

      <transition name="fade-slide">
        <el-alert
          v-if="error"
          :title="error"
          type="error"
          show-icon
          closable
          class="error-alert"
          @close="error = ''"
        />
      </transition>

      <transition name="fade-slide">
        <ResultPanel
          v-if="report"
          :report="report"
          @reset="handleReset"
        />
      </transition>
    </main>

    <footer class="app-footer">
      <div class="footer-rule"></div>
      <p>Precruit &copy; 2026 &middot; Powered by LangChain + DeepSeek</p>
    </footer>
  </div>
</template>

<style>
/* ═══════════════════════════════════════════
   Design Tokens — Warm Editorial
   ═══════════════════════════════════════════ */
:root {
  --bg: #f9f6f0;
  --surface: #ffffff;
  --surface-hover: #f5f1ea;
  --text: #2c2416;
  --text-secondary: #8c7b6a;
  --text-muted: #bfb5a6;
  --border: #e8e2d6;
  --border-light: #f0ebe2;

  --accent: #b8834c;
  --accent-hover: #9c6d3c;
  --accent-subtle: rgba(184, 131, 76, 0.08);

  --success: #5d8a5e;
  --success-bg: #ecf5ec;
  --warning: #c4943a;
  --warning-bg: #fdf6ed;
  --danger: #c4665a;
  --danger-bg: #fdf0ee;

  --font-display: 'Playfair Display', 'Times New Roman', serif;
  --font-body: 'DM Sans', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;

  --radius: 2px;
  --radius-md: 4px;

  --shadow-subtle: 0 1px 3px rgba(44, 36, 22, 0.04);
  --shadow-medium: 0 4px 16px rgba(44, 36, 22, 0.06);
}

/* ── Reset & Base ── */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.65;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Subtle noise texture overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* ── App Layout ── */
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Header ── */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 32px;
  height: 52px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(249, 246, 240, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.app-logo {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  font-style: italic;
  color: var(--text);
  text-decoration: none;
  letter-spacing: -0.01em;
}

.app-tagline {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

/* ── Hero ── */
.hero-section {
  text-align: center;
  padding: 40px 0 32px;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--text);
  margin-bottom: 16px;
}

.hero-accent {
  color: var(--accent);
  font-style: italic;
}

.hero-desc {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 480px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ── Main ── */
.app-main {
  flex: 1;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.error-alert {
  margin-top: 20px;
}

/* ── Footer ── */
.app-footer {
  text-align: center;
  padding: 32px 24px;
}

.footer-rule {
  width: 40px;
  height: 1px;
  background: var(--border);
  margin: 0 auto 16px;
}

.app-footer p {
  font-family: var(--font-body);
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

/* ── Transitions ── */
.fade-slide-enter-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-slide-leave-active {
  transition: all 0.25s ease-in;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ── Element Plus overrides ── */
.el-card {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: none !important;
}

.el-button--primary {
  --el-button-bg-color: var(--accent);
  --el-button-border-color: var(--accent);
  --el-button-hover-bg-color: var(--accent-hover);
  --el-button-hover-border-color: var(--accent-hover);
  --el-button-active-bg-color: var(--accent-hover);
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-weight: 500;
  letter-spacing: 0.01em;
}

.el-button {
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-weight: 500;
}

.el-textarea__inner {
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.7;
  resize: vertical;
  border-color: var(--border);
  background: var(--surface);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.el-textarea__inner:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-subtle);
}

.el-textarea__inner::placeholder {
  color: var(--text-muted);
}

.el-tabs__header {
  border-bottom-color: var(--border) !important;
}

.el-tabs__item {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

.el-tabs__item.is-active {
  color: var(--text);
  font-weight: 600;
}

.el-tabs__active-bar {
  background-color: var(--accent) !important;
  height: 2px !important;
}

.el-tag {
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-weight: 500;
  border: none;
}

.el-empty__description {
  color: var(--text-muted);
  font-family: var(--font-body);
}

.el-alert--error {
  background: var(--danger-bg);
  border: 1px solid #f0d5d2;
}

.el-progress-bar__outer {
  background: var(--border);
}
</style>
