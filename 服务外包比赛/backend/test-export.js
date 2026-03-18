
/**
 * 导出功能测试脚本
 * 用于测试 Puppeteer + Sharp 导出功能
 */

import fetch from 'node-fetch'

const API_BASE = 'http://localhost:3002'

// 简单的 HTML 测试内容
const TEST_HTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>故障树测试</title>
</head>
<body style="padding: 20px; font-family: Arial;">
  <h1>故障树示例</h1>
  <div style="border: 2px solid #333; padding: 20px; margin: 20px 0;">
    <h2>顶事件：设备无法启动</h2>
    <ul>
      <li>中间事件 1: 电源故障
        <ul>
          <li>底事件：电池没电</li>
          <li>底事件：电路断路</li>
        </ul>
      </li>
      <li>中间事件 2: 电机损坏
        <ul>
          <li>底事件：线圈烧毁</li>
          <li>底事件：轴承卡死</li>
        </ul>
      </li>
    </ul>
  </div>
</body>
</html>
`

async function testExport(endpoint, format) {
  console.log(`🧪 测试${format}导出...`)

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        html: TEST_HTML,
        dpi: 150,
        width: 1200,
        height: 800
      })
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`HTTP ${response.status}: ${error}`)
    }

    const buffer = await response.arrayBuffer()
    console.log(`✅ ${format}导出成功！文件大小：${(buffer.byteLength / 1024).toFixed(2)} KB`)
    return true

  } catch (error) {
    console.error(`❌ ${format}导出失败：`, error.message)
    return false
  }
}

async function testHealth() {
  console.log('🏥 测试健康检查...')

  try {
    const response = await fetch(`${API_BASE}/api/health`)
    const data = await response.json()
    console.log('✅ 健康检查通过:', data)
    return true

  } catch (error) {
    console.error('❌ 健康检查失败:', error.message)
    return false
  }
}

async function runTests() {
  console.log('\n╔══════════════════════════════════════╗')
  console.log('║   故障树导出服务测试                ║')
  console.log('╚══════════════════════════════════════╝\n')

  // 等待服务启动
  console.log('⏳ 等待服务启动...')
  await new Promise(resolve => setTimeout(resolve, 2000))

  let passed = 0
  let failed = 0

  // 测试健康检查
  if (await testHealth()) passed++
  else failed++

  // 测试各种导出格式
  if (await testExport('/api/export/png', 'PNG')) passed++
  else failed++

  if (await testExport('/api/export/jpg', 'JPG')) passed++
  else failed++

  if (await testExport('/api/export/pdf', 'PDF')) passed++
  else failed++

  // 输出测试结果
  console.log('\n' + '='.repeat(40))
  console.log(`测试结果：${passed} 通过，${failed} 失败`)
  console.log('='.repeat(40) + '\n')

  process.exit(failed > 0 ? 1 : 0)
}

// 运行测试
runTests().catch(err => {
  console.error('💥 测试执行错误:', err)
  process.exit(1)
})
