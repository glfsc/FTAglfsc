"""
故障树生成模块API
=================
完整实现故障树的生成、优化、导出和列表查询功能
【重要】请仔细阅读代码中的【需手动修改】标注
"""

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid
import os
import json
import logging
from enum import Enum

# ==================== 【需手动修改 1】 ====================
# 根据你的项目结构调整导入路径
# 如果你的项目结构不同，请修改以下导入语句
# =========================================================
try:
    # 假设你的服务层在 app/services/fault_tree_generator.py
    from app.services.fault_tree_generator import FaultTreeGenerator
    from app.services.neo4j_client import Neo4jClient  # 如果使用Neo4j
    from app.core.config import settings
    from app.models.schemas import (
        FaultTreeResponse,
        FaultTreeOptimizeRequest,
        FaultTreeExportResponse,
        FaultTreeListItem
    )
except ImportError:
    # 【需手动修改 2】如果上述导入失败，请根据实际项目结构调整
    # 临时方案：在本文件内定义必要模型（仅用于示例，生产环境应分离）
    logging.warning("使用内联模型定义，生产环境请移至 app/models/schemas.py")

    class NodeType(str, Enum):
        TOP = "1"      # 顶事件
        MIDDLE = "2"   # 中间事件
        BASE = "3"     # 底事件

    class GateType(str, Enum):
        AND = "1"
        OR = "2"
        NONE = ""

    class EdgeType(str, Enum):
        RESULTS_IN = "resultsIn"
        JOINTLY_RESULTS_IN = "jointly_resultsIn"
        CAUSED_BY = "causedBy"
        RELATED_TO = "relatedTo"

    class TripletSource(BaseModel):
        evidence: str = Field(..., description="证据来源")
        confidence: float = Field(0.8, ge=0.0, le=1.0, description="置信度")

    class EventDetail(BaseModel):
        id: str
        name: str
        description: str = ""
        errorLevel: str = ""
        priority: int = 0
        probability: float = 1e-8
        showProbability: float = 0.000001
        rules: Dict = Field(default_factory=dict)
        investigateMethod: str = ""
        documents: List[str] = Field(default_factory=list)

    class Node(BaseModel):
        id: str
        name: str
        type: NodeType
        gate: GateType = GateType.NONE
        x: int
        y: int
        event: EventDetail
        transfer: str = ""

    class Link(BaseModel):
        id: str
        type: Literal["link"] = "link"
        sourceId: str
        targetId: str
        edgeType: EdgeType
        isCondition: bool = False
        traceability: TripletSource

    class CanvasAttr(BaseModel):
        background: str = "#fff"
        fontColor: str = "#000"
        eventColor: str = "#000"
        eventFillColor: str = "#fff"
        gateColor: str = "#000"
        gateFillColor: str = "#fff"
        linkColor: str = "#456"
        eventCode: bool = True
        eventProbability: bool = False
        containerX: int = -53
        containerY: int = -74
        width: int = 1920
        height: int = 1080

    class FaultTreeResponse(BaseModel):
        attr: CanvasAttr
        nodeList: List[Node]
        linkList: List[Link]

    class FaultTreeOptimizeRequest(BaseModel):
        tree_id: str
        modified_nodes: Optional[List[Dict]] = None
        modified_edges: Optional[List[Dict]] = None

    class FaultTreeExportResponse(BaseModel):
        tree_id: str
        format: str
        download_url: str
        file_size: Optional[int] = None

    class FaultTreeListItem(BaseModel):
        id: str
        name: str
        top_event: str
        created_at: datetime
        updated_at: datetime
        node_count: int
        knowledge_id: str

# ==================== 【需手动修改 3】 ====================
# 配置导出目录（根据你的服务器环境修改）
# =========================================================
# 获取 backend 目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

# ==================== 【需手动修改 4】 ====================
import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter
from neo4j import GraphDatabase, exceptions

# ==================== 【需手动修改 4】 ====================
# 数据库存储方案选择（根据你的项目选择一种）
# =========================================================
# 配置项：选择存储方案 ("memory" / "file" / "neo4j")
STORAGE_SCHEME = "neo4j"  # 【核心配置】切换存储方案

