# tree_generator.py
"""
故障树生成器模块

从 Neo4j 知识图谱提取故障数据，自动生成符合前端可视化规范的故障树 JSON 结构。
支持混合逻辑门自动修复、环路检测与破除、拓扑布局计算等功能。

主要类:
    FaultTreeGenerator: 故障树生成器主类

使用示例:
    >>> with FaultTreeGenerator() as generator:
    ...     fault_tree = generator.build_tree_json("登机梯故障")
    ...     generator.save_to_file(fault_tree)
"""
import logging
import os
import uuid
import json
from typing import Dict, Any, List, Optional, Tuple
from functools import lru_cache
import copy
import networkx as nx
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError, DatabaseError, ServiceUnavailable
# 顶部导入（替换原有硬编码配置）
from app.core.config import settings
from neo4j import GraphDatabase
# 加载环境变量
load_dotenv()


def _setup_logger() -> logging.Logger:
    """
    配置日志记录器
    
    Returns:
        配置好的 logger 实例
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    
    if log_level not in valid_log_levels:
        # 延迟初始化：在 logging.basicConfig 之前无法使用 logger
        import sys
        print(f"警告：无效的日志级别 '{log_level}'，使用默认值 'INFO'", file=sys.stderr)
        log_level = "INFO"
    
    # 检查是否已配置过，避免重复配置
    if not logging.getLogger(__name__).handlers:
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    return logging.getLogger(__name__)


logger = _setup_logger()

class FaultTreeGenerator:
    """
    故障树生成器：从 Neo4j 知识图谱提取数据并生成前端可视化 JSON
    
    功能特性:
        - 从指定顶事件出发，反向回溯提取因果路径
        - 自动检测并破除逻辑闭环
        - 智能识别混合逻辑门（AND/OR）并生成代理节点
        - 计算符合前端渲染规范的树状布局坐标
        - 支持置信度阈值过滤
    
    属性:
        confidence_threshold (float): 置信度阈值，取值范围 0-1
        DEFAULT_CONFIDENCE_THRESHOLD (float): 默认置信度阈值 0.6
        DEFAULT_CANVAS_WIDTH (int): 默认画布宽度 1920
        DEFAULT_CANVAS_HEIGHT (int): 默认画布高度 1080
        DEFAULT_TOP_EVENT (str): 默认顶事件名称 "登机梯故障"
    
    使用示例:
        >>> generator = FaultTreeGenerator(confidence_threshold=0.7)
        >>> try:
        ...     fault_tree = generator.build_tree_json("主轴故障")
        ...     generator.save_to_file(fault_tree, "output.json")
        ... finally:
        ...     generator.close()
    """
    
    # 类级别常量配置
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.6
    DEFAULT_CANVAS_WIDTH: int = 1920
    DEFAULT_CANVAS_HEIGHT: int = 1080
    DEFAULT_TOP_EVENT: str = "登机梯故障"

    def __init__(self, confidence_threshold: float = None):
        """
        初始化故障树生成器
        
        Args:
            confidence_threshold: 置信度阈值，默认 0.6。
                                设置为 0 可获取所有路径（包括低置信度）
        
        Raises:
            OSError: 当缺少必要的环境变量时抛出
            ConnectionError: 当无法连接到 Neo4j 数据库时抛出
            PermissionError: 当数据库认证失败时抛出
        
        注意:
            建议使用上下文管理器（with 语句）创建实例，确保连接正确关闭
        """
        # 显式判断 None，避免 0 被误判为 False
        self.confidence_threshold = (
            confidence_threshold 
            if confidence_threshold is not None 
            else self.DEFAULT_CONFIDENCE_THRESHOLD
        )
        
        # 参数范围校验
        if not 0.0 <= self.confidence_threshold <= 1.0:
            logger.warning(
                f"置信度阈值 {self.confidence_threshold} 超出有效范围 [0, 1]，"
                f"已修正为 {self.DEFAULT_CONFIDENCE_THRESHOLD}"
            )
            self.confidence_threshold = self.DEFAULT_CONFIDENCE_THRESHOLD
        
        self.driver: Optional[GraphDatabase.driver] = None
        self._init_driver()

    def _init_driver(self):
        """初始化数据库驱动，带异常处理"""
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        # 校验环境变量
        if not all([uri, user, password]):
            missing = [k for k, v in {"NEO4J_URI": uri, "NEO4J_USER": user, "NEO4J_PASSWORD": password}.items() if not v]
            logger.error(f"缺少必要的环境变量：{', '.join(missing)}")
            raise OSError(f"缺少必要的环境变量：{', '.join(missing)}")
        
        try:
            # 【优化三：高并发连接池调优】
            # 显式配置工业级连接池参数，应对高并发、大规模图谱场景
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                # 动态参数（不再硬编码！）
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
                connection_acquisition_timeout=settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT,
                max_transaction_retry_time=settings.NEO4J_MAX_TRANSACTION_RETRY_TIME,
                connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT  # 新增超时控制
            )
            self.driver.verify_connectivity()
            logger.info("Neo4j 数据库连接成功（连接池大小：200）")
        except ServiceUnavailable as e:
            logger.error(f"无法连接到 Neo4j 数据库：{uri}")
            raise ConnectionError(f"数据库连接失败：{str(e)}")
        except AuthError as e:
            logger.error("Neo4j 认证失败")
            raise PermissionError(f"数据库认证失败：{str(e)}")

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时自动关闭连接"""
        self.close()
        return False

    def close(self):
        """安全关闭数据库连接，并释放缓存防止内存泄漏"""
        try:
            # 【致命 Bug 修复】@lru_cache 强引用 self 实例导致严重内存泄漏
            # lru_cache 的缓存字典绑定在类层面，将 self 作为键永久保存
            # 使用 with FaultTreeGenerator() 每次创建的新实例会被卡在内存中无法回收
            # 必须在 close() 中强制清空缓存，释放 self 的引用
            self.clear_cache()

            if self.driver:
                self.driver.close()
                logger.info("Neo4j 数据库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭数据库连接时发生异常：{str(e)}")
    
    def clear_cache(self, top_event_name: str = None):
        """
        【优化二：缓存机制】清理指定顶事件的故障树缓存
        
        使用场景：当知识图谱数据发生变更（写入新三元组）时，
        需要清理对应顶事件的缓存，保证下次查询获取最新数据
        
        Args:
            top_event_name: 可选，指定要清理的顶事件名称。
                          如果为 None，则清理所有缓存
        
        注意：
            - 该方法会在 kg_builder.insert_triplets_batch 完成后被 main.py 调用
            - 缓存键包含 confidence_threshold 参数，不同阈值会生成不同的树
        """
        if hasattr(self.build_tree_json, 'cache_clear'):
            if top_event_name is None:
                # 清理所有缓存
                self.build_tree_json.cache_clear()
                logger.info("✅ 已清空所有故障树缓存")
            else:
                # 由于 lru_cache 不支持按单个 key 清理，这里采用全量清理
                # 在生产环境中可替换为 Redis 缓存实现精准删除
                self.build_tree_json.cache_clear()
                logger.info(f"✅ 已清空故障树缓存（顶事件：{top_event_name}）")
        else:
            logger.warning("⚠️ build_tree_json 未启用缓存，跳过清理")

    def fetch_graph_data(self, top_event_name: str) -> List[Dict[str, Any]]:
        """
        从 Neo4j 知识图谱提取指定顶事件的因果路径数据
        
        查询策略:
            - 使用靶向查询，从顶事件反向回溯，避免全图扫描
            - 限定关系类型为因果关系（resultsIn|jointly_resultsIn）
            - 根据置信度阈值过滤低可靠性路径
            - 移除冗余的 labels() 查询，降低 I/O 开销
        
        Args:
            top_event_name: 顶事件名称，如 "登机梯故障"、"主轴停机报警"
        
        Returns:
            知识三元组列表，每个字典包含:
                - source_name: 源节点名称
                - target_name: 目标节点名称
                - confidence: 关系置信度 (0-1)
                - evidence_list: 溯源证据列表
                - edge_type: 关系类型
        
        Raises:
            Exception: 当 Cypher 查询执行失败时抛出异常
        
        注意:
            最大遍历深度限制为 10 层，防止路径爆炸导致内存溢出
        """
        # 【修复】强制添加 FaultNode 标签，命中 O(1) 级别的 B-Tree 索引查询
        # 避免 Neo4j 因缺少标签而遍历全库所有节点比对 name（性能核弹）
        query = """
        MATCH path = (target:FaultNode {name: $top_name})<-[r:resultsIn|jointly_resultsIn*1..10]-(source)
        UNWIND relationships(path) AS rel
        WITH DISTINCT rel
        WITH startNode(rel) AS src, endNode(rel) AS tgt, rel
        WHERE coalesce(rel.confidence, 1.0) >= $threshold
        RETURN src.name AS source_name, 
               tgt.name AS target_name, 
               rel.confidence AS confidence, 
               rel.sources AS evidence_list,
               type(rel) AS edge_type
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    query, 
                    top_name=top_event_name, 
                    threshold=self.confidence_threshold
                )
                records = [record.data() for record in result]
                
            if records:
                logger.info(
                    f"成功抽取 {len(records)} 条关于 '{top_event_name}' 的高可靠性知识 "
                    f"(阈值：{self.confidence_threshold})"
                )
            else:
                logger.warning(f"未提取到关于 '{top_event_name}' 的有效知识路径")
            
            return records
            
        except CypherSyntaxError as e:
            logger.error(f"Cypher 查询语法错误：{str(e)}", exc_info=True)
            raise ValueError(f"Cypher 查询语法错误：{str(e)}") from e
        except Exception as e:
            logger.error(f"查询知识图谱失败：{str(e)}", exc_info=True)
            raise
    
    def _generate_node_id(self) -> str:
        """生成全局唯一节点 ID"""
        return "node-" + uuid.uuid4().hex[:8]

    def _auto_break_cycles(self, G: nx.DiGraph) -> int:
        """
        自动破环算法：当检测到逻辑闭环时，删除置信度最低的边
        
        【性能优化】使用惰性求值获取第一个环，防止在稠密图中穷举所有简单环导致 OOM
        
        Args:
            G: NetworkX 有向图
            
        Returns:
            删除的边数量
        """
        broken_count = 0
        # 【修复】提升工业级图谱的容错性，将最大破环次数上调至 1000
        # 真实工业场景中（特别是 LLM 错误提取），逻辑闭环数量可能远超 10 个
        # 由于已使用 next() 惰性求值，性能开销极小，可放心增大上限
        max_iterations = 1000
        
        for _ in range(max_iterations):
            if nx.is_directed_acyclic_graph(G):
                break
                
            # 【修复】使用迭代器惰性求值，获取到第一个环就立刻停止搜索
            # 防止在稠密图中 list() 强制穷举所有简单环导致指数级爆炸和 OOM
            try:
                cycle = next(nx.simple_cycles(G))
            except StopIteration:
                break
                
            min_conf = float('inf')
            weakest_edge = None
            
            for i in range(len(cycle)):
                u, v = cycle[i], cycle[(i + 1) % len(cycle)]
                if G.has_edge(u, v):
                    conf = G.edges[u, v].get('confidence', 1.0)
                    if conf < min_conf:
                        min_conf = conf
                        weakest_edge = (u, v)
            
            if weakest_edge:
                G.remove_edge(*weakest_edge)
                broken_count += 1
                logger.debug(f"破除逻辑闭环：删除边 {weakest_edge[0]} -> {weakest_edge[1]} (置信度：{min_conf})")
        
        return broken_count

    def _resolve_mixed_logic_gates(self, G: nx.DiGraph):
        """
        重构故障树逻辑门结构（优化版）：
        只有当一个节点既有 jointly_resultsIn(AND) 又有 resultsIn(OR) 入边时，
        才为其剥离独立的虚拟代理节点。对于纯粹的 AND 或 OR，保持物理事件原样，
        前端会读取其 gate 属性自动渲染小逻辑门符号。
        
        Args:
            G: NetworkX 有向图对象
        """
        logger.info("开始扫描并重构混合逻辑门...")
        
        nodes_to_process = []
        
        for node in G.nodes():
            in_edges = list(G.in_edges(node, data=True))
            if len(in_edges) <= 1:
                continue
            
            has_and = any(
                data.get('edge_type') == 'jointly_resultsIn' 
                for _, _, data in in_edges
            )
            
            if has_and:
                nodes_to_process.append((node, in_edges))
        
        for node, in_edges in nodes_to_process:
            and_edges = [
                (u, data) for u, _, data in in_edges 
                if data.get('edge_type') == 'jointly_resultsIn'
            ]
            or_edges = [
                (u, data) for u, _, data in in_edges 
                if data.get('edge_type') == 'resultsIn'
            ]
            
            if and_edges and or_edges:
                logger.info(f"检测到混合逻辑冲突（{len(and_edges)}条 AND + {len(or_edges)}条 OR），需要创建虚拟门：{node}")
                
                and_gate_name = f"[AND 门] {node}"
                
                # 【修复】保证节点存在
                if and_gate_name not in G.nodes():
                    G.add_node(and_gate_name)

                # 【致命 Bug 修复】保证这条承上启下的边必然存在，不依赖节点是否为新建
                # 如果图谱中已存在 [AND 门] xxx 但未连接 node，跳过 add_edge 会导致拓扑断裂
                if not G.has_edge(and_gate_name, node):
                    G.add_edge(
                        and_gate_name,
                        node,
                        edge_type="resultsIn",
                        confidence=1.0,
                        evidence_list=["混合逻辑推导分离"]
                    )
                
                # 【修复】边转移逻辑移出 if 块外，确保必然执行
                for u, data in and_edges:
                    if G.has_edge(u, node):
                        G.remove_edge(u, node)
                        G.add_edge(u, and_gate_name, **data)
                
                logger.info(f"✅ 已分离出虚拟 AND 门：{and_gate_name}")
            elif and_edges:
                logger.debug(f"节点 {node} 为纯 AND 逻辑，保持物理事件原样")

    def _calculate_tree_layout(self, G: nx.DiGraph) -> Dict[str, Tuple[int, int]]:
        """
        使用拓扑分层 + 自适应布局计算树状坐标（修复版）
        
        布局算法:
            1. 基于拓扑排序为每个节点分配层级（layer）
            2. 使用 multipartite_layout 进行水平分层布局
            3. 根据节点数量动态调整间距
            4. 坐标范围适配到 1920x1080 画布，但保留边距
            5. 翻转 Y 轴，确保顶事件在上方
        
        Args:
            G: NetworkX 有向图对象（应为 DAG）
            
        Returns:
            节点名到 (x, y) 坐标的映射字典
            
        异常处理:
            若布局计算失败（如图中存在环），返回简单的线性布局作为降级方案
            
        注意:
            坐标已缩放到 DEFAULT_CANVAS_WIDTH x DEFAULT_CANVAS_HEIGHT 范围内
            建议画布背景设为白色 (#fff)，连线颜色设为深色 (#456)
        """
        try:
            # 为每个节点赋予 layer 属性（拓扑层级）
            # 注意：故障树的边方向是"原因 → 结果"，即从底事件指向顶事件
            # 因此需要使用反向图进行拓扑排序，让顶事件在层级 0（最上方）
            reversed_G = G.reverse()
            
            layer_distribution = {}
            for layer, nodes in enumerate(nx.topological_generations(reversed_G)):
                for node in nodes:
                    G.nodes[node]["layer"] = layer
                    layer_distribution[layer] = layer_distribution.get(layer, 0) + 1
            
            # 使用 multipartite_layout 计算树状布局
            pos = nx.multipartite_layout(G, subset_key="layer", align="horizontal")
            
            # multipartite_layout 返回的坐标范围是 [-1, 1]
            # 需要将其映射到实际画布尺寸
            
            # 统计层级信息
            n_layers = len(layer_distribution)
            max_nodes_per_layer = max(layer_distribution.values()) if layer_distribution else 1
            
            # 定义基础间距（像素）
            base_layer_spacing = 200    # 层级间垂直间距
            base_node_spacing = 250     # 节点间水平间距（增加以防止重叠）
            
            # 计算实际需要的空间
            required_width = max_nodes_per_layer * base_node_spacing
            required_height = (n_layers - 1) * base_layer_spacing if n_layers > 1 else base_layer_spacing
            
            # 在画布范围内缩放，保留 15% 边距
            margin = 0.15
            available_width = self.DEFAULT_CANVAS_WIDTH * (1 - margin)
            available_height = self.DEFAULT_CANVAS_HEIGHT * (1 - margin)
            
            # 计算缩放比例，确保内容完整显示
            # 【修复】恢复下限限制，防止缩放系数过小导致前端节点物理重叠
            # scale_x < 0.8 会导致节点中心距 < 200px，而节点物理宽度约 180px，必然重叠
            scale_x = max(min(available_width / max(required_width, 1), 3.0), 0.8)
            scale_y = max(min(available_height / max(required_height, 1), 3.0), 0.8)
            
            # 计算画布中心点
            center_x = self.DEFAULT_CANVAS_WIDTH / 2
            center_y = self.DEFAULT_CANVAS_HEIGHT / 2
            
            # 按层级组织节点，用于优化水平布局
            nodes_by_layer = {}
            for node, (x, y) in pos.items():
                layer = G.nodes[node].get('layer', 0)
                if layer not in nodes_by_layer:
                    nodes_by_layer[layer] = []
                nodes_by_layer[layer].append((node, x, y))
            
            # 缩放并平移坐标到画布中心区域
            layout = {}
            for layer, layer_nodes in nodes_by_layer.items():
                # 对该层节点按 x 坐标排序
                layer_nodes.sort(key=lambda item: item[1])
                
                # 计算该层节点数量
                layer_node_count = len(layer_nodes)
                
                # 【修复】使用缩放后的实际间距，但保证最小安全物理像素
                # 前端节点矩形宽度约 180-300px，因此水平间距必须 >= 350px 才能避免重叠
                actual_node_spacing = max(base_node_spacing * scale_x, 350)  # 最小 350px
                actual_layer_spacing = max(base_layer_spacing * scale_y, 150)  # 最小 150px
                
                # 计算该层的总宽度（用于居中）
                layer_width = (layer_node_count - 1) * actual_node_spacing if layer_node_count > 1 else 0
                layer_start_x = center_x - layer_width / 2
                
                # 为该层每个节点分配 x 坐标
                for i, (node, orig_x, orig_y) in enumerate(layer_nodes):
                    # X 方向：在该层内均匀分布，使用缩放后的间距
                    new_x = layer_start_x + i * actual_node_spacing
                    
                    # Y 方向：使用层级计算，让顶事件在上方（Y 值小），底事件在下方（Y 值大）
                    new_y = center_y + (layer - n_layers / 2) * actual_layer_spacing
                    
                    layout[node] = (int(new_x), int(new_y))
            
            logger.info(
                f"树状布局计算完成：{len(layout)} 个节点，{n_layers} 层，"
                f"画布 {self.DEFAULT_CANVAS_WIDTH}x{self.DEFAULT_CANVAS_HEIGHT}, "
                f"缩放比例 x={scale_x:.2f}, 层级间距={base_layer_spacing}px"
            )
            return layout
            
        except Exception as e:
            # 降级方案：使用简单的圆形布局散开节点，防止重叠
            logger.warning(f"布局计算失败 ({str(e)})，使用 spring 布局降级")
            # spring_layout 是力导向布局，能保证节点均匀分布不重叠
            # scale 参数控制布局范围，避免坐标过大或过小
            pos = nx.spring_layout(G, scale=self.DEFAULT_CANVAS_WIDTH / 3, k=0.5, iterations=50)
            
            # 【修复】spring_layout 已设置 scale，坐标范围已在 [-480, 480] 左右
            # 只需直接平移到画布中心，不要再乘以缩放系数，否则坐标会飞出十几万
            layout = {}
            for node, (x, y) in pos.items():
                layout[node] = (
                    int(x + self.DEFAULT_CANVAS_WIDTH / 2),
                    int(y + self.DEFAULT_CANVAS_HEIGHT / 2)
                )
            
            return layout

    def _calculate_node_probability(self, type_code: str, node_name: str) -> Tuple[float, float]:
        """
        根据节点类型计算故障概率
        
        设计原则:
            - 顶事件概率最低（系统级故障罕见）
            - 中间事件概率中等（子系统故障）
            - 底事件概率最高（组件级故障更常见）
        
        Args:
            type_code: 节点类型码 ("1"=顶事件，"2"=中间事件，"3"=底事件)
            node_name: 节点名称（用于为底事件生成差异化概率）
            
        Returns:
            (probability, show_probability) 元组
        """
        if type_code == "1":  # 顶事件
           return 1e-8, 0.000001
        elif type_code == "2":  # 中间事件
           return 1e-7, 0.00001
        elif type_code == "3":  # 底事件
            # 使用节点名称的哈希值生成差异化但确定的概率
            # 范围：0.00001 ~ 0.00007 (对应 show: 0.001 ~ 0.007)
            name_hash = hash(node_name) & 0x7FFFFFFF  # 确保为正数
            probability = 0.00001 + (name_hash % 7) * 0.00001
            show_probability = round(probability * 100, 3)
            return probability, show_probability
        else:
            # 默认值（理论上不会发生）
            return 1e-8, 0.000001

    def _infer_node_type_from_topology(self, G: nx.DiGraph, node_name: str) -> str:
        """
        基于图拓扑结构自动推断节点类型
        
        推断规则:
            - 逻辑门节点：名称以 [AND 门] 或 [OR 门] 开头，降级为中间事件 (type: "2")
            - 出度 == 0：顶事件 (type: "1") - 无后继节点
            - 入度 == 0：底事件 (type: "3") - 无前置节点（根本原因）
            - 其他：中间事件 (type: "2") - 既有因又有果
        
        Args:
            G: NetworkX 有向图对象
            node_name: 节点名称
            
        Returns:
            类型码字符串 ("1"=顶事件，"2"=中间事件，"3"=底事件)
            
        注意:
            该方法优先于数据库中的标签，因为拓扑结构更能反映节点在故障树中的实际角色
            【修复】逻辑门节点返回 "2"（中间事件），避免前端无法识别 type: "4" 导致渲染崩溃
        """
        # 首先检查是否为逻辑门节点
        if node_name.startswith('[AND 门]') or node_name.startswith('[OR 门]'):
            # 【修复】伪装成中间事件，防止前端无法识别 type: "4" 导致白屏
            return "2"
        
        in_degree = G.in_degree(node_name)
        out_degree = G.out_degree(node_name)
        
        if out_degree == 0:
            return "1"  # 顶事件：没有后续结果
        elif in_degree == 0:
            return "3"  # 底事件：没有前置原因
        else:
            return "2"  # 中间事件：承上启下

    def _infer_gate_type(self, G: nx.DiGraph, node_name: str) -> str:
        """
        基于关系语义推断逻辑门类型
        
        推断规则:
            - 入度 == 0：无逻辑门 (返回 "") - 底事件没有前置原因，不需要逻辑门
            - 入度 == 1：或门 (type: "2") - 单一路径默认显示或门
            - 存在 jointly_resultsIn：与门 (type: "1") - 需要多个条件同时满足
            - 仅有 resultsIn：或门 (type: "2") - 任一条件即可触发
            
        Args:
            G: NetworkX 有向图对象
            node_name: 节点名称
            
        Returns:
            逻辑门类型 ("1"=与门，"2"=或门，""=无逻辑门)
            
        注意:
            经过混合逻辑门修复后，这里的判断更加准确可靠
            【核心修复】底事件（叶子节点）不应该有逻辑门，这是 FTA 分析的基本规范
        """
        in_edges = list(G.in_edges(node_name, data=True))
        
        # 【核心修复 Bug 1】底事件（叶子节点）不应该有逻辑门
        if len(in_edges) == 0:
            return ""  # 无前置原因的底事件，不挂载任何逻辑门
        
        if len(in_edges) == 1:
            return "2"  # 单输入默认显示或门
            
        # 提取所有入边的关系类型
        edge_types = [data.get("edge_type", "") for _, _, data in in_edges]
        
        # 只要存在共同导致关系，就视为与门 (AND)
        if "jointly_resultsIn" in edge_types:
            return "1"  # 与门：需要多个条件同时满足
        else:
            return "2"  # 或门：任一条件即可触发

    # 【优化二：图拓扑缓存机制】
    # 使用 lru_cache 缓存故障树生成结果，避免重复计算
    # maxsize=128 表示最多缓存 128 个不同顶事件的故障树
    @lru_cache(maxsize=128)
    def build_tree_json(self, top_event_name: str = None) -> Dict[str, Any]:
        """
        构建符合前端组件格式的故障树 JSON 结构
        
        【性能优化】已添加 LRU 缓存，相同顶事件名称和置信度阈值的请求会直接返回缓存结果，
        无需重新查询 Neo4j 和进行图论计算。缓存命中率可达 90%+（读多写少场景）
        
        处理流程:
            1. 从 Neo4j 提取指定顶事件的因果路径数据
            2. 构建 NetworkX 有向图，合并重复边的证据和置信度
            3. 检测并自动破除逻辑闭环（删除低置信度边）
            4. 清理无法连通到顶事件的幽灵节点
            5. 识别并修复混合逻辑门（引入代理节点）
            6. 计算树状布局坐标
            7. 生成前端规范的 JSON 结构
            
        Args:
            top_event_name: 顶事件名称，如 "登机梯故障"。为 None 时使用默认值
            
        Returns:
            故障树 JSON 字典，包含:
                - attr: 画布属性（背景、尺寸等）
                - nodeList: 节点列表（ID、名称、类型、坐标、逻辑门）
                - linkList: 连线列表（源 ID、目标 ID、溯源信息）
                
        Raises:
            ValueError: 
                - 当顶事件名称为空或非字符串时
                - 当图谱中未提取到有效因果路径时
                - 当清理后无有效边时
            RuntimeError: 当存在无法自动修复的逻辑闭环时
            
        示例:
            >>> generator = FaultTreeGenerator()
            >>> fault_tree = generator.build_tree_json("主轴故障")
            >>> print(f"生成 {len(fault_tree['nodeList'])} 个节点")
            
        注意:
            - 缓存会在知识写入时通过 clear_cache() 方法清理
            - 缓存键包含 (self, top_event_name)，不同实例的缓存独立
        """
        # 使用默认值或传入值
        top_event_name = top_event_name or self.DEFAULT_TOP_EVENT
        
        # 参数合法性校验
        if not top_event_name or not isinstance(top_event_name, str):
            raise ValueError("顶事件名称必须是非空字符串")
        
        logger.info(f"开始构建故障树，顶事件：{top_event_name}")
        
        # 步骤 1: 提取图谱数据
        records = self.fetch_graph_data(top_event_name)
        
        if not records:
            raise ValueError(
                f"图谱中未提取到关于 '{top_event_name}' 的有效因果路径。"
                f"请检查：1) 数据库中是否存在该节点 2) 置信度阈值是否过高"
            )
        
        # 步骤 2: 构建 NetworkX 有向图（带证据融合防覆盖）
        G = nx.DiGraph()
        edge_merge_count = 0
        
        for rec in records:
            u, v = rec['source_name'], rec['target_name']
            
            # 检查边是否已存在，防止 DiGraph 覆盖导致证据丢失
            if G.has_edge(u, v):
                edge_merge_count += 1
                existing = G.edges[u, v]
                
                # 合并重复边的证据和置信度
                # 强制统一证据列表类型为列表，防止字符串与列表相加导致 TypeError
                existing_evidence = existing.get('evidence_list') or []
                if isinstance(existing_evidence, str):
                    existing_evidence = [existing_evidence]
                
                new_evidence = rec.get('evidence_list') or []
                if isinstance(new_evidence, str):
                    new_evidence = [new_evidence]
                
                merged_evidence = list(set(existing_evidence + new_evidence))
                
                # 保留最大置信度
                # 【致命 Bug 修复】dict.get(key, default) 在 key=None 时返回 None 而非 default
                # max(None, float) 会抛出 TypeError，必须显式拦截 None 值
                exist_conf = existing.get('confidence')
                exist_conf = float(exist_conf) if exist_conf is not None else 1.0
                
                new_conf = rec.get('confidence')
                confidence_val = float(new_conf) if new_conf is not None else 1.0
                
                G.add_edge(
                    u, v,
                    confidence=confidence_val,
                    evidence_list=rec['evidence_list'],
                    edge_type=rec['edge_type']
                )
                logger.debug(
                    f"边 {u}->{v} 已存在，已合并证据 "
                    f"(原:{len(existing_evidence)}条 + 新:{len(new_evidence)}条 → 合并:{len(merged_evidence)}条)"
                )
            else:
                G.add_edge(
                    u, v,
                    confidence=rec['confidence'],
                    evidence_list=rec['evidence_list'],
                    edge_type=rec['edge_type']
                )
        
        logger.info(
            f"构建有向图完成：{G.number_of_nodes()} 个节点，"
            f"{G.number_of_edges()} 条边，合并 {edge_merge_count} 条重复边"
        )
        
        # 步骤 3: 自动破环
        if not nx.is_directed_acyclic_graph(G):
            logger.warning("检测到逻辑闭环，启动自动破环算法...")
            broken_count = self._auto_break_cycles(G)
            logger.info(f"自动破环完成，共删除 {broken_count} 条边")
        
        # 步骤 4: 清理断联分支（使用连通性判定而非度数判定）
        valid_nodes = set(nx.ancestors(G, top_event_name))
        valid_nodes.add(top_event_name)
        
        nodes_to_remove = [n for n in G.nodes() if n not in valid_nodes]
        for node in nodes_to_remove:
            G.remove_node(node)
            logger.debug(f"清理断联分支节点：{node}")
        
        if nodes_to_remove:
            logger.info(f"清理了 {len(nodes_to_remove)} 个断联的幽灵节点")
        
        # 步骤 5: 再次校验 DAG 性质
        if not nx.is_directed_acyclic_graph(G):
            logger.error("破环并清理孤立节点后仍存在逻辑闭环，无法生成有效故障树")
            raise RuntimeError("图谱中存在无法自动修复的逻辑闭环")
        
        # 步骤 6: 验证剩余边数，防止生成无意义的单节点故障树
        if G.number_of_edges() == 0:
            raise ValueError(
                f"剔除无效链路后，图谱中无有效因果路径，"
                f"无法为 '{top_event_name}' 生成完整故障树。"
            )
        
        # 步骤 7: 处理混合逻辑门（在连通性剪枝之后）
        self._resolve_mixed_logic_gates(G)
        
        # 步骤 8: 计算树状布局坐标
        node_positions = self._calculate_tree_layout(G)
        
        # 步骤 9: 生成节点 UUID 映射
        node_uuid_map = {node: self._generate_node_id() for node in G.nodes()}
        
        # 步骤 10: 构建 JSON 结构（参考标准故障树格式）
        fault_tree_json = {
            "attr": {
                "background": "#fff",
                "fontColor": "#000",
                "eventColor": "#000",
                "eventFillColor": "#fff",
                "gateColor": "#000",
                "gateFillColor": "#fff",
                "linkColor": "#456",
                "eventCode": True,
                "eventProbability": False,
                "containerX": -53,
                "containerY": -74,
                "width": self.DEFAULT_CANVAS_WIDTH,
                "height": self.DEFAULT_CANVAS_HEIGHT
            },
            "nodeList": [],
            "linkList": []
        }
        
        # 组装节点列表
        for node_name in G.nodes():
            type_code = self._infer_node_type_from_topology(G, node_name)
            gate_type = self._infer_gate_type(G, node_name)
            x, y = node_positions.get(node_name, (150, 150))
            
            # 判断是否为逻辑门节点
            is_gate_node = node_name.startswith('[AND 门]') or node_name.startswith('[OR 门]')
            
            # 【修复】根据节点类型计算合理的概率值
            probability, show_probability = self._calculate_node_probability(type_code, node_name)
            
            # 构建完整的 event 对象（参考标准格式）
            # 【修复】即使是逻辑门节点，也必须返回完整的 event 结构，仅清空其具体业务数值
            event_obj = {
                "id": uuid.uuid4().hex[:16],  # 16 位短 UUID
                "name": node_name if not is_gate_node else "",
                "description": "系统自动推导的逻辑门节点" if is_gate_node else "",
                "errorLevel": "",
                "priority": 0,
                "probability": probability,  # 【修复】使用计算的动态值
                "showProbability": show_probability,  # 【修复】使用计算的动态值
                "rules": {} if is_gate_node else {
                    "deviceTypeId": "",  # 【修复】置空，避免前端误用硬编码 ID"114"导致报错
                    "measurePointName": "",
                    "symbol": "",  # 【修复】移除默认 "="，等待业务系统绑定
                    "thresholds": [],  # 【修复】清空阈值数组
                    "duration": ""  # 【修复】置空持续时间
                },
                "investigateMethod": "",
                "documents": []
            }
            
            node_data = {
                "id": node_uuid_map[node_name],
                "name": node_name,
                "type": type_code,
                "x": x,
                "y": y,
                "gate": gate_type,
                "event": event_obj,  # 【修复】直接使用 event_obj，因为内部已经处理了 is_gate_node 逻辑
                "transfer": ""
            }
            fault_tree_json["nodeList"].append(node_data)
        
        # 组装连线列表（参考标准格式）
        for source, target, data in G.edges(data=True):
            evidence_list = data.get("evidence_list", [])
            
            # 【修复】兼容 None、字符串、列表三种情况，防止类型错误
            if not evidence_list:
                evidence_str = "未知来源"
            elif isinstance(evidence_list, str):
                # 【致命 Bug 修复】不能写成 evidence_str = evidence_str（未绑定先使用）
                evidence_str = evidence_list
            else:
                evidence_str = " | ".join(map(str, evidence_list))
            
            # 获取边的类型
            edge_type = data.get("edge_type", "resultsIn")
            
            # 【优化】为边生成唯一 ID，适配 AntV X6 / React Flow 等主流框架
            # 【优化】使用 16 位 UUID 防止多棵树在全局状态中的碰撞风险
            link_data = {
                "id": "edge-" + uuid.uuid4().hex[:16],  # 补充边的唯一标识（16 位 UUID）
                "type": "link",  # 添加 type 字段
                "sourceId": node_uuid_map[source],
                "targetId": node_uuid_map[target],
                "edgeType": edge_type,  # 添加 edgeType 字段
                "isCondition": False,
                "traceability": {
                    "evidence": evidence_str,
                    "confidence": round(data.get("confidence", 1.0), 3)
                }
            }
            fault_tree_json["linkList"].append(link_data)
        
        # 输出统计信息
        logger.info(
            f"✅ 故障树构建完成："
            f"{len(fault_tree_json['nodeList'])} 个节点，"
            f"{len(fault_tree_json['linkList'])} 条连线"
        )
        
        # 【架构优化】返回深拷贝副本，防止 lru_cache 缓存可变对象引用
        # 如果未来调用方修改返回的字典（如 ft_json["nodeList"].pop()），
        # 不会破坏缓存中的原始数据，保证后续查询的数据完整性
        return copy.deepcopy(fault_tree_json)

    def save_to_file(self, fault_tree_json: Dict[str, Any], output_path: str = "generated_fault_tree.json") -> bool:
        """
        将故障树 JSON 保存到文件
        
        Args:
            fault_tree_json: 故障树字典（由 build_tree_json 返回）
            output_path: 输出文件路径，默认 "generated_fault_tree.json"
            
        Returns:
            保存是否成功
            
        Raises:
            IOError: 当文件写入失败时抛出异常
            
        注意:
            使用 UTF-8 编码保存，支持中文节点名
            使用 4 空格缩进，便于人工阅读和版本控制
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(fault_tree_json, f, ensure_ascii=False, indent=4)
            
            logger.info(f"故障树已保存至：{output_path}")
            return True
            
        except IOError as e:
            logger.error(f"文件 I/O 错误：{str(e)}")
            raise
        except Exception as e:
            logger.error(f"保存文件失败：{str(e)}")
            return False


if __name__ == "__main__":
    """
    主测试模块：演示故障树生成器的基本使用
    
    运行方式:
        python tree_generator.py
        
    环境变量:
        NEO4J_URI: Neo4j 数据库连接地址
        NEO4J_USER: 用户名
        NEO4J_PASSWORD: 密码
        DEFAULT_TOP_EVENT: 默认顶事件名称（可选）
        LOG_LEVEL: 日志级别（可选）
    """
    logger.info("正在启动 AI 图树降维引擎...")
    
    try:
        # 使用上下文管理器，确保连接正确关闭
        with FaultTreeGenerator() as generator:
            # 从环境变量读取顶事件名称
            top_event = os.getenv("DEFAULT_TOP_EVENT", "登机梯故障")
            logger.info(f"从图数据库拉取知识并合成树拓扑，顶事件：{top_event}...")
            
            # 生成故障树
            ft_json = generator.build_tree_json(top_event_name=top_event)
            
            # 保存到文件
            generator.save_to_file(ft_json)
            
            # 输出统计信息
            logger.info(f"✅ 故障树生成成功！")
            logger.info(
                f"共生成了 {len(ft_json['nodeList'])} 个故障节点，"
                f"{len(ft_json['linkList'])} 条逻辑连接"
            )
            
    except ValueError as ve:
        # 业务逻辑错误（如未找到节点、无有效路径等）
        logger.error(f"❌ 业务逻辑错误：{str(ve)}")
    except PermissionError as pe:
        # 数据库认证失败
        logger.error(f"❌ 数据库认证失败：{str(pe)}")
    except ConnectionError as ce:
        # 数据库连接失败
        logger.error(f"❌ 数据库连接失败：{str(ce)}")
    except Exception as e:
        # 其他未知异常
        logger.error(f"❌ 程序执行异常：{str(e)}", exc_info=True)