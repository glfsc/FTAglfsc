import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,  // 增加到 120 秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 如果是 FormData，让浏览器自动设置 Content-Type（包括 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
   return response.data
  },
  error => {
    const errorMsg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(errorMsg)
   return Promise.reject(error)
  }
)

/**
 * 健康检查接口
 * GET /api/health
 */
export const healthCheck = () => {
  return api.get('/health')
}

/**
 * 上传知识三元组
 * POST /api/v1/fault-tree/upload_knowledge
 * @param {Array} triplets - 三元组数组
 */
export const uploadKnowledge = (triplets) => {
  // 支持两种格式：直接数组或包含 triplets 字段的对象
  const payload = Array.isArray(triplets) ? { triplets } : triplets
  return api.post('/fault-tree/upload_knowledge', payload)
}

/**
 * 上传文档
 * POST /api/v1/document/upload
 * @param {FormData} formData - FormData 对象（包含 file 字段）
 */
export const uploadDocument = async (formData) => {
  const response = await api.post('/document/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response
}

/**
 * 验证文档
 * POST /api/v1/document/validate
 * @param {FormData} formData - FormData 对象（包含 file 字段）
 */
export const validateDocument = async (formData) => {
  const response = await api.post('/document/validate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response
}

/**
 * 上传文件（已废弃，使用 uploadDocument 替代）
 * @deprecated Use uploadDocument instead
 */
export const uploadFile = uploadDocument

/**
 * 提取知识
 * POST /api/v1/knowledge/extract
 * @param {Object} data - 提取请求数据
 * @param {string} data.file_id - 文件 ID
 * @param {string} data.top_event - 顶事件名称
 * @param {string} data.output_dir - 输出目录
 */
export const extractKnowledge = (data) => {
  return api.post('/knowledge/extract', {
    file_id: data.file_id,
    top_event: data.top_event || 'Top Event',
    output_dir: data.output_dir || 'data/triplets'
  })
}

/**
 * 提取并上传知识到图谱
 * POST /api/v1/knowledge/extract_and_upload
 * @param {Object} data - 提取请求数据
 */
export const extractAndUploadKnowledge = (data) => {
  return api.post('/knowledge/extract_and_upload', {
    file_id: data.file_id,
    top_event: data.top_event || 'Top Event',
    output_dir: data.output_dir || 'data/triplets'
  })
}

/**
 * 生成故障树（简化版 GET 接口）
 * GET /api/v1/fault-tree/generate_simple?top_event=xxx
 * @param {string} topEvent - 顶事件名称
 * @param {boolean} exportToFile - 是否导出为文件
 */
export const generateFaultTree = (topEvent, exportToFile = false) => {
  return api.get('/fault-tree/generate_simple', {
    params: {
      top_event: topEvent,
      export: exportToFile
    }
  })
}

/**
 * 生成故障树（POST 接口，支持更多选项）
 * POST /api/v1/fault-tree/generate
 * @param {Object} data - 生成请求数据
 * @param {string} data.top_event - 顶事件名称
 * @param {boolean} data.use_file - 是否使用文件模式
 * @param {string} data.file_id - 文件 ID（可选）
 * @param {boolean} data.export - 是否导出为文件
 */
export const generateFaultTreeAdvanced = (data) => {
  return api.post('/fault-tree/generate', data)
}

/**
 * 从文件一键生成故障树（不依赖 Neo4j，已废弃）
 * @deprecated Use generateFaultTreeAdvanced with use_file=true instead
 */
export const generateFaultTreeFromFile = (data) => {
  return generateFaultTreeAdvanced({
    ...data,
    use_file: true
  })
}

/**
 * 下载故障树 JSON 文件
 * @param {string} filename - 文件名
 */
export const downloadFaultTreeFile = (filename) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${baseUrl}/fault-tree/download/${filename}`
}

/**
 * 生成并下载故障树（一键操作）
 * @param {string} topEvent - 顶事件名称
 */
export const generateAndDownloadFaultTree = (topEvent) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${baseUrl}/fault-tree/generate_and_download?top_event=${encodeURIComponent(topEvent)}`
}

/**
 * 优化故障树（专家修正）
 * POST /api/v1/fault-tree/optimize
 * @param {Object} data - 修正数据
 */
export const optimizeFaultTree = (data) => {
  return api.post('/fault-tree/optimize', data)
}

/**
 * 导出故障树
 * GET /api/v1/fault-tree/export?tree_id=xxx&format=json
 * @param {string} treeId - 树 ID
 * @param {string} format - 导出格式 (json/png/svg)
 */
export const exportFaultTree = (treeId, format = 'json') => {
  return api.get('/fault-tree/export', {
   params: { tree_id: treeId, format }
  })
}

/**
 * AI 对话接口
 * POST /api/v1/ai/chat
 * @param {Object} data - 对话请求数据
 * @param {Array} data.messages - 消息历史
 * @param {Object} data.context - 故障树上下文
 */
export const chatWithAI = (data) => {
  return api.post('/ai/chat', data)
}

export default api