# -------------------------- 方案A：内存存储（开发测试） --------------------------
if STORAGE_SCHEME == "memory":
    FAULT_TREES_DB: Dict[str, Dict[str, Any]] = {}  # key: tree_id, value: FaultTreeResponse

# -------------------------- 方案B：文件存储（持久化） --------------------------
elif STORAGE_SCHEME == "file":
    FAULT_TREES_DIR = "fault_trees"  # 【可修改】存储目录
    os.makedirs(FAULT_TREES_DIR, exist_ok=True)

    def save_fault_tree_to_file(tree_id: str, tree_data: dict, knowledge_id: str = ""):
        """将故障树数据保存到文件"""
        file_path = os.path.join(FAULT_TREES_DIR, f"{tree_id}.json")
        save_data = {
            "tree_id": tree_id,
            "knowledge_id": knowledge_id,
            "tree_data": tree_data,
            "create_time": datetime.now().isoformat(),
            "update_time": datetime.now().isoformat()
        }
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            logger.info(f"故障树 {tree_id} 已保存到文件: {file_path}")
        except Exception as e:
            logger.error(f"保存故障树文件失败: {str(e)}", exc_info=True)
            raise

    def get_fault_tree_from_file(tree_id: str) -> Optional[dict]:
        """从文件读取故障树数据"""
        file_path = os.path.join(FAULT_TREES_DIR, f"{tree_id}.json")
        if not os.path.exists(file_path):
            logger.warning(f"故障树文件不存在: {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("tree_data")
        except Exception as e:
            logger.error(f"读取故障树文件失败: {str(e)}", exc_info=True)
            return None

# -------------------------- 方案C：Neo4j数据库存储（生产环境） --------------------------
elif STORAGE_SCHEME == "neo4j":
    # Neo4j连接配置（从环境变量读取，与项目统一配置对齐）
    NEO4J_CONFIG = {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "your_password")
    }

    # 初始化Neo4j驱动
    try:
        neo4j_driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"])
        )
        # 测试连接
        neo4j_driver.verify_connectivity()
        logger.info("✅ Neo4j 故障树存储连接成功")
    except exceptions.Neo4jError as e:
        logger.error(f"❌ Neo4j 连接失败: {str(e)}", exc_info=True)
        raise

    def save_fault_tree_to_db(tree_id: str, tree_data: dict, knowledge_id: str = ""):
        """将故障树数据保存到Neo4j数据库"""
        cypher_query = """
        MERGE (t:FaultTree {tree_id: $tree_id})
        SET t.tree_data = $tree_data,
            t.knowledge_id = $knowledge_id,
            t.create_time = $create_time,
            t.update_time = $update_time
        """
        params = {
            "tree_id": tree_id,
            "tree_data": tree_data,
            "knowledge_id": knowledge_id,
            "create_time": datetime.now().isoformat(),
            "update_time": datetime.now().isoformat()
        }
        try:
            with neo4j_driver.session() as session:
                session.run(cypher_query, params)
            logger.info(f"故障树 {tree_id} 已保存到Neo4j数据库")
        except exceptions.Neo4jError as e:
            logger.error(f"保存故障树到Neo4j失败: {str(e)}", exc_info=True)
            raise

    def get_fault_tree_from_db(tree_id: str) -> Optional[dict]:
        """从Neo4j数据库读取故障树数据"""
        cypher_query = """
        MATCH (t:FaultTree {tree_id: $tree_id})
        RETURN t.tree_data AS tree_data
        """
        try:
            with neo4j_driver.session() as session:
                result = session.run(cypher_query, {"tree_id": tree_id})
                record = result.single()
                if record:
                    return record["tree_data"]
                logger.warning(f"未找到故障树数据: {tree_id}")
                return None
        except exceptions.Neo4jError as e:
            logger.error(f"读取故障树从Neo4j失败: {str(e)}", exc_info=True)
            return None

