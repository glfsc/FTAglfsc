import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { saveAs } from 'file-saver'

/**
 * 方案一：前端导出 - html2canvas + jsPDF
 * 优点：无需后端，快速集成
 * 缺点：清晰度受限，大画布可能变形
 */

export const exporters = {
  /**
   * 导出为高清PNG图片
   * @param {HTMLElement} element - 要导出的DOM元素
   * @param {string} filename - 文件名
   * @param {Object} options - 配置选项
   */
  async exportToPNG(element, filename = 'fault-tree.png', options = {}) {
    const {
      scale = 2, // 缩放倍数，越大越清晰但越慢
      quality = 0.95,
      backgroundColor = '#ffffff'
    } = options

    try {
      const canvas = await html2canvas(element, {
        scale,
        useCORS: true,
        allowTaint: true,
        backgroundColor,
        logging: false,
        windowHeight: element.scrollHeight,
        windowWidth: element.scrollWidth
      })

      canvas.toBlob((blob) => {
        saveAs(blob, filename)
      }, 'image/png', quality)

      return { success: true, message: 'PNG导出成功' }
    } catch (error) {
      console.error('PNG导出失败:', error)
      return { success: false, message: `PNG导出失败: ${error.message}` }
    }
  },

  /**
   * 导出为JPG图片（文件更小）
   */
  async exportToJPG(element, filename = 'fault-tree.jpg', options = {}) {
    const {
      scale = 2,
      quality = 0.85,
      backgroundColor = '#ffffff'
    } = options

    try {
      const canvas = await html2canvas(element, {
        scale,
        useCORS: true,
        allowTaint: true,
        backgroundColor,
        logging: false,
        windowHeight: element.scrollHeight,
        windowWidth: element.scrollWidth
      })

      canvas.toBlob((blob) => {
        saveAs(blob, filename)
      }, 'image/jpeg', quality)

      return { success: true, message: 'JPG导出成功' }
    } catch (error) {
      console.error('JPG导出失败:', error)
      return { success: false, message: `JPG导出失败: ${error.message}` }
    }
  },

  /**
   * 导出为PDF
   */
  async exportToPDF(element, filename = 'fault-tree.pdf', options = {}) {
    const {
      scale = 2,
      orientation = 'landscape', // 'portrait' 或 'landscape'
      format = 'a4'
    } = options

    try {
      const canvas = await html2canvas(element, {
        scale,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        windowHeight: element.scrollHeight,
        windowWidth: element.scrollWidth
      })

      const imgData = canvas.toDataURL('image/png')
      const imgWidth = orientation === 'landscape' ? 297 : 210 // mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width

      const pdf = new jsPDF({
        orientation,
        unit: 'mm',
        format
      })

      let heightLeft = imgHeight
      let position = 0

      // 处理多页PDF
      while (heightLeft >= 0) {
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
        heightLeft -= pdf.internal.pageSize.getHeight()
        if (heightLeft > 0) {
          pdf.addPage()
          position = heightLeft - imgHeight
        }
      }

      pdf.save(filename)
      return { success: true, message: 'PDF导出成功' }
    } catch (error) {
      console.error('PDF导出失败:', error)
      return { success: false, message: `PDF导出失败: ${error.message}` }
    }
  },

  /**
   * 导出为JSON（原生数据格式）
   */
  async exportToJSON(data, filename = 'fault-tree.json') {
    try {
      const jsonStr = JSON.stringify(data, null, 2)
      const blob = new Blob([jsonStr], { type: 'application/json' })
      saveAs(blob, filename)
      return { success: true, message: 'JSON导出成功' }
    } catch (error) {
      console.error('JSON导出失败:', error)
      return { success: false, message: `JSON导出失败: ${error.message}` }
    }
  },

  /**
   * 导出为SVG（矢量格式）
   */
  async exportToSVG(svgElement, filename = 'fault-tree.svg') {
    try {
      const svgData = new XMLSerializer().serializeToString(svgElement)
      const blob = new Blob([svgData], { type: 'image/svg+xml' })
      saveAs(blob, filename)
      return { success: true, message: 'SVG导出成功' }
    } catch (error) {
      console.error('SVG导出失败:', error)
      return { success: false, message: `SVG导出失败: ${error.message}` }
    }
  }
}

/**
 * 获取导出配置预设
 */
export const exportPresets = {
  // 快速导出（低清晰度，快速）
  fast: {
    scale: 1,
    quality: 0.75
  },
  // 标准导出（中等清晰度）
  standard: {
    scale: 2,
    quality: 0.85
  },
  // 高质量导出（高清晰度，较慢）
  highQuality: {
    scale: 3,
    quality: 0.95
  },
  // 超高质量导出（最高清晰度，很慢）
  ultraHigh: {
    scale: 4,
    quality: 0.99
  }
}
