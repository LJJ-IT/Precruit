<script setup>
import { computed } from 'vue'

const props = defineProps({
  report: { type: Object, required: true },
})

const emit = defineEmits(['reset'])

const scoreColor = computed(() => {
  const s = props.report.final_score || 0
  if (s >= 80) return '#67c23a'
  if (s >= 60) return '#e6a23c'
  return '#f56c6c'
})

const activeTab = computed(() => {
  return 'skills'
})

// 分数卡片配置
const scoreCards = computed(() => [
  { label: '硬实力', score: props.report.hard_skill_score, icon: 'CPU', color: '#409eff' },
  { label: '文化匹配', score: props.report.culture_fit_score, icon: 'Connection', color: '#67c23a' },
  { label: '简历完整度', score: props.report.completeness_score, icon: 'DocumentChecked', color: '#e6a23c' },
  { label: '综合竞争力', score: props.report.competitiveness_score, icon: 'TrendCharts', color: '#764ba2' },
])

// 技能匹配数据
const skillMatch = computed(() => props.report.hard_skill || {})
const cultureFit = computed(() => props.report.culture_fit || {})

// GitHub 数据
const github = computed(() => skillMatch.value.github || {})
</script>

<template>
  <div class="result-panel">
    <!-- 评分总览 -->
    <el-card shadow="hover" class="score-overview">
      <div class="score-main">
        <!-- 最终得分环形图 -->
        <div class="score-ring-wrapper">
          <el-progress
            type="dashboard"
            :percentage="report.final_score || 0"
            :color="scoreColor"
            :stroke-width="14"
            :width="180"
          >
            <template #default="{ percentage }">
              <div class="ring-content">
                <span class="ring-score">{{ percentage }}<small>分</small></span>
                <el-tag
                  :type="percentage >= 80 ? 'success' : percentage >= 60 ? 'warning' : 'danger'"
                  size="large"
                  effect="dark"
                >
                  {{ percentage >= 80 ? '通过' : percentage >= 60 ? '接近' : '不匹配' }}
                </el-tag>
              </div>
            </template>
          </el-progress>
        </div>

        <!-- 基本信息 -->
        <div class="score-info">
          <h2 class="candidate-name">
            {{ report.candidate_name || '未知' }}
            <el-tag v-if="report.email_sent" type="success" size="small">已发面试邀请</el-tag>
          </h2>
          <p class="position-info">
            <el-icon><OfficeBuilding /></el-icon>
            {{ report.company || '未知公司' }} — {{ report.position || '未知职位' }}
          </p>
          <div class="score-cards">
            <div
              v-for="card in scoreCards"
              :key="card.label"
              class="score-card"
              :style="{ borderColor: card.color }"
            >
              <el-icon :size="20" :color="card.color"><component :is="card.icon" /></el-icon>
              <span class="card-label">{{ card.label }}</span>
              <span class="card-score" :style="{ color: card.color }">{{ card.score }}<small>分</small></span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 详情 tabs -->
    <el-card shadow="hover" class="detail-card">
      <el-tabs type="border-card">
        <!-- 技能匹配 -->
        <el-tab-pane>
          <template #label>
            <span><el-icon><Connection /></el-icon> 技能匹配</span>
          </template>

          <div class="tab-section">
            <h4>已匹配技能</h4>
            <div class="tag-group">
              <el-tag
                v-for="s in skillMatch.matched_skills"
                :key="s"
                type="success"
                effect="plain"
                class="skill-tag"
              >{{ s }}</el-tag>
              <span v-if="!skillMatch.matched_skills?.length" class="empty-hint">无</span>
            </div>
          </div>

          <div class="tab-section">
            <h4>缺失技能</h4>
            <div class="tag-group">
              <el-tag
                v-for="s in skillMatch.missing_skills"
                :key="s"
                type="danger"
                effect="plain"
                class="skill-tag"
              >{{ s }}</el-tag>
              <span v-if="!skillMatch.missing_skills?.length" class="empty-hint">无</span>
            </div>
          </div>

          <div class="tab-section">
            <h4>匹配项目经历</h4>
            <ul class="text-list">
              <li v-for="p in skillMatch.matched_projects" :key="p">{{ p }}</li>
              <li v-if="!skillMatch.matched_projects?.length" class="empty-hint">无</li>
            </ul>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="tab-section">
                <h4>✊ 优势</h4>
                <ul class="text-list">
                  <li v-for="s in skillMatch.strengths" :key="s">{{ s }}</li>
                </ul>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="tab-section">
                <h4>⚠️ 不足</h4>
                <ul class="text-list">
                  <li v-for="g in skillMatch.gaps" :key="g">{{ g }}</li>
                </ul>
              </div>
            </el-col>
          </el-row>

          <!-- GitHub -->
          <div v-if="github.available" class="tab-section github-box">
            <h4>
              <el-icon><Star /></el-icon> GitHub 评估
              <el-tag :type="github.score >= 70 ? 'success' : 'warning'" size="small">
                {{ github.score }} 分
              </el-tag>
            </h4>
            <p>活跃度: {{ github.activity_level }}</p>
            <p v-if="github.top_repos?.length">代表仓库: {{ github.top_repos.join(', ') }}</p>
            <p>{{ github.summary }}</p>
          </div>
        </el-tab-pane>

        <!-- 文化匹配 -->
        <el-tab-pane>
          <template #label>
            <span><el-icon><UserFilled /></el-icon> 文化匹配</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="tab-section">
                <h4>公司文化画像</h4>
                <p class="desc-text">{{ cultureFit.company_culture || '未知' }}</p>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="tab-section">
                <h4>主营业务方向</h4>
                <p class="desc-text">{{ cultureFit.company_business || '未知' }}</p>
              </div>
            </el-col>
          </el-row>

          <div class="tab-section">
            <h4>候选人软性画像</h4>
            <p class="desc-text">{{ cultureFit.candidate_profile || '未知' }}</p>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="tab-section">
                <h4>✅ 匹配点</h4>
                <ul class="text-list">
                  <li v-for="p in cultureFit.match_points" :key="p">{{ p }}</li>
                </ul>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="tab-section">
                <h4>⚠️ 风险点</h4>
                <ul class="text-list">
                  <li v-for="r in cultureFit.risk_points" :key="r" class="text-danger">{{ r }}</li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 优化建议 -->
        <el-tab-pane>
          <template #label>
            <span><el-icon><EditPen /></el-icon> 简历优化建议</span>
          </template>

          <el-empty v-if="!report.optimization_suggestions?.length" description="暂无建议" />
          <div v-else class="tab-section">
            <el-timeline>
              <el-timeline-item
                v-for="(tip, i) in report.optimization_suggestions"
                :key="i"
                :type="i === 0 ? 'primary' : 'info'"
                :hollow="i !== 0"
              >
                {{ tip }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-tab-pane>

        <!-- 面试问题 -->
        <el-tab-pane>
          <template #label>
            <span><el-icon><ChatLineSquare /></el-icon> 建议面试问题</span>
          </template>

          <el-empty v-if="!report.interview_questions?.length" description="暂无问题" />
          <div v-else class="tab-section">
            <el-timeline>
              <el-timeline-item
                v-for="(q, i) in report.interview_questions"
                :key="i"
                :type="i === 0 ? 'primary' : 'info'"
                :hollow="i !== 0"
              >
                {{ q }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 综合评价 + 风险 -->
    <el-card shadow="hover" class="summary-card">
      <el-row :gutter="20">
        <el-col :span="16">
          <h4>综合评价</h4>
          <p class="desc-text">{{ report.overall_summary || '无' }}</p>
        </el-col>
        <el-col :span="8">
          <h4>🚩 风险标记</h4>
          <el-empty v-if="!report.risk_flags?.length" description="无风险" :image-size="40" />
          <ul v-else class="risk-list">
            <li v-for="f in report.risk_flags" :key="f" class="text-danger">{{ f }}</li>
          </ul>
        </el-col>
      </el-row>

      <div class="reset-area">
        <el-button type="primary" @click="emit('reset')">
          <el-icon><Refresh /></el-icon> 重新分析
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.result-panel {
  margin-top: 24px;
}

/* ── 评分总览 ── */
.score-overview {
  margin-bottom: 20px;
}

.score-main {
  display: flex;
  align-items: center;
  gap: 32px;
}

.score-ring-wrapper {
  flex-shrink: 0;
}

.ring-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.ring-score {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.ring-score small {
  font-size: 14px;
  font-weight: 400;
  color: #999;
}

.score-info {
  flex: 1;
}

.candidate-name {
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.position-info {
  color: #666;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 16px;
}

.score-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.score-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.card-label {
  font-size: 12px;
  color: #888;
}

.card-score {
  font-size: 22px;
  font-weight: 700;
}

.card-score small {
  font-size: 11px;
  font-weight: 400;
}

/* ── 详情 tabs ── */
.detail-card {
  margin-bottom: 20px;
}

.tab-section {
  margin-bottom: 20px;
}

.tab-section h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: #444;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  font-size: 13px;
}

.text-list {
  list-style: none;
  padding: 0;
}

.text-list li {
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
  color: #555;
}

.text-list li::before {
  content: '• ';
  color: var(--primary);
}

.text-danger {
  color: var(--danger) !important;
}

.text-danger::before {
  color: var(--danger) !important;
}

.desc-text {
  font-size: 13px;
  color: #666;
  line-height: 1.7;
}

.empty-hint {
  color: #bbb;
  font-size: 13px;
}

.github-box {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #eee;
}

.github-box h4 {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── 综合评价 ── */
.summary-card {
  margin-bottom: 20px;
}

.summary-card h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: #444;
}

.risk-list {
  list-style: none;
  padding: 0;
}

.risk-list li {
  padding: 4px 0;
  font-size: 13px;
}

.risk-list li::before {
  content: '⚠ ';
}

.reset-area {
  margin-top: 20px;
  text-align: center;
}
</style>
