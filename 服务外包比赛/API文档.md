# 故障树智能生成系统 - API接口文档

## 基础信息
- 基础URL：http://localhost:8000/api/v1
- 数据格式：JSON
- 字符编码：UTF-8

## 1. 数据导入模块

### 1.1 文件上传
**接口地址**：POST /data/import

**请求参数**：
- file：文件对象（multipart/form-data）

**响应示例**：
```json
{
  "file_id": "uuid",
  "filename": "设备手册.docx",
  "file_size": 1024000,
  "status": "success",
  "message": "文件解析成功，提取100条文本记录"
}
```

## 2. 知识提取模块

### 2.1 提取知识
**接口地址**：POST /knowledge/extract

**请求参数**：
- file_id：文件ID（query参数）

**响应示例**：
```json
{
  "task_id": "uuid",
  "events": [
    {
      "event_id": "E1",
      "event_name": "系统故障",
      "event_type": "top",
      "description": "整个系统发生故障",
      "probability": 0.01
    }
  ],
  "gates": [
    {
      "gate_id": "G1",
      "gate_type": "OR",
      "input_events": ["E2", "E3"],
      "output_event": "E1"
    }
  ],
  "status": "completed",
  "progress": 1.0
}
```

## 3. 故障树生成模块

### 3.1 生成故障树
**接口地址**：POST /fault/tree/generate

**请求体**：
```json
{
  "knowledge_id": "uuid",
  "top_event": "系统故障",
  "max_depth": 5
}
```

**响应示例**：
```json
{
  "tree_id": "uuid",
  "nodes": [
    {
      "node_id": "N1",
      "node_type": "event",
      "label": "系统故障",
      "level": 0,
      "x": 200,
      "y": 50
    }
  ],
  "edges": [
    {
      "source": "N1",
      "target": "N2",
      "edge_type": "input"
    }
  ],
  "metadata": {}
}
```

### 3.2 优化故障树
**接口地址**：POST /fault/tree/optimize

**请求体**：
```json
{
  "tree_id": "uuid",
  "modified_nodes": [],
  "modified_edges": []
}
```

### 3.3 导出故障树
**接口地址**：GET /fault/tree/{tree_id}/export

**请求参数**：
- format：导出格式（json/png/svg）

## 错误码说明
- 200：成功
- 400：请求参数错误
- 500：服务器内部错误
