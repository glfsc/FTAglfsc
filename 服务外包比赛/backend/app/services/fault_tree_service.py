# app/services/fault_tree_service.py

"""
故障树协调服务
整合知识图谱构建与故障树生成，支持注入 kg_builder / tree_generator（由 main 的 lifespan 注入）。
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.kg_builder import FaultTreeKGBuilder
from app.services.tree_generator import FaultTreeGenerator
from app.models.schemas import (
    KnowledgeExtractRequest,
    FaultTreeGenerateRequest,
)

logger = logging.getLogger(__name__)


class FaultTreeService:
    """故障树服务协调器。可注入 kg_builder/tree_generator，未注入时自行创建（便于单测或独立使用）。"""

    def __init__(
        self,
        kg_builder: Optional[FaultTreeKGBuilder] = None,
        tree_generator: Optional[FaultTreeGenerator] = None,
    ):
        if kg_builder is not None:
            self.kg_builder = kg_builder
            self._owns_kg = False
        else:
            self.kg_builder = FaultTreeKGBuilder()
            self._owns_kg = True
        if tree_generator is not None:
            self.tree_generator = tree_generator
            self._owns_tree = False
        else:
            self.tree_generator = FaultTreeGenerator()
            self._owns_tree = True

    def extract_knowledge(self, request: KnowledgeExtractRequest) -> Dict[str, Any]:
        """
        从文档提取知识并构建知识图谱
        复用你提供的kg_builder代码
        """
        logger.info(f"开始知识提取，顶事件: {request.top_event}")

        try:
            # 模拟知识提取（实际应调用NLP服务）
            triplets = [
                {
                    "subject_name": "电源模块故障",
                    "subject_type": "BasicEvent",
                    "relation": "resultsIn",
                    "object_name": "系统宕机",
                    "object_type": "TopEvent",
                    "confidence": 0.95,
                    "source": "设备手册"
                },
                {
                    "subject_name": "线缆老化",
                    "subject_type": "BasicEvent",
                    "relation": "resultsIn",
                    "object_name": "电源模块故障",
                    "object_type": "IntermediateEvent",
                    "confidence": 0.85,
                    "source": "维修记录"
                }
            ]

            # 插入到知识图谱
            inserted_count, skipped, duplicates = self.kg_builder.insert_triplets_batch(triplets)

            return {
                "task_id": f"task_{request.file_id[:8]}",
                "inserted": inserted_count,
                "skipped": skipped,
                "duplicates": duplicates,
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"知识提取失败: {str(e)}")
            raise

    def generate_fault_tree(self, request: FaultTreeGenerateRequest) -> Dict[str, Any]:
        """
        生成故障树
        复用你提供的tree_generator代码
        """
        logger.info(f"生成故障树，顶事件: {request.top_event}")

        try:
            # 使用tree_generator生成JSON
            tree_json = self.tree_generator.build_tree_json(
                top_event_name=request.top_event
            )

            # 清理缓存（确保下次获取最新数据）
            self.tree_generator.clear_cache(request.top_event)

            return {
                "tree_id": f"tree_{request.top_event.replace(' ', '_')}",
                "tree_data": tree_json,
                "metadata": {
                    "top_event": request.top_event,
                    "node_count": len(tree_json["nodeList"]),
                    "link_count": len(tree_json["linkList"])
                }
            }

        except Exception as e:
            logger.error(f"故障树生成失败: {str(e)}")
            raise

    def close(self):
        """关闭连接；仅关闭由本服务创建的实例，注入的实例由 lifespan 负责关闭。"""
        if self._owns_kg:
            self.kg_builder.close()
        if self._owns_tree:
            self.tree_generator.close()