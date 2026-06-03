import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000,
})

/**
 * 提交简历+JD进行匹配分析（等待完成）
 */
export async function submitAnalysis(resumeText, jdText) {
  const { data } = await api.post('/analysis/submit', {
    resume_text: resumeText,
    jd_text: jdText,
  })
  return data
}

/**
 * 提交简历+JD进行匹配分析（SSE 实时推送进度）
 *
 * @param {string} resumeText
 * @param {string} jdText
 * @param {function} onProgress - ({ step, agent }) => void
 * @param {function} onResult - (data) => void
 * @param {function} onError - (message) => void
 */
export async function submitAnalysisStream(resumeText, jdText, onProgress, onResult, onError) {
  const response = await fetch('/api/analysis/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, jd_text: jdText }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(err.detail || '请求失败')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.slice(6))
          switch (event.type) {
            case 'progress':
              onProgress && onProgress(event)
              break
            case 'result':
              onResult && onResult(event.data)
              break
            case 'error':
              onError && onError(event.message)
              break
          }
        } catch {
          // 跳过无法解析的行
        }
      }
    }
  }
}

/**
 * 健康检查
 */
export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}