# -------------------------- 统一封装存储接口（适配所有方案） --------------------------
def save_fault_tree(tree_id: str, tree_data: dict, knowledge_id: str = ""):
    """统一保存故障树接口（自动适配所选存储方案）"""
    if STORAGE_SCHEME == "memory":
        FAULT_TREES_DB[tree_id] = {
            "tree_data": tree_data,
            "knowledge_id": knowledge_id,
            "create_time": datetime.now().isoformat(),
            "update_time": datetime.now().isoformat()
        }
        logger.info(f"故障树 {tree_id} 已保存到内存")
    elif STORAGE_SCHEME == "file":
        save_fault_tree_to_file(tree_id, tree_data, knowledge_id)
    elif STORAGE_SCHEME == "neo4j":
        save_fault_tree_to_db(tree_id, tree_data, knowledge_id)

def get_fault_tree(tree_id: str) -> Optional[dict]:
    """统一读取故障树接口（自动适配所选存储方案）"""
    if STORAGE_SCHEME == "memory":
        tree_info = FAULT_TREES_DB.get(tree_id)
        return tree_info["tree_data"] if tree_info else None
    elif STORAGE_SCHEME == "file":
        return get_fault_tree_from_file(tree_id)
    elif STORAGE_SCHEME == "neo4j":
        return get_fault_tree_from_db(tree_id)
    return None

# -------------------------- 路由初始化 --------------------------
router = APIRouter(prefix="/fault/tree", tags=["故障树生成"])
logger = logging.getLogger(__name__)

# ==================== 【需手动修改 5】 ====================
# 初始化故障树生成器（根据你的实现调整）
# =========================================================
try:
    # 假设你已实现 FaultTreeGenerator 类
    tree_generator = FaultTreeGenerator()
except Exception as e:
    logger.warning(f"故障树生成器初始化失败（开发模式）: {e}")
    # 【需手动修改】开发测试用的简化生成器
    class MockFaultTreeGenerator:
        def generate(self, knowledge_id: str, top_event: str, max_depth: int = 5):
            """简化版生成逻辑（仅用于测试）"""
            # 【需手动修改】此处应替换为真实算法
            # 示例：返回固定结构的故障树
            return FaultTreeResponse(
                attr=CanvasAttr(),
                nodeList=[
                    Node(
                        id="node-top0001",
                        name=top_event,
                        type=NodeType.TOP,
                        gate=GateType.OR,
                        x=860, y=100,
                        event=EventDetail(
                            id=f"evt_{uuid.uuid4().hex[:8]}",
                            name=top_event,
                            description="系统级故障",
                            probability=1e-5
                        )
                    ),
                    Node(
                        id="node-base0001",
                        name="液压系统失效",
                        type=NodeType.BASE,
                        gate=GateType.NONE,
                        x=700, y=300,
                        event=EventDetail(
                            id=f"evt_{uuid.uuid4().hex[:8]}",
                            name="液压系统失效",
                            description="根本原因",
                            probability=1e-6
                        )
                    )
                ],
                linkList=[
                    Link(
                        id=f"edge-{uuid.uuid4().hex[:8]}",
                        sourceId="node-base0001",
                        targetId="node-top0001",
                        edgeType=EdgeType.RESULTS_IN,
                        traceability=TripletSource(
                            evidence="维修手册 P45",
                            confidence=0.92
                        )
                    )
                ]
            )

    tree_generator = MockFaultTreeGenerator()

