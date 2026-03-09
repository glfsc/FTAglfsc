import os
import logging
import math
import re
from collections import defaultdict
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, CypherSyntaxError, DatabaseError
from typing import List, Any, Dict, Tuple
# 顶部导入
from app.core.config import settings
from neo4j import GraphDatabase

# 加载 .env 文件
load_dotenv()

# 从环境变量读取日志级别，默认为 INFO
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# 验证日志级别是否有效
valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if log_level not in valid_levels:
    print(f"警告：无效的日志级别 '{log_level}'，使用默认级别 'INFO'")
    log_level = "INFO"

# 配置日志
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class FaultTreeKGBuilder:
    # 定义允许的实体类型白名单
    ALLOWED_ENTITY_TYPES = {"BasicEvent", "IntermediateEvent", "TopEvent"}
    # 定义允许的关系类型白名单
    ALLOWED_RELATIONS = {"resultsIn", "causedBy", "relatedTo", "jointly_resultsIn"}

    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        # 校验环境变量
        if not all([uri, user, password]):
            missing = []
            if not uri:
                missing.append("NEO4J_URI")
            if not user:
                missing.append("NEO4J_USER")
            if not password:
                missing.append("NEO4J_PASSWORD")
            logger.error(f"缺少必要的环境变量：{', '.join(missing)}")
            raise OSError(f"缺少必要的环境变量：{', '.join(missing)}")

        try:
            # 【优化三：高并发连接池调优】
            # 显式配置工业级连接池参数，应对高并发、大规模图谱场景
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
                connection_acquisition_timeout=settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT,
                max_transaction_retry_time=settings.NEO4J_MAX_TRANSACTION_RETRY_TIME,
                connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT
            )
            self.driver.verify_connectivity()
            logger.info("Neo4j 数据库连接成功（连接池大小：200）")

            # 【修复 3】在 try 块内初始化约束，并用嵌套异常处理防止资源泄露
            try:
                self.init_constraints()
            except Exception as e:
                logger.error(f"约束初始化失败，正在安全关闭数据库连接...")
                self.driver.close()
                raise RuntimeError(f"图数据库约束初始化失败，已安全关闭连接：{e}") from e
                
        except ServiceUnavailable as e:
            logger.error(f"无法连接到 Neo4j 数据库：{uri}")
            raise ConnectionError(f"数据库连接失败：{str(e)}") from e
        except AuthError as e:
            logger.error("Neo4j 认证失败，请检查用户名和密码")
            raise PermissionError(f"数据库认证失败：{str(e)}") from e
        except Exception as e:
            logger.error(f"初始化数据库驱动时发生未知错误：{str(e)}")
            raise

    def __enter__(self):
        """进入上下文时返回实例本身"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close()
        return False

    def close(self):
        """安全关闭数据库连接"""
        try:
            if self.driver:
                self.driver.close()
                logger.info("Neo4j 数据库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭数据库连接时发生异常：{str(e)}")

    def init_constraints(self):
        """
        【优化 3:平滑降级】自动创建约束，若因权限不足失败则仅告警，不阻断服务启动
        【修复】新增 FaultNode 基础标签的唯一性约束，防止同名节点因类型标签不同而分裂
        """
        node_types = list(self.ALLOWED_ENTITY_TYPES)
        with self.driver.session() as session:
            # 为 FaultNode 基础标签创建 name 唯一性约束（保证全局物理唯一性）
            fault_node_constraint = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:FaultNode) REQUIRE n.name IS UNIQUE"
            try:
                session.run(fault_node_constraint)
                logger.info("✅ 已为 FaultNode 创建 name 唯一性约束")
            except Exception as e:
                logger.warning(f"⚠️ 无法自动创建 FaultNode 约束 (可能因权限不足)，请确保数据库已有索引：{e}")
            
            # 为具体事件类型创建约束（辅助查询优化）
            for nt in node_types:
                query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{nt}) REQUIRE n.name IS UNIQUE"
                try:
                    session.run(query)
                except Exception as e:
                    logger.warning(f"⚠️ 无法自动创建节点约束 {nt} (可能因权限不足)，请确保数据库已有索引：{e}")
        logger.info(f"已为 FaultNode 和 {len(node_types)} 种节点类型尝试创建唯一性约束")

    def _validate_identifier(self, value, allowed_set, type_name):
        """校验标识符是否在白名单内且符合安全字符规范"""
        if value not in allowed_set:
            raise ValueError(f"非法的 {type_name}：{value}，不在允许范围内")
        # 【优化】移除冗余的正则校验：allowed_set 是硬编码白名单，通过集合检查后必然符合安全字符规范

    def insert_triplet(
        self,
        subject_name: str,
        subject_type: str,
        relation: str,
        object_name: str,
        object_type: str,
        confidence: float,
        source: str
    ) -> Any:
        """
        单条三元组插入（兼容旧接口）
        """
        return self.insert_triplets_batch([{
            "subject_name": subject_name,
            "subject_type": subject_type,
            "relation": relation,
            "object_name": object_name,
            "object_type": object_type,
            "confidence": confidence,
            "source": source
        }])

    def insert_triplets_batch(self, triplets: List[Any]) -> int:
        """
        【终极完美版】高性能批量写入：
        - 修复原子性失效 Bug：所有数据在单个事务中提交
        - 修复 AttributeError 崩溃：使用 isinstance 安全判定类型
        - 修复大小写容错逻辑 Bug：真正实现格式纠偏
        - 增加智能纠偏映射字典：自动纠正大模型格式幻觉
        - 【新增】NaN 防御：利用比较特性拦截越界、NaN 幻觉
        - 【新增】内存级去重：指纹追踪器防止 LLM 复读机式输出
        - 增加置信度纵深防御：强制截断越界值
        - 严防超级节点污染：缺失名称的三元组直接丢弃
        - 单条异常隔离：保障整批数据不会因 1 条不合规而全盘崩溃
        - 强制 str() 转换：杜绝大模型输出数字/布尔值导致的崩溃
        - 来源标准化去重：防止同一来源因大小写不同被重复计算
        - 【修复】伪空值污染：引入正则表达式和黑名单拦截
        - 【修复】格式纠偏漏网之鱼：通过正则清洗实现极致扁平化匹配
        """
        if not triplets:
            logger.warning("批量插入列表为空")
            return 0

        # 【优化 2】定义智能纠偏映射字典（防大模型大小写或格式幻觉）
        # 【修复】字典键极致扁平化（无空格、无下划线），配合正则清洗
        type_mapping = {
            "basicevent": "BasicEvent",
            "intermediateevent": "IntermediateEvent",
            "topevent": "TopEvent"
        }
        rel_mapping = {
            "resultsin": "resultsIn",
            "jointlyresultsin": "jointly_resultsIn",
            "causedby": "causedBy",
            "relatedto": "relatedTo"
        }

        # 【修复 1】伪空值黑名单拦截（防大模型幻觉输出 "None"、"未知" 等）
        INVALID_NAMES = {"none", "null", "未知", "n/a", "na", "undefined"}

        # 1. 对大模型传来的三元组进行分组
        grouped_data: Dict[Tuple[str, str, str], List[Dict]] = defaultdict(list)
        skip_count = 0  # 记录跳过的脏数据数量
        duplicate_count = 0  # 【新增】记录内存去重的正常重复三元组数量
        
        # 【优化 2：内存级去重指纹库】
        unique_fingerprints = set()
        
        for t in triplets:
            try:
                # 【修复 2】安全的类型兼容判定，彻底杜绝 AttributeError
                if isinstance(t, dict):
                    # 字典类型
                    subject_name = t.get('subject_name')
                    subject_type = t.get('subject_type')
                    relation = t.get('relation')
                    object_name = t.get('object_name')
                    object_type = t.get('object_type')
                    confidence = t.get('confidence')
                    source = t.get('source')
                else:
                    # Pydantic 对象或其他对象类型
                    subject_name = getattr(t, 'subject_name', None)
                    subject_type = getattr(t, 'subject_type', None)
                    relation = getattr(t, 'relation', None)
                    object_name = getattr(t, 'object_name', None)
                    object_type = getattr(t, 'object_type', None)
                    confidence = getattr(t, 'confidence', None)
                    source = getattr(t, 'source', None)

                # 【修复 1】实体为空时直接丢弃，严防图谱被超大"脏节点"污染
                # 绝对不能使用统一默认值（如"未知实体"），否则会导致超级节点污染
                sub_name_clean = str(subject_name).strip() if subject_name is not None else ""
                obj_name_clean = str(object_name).strip() if object_name is not None else ""
                
                # 【修复 1】联合拦截真正的空值和伪空值（"None"、"未知" 等）
                if (not sub_name_clean or sub_name_clean.lower() in INVALID_NAMES or 
                    not obj_name_clean or obj_name_clean.lower() in INVALID_NAMES):
                    logger.warning(f"跳过残次三元组：包含伪空值实体 -> {t}")
                    skip_count += 1
                    continue  # 直接丢弃这条脏数据

                # 2. 【修复】强制转换为字符串，杜绝大模型输出数字/布尔值导致的 AttributeError
                # 如果大模型把类型输出成了数字（如 1），整数没有.strip()方法会崩溃
                sub_type_str = str(subject_type) if subject_type is not None else ""
                # 【修复 2】使用正则剔除所有空白符和下划线，实现极致扁平化
                sub_type_clean = re.sub(r'[\s_]+', '', sub_type_str).lower()
                # 【修复 Bug 2】确保纯空格字符串也能正确触发兜底默认值
                sub_type = type_mapping.get(
                    sub_type_clean, 
                    sub_type_str.strip() if sub_type_str.strip() else "BasicEvent"
                )
                
                obj_type_str = str(object_type) if object_type is not None else ""
                # 【修复 2】使用正则剔除所有空白符和下划线，实现极致扁平化
                obj_type_clean = re.sub(r'[\s_]+', '', obj_type_str).lower()
                # 【修复 Bug 2】确保纯空格字符串也能正确触发兜底默认值
                obj_type = type_mapping.get(
                    obj_type_clean, 
                    obj_type_str.strip() if obj_type_str.strip() else "IntermediateEvent"
                )
                
                # 【修复 2】rel_type 空值兜底与转换，使用正则扁平化
                rel_type_str = str(relation) if relation is not None else ""
                rel_type_clean = re.sub(r'[\s_]+', '', rel_type_str).lower()
                # 【修复 Bug 2】确保纯空格字符串也能正确触发兜底默认值
                rel_type = rel_mapping.get(
                    rel_type_clean, 
                    rel_type_str.strip() if rel_type_str.strip() else "resultsIn"
                )

                # 3. 校验实体类型是否合法
                self._validate_identifier(sub_type, self.ALLOWED_ENTITY_TYPES, "实体类型")
                self._validate_identifier(obj_type, self.ALLOWED_ENTITY_TYPES, "实体类型")

                # 4. 校验关系类型是否合法
                self._validate_identifier(rel_type, self.ALLOWED_RELATIONS, "关系类型")

                # 5. 【核心修复】安全解析置信度，严防幻觉或 None 导致的数据丢失和 Null 传染
                try:
                    if confidence is None:
                        confidence_val = 1.0  # 默认满置信度
                    else:
                        confidence_val = float(confidence)
                        
                    if not (0.0 <= confidence_val <= 1.0):
                        logger.warning(f"置信度 {confidence_val} 越界，已截断并修正为 1.0")
                        confidence_val = 1.0
                except (ValueError, TypeError):
                    logger.warning(f"大模型幻觉：置信度字段非法 '{confidence}'，保留知识实体，使用默认值 1.0")
                    confidence_val = 1.0

                # 6. 标准化来源字段（为空时给予清晰的兜底说明）
                source_clean = str(source).strip() if source is not None else ""
                if not source_clean or source_clean.lower() in INVALID_NAMES:
                    source_clean = "未知来源"

                # 7. 生成三元组指纹（使用清洗后的 safe 值）
                fingerprint = (sub_name_clean, sub_type, rel_type, obj_name_clean, obj_type, confidence_val, source_clean)
                if fingerprint in unique_fingerprints:
                    duplicate_count += 1
                    continue  # 跳过重复的三元组
                unique_fingerprints.add(fingerprint)

                # 8. 按 Schema 拓扑结构分组，以便使用 UNWIND 高效解包
                group_key = (sub_type, rel_type, obj_type)
                grouped_data[group_key].append({
                    "sub_name": sub_name_clean,
                    "obj_name": obj_name_clean,
                    "confidence": confidence_val,  # 使用绝对安全的 float
                    "source": source_clean
                })

            except ValueError as ve:
                # 【核心修复 Bug 2】不再抛出异常打断整批数据，而是记录日志并跳过
                logger.warning(f"检测到格式错误，丢弃该条数据：{ve}")
                skip_count += 1
                continue  # 跳过当前脏数据，继续处理下一条
            except Exception as e:
                logger.error(f"处理三元组时发生未知异常：{str(e)}，跳过该条数据 -> {t}")
                skip_count += 1

        # 9. 【核心修复】使用 UNWIND 批量插入，并采用受管事务保证原子性
        inserted_count = 0
        try:
            with self.driver.session() as session:
                def execute_chunks(tx):
                    """使用受管事务执行所有 chunk，确保原子性"""
                    inserted = 0
                    for (sub_type, rel_type, obj_type), batch_rows in grouped_data.items():
                        # 动态拼接安全的类型白名单变量，规避 Cypher 参数化限制
                        query = f"""
                        UNWIND $batch AS row
                        
                        // 保证物理唯一性
                        MERGE (s:FaultNode {{name: row.sub_name}})
                        SET s:{sub_type}
                        
                        MERGE (o:FaultNode {{name: row.obj_name}})
                        SET o:{obj_type}
                        
                        // 建立关联
                        MERGE (s)-[r:{rel_type}]->(o)
                        
                        ON CREATE SET 
                            r.confidence = row.confidence, 
                            r.sources = [row.source]
                            
                        ON MATCH SET 
                            // 【核心算法修复】数学与工程的完美融合：
                            // 1. 同源更新：如果来源相同，视为纠正数据，取最大值
                            // 2. 异源印证：如果来源不同，触发 D-S 证据融合公式，提升整体置信度
                            r.confidence = CASE 
                                WHEN row.source IN COALESCE(r.sources, []) 
                                THEN CASE 
                                    WHEN row.confidence > COALESCE(r.confidence, 0.0) THEN row.confidence 
                                    ELSE r.confidence 
                                END
                                ELSE round(COALESCE(r.confidence, 0.0) + row.confidence - (COALESCE(r.confidence, 0.0) * row.confidence), 3)
                            END,
                            // 来源去重追加
                            r.sources = CASE 
                                WHEN row.source IN COALESCE(r.sources, []) 
                                THEN r.sources 
                                ELSE COALESCE(r.sources, []) + [row.source] 
                            END
                        """
                        
                        # 为了防止极大数据量导致内存爆炸，建议将大 batch 切片（每 2000 条一次事务）
                        CHUNK_SIZE = 2000
                        for i in range(0, len(batch_rows), CHUNK_SIZE):
                            chunk = batch_rows[i:i + CHUNK_SIZE]
                            tx.run(query, batch=chunk)
                            inserted += len(chunk)
                    return inserted
                
                # 使用 execute_write 将所有 chunk 包裹在同一个事务上下文中，确保原子性
                inserted_count = session.execute_write(execute_chunks)
                        
        except Exception as e:
            logger.error(f"数据库批量写入事务失败：{str(e)}")
            raise RuntimeError(f"图数据库写入失败：{str(e)}") from e

        # 10. 结构化日志输出
        log_msg = f"批量插入处理完成：有效入库 {inserted_count} 条"
        if skip_count > 0:
            log_msg += f"，拦截脏数据 {skip_count} 条"
        if duplicate_count > 0:
            log_msg += f"，内存去重 {duplicate_count} 条"

        if skip_count > 0:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        return inserted_count, skip_count, duplicate_count
