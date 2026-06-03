<script setup>
import { ref } from 'vue'
import { submitAnalysis } from '../api/analysis.js'

const emit = defineEmits(['result', 'error', 'update:loading'])

const props = defineProps({
  loading: Boolean,
})

const resumeText = ref('')
const jdText = ref('')

async function handleSubmit() {
  // 校验
  if (!resumeText.value.trim()) {
    emit('error', '请输入简历内容')
    return
  }
  if (!jdText.value.trim() || jdText.value.trim().length < 50) {
    emit('error', 'JD内容至少50个字符')
    return
  }

  emit('update:loading', true)
  emit('error', '')

  try {
    const data = await submitAnalysis(resumeText.value.trim(), jdText.value.trim())
    emit('result', data)
  } catch (err) {
    const msg = err.response?.data?.detail || err.message || '请求失败，请检查后端是否启动'
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
  <el-card class="input-panel" shadow="hover">
    <template #header>
      <div class="panel-header">
        <span class="panel-title">
          <el-icon><Edit /></el-icon> 分析提交
        </span>
        <el-button text type="info" @click="handleClear">清空</el-button>
      </div>
    </template>

    <el-row :gutter="20">
      <!-- 简历输入 -->
      <el-col :span="12">
        <div class="input-group">
          <div class="input-label">
            <el-icon><User /></el-icon> 简历内容
            <el-tooltip content="粘贴简历全文，或输入PDF/DOCX/TXT文件路径" placement="top">
              <el-icon class="hint-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-input
            v-model="resumeText"
            type="textarea"
            :rows="14"
            placeholder="请粘贴简历全文内容……
例如：
张三 | Java高级工程师 | 138-xxxx-xxxx | zhangsan@qq.com

技能：Java, Spring Boot, MySQL, Redis, Docker……

工作经历：
- 高级Java工程师 | XX科技 | 2021.03 - 至今……"
          />
          <div class="char-count">{{ resumeText.length }} 字</div>
        </div>
      </el-col>

      <!-- JD输入 -->
      <el-col :span="12">
        <div class="input-group">
          <div class="input-label">
            <el-icon><Document /></el-icon> 职位描述 (JD)
          </div>
          <el-input
            v-model="jdText"
            type="textarea"
            :rows="14"
            placeholder="请粘贴职位描述全文……
例如：
高级Java工程师

公司: XX科技 | 地点: 北京 | 薪资: 25k-40k

岗位职责
- 负责公司核心产品的后端架构设计和开发……

任职要求
- 5年以上Java开发经验，熟悉Spring Boot等框架……"
          />
          <div class="char-count">{{ jdText.length }} 字</div>
        </div>
      </el-col>
    </el-row>

    <!-- 提交按钮 -->
    <div class="submit-area">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!resumeText.trim() || !jdText.trim()"
        @click="handleSubmit"
      >
        <el-icon v-if="!loading"><Search /></el-icon>
        {{ loading ? 'AI分析中，请耐心等待……' : '开始智能匹配分析' }}
      </el-button>
      <span class="submit-hint">分析过程约需 30-60 秒</span>
    </div>
  </el-card>
</template>

<style scoped>
.input-panel {
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.input-group {
  margin-bottom: 8px;
}

.input-label {
  margin-bottom: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #555;
}

.hint-icon {
  color: #aaa;
  cursor: help;
  font-size: 14px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.submit-area {
  margin-top: 20px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.submit-hint {
  font-size: 12px;
  color: #aaa;
}
</style>