@router.post("/generate", response_model=FaultTreeResponse, summary="生成故障树")
async def generate_fault_tree(
    knowledge_id: str = Field(..., description="知识库ID"),
    top_event: str = Field(..., description="顶事件名称"),
    max_depth: int = Field(5, ge=1, le=10, description="最大深度")
):
    """
    基于知识图谱生成故障树

    【需手动修改 6】业务逻辑实现：
    1. 验证 knowledge_id 是否存在
    2. 从知识库获取三元组数据
    3. 调用故障树生成算法
    4. 保存生成结果到存储（内存/文件/数据库）
    """
    import uuid
    from typing import Optional, Dict, Any
    from fastapi import HTTPException

    # 请确保引入项目内的相关模块/实例/方法
    # 如：从app.state获取kg_builder、tree_generator实例，从存储模块引入save_fault_tree
    # from your_module import save_fault_tree  # 对应之前定义的统一存储方法

    try:
        logger.info(f"开始生成故障树: knowledge_id={knowledge_id}, top_event={top_event}")

        # ===================== 1. 验证 knowledge_id 是否存在 =====================
        # 从Neo4j校验知识集ID存在性（通过FaultTreeKnowledge节点/关系关联校验，贴合项目图谱设计）
        kg_builder = getattr(request.app.state, 'kg_builder', None)
        if not kg_builder:
            logger.error("知识图谱构建实例未初始化，数据库连接断开")
            raise HTTPException(status_code=503, detail="服务暂时不可用：数据库连接未初始化")

        # Cypher查询校验knowledge_id，项目统一使用Neo4j session执行查询
        verify_cypher = """
        MATCH (k:FaultTreeKnowledge {knowledge_id: $knowledge_id})
        RETURN count(k) > 0 AS exists
        """
        with kg_builder.driver.session() as session:
            verify_result = session.run(verify_cypher, {"knowledge_id": knowledge_id})
            is_exist = verify_result.single()["exists"] if verify_result.single() else False

        if not is_exist:
            logger.error(f"知识集ID不存在: knowledge_id={knowledge_id}")
            raise HTTPException(status_code=404, detail=f"knowledge_id={knowledge_id} 不存在，请检查后重试")

        # ===================== 2. 从知识库获取三元组数据 =====================
        # 按knowledge_id关联查询对应的故障因果三元组（主语-关系-宾语+属性）
        triplet_cypher = """
        MATCH (k:FaultTreeKnowledge {knowledge_id: $knowledge_id})-[:CONTAINS]->(s:FaultNode)-[r]->(o:FaultNode)
        RETURN s.name AS subject_name, labels(s)[0] AS subject_type,
               type(r) AS relation, o.name AS object_name, labels(o)[0] AS object_type,
               r.confidence AS confidence, r.sources AS source
        """
        with kg_builder.driver.session() as session:
            triplet_result = session.run(triplet_cypher, {"knowledge_id": knowledge_id})
            triplets = [record.data() for record in triplet_result]

        if not triplets:
            logger.warning(f"知识集无有效三元组数据: knowledge_id={knowledge_id}")
            raise HTTPException(status_code=400, detail=f"knowledge_id={knowledge_id} 无有效故障因果三元组数据")

        logger.info(f"从知识集获取有效三元组 {len(triplets)} 条: knowledge_id={knowledge_id}")

        # ===================== 3. 调用故障树生成算法 =====================
        # 获取故障树生成实例，调用项目原生build_tree_json方法生成标准化渲染数据
        tree_generator = getattr(request.app.state, 'tree_generator', None)
        if not tree_generator:
            logger.error("故障树生成实例未初始化，数据库连接断开")
            raise HTTPException(status_code=503, detail="服务暂时不可用：数据库连接未初始化")

        # 核心调用：传入顶事件，生成前端可渲染的故障树JSON（自动处理破环/逻辑门/布局）
        fault_tree_data = tree_generator.build_tree_json(top_event_name=top_event)
        if not fault_tree_data or not fault_tree_data.get("nodeList"):
            logger.error(f"故障树生成失败，无有效节点数据: top_event={top_event}, knowledge_id={knowledge_id}")
            raise HTTPException(status_code=422, detail=f"基于顶事件{top_event}未生成有效故障树，请检查知识图谱数据")

        node_count = len(fault_tree_data.get("nodeList", []))
        link_count = len(fault_tree_data.get("linkList", []))
        logger.info(f"故障树生成成功: top_event={top_event}, 节点数={node_count}, 连线数={link_count}")

        # ===================== 4. 保存生成结果到存储（内存/文件/数据库） =====================
        # 生成唯一故障树ID（UUID保证唯一性），贴合项目存储的tree_id设计
        tree_id = f"tree_{uuid.uuid4().hex[:16]}"
        # 调用统一存储方法（适配内存/文件/Neo4j，对应之前定义的save_fault_tree）
        save_fault_tree(tree_id=tree_id, tree_data=fault_tree_data, knowledge_id=knowledge_id)

        logger.info(f"故障树结果保存成功: tree_id={tree_id}, knowledge_id={knowledge_id}")

        # 返回复用结果（含tree_id方便前端查询/渲染）
        return {
            "status": "success",
            "tree_id": tree_id,
            "knowledge_id": knowledge_id,
            "top_event": top_event,
            "data": fault_tree_data,
            "message": f"故障树生成成功，共{node_count}个节点，{link_count}条连线"
        }

    except HTTPException as e:
        # 抛出FastAPI标准异常，直接返回给前端
        raise e
    except Exception as e:
        # 捕获未知异常，记录完整堆栈并返回通用错误
        logger.error(f"故障树生成业务逻辑执行失败: knowledge_id={knowledge_id}, top_event={top_event}, error={str(e)}",
                     exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"故障树生成失败：{str(e)}，请联系管理员排查"
        )
        # 【需手动修改 7】添加知识库验证逻辑
        # if not knowledge_service.exists(knowledge_id):
        #     raise HTTPException(status_code=404, detail=f"未找到知识ID: {knowledge_id}")

        # 生成故障树
        fault_tree = tree_generator.generate(knowledge_id, top_event, max_depth)

        # 生成唯一ID
        tree_id = f"tree_{uuid.uuid4().hex[:10]}"

        # 【需手动修改 8】保存故障树到存储
        # 方案A（内存）：
        FAULT_TREES_DB[tree_id] = {
            "id": tree_id,
            "data": fault_tree.dict(),
            "knowledge_id": knowledge_id,
            "top_event": top_event,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "node_count": len(fault_tree.nodeList)
        }

        # 方案B（文件）：
        # tree_path = os.path.join(FAULT_TREES_DIR, f"{tree_id}.json")
        # with open(tree_path, "w", encoding="utf-8") as f:
        #     json.dump(fault_tree.dict(), f, ensure_ascii=False, indent=2)

        # 方案C（数据库）：
        # save_fault_tree_to_db(tree_id, fault_tree.dict(), knowledge_id)

        logger.info(f"故障树生成成功: tree_id={tree_id}, 节点数={len(fault_tree.nodeList)}")
        return fault_tree

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"故障树生成失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"故障树生成失败: {str(e)}"
        )

