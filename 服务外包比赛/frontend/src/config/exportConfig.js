/**
 * 导出配置文件
 * 集中管理所有导出相关的配置参数
 */

export const exportConfig = {
  // ============ 方案一配置 ============
  scheme1: {
    name: '前端快速方案（html2canvas + jsPDF）',
    enabled: true,
    
    // 质量预设
    presets: {
      fast: {
        scale: 1,
        quality: 0.75,
        description: '快速导出，清晰度一般，适合预览'
      },
      standard: {
        scale: 2,
        quality: 0.85,
        description: '标准质量，清晰度中等，推荐使用'
      },
      highQuality: {
        scale: 3,
        quality: 0.95,
        description: '高质量导出，清晰度高，导出较慢'
      },
      ultraHigh: {
        scale: 4,
        quality: 0.99,
        description: '超高质量，最高清晰度，导出很慢'
      }
    },

    // PNG导出配置
    png: {
      enabled: true,
      mimeType: 'image/png',
      defaultQuality: 0.95,
      maxScale: 4,
      backgroundColor: '#ffffff'
    },

    // JPG导出配置
    jpg: {
      enabled: true,
      mimeType: 'image/jpeg',
      defaultQuality: 0.85,
      maxScale: 4,
      backgroundColor: '#ffffff'
    },

    // PDF导出配置
    pdf: {
      enabled: true,
      format: 'a4',
      orientations: ['portrait', 'landscape'],
      defaultOrientation: 'landscape',
      margins: { top: 10, right: 10, bottom: 10, left: 10 }
    },

    // JSON导出配置
    json: {
      enabled: true,
      pretty: true,
      indent: 2
    },

    // SVG导出配置
    svg: {
      enabled: true,
      includeXmlDeclaration: true
    }
  },

  // ============ 方案二配置 ============
  scheme2: {
    name: '后端高保真方案（Puppeteer + Sharp）',
    enabled: false, // 需要后端服务
    
    // 后端服务配置
    backend: {
      url: 'http://localhost:3002',
      timeout: 30000, // 30秒超时
      retries: 3,
      retryDelay: 1000
    },

    // DPI配置
    dpi: {
      screen: 96,
      highDpi: 150,
      print: 300,
      default: 150
    },

    // 视口配置
    viewport: {
      width: 1200,
      height: 800,
      deviceScaleFactor: 1
    },

    // PNG导出配置
    png: {
      enabled: true,
      quality: 95,
      compressionLevel: 9
    },

    // JPG导出配置
    jpg: {
      enabled: true,
      quality: 95,
      progressive: true
    },

    // PDF导出配置
    pdf: {
      enabled: true,
      format: 'A4',
      landscape: true,
      printBackground: true,
      margins: {
        top: 10,
        right: 10,
        bottom: 10,
        left: 10
      }
    },

    // 缩略图配置
    thumbnails: {
      enabled: true,
      sizes: [
        { name: 'small', width: 400, height: 300 },
        { name: 'medium', width: 800, height: 600 },
        { name: 'large', width: 1200, height: 900 }
      ]
    }
  },

  // ============ 方案三配置 ============
  scheme3: {
    name: 'SVG原生导出方案',
    enabled: true,

    // SVG导出配置
    svg: {
      enabled: true,
      includeXmlDeclaration: true,
      optimize: true
    },

    // SVG转PDF配置
    svgToPdf: {
      enabled: true,
      orientation: 'landscape',
      format: 'a4',
      scale: 1
    },

    // SVG转PNG配置
    svgToPng: {
      enabled: true,
      scale: 2,
      quality: 0.95
    },

    // SVG转JPG配置
    svgToJpg: {
      enabled: true,
      scale: 2,
      quality: 0.85
    }
  },

  // ============ 全局配置 ============
  global: {
    // 文件名配置
    filename: {
      prefix: 'fault-tree',
      timestamp: true,
      format: '{prefix}-{timestamp}.{ext}'
    },

    // 导出限制
    limits: {
      maxFileSize: 50 * 1024 * 1024, // 50MB
      maxCanvasSize: 4096 * 4096, // 4096x4096
      timeout: 30000 // 30秒
    },

    // 缓存配置
    cache: {
      enabled: true,
      maxAge: 3600000, // 1小时
      maxSize: 100 * 1024 * 1024 // 100MB
    },

    // 日志配置
    logging: {
      enabled: true,
      level: 'info', // 'debug', 'info', 'warn', 'error'
      logExportTime: true,
      logFileSize: true
    },

    // 错误处理
    errorHandling: {
      showDetailedErrors: true,
      retryOnFailure: true,
      maxRetries: 3
    }
  },

  // ============ 推荐配置 ============
  recommendations: {
    // 快速预览
    preview: {
      scheme: 'scheme1',
      format: 'png',
      quality: 'fast',
      description: '快速预览，无需等待'
    },

    // 常规使用
    standard: {
      scheme: 'scheme1',
      format: 'png',
      quality: 'standard',
      description: '平衡清晰度和速度'
    },

    // 高质量导出
    highQuality: {
      scheme: 'scheme2',
      format: 'png',
      dpi: 150,
      description: '高清晰度，适合打印'
    },

    // 矢量需求
    vector: {
      scheme: 'scheme3',
      format: 'svg',
      description: '保留矢量信息，可无限缩放'
    },

    // 数据导出
    data: {
      scheme: 'scheme1',
      format: 'json',
      description: '导出原始数据'
    }
  }
}

