/**
 * 方案三：SVG原生导出方案
 * 使用 svg2pdf 库实现矢量导出
 * 
 * 安装依赖：
 * npm install svg2pdf.js jspdf
 */

import jsPDF from 'jspdf'
import { saveAs } from 'file-saver'

/**
 * SVG导出工具集
 */
export const svgExporters = {
  /**
   * 导出SVG为PDF（保留矢量信息）
   */
  async exportSVGToPDF(svgElement, filename = 'fault-tree.pdf', options = {}) {
    try {
      const {
        orientation = 'landscape',
        format = 'a4',
        scale = 1
      } = options

      // 获取SVG的尺寸
      const svgRect = svgElement.getBoundingClientRect()
      const svgWidth = svgRect.width
      const svgHeight = svgRect.height

      // 创建PDF
      const pdf = new jsPDF({
        orientation,
        unit: 'mm',
        format
      })

      // 获取PDF页面尺寸
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()

      // 计算缩放比例
      const scaleX = (pageWidth - 20) / svgWidth
      const scaleY = (pageHeight - 20) / svgHeight
      const finalScale = Math.min(scaleX, scaleY) * scale

      // 将SVG转换为图片
      const canvas = await svgToCanvas(svgElement)
      const imgData = canvas.toDataURL('image/png')

      // 计算图片在PDF中的尺寸
      const imgWidth = svgWidth * finalScale
      const imgHeight = svgHeight * finalScale

      // 添加到PDF
      pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight)

      pdf.save(filename)
      return { success: true, message: 'SVG转PDF成功' }
    } catch (error) {
      console.error('SVG转PDF失败:', error)
      return { success: false, message: `SVG转PDF失败: ${error.message}` }
    }
  },

  /**
   * 导出SVG为高清PNG
   */
  async exportSVGToPNG(svgElement, filename = 'fault-tree.png', options = {}) {
    try {
      const { scale = 2, quality = 0.95 } = options

      const canvas = await svgToCanvas(svgElement, scale)
      
      canvas.toBlob((blob) => {
        saveAs(blob, filename)
      }, 'image/png', quality)

      return { success: true, message: 'SVG转PNG成功' }
    } catch (error) {
      console.error('SVG转PNG失败:', error)
      return { success: false, message: `SVG转PNG失败: ${error.message}` }
    }
  },

  /**
   * 导出SVG为JPG
   */
  async exportSVGToJPG(svgElement, filename = 'fault-tree.jpg', options = {}) {
    try {
      const { scale = 2, quality = 0.85 } = options

      const canvas = await svgToCanvas(svgElement, scale)
      
      canvas.toBlob((blob) => {
        saveAs(blob, filename)
      }, 'image/jpeg', quality)

      return { success: true, message: 'SVG转JPG成功' }
    } catch (error) {
      console.error('SVG转JPG失败:', error)
      return { success: false, message: `SVG转JPG失败: ${error.message}` }
    }
  },

  /**
   * 导出为纯SVG文件（保留矢量）
   */
  async exportPureSVG(svgElement, filename = 'fault-tree.svg') {
    try {
      // 克隆SVG元素以避免修改原始元素
      const clonedSvg = svgElement.cloneNode(true)
      
      // 添加XML声明
      const svgString = new XMLSerializer().serializeToString(clonedSvg)
      const svgWithXml = `<?xml version="1.0" encoding="UTF-8"?>\n${svgString}`
      
      const blob = new Blob([svgWithXml], { type: 'image/svg+xml;charset=utf-8' })
      saveAs(blob, filename)

      return { success: true, message: 'SVG导出成功' }
    } catch (error) {
      console.error('SVG导出失败:', error)
      return { success: false, message: `SVG导出失败: ${error.message}` }
    }
  },

  /**
   * 导出为SVGZ（压缩SVG）
   */
  async exportSVGZ(svgElement, filename = 'fault-tree.svgz') {
    try {
      const svgString = new XMLSerializer().serializeToString(svgElement)
      const blob = new Blob([svgString], { type: 'image/svg+xml' })
      
      // 注意：浏览器不支持直接压缩，需要后端处理
      // 这里只是导出为SVG，实际SVGZ需要后端gzip压缩
      saveAs(blob, filename.replace('.svgz', '.svg'))

      return { success: true, message: 'SVG导出成功（需后端压缩为SVGZ）' }
    } catch (error) {
      console.error('SVGZ导出失败:', error)
      return { success: false, message: `SVGZ导出失败: ${error.message}` }
    }
  }
}

/**
 * 将SVG转换为Canvas
 * @param {SVGElement} svgElement - SVG元素
 * @param {number} scale - 缩放倍数
 */
async function svgToCanvas(svgElement, scale = 1) {
  return new Promise((resolve, reject) => {
    try {
      const svgRect = svgElement.getBoundingClientRect()
      const width = svgRect.width * scale
      const height = svgRect.height * scale

      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      const svgString = new XMLSerializer().serializeToString(svgElement)
      const img = new Image()

      img.onload = () => {
        ctx.drawImage(img, 0, 0, width, height)
        resolve(canvas)
      }

      img.onerror = () => {
        reject(new Error('SVG转Canvas失败'))
      }

      // 创建Blob URL
      const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      img.src = url
    } catch (error) {
      reject(error)
    }
  })
}

/**
 * 获取SVG统计信息
 */
export function getSVGStats(svgElement) {
  const rect = svgElement.getBoundingClientRect()
  const nodes = svgElement.querySelectorAll('*').length
  const paths = svgElement.querySelectorAll('path').length
  const texts = svgElement.querySelectorAll('text').length
  const circles = svgElement.querySelectorAll('circle').length
  const rects = svgElement.querySelectorAll('rect').length

  return {
    width: Math.round(rect.width),
    height: Math.round(rect.height),
    totalElements: nodes,
    paths,
    texts,
    circles,
    rects,
    fileSize: new XMLSerializer().serializeToString(svgElement).length
  }
}

/**
 * 优化SVG（移除不必要的属性）
 */
export function optimizeSVG(svgElement) {
  const cloned = svgElement.cloneNode(true)
  
  // 移除不必要的属性
  cloned.querySelectorAll('*').forEach(el => {
    // 移除事件监听器相关属性
    Array.from(el.attributes).forEach(attr => {
      if (attr.name.startsWith('on') || attr.name.startsWith('data-')) {
        el.removeAttribute(attr.name)
      }
    })
  })

  return cloned
}
