#!/usr/bin/env node

/**
 * 后端导出服务启动脚本
 * 
 * 使用方法：
 * npm start              - 启动服务
 * npm run dev            - 开发模式（自动重启）
 * npm test               - 测试导出功能
 */

import express from 'express'
import puppeteer from 'puppeteer'
import sharp from 'sharp'
import cors from 'cors'
import bodyParser from 'body-parser'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const app = express()

// ============ 中间件配置 ============
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:5173'],
  credentials: true
}))
app.use(bodyParser.json({ limit: '50mb' }))
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }))

// ============ 全局变量 ============
let browser = null
const stats = {
  totalRequests: 0,
  successfulExports: 0,
  failedExports: 0,
  totalProcessingTime: 0,
  startTime: Date.now()
}

// ============ 初始化浏览器 ============
async function initBrowser() {
  if (browser) return browser
  
  console.log('🚀 正在启动Puppeteer浏览器...')
  
  browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-web-resources',
      '--disable-extensions'
    ]
  })
  
  console.log('✅ Puppeteer浏览器启动成功')
  return browser
}

// ============ 导出函数 ============

async function generatePNG(htmlContent, dpi = 150, options = {}) {
  const browser = await initBrowser()
  const page = await browser.newPage()
  
  try {
    const deviceScaleFactor = dpi / 96
    
    await page.setViewport({
      width: options.width || 1200,
      height: options.height || 800,
      deviceScaleFactor
    })

    await page.setContent(htmlContent, { waitUntil: 'networkidle0' })
    await page.waitForTimeout(500)

    const screenshot = await page.screenshot({
      type: 'png',
      fullPage: true,
      omitBackground: false
    })

    const processed = await sharp(screenshot)
      .png({ quality: 95, compressionLevel: 9 })
      .toBuffer()

    return processed
  } finally {
    await page.close()
  }
}

async function generateJPG(htmlContent, dpi = 150, options = {}) {
  const browser = await initBrowser()
  const page = await browser.newPage()
  
  try {
    const deviceScaleFactor = dpi / 96
    
    await page.setViewport({
      width: options.width || 1200,
      height: options.height || 800,
      deviceScaleFactor
    })

    await page.setContent(htmlContent, { waitUntil: 'networkidle0' })
    await page.waitForTimeout(500)

    const screenshot = await page.screenshot({
      type: 'jpeg',
      fullPage: true,
      quality: 95
    })

    const processed = await sharp(screenshot)
      .jpeg({ quality: 95, progressive: true })
      .toBuffer()

    return processed
  } finally {
    await page.close()
  }
}

async function generatePDF(htmlContent, options = {}) {
  const browser = await initBrowser()
  const page = await browser.newPage()
  
  try {
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' })
    await page.waitForTimeout(500)

    const pdf = await page.pdf({
      format: options.format || 'A4',
      landscape: options.landscape !== false,
      margin: {
        top: 10,
        right: 10,
        bottom: 10,
        left: 10
      },
      printBackground: true
    })

    return pdf
  } finally {
    await page.close()
  }
}

// ============ API 路由 ============

/**
 * POST /api/export/png
 */
app.post('/api/export/png', async (req, res) => {
  const startTime = Date.now()
  stats.totalRequests++
  
  try {
    const { html, dpi = 150, width = 1200, height = 800 } = req.body

    if (!html) {
      return res.status(400).json({ error: 'HTML内容不能为空' })
    }

    console.log(`📝 处理PNG导出请求 (DPI: ${dpi})`)
    
    const png = await generatePNG(html, dpi, { width, height })

    const processingTime = Date.now() - startTime
    stats.successfulExports++
    stats.totalProcessingTime += processingTime

    console.log(`✅ PNG导出成功 (${processingTime}ms, ${(png.length / 1024 / 1024).toFixed(2)}MB)`)

    res.setHeader('Content-Type', 'image/png')
    res.setHeader('Content-Disposition', 'attachment; filename="fault-tree.png"')
    res.setHeader('X-Processing-Time', processingTime)
    res.send(png)
  } catch (error) {
    stats.failedExports++
    console.error('❌ PNG导出错误:', error.message)
    res.status(500).json({ error: error.message })
  }
})

/**
 * POST /api/export/jpg
 */