/**
 * 获取推荐配置
 */
export function getRecommendedConfig(useCase) {
  return exportConfig.recommendations[useCase] || exportConfig.recommendations.standard
}

/**
 * 获取方案配置
 */
export function getSchemeConfig(scheme) {
  return exportConfig[scheme]
}

/**
 * 获取格式配置
 */
export function getFormatConfig(scheme, format) {
  const schemeConfig = exportConfig[scheme]
  return schemeConfig?.[format]
}

/**
 * 验证配置
 */
export function validateConfig(config) {
  const errors = []

  if (!config.scheme) {
    errors.push('缺少scheme配置')
  }

  if (!config.format) {
    errors.push('缺少format配置')
  }

  if (config.scheme === 'scheme2' && !exportConfig.scheme2.enabled) {
    errors.push('方案二未启用，请先启动后端服务')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 合并配置
 */
export function mergeConfig(baseConfig, overrides) {
  return {
    ...baseConfig,
    ...overrides
  }
}

/**
 * 导出配置预设
 */
export const exportPresets = {
  // 快速预览
  preview: {
    scheme: 'scheme1',
    format: 'png',
    scale: 1,
    quality: 0.75,
    timeout: 5000
  },

  // 标准导出
  standard: {
    scheme: 'scheme1',
    format: 'png',
    scale: 2,
    quality: 0.85,
    timeout: 10000
  },

  // 高质量
  highQuality: {
    scheme: 'scheme1',
    format: 'png',
    scale: 3,
    quality: 0.95,
    timeout: 20000
  },

  // 超高质量（后端）
  ultraHigh: {
    scheme: 'scheme2',
    format: 'png',
    dpi: 300,
    quality: 0.99,
    timeout: 30000
  },

  // 矢量
  vector: {
    scheme: 'scheme3',
    format: 'svg',
    optimize: true
  },

  // 数据
  data: {
    scheme: 'scheme1',
    format: 'json',
    pretty: true
  }
}

/**
 * 获取预设
 */
export function getPreset(presetName) {
  return exportPresets[presetName] || exportPresets.standard
}

/**
 * 格式支持矩阵
 */
export const formatSupportMatrix = {
  scheme1: ['png', 'jpg', 'pdf', 'json', 'svg'],
  scheme2: ['png', 'jpg', 'pdf'],
  scheme3: ['svg', 'pdf', 'png', 'jpg']
}

/**
 * 检查格式是否支持
 */
export function isFormatSupported(scheme, format) {
  return formatSupportMatrix[scheme]?.includes(format) || false
}

/**
 * 获取支持的格式列表
 */
export function getSupportedFormats(scheme) {
  return formatSupportMatrix[scheme] || []
}

/**
 * 性能基准数据
 */
export const performanceBenchmarks = {
  scheme1: {
    png: { time: 300, size: 2.1 }, // ms, MB
    jpg: { time: 250, size: 1.2 },
    pdf: { time: 400, size: 2.5 },
    json: { time: 50, size: 0.045 }
  },
  scheme2: {
    png: { time: 1500, size: 1.8 },
    jpg: { time: 1400, size: 0.9 },
    pdf: { time: 2000, size: 2.2 }
  },
  scheme3: {
    svg: { time: 200, size: 0.05 },
    pdf: { time: 800, size: 1.5 },
    png: { time: 300, size: 2.0 }
  }
}

/**
 * 获取性能预期
 */
export function getPerformanceExpectation(scheme, format) {
  return performanceBenchmarks[scheme]?.[format] || { time: 0, size: 0 }
}

export default exportConfig
