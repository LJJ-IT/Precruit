<script setup>
import { computed } from 'vue'

const props = defineProps({
  report: { type: Object, required: true },
})

const emit = defineEmits(['reset'])

const scoreColor = computed(() => {
  const s = props.report.final_score || 0
  if (s >= 80) return 'var(--success)'
  if (s >= 60) return 'var(--warning)'
  return 'var(--danger)'
})

const scoreLabel = computed(() => {
  const s = props.report.final_score || 0
  if (s >= 80) return '高度匹配'
  if (s >= 60) return '基本匹配'
  return '匹配度低'
})

const scoreVerdict = computed(() => {
  const s = props.report.final_score || 0
  if (s >= 80) return '建议发送面试邀请'
  if (s >= 60) return '可进入备选池，建议进一步沟通'
  return '暂不推荐，可关注其他候选人'
})

const scoreBars = computed(() => [
  { label: '硬实力', score: props.report.hard_skill_score || 0 },
  { label: '文化匹配', score: props.report.culture_fit_score || 0 },
  { label: '完整度', score: props.report.completeness_score || 0 },
  { label: '竞争力', score: props.report.competitiveness_score || 0 },
])

const skillMatch = computed(() => props.report.hard_skill || {})
const cultureFit = computed(() => props.report.culture_fit || {})
const github = computed(() => skillMatch.value.github || {})
</script>