app.post('/api/export/jpg', async (req, res) => {
  const startTime = Date.now()
  stats.totalRequests++
  
  try {
    const { html, dpi = 150, width = 1200, height = 800 } = req.body

    if (!html) {
      return res.status(400).json({ error: 'HTML内容不能为空' })
    }

    console.log(`📝 处理JPG导出请求 (DPI: ${dpi})`)
    
    const jpg = await generateJPG(html, dpi, { width, height })

    const processingTime = Date.now() - startTime
    stats.successfulExports++
    stats.totalProcessingTime += processingTime

    console.log(`✅ JPG导出成功 (${processingTime}ms, ${(jpg.length / 1024 / 1024).toFixed(2)}MB)`)

    res.setHeader('Content-Type', 'image/jpeg')
    res.setHeader('Content-Disposition', 'attachment; filename="fault-tree.jpg"')
    res.setHeader('X-Processing-Time', processingTime)
    res.send(jpg)
  } catch (error) {
    stats.failedExports++
    console.error('❌ JPG导出错误:', error.message)
    res.status(500).json({ error: error.message })
  }
})

/**
 * POST /api/export/pdf
 */
app.post('/api/export/pdf', async (req, res) => {
  const startTime = Date.now()
  stats.totalRequests++
  
  try {
    const { html, format = 'A4', landscape = true } = req.body

    if (!html) {
      return res.status(400).json({ error: 'HTML内容不能为空' })
    }

    console.log(`📝 处理PDF导出请求 (格式: ${format}, 方向: ${landscape ? '横向' : '竖向'})`)
    
    const pdf = await generatePDF(html, { format, landscape })

    const processingTime = Date.now() - startTime
    stats.successfulExports++
    stats.totalProcessingTime += processingTime

    console.log(`✅ PDF导出成功 (${processingTime}ms, ${(pdf.length / 1024 / 1024).toFixed(2)}MB)`)

    res.setHeader('Content-Type', 'application/pdf')
    res.setHeader('Content-Disposition', 'attachment; filename="fault-tree.pdf"')
    res.setHeader('X-Processing-Time', processingTime)
    res.send(pdf)
  } catch (error) {
    stats.failedExports++
    console.error('❌ PDF导出错误:', error.message)
    res.status(500).json({ error: error.message })
  }
})

/**
 * GET /api/health
 */
app.get('/api/health', (req, res) => {
  const uptime = Date.now() - stats.startTime
  const avgTime = stats.successfulExports > 0 
    ? (stats.totalProcessingTime / stats.successfulExports).toFixed(0)
    : 0

  res.json({
    status: 'ok',
    service: 'export-service',
    uptime: `${(uptime / 1000 / 60).toFixed(1)}分钟`,
    stats: {
      totalRequests: stats.totalRequests,
      successfulExports: stats.successfulExports,
      failedExports: stats.failedExports,
      averageProcessingTime: `${avgTime}ms`
    }
  })
})

/**
 * GET /api/stats
 */
app.get('/api/stats', (req, res) => {
  const uptime = Date.now() - stats.startTime
  const successRate = stats.totalRequests > 0 
    ? ((stats.successfulExports / stats.totalRequests) * 100).toFixed(1)
    : 0

  res.json({
    uptime: `${(uptime / 1000 / 60).toFixed(1)}分钟`,
    totalRequests: stats.totalRequests,
    successfulExports: stats.successfulExports,
    failedExports: stats.failedExports,
    successRate: `${successRate}%`,
    averageProcessingTime: stats.successfulExports > 0 
      ? `${(stats.totalProcessingTime / stats.successfulExports).toFixed(0)}ms`
      : '0ms'
  })
})

// ============ 错误处理 ============
app.use((err, req, res, next) => {
  console.error('❌ 服务器错误:', err)
  res.status(500).json({ error: '服务器内部错误' })
})

// ============ 优雅关闭 ============
process.on('SIGTERM', async () => {
  console.log('\n📛 收到SIGTERM信号，正在关闭...')
  if (browser) {
    await browser.close()
  }
  process.exit(0)
})

process.on('SIGINT', async () => {
  console.log('\n📛 收到SIGINT信号，正在关闭...')
  if (browser) {
    await browser.close()
  }
  process.exit(0)
})

// ============ 启动服务器 ============
const PORT = process.env.PORT || 3002

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║     故障树导出服务 - Puppeteer + Sharp                    ║
║                                                            ║
║  🚀 服务运行在: http://localhost:${PORT}                  ║
║                                                            ║
║  📚 支持的API:                                             ║
║     POST /api/export/png      - 导出PNG                   ║
║     POST /api/export/jpg      - 导出JPG                   ║
║     POST /api/export/pdf      - 导出PDF                   ║
║     GET  /api/health          - 健康检查                  ║
║     GET  /api/stats           - 统计信息                  ║
║                                                            ║
║  ⚙️  配置:                                                 ║
║     前端地址: http://localhost:3000                       ║
║     测试地址: http://localhost:3001                       ║
║                                                            ║
║  💡 提示:                                                  ║
║     使用 npm run dev 启动开发模式                         ║
║     使用 npm test 测试导出功能                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
  `)
})

export { app, initBrowser }
