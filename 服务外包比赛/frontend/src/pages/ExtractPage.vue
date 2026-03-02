<template>
  <div class="extract-page">
    <div class="page-header">
      <h2><el-icon><DataAnalysis /></el-icon> 故障知识提取</h2>
      <p class="description">基于AI大模型智能提取故障事件和逻辑关系</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="control-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><MagicStick /></el-icon> 知识提取控制台</span>
              <el-tag type="warning">步骤 2-3/6</el-tag>
            </div>
          </template>

          <div class="control-panel">
            <el-alert
              v-if="!fileId"
              title="提示"
              type="info"
              description="请先上传文件，然后返回此页面进行知识提取"
              show-icon
              :closable="false"
            />

            <div v-else class="extract-controls">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="文件ID">{{ fileId }}</el-descriptions-item>
                <el-descriptions-item label="提取状态">
                  <el-tag :type="extracting ? 'warning' : events.length > 0 ? 'success' : 'info'">
                    {{ extracting ? '提取中...' : events.length > 0 ? '已完成' : '待提取' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <div class="action-area">
                <el-button 
                  type="primary" 
                  size="large"
                  :loading="extracting"
                  :disabled="events.length > 0"
                  @click="startExtract"
                >
                  <el-icon><MagicStick /></el-icon>
                  {{ events.length > 0 ? '已提取完成' : '开始AI智能提取' }}
                </el-button>

                <el-button 
                  v-if="events.length > 0"
                  type="success" 
                  size="large"
                  @click="goToGenerate"
                >
                  <el-icon><Right /></el-icon>
                  生成故障树
                </el-button>
              </div>

              <el-progress 
                v-if="extractProgress > 0 && extractProgress < 100"
                :percentage="extractProgress"
                :stroke-width="10"
                status="success"
              >
                <span class="progress-text">AI模型分析中...</span>
              </el-progress>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-if="events.length > 0" style="margin-top: 20px">
      <el-col :span="14">
        <el-card class="events-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 提取的故障事件</span>
              <el-tag type="success">{{ events.length }} 个事件</el-tag>
            </div>
          </template>

          <el-table :data="events" stripe max-height="500">
            <el-table-column type="index" label="#" width="60" />
            <el-table-column prop="event_name" label="事件名称" min-width="150">
              <template #default="{ row }">
                <el-tag :type="getEventTypeColor(row.event_type)" size="small">
                  {{ getEventTypeLabel(row.event_type) }}
                </el-tag>
                <span style="margin-left: 8px">{{ row.event_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="probability" label="概率" width="100">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.probability * 100" 
                  :stroke-width="6"
                  :show-text="false"
                />
                <span style="font-size: 12px">{{ (row.probability * 100).toFixed(1) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="editEvent(row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="gates-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Connection /></el-icon> 逻辑门关系</span>
              <el-tag type="primary">{{ gates.length }} 个逻辑门</el-tag>
            </div>
          </template>

          <div class="gates-list">
            <el-timeline>
              <el-timeline-item 
                v-for="gate in gates" 
                :key="gate.gate_id"
                :timestamp="gate.gate_type + ' 门'"
                placement="top"
              >
                <el-card shadow="hover">
                  <p><strong>输入事件：</strong></p>
                  <el-tag 
                    v-for="eventId in gate.input_events" 
                    :key="eventId"
                    size="small"
                    style="margin: 2px"
                  >
                    {{ eventId }}
                  </el-tag>
                  <p style="margin-top: 10px"><strong>输出事件：</strong></p>
                  <el-tag type="success" size="small">{{ gate.output_event }}</el-tag>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>

        <el-card class="stats-card" shadow="hover" style="margin-top: 20px">
          <template #header>
            <span><el-icon><DataLine /></el-icon> 提取统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-statistic title="顶事件" :value="topEventCount" />
            </el-col>
            <el-col :span="12">
              <el-statistic title="中间事件" :value="middleEventCount" />
            </el-col>
            <el-col :span="12" style="margin-top: 20px">
              <el-statistic title="底事件" :value="bottomEventCount" />
            </el-col>
            <el-col :span="12" style="margin-top: 20px">
              <el-statistic title="逻辑门" :value="gates.length" />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  DataAnalysis, MagicStick, Document, Connection, 
  Edit, Right, DataLine 
} from '@element-plus/icons-vue'
import { extractKnowledge } from '@/api'

const route = useRoute()
const router = useRouter()
const fileId = ref(route.query.fileId || '')
const extracting = ref(false)
const extractProgress = ref(0)
const events = ref([])
const gates = ref([])

const topEventCount = computed(() => 
  events.value.filter(e => e.event_type === 'top').length
)
const middleEventCount = computed(() => 
  events.value.filter(e => e.event_type === 'middle').length
)
const bottomEventCount = computed(() => 
  events.value.filter(e => e.event_type === 'bottom').length
)

const getEventTypeLabel = (type) => {
  const labels = { top: '顶事件', middle: '中间事件', bottom: '底事件' }
  return labels[type] || type
}

const getEventTypeColor = (type) => {
  const colors = { top: 'danger', middle: 'warning', bottom: 'success' }
  return colors[type] || 'info'
}

const startExtract = async () => {
  if (!fileId.value) {
    ElMessage.warning('请先上传文件')
    return
  }

  extracting.value = true
  extractProgress.value = 0

  const progressInterval = setInterval(() => {
    if (extractProgress.value < 90) {
      extractProgress.value += 5
    }
  }, 300)

  try {
    const result = await extractKnowledge(fileId.value)
    clearInterval(progressInterval)
    extractProgress.value = 100
    
    events.value = result.events
    gates.value = result.gates
    
    ElMessage.success({
      message: `知识提取完成！提取到 ${result.events.length} 个故障事件`,
      duration: 3000
    })
  } catch (error) {
    clearInterval(progressInterval)
    extractProgress.value = 0
    ElMessage.error('知识提取失败，请重试')
  } finally {
    extracting.value = false
  }
}

const editEvent = (event) => {
  ElMessage.info('编辑功能开发中...')
}

const goToGenerate = () => {
  router.push('/generate')
}

onMounted(() => {
  if (fileId.value) {
    // 自动开始提取
    setTimeout(() => {
      if (events.value.length === 0) {
        startExtract()
      }
    }, 500)
  }
})
</script>

<style scoped>
.extract-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.description {
  color: #606266;
  font-size: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-panel {
  padding: 10px 0;
}

.extract-controls {
  margin-top: 20px;
}

.action-area {
  margin: 25px 0;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.progress-text {
  font-size: 14px;
  color: #67C23A;
  margin-left: 10px;
}

.events-card, .gates-card, .stats-card {
  animation: slideUp 0.5s ease;
}

.gates-list {
  max-height: 400px;
  overflow-y: auto;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