@router.post("/optimize", response_model=FaultTreeResponse, summary="优化故障树")
async def optimize_fault_tree(request: FaultTreeOptimizeRequest):
    """
    专家优化故障树结构

    【需手动修改 9】优化逻辑实现：
    1. 验证 tree_id 是否存在
    2. 应用专家修改（节点/连线）
    3. 重新验证逻辑一致性
    4. 保存优化结果
    """
    try:
        # 【需手动修改 10】验证 tree_id
        # tree_data = get_fault_tree_from_db(request.tree_id)
        # if not tree_data:
        #     raise HTTPException(status_code=404, detail=f"未找到故障树: {request.tree_id}")

        # 【需手动修改 11】应用优化逻辑
        # optimized_tree = tree_generator.optimize(
        #     original_tree=tree_data,
        #     modified_nodes=request.modified_nodes,
        #     modified_edges=request.modified_edges
        # )

        # 【需手动修改 12】保存优化结果
        # FAULT_TREES_DB[request.tree_id]["data"] = optimized_tree.dict()
        # FAULT_TREES_DB[request.tree_id]["updated_at"] = datetime.now()

        # 临时返回原树（开发测试）
        if request.tree_id not in FAULT_TREES_DB:
            raise HTTPException(status_code=404, detail=f"未找到故障树: {request.tree_id}")

        # 简化：返回原树（实际应返回优化后结果）
        return FaultTreeResponse(**FAULT_TREES_DB[request.tree_id]["data"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"故障树优化失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"故障树优化失败: {str(e)}"
        )

@router.get("/{tree_id}/export", response_model=FaultTreeExportResponse, summary="导出故障树")
async def export_fault_tree(
    tree_id: str = Path(..., description="故障树ID"),
    format: Literal["json", "png", "svg"] = Query("json", description="导出格式")
):
    """
    导出故障树为指定格式

    【需手动修改 13】导出功能实现：
    1. 验证 tree_id 和 format
    2. 生成对应格式文件
    3. 返回下载链接
    """
    try:
        # 【需手动修改 14】验证 tree_id
        # tree_data = get_fault_tree_from_db(tree_id)
        # if not tree_data:
        #     raise HTTPException(status_code=404, detail=f"未找到故障树: {tree_id}")

        # 临时使用内存存储
        if tree_id not in FAULT_TREES_DB:
            raise HTTPException(status_code=404, detail=f"未找到故障树: {tree_id}")

        tree_data = FAULT_TREES_DB[tree_id]["data"]

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fault_tree_{tree_id}_{timestamp}.{format}"
        filepath = os.path.join(EXPORT_DIR, filename)

        # 【需手动修改 15】根据格式生成文件
        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(tree_data, f, ensure_ascii=False, indent=2)
        elif format == "png":
            # 【需手动修改】需要集成图形渲染库（如 cairosvg + PIL）
            raise HTTPException(
                status_code=501,
                detail="PNG导出功能暂未实现，请联系开发人员"
            )
        elif format == "svg":
            # 【需手动修改】需要生成SVG格式的故障树可视化
            raise HTTPException(
                status_code=501,
                detail="SVG导出功能暂未实现，请联系开发人员"
            )

        # 【需手动修改 16】生成可访问的下载URL
        # 生产环境应使用静态文件服务或临时下载链接
        # download_url = f"/static/exports/{filename}"
        download_url = f"/api/v1/fault/tree/download/{filename}"  # 需实现下载接口

        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

        logger.info(f"故障树导出成功: {filename}, 大小={file_size} bytes")

        return FaultTreeExportResponse(
            tree_id=tree_id,
            format=format,
            download_url=download_url,
            file_size=file_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"故障树导出失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )

@router.get("/list", response_model=List[FaultTreeListItem], summary="获取故障树列表")
async def list_fault_trees():
    """获取所有已生成的故障树列表"""
    try:
        # 【需手动修改 17】从存储中获取列表
        # 方案A（内存）：
        trees = [
            FaultTreeListItem(
                id=tree["id"],
                name=f"故障树-{tree['id']}",
                top_event=tree["top_event"],
                created_at=tree["created_at"],
                updated_at=tree["updated_at"],
                node_count=tree["node_count"],
                knowledge_id=tree["knowledge_id"]
            )
            for tree in FAULT_TREES_DB.values()
        ]

        # 方案B（数据库）：
        # trees = fault_tree_service.get_all_trees()

        logger.info(f"返回故障树列表，共 {len(trees)} 条")
        return trees

    except Exception as e:
        logger.error(f"获取故障树列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取列表失败: {str(e)}"
        )

# ==================== 【需手动修改 18】 ====================
# 添加文件下载接口（用于导出文件下载）
# =========================================================
@router.get("/download/{filename}", summary="下载导出的故障树文件")
async def download_exported_file(filename: str):
    """
    【需手动修改】实现文件下载功能
    注意：生产环境需添加安全验证，防止路径遍历攻击
    """
    try:
        filepath = os.path.join(EXPORT_DIR, filename)

        # 【需手动修改】安全验证：防止路径遍历
        # if ".." in filename or filename.startswith("/"):
        #     raise HTTPException(status_code=403, detail="非法文件名")

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 【需手动修改】根据文件类型设置Content-Type
        # 此处简化返回文件内容（实际应使用FileResponse）
        with open(filepath, "rb") as f:
            content = f.read()

        # 实际应使用：
        # from fastapi.responses import FileResponse
        # return FileResponse(filepath, filename=filename)

        return {"message": "文件下载功能需完善，请参考注释实现"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

# ==================== 【需手动修改 19】 ====================
# 添加启动时初始化逻辑（可选）
# =========================================================
@router.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("故障树模块初始化中...")

    # 【需手动修改】初始化数据库连接、加载缓存等
    # 示例：
    # global neo4j_client
    # neo4j_client = Neo4jClient(
    #     uri=settings.NEO4J_URI,
    #     user=settings.NEO4J_USER,
    #     password=settings.NEO4J_PASSWORD
    # )

    logger.info("故障树模块初始化完成")

# ==================== 【需手动修改 20】 ====================
# 添加关闭时清理逻辑（可选）
# =========================================================
@router.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("故障树模块清理中...")

    # 【需手动修改】关闭数据库连接、释放资源等
    # 示例：
    # if 'neo4j_client' in globals():
    #     neo4j_client.close()

    logger.info("故障树模块清理完成")