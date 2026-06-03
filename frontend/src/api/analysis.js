import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000, // 分析需要较长时间
})

/**
 * 提交简历+JD进行匹配分析
 * @param {string} resumeText - 简历文本或文件路径
 * @param {string} jdText - JD全文
 * @returns {Promise} 分析响应
 */
export async function submitAnalysis(resumeText, jdText) {
  const { data } = await api.post('/analysis/submit', {
    resume_text: resumeText,
    jd_text: jdText,
  })
  return data
}

/**
 * 健康检查
 */
export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}