<template>
  <div class="result-panel">
    <!-- ═══ 评分 Hero ═══ -->
    <section class="score-hero">
      <div class="score-hero-main">
        <p class="score-overline">匹配分析报告</p>
        <div class="score-big-row">
          <span class="score-number">{{ report.final_score || 0 }}</span>
          <span class="score-unit">/ 100</span>
        </div>
        <div class="score-meta">
          <span class="score-label-tag" :class="scoreLabel">{{ scoreLabel }}</span>
          <span class="score-verdict">{{ scoreVerdict }}</span>
        </div>
        <p v-if="report.email_sent" class="email-notice">
          已向 {{ report.candidate_email }} 发送面试邀请
        </p>
      </div>

      <!-- 候选人信息 -->
      <div class="score-hero-side">
        <p class="candidate-name">{{ report.candidate_name || '未知候选人' }}</p>
        <p class="candidate-pos">{{ report.company || '未知公司' }} &middot; {{ report.position || '未知职位' }}</p>
      </div>
    </section>

    <!-- ═══ 维度条形图 ═══ -->
    <section class="score-bars">
      <div
        v-for="bar in scoreBars"
        :key="bar.label"
        class="score-bar-item"
      >
        <div class="score-bar-head">
          <span class="score-bar-label">{{ bar.label }}</span>
          <span class="score-bar-value">{{ bar.score }}</span>
        </div>
        <div class="score-bar-track">
          <div
            class="score-bar-fill"
            :style="{ width: bar.score + '%' }"
          ></div>
        </div>
      </div>
    </section>

    <!-- ═══ 详情 Tabs ═══ -->
    <section class="detail-section">
      <el-tabs>
        <el-tab-pane label="技能评估">
          <div class="detail-grid">
            <div class="detail-block">
              <h4 class="detail-heading">已匹配技能</h4>
              <div class="tag-row">
                <span v-for="s in skillMatch.matched_skills" :key="s" class="tag tag-ok">{{ s }}</span>
                <span v-if="!skillMatch.matched_skills?.length" class="no-data">暂无</span>
              </div>
            </div>

            <div class="detail-block">
              <h4 class="detail-heading">缺失技能</h4>
              <div class="tag-row">
                <span v-for="s in skillMatch.missing_skills" :key="s" class="tag tag-bad">{{ s }}</span>
                <span v-if="!skillMatch.missing_skills?.length" class="no-data">暂无</span>
              </div>
            </div>

            <div class="detail-block">
              <h4 class="detail-heading">项目经历</h4>
              <ul class="bullet-list">
                <li v-for="p in skillMatch.matched_projects" :key="p">{{ p }}</li>
                <li v-if="!skillMatch.matched_projects?.length" class="no-data">暂无</li>
              </ul>
            </div>

            <div class="detail-block">
              <h4 class="detail-heading">优势</h4>
              <ul class="bullet-list">
                <li v-for="s in skillMatch.strengths" :key="s">{{ s }}</li>
              </ul>
            </div>

            <div class="detail-block">
              <h4 class="detail-heading">待提升</h4>
              <ul class="bullet-list bullet-negative">
                <li v-for="g in skillMatch.gaps" :key="g">{{ g }}</li>
              </ul>
            </div>
          </div>

          <!-- GitHub -->
          <div v-if="github.available" class="github-card">
            <p class="github-card-title">GitHub 评估 &mdash; +{{ github.score }} 分</p>
            <p class="github-card-line">活跃度 {{ github.activity_level }}</p>
            <p v-if="github.top_repos?.length" class="github-card-line">{{ github.top_repos.join(' &middot; ') }}</p>
            <p class="github-card-line">{{ github.summary }}</p>
          </div>
        </el-tab-pane>

        <el-tab-pane label="文化匹配">
          <div class="detail-grid cols-2">
            <div class="detail-block">
              <h4 class="detail-heading">公司文化</h4>
              <p class="body-text">{{ cultureFit.company_culture || '暂无数据' }}</p>
            </div>
            <div class="detail-block">
              <h4 class="detail-heading">主营业务</h4>
              <p class="body-text">{{ cultureFit.company_business || '暂无数据' }}</p>
            </div>
          </div>

          <div class="detail-block">
            <h4 class="detail-heading">候选人画像</h4>
            <p class="body-text">{{ cultureFit.candidate_profile || '暂无数据' }}</p>
          </div>

          <div class="detail-grid cols-2">
            <div class="detail-block">
              <h4 class="detail-heading">匹配点</h4>
              <ul class="bullet-list">
                <li v-for="p in cultureFit.match_points" :key="p">{{ p }}</li>
              </ul>
            </div>
            <div class="detail-block">
              <h4 class="detail-heading">风险点</h4>
              <ul class="bullet-list bullet-negative">
                <li v-for="r in cultureFit.risk_points" :key="r">{{ r }}</li>
              </ul>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="优化建议">
          <el-empty v-if="!report.optimization_suggestions?.length" description="暂无建议" />
          <ol v-else class="numbered-list">
            <li v-for="(tip, i) in report.optimization_suggestions" :key="i">{{ tip }}</li>
          </ol>
        </el-tab-pane>

        <el-tab-pane label="面试问题">
          <el-empty v-if="!report.interview_questions?.length" description="暂无问题" />
          <ol v-else class="numbered-list">
            <li v-for="(q, i) in report.interview_questions" :key="i">{{ q }}</li>
          </ol>
        </el-tab-pane>
      </el-tabs>
    </section>

    <!-- ═══ 综合评价 ═══ -->
    <section class="summary-section">
      <div class="summary-layout">
        <div class="summary-main">
          <h3 class="summary-heading">综合评价</h3>
          <p class="body-text">{{ report.overall_summary || '暂无' }}</p>
        </div>
        <aside class="summary-risks">
          <h3 class="summary-heading">风险</h3>
          <ul v-if="report.risk_flags?.length" class="risk-list">
            <li v-for="f in report.risk_flags" :key="f">{{ f }}</li>
          </ul>
          <p v-else class="no-data">无风险标记</p>
        </aside>
      </div>

      <div class="reset-row">
        <div class="reset-rule"></div>
        <button class="reset-btn" @click="emit('reset')">
          开始新的分析 &rarr;
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.result-panel {
  animation: result-enter 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes result-enter {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ═══ Score Hero ═══ */
.score-hero {
  display: flex;
  align-items: flex-start;
  gap: 48px;
  padding: 40px 0 32px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
}

.score-hero-main {
  flex-shrink: 0;
}

.score-overline {
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.score-big-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-number {
  font-family: var(--font-display);
  font-size: 96px;
  font-weight: 700;
  font-style: italic;
  line-height: 1;
  color: var(--text);
  letter-spacing: -0.03em;
}

.score-unit {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--text-muted);
  font-weight: 400;
}

.score-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
}

.score-label-tag {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.score-label-tag.高度匹配 {
  background: var(--success-bg);
  color: var(--success);
}

.score-label-tag.基本匹配 {
  background: var(--warning-bg);
  color: var(--warning);
}

.score-label-tag.匹配度低 {
  background: var(--danger-bg);
  color: var(--danger);
}

.score-verdict {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
}

.email-notice {
  margin-top: 8px;
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--success);
  font-weight: 500;
}

/* ── Candidate Info ── */
.score-hero-side {
  flex: 1;
  padding-top: 24px;
}

.candidate-name {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
  line-height: 1.2;
  margin-bottom: 6px;
}

.candidate-pos {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ═══ Score Bars ═══ */
.score-bars {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 32px;
}

.score-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.score-bar-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.score-bar-label {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

.score-bar-value {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  font-style: italic;
}

.score-bar-track {
  height: 4px;
  background: var(--border);
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  background: var(--accent);
  transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ═══ Detail Section ═══ */
.detail-section {
  margin-bottom: 24px;
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-grid.cols-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.detail-block {
  min-width: 0;
}

.detail-heading {
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
}

/* ── Tags ── */
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
}

.tag-ok {
  background: var(--success-bg);
  color: var(--success);
}

.tag-bad {
  background: var(--danger-bg);
  color: var(--danger);
}

/* ── Lists ── */
.bullet-list {
  list-style: none;
  padding: 0;
}

.bullet-list li {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
  padding: 6px 0;
  border-bottom: 1px solid var(--border-light);
  line-height: 1.5;
}

.bullet-negative li {
  color: #9b554c;
}

.numbered-list {
  padding-left: 0;
  list-style: none;
  counter-reset: item;
}

.numbered-list li {
  counter-increment: item;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
  line-height: 1.55;
  display: flex;
  gap: 14px;
}

.numbered-list li::before {
  content: counter(item, decimal-leading-zero);
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  font-style: italic;
  color: var(--accent);
  flex-shrink: 0;
  opacity: 0.7;
}

.no-data {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
}

.body-text {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* ── GitHub ── */
.github-card {
  margin-top: 20px;
  background: var(--surface-hover);
  padding: 16px;
  border-left: 2px solid var(--accent);
}

.github-card-title {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.github-card-line {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-secondary);
  margin: 2px 0;
}

/* ═══ Summary ═══ */
.summary-section {
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.summary-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
}

.summary-heading {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  font-style: italic;
  color: var(--text);
  letter-spacing: -0.01em;
  margin-bottom: 14px;
}

.risk-list {
  list-style: none;
  padding: 0;
}

.risk-list li {
  font-family: var(--font-body);
  font-size: 12px;
  color: #9b554c;
  padding: 4px 0;
  line-height: 1.5;
}

/* ── Reset ── */
.reset-row {
  margin-top: 36px;
  text-align: center;
}

.reset-rule {
  width: 100%;
  height: 1px;
  background: var(--border-light);
  margin-bottom: 20px;
}

.reset-btn {
  background: none;
  border: 1px solid var(--border);
  padding: 10px 32px;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.02em;
}

.reset-btn:hover {
  border-color: var(--text);
  color: var(--text);
}

/* ── Responsive ── */
@media (max-width: 680px) {
  .score-hero {
    flex-direction: column;
    gap: 24px;
  }

  .score-number {
    font-size: 64px;
  }

  .summary-layout {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .detail-grid.cols-2 {
    grid-template-columns: 1fr;
  }
}
</style>
