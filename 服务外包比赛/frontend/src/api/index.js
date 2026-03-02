import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

// 文件上传
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/data/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 知识提取
export const extractKnowledge = (fileId) => {
  return api.post('/knowledge/extract', null, { params: { file_id: fileId } })
}

// 获取提取进度
export const getExtractProgress = (taskId) => {
  return api.get(`/knowledge/extract/progress/${taskId}`)
}

// 生成故障树
export const generateFaultTree = (data) => {
  return api.post('/fault/tree/generate', data)
}

// 优化故障树
export const optimizeFaultTree = (data) => {
  return api.post('/fault/tree/optimize', data)
}

// 导出故障树
export const exportFaultTree = (treeId, format) => {
  return api.get(`/fault/tree/${treeId}/export`, { params: { format } })
}

export default api
