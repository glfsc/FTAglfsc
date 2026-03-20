# app/services/fault_tree_service.py

"""
故障树协调服务
整合知识图谱构建与故障树生成，支持注入 kg_builder / tree_generator（由 main 的 lifespan 注入）。
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional
from app.services.kg_builder import FaultTreeKGBuilder
from app.services.tree_generator import FaultTreeGenerator
from app.services.knowledge_extraction_service import KnowledgeExtractionService
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
        extraction_service: Optional[KnowledgeExtractionService] = None,
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
        
        # 知识抽取服务（新增）
        if extraction_service is not None:
            self.extraction_service = extraction_service
            self._owns_extraction = False
        else:
            self.extraction_service = KnowledgeExtractionService()
            self._owns_extraction = True

    def extract_knowledge(self, request: KnowledgeExtractRequest) -> Dict[str, Any]:
        """
        从文档提取知识并构建知识图谱
        整合 triplet_extractor 模块
        """
        logger.info(f"开始知识提取，文件 ID: {request.file_id}, 顶事件：{request.top_event}")
        
        try:
            # 判断 file_id 是文件路径还是已上传的文件 ID
            if os.path.exists(request.file_id):
                # 直接是文件路径
                file_path = request.file_id
            else:
                # 假设是 uploads 目录下的文件
                file_path = os.path.join("uploads", request.file_id)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"文件不存在：{request.file_id}")
            
            # 使用知识抽取服务提取三元组，必须传入顶事件用于命名
            result = self.extraction_service.extract_and_save(
                file_path=file_path,
                output_dir="data/triplets",
                top_event=request.top_event  # 使用顶事件命名
            )
            
            if not result["success"]:
                raise RuntimeError(f"知识提取失败：{result.get('error', '未知错误')}")
            
            triplets = result["triplets"]
            output_path = result.get("output_path")
            
            # 插入到知识图谱
            inserted_count, skipped, duplicates = self.kg_builder.insert_triplets_batch(triplets)
            
            # 转换为事件和逻辑门格式（兼容旧版前端）
            events = self._triplets_to_events(triplets)
            gates = self._triplets_to_gates(triplets)
            
            # 清理缓存（确保生成时获取最新数据）
            self.tree_generator.clear_cache(None)  # 清理所有缓存
            
            return {
                "task_id": f"extract_{request.file_id[:8]}",
                "triplets": triplets,
                "events": events,
                "gates": gates,
                "inserted": inserted_count,
                "skipped": skipped,
                "duplicates": duplicates,
                "status": "completed",
                "progress": 1.0,
                "output_file": output_path,
                "traceability": [{"file": request.file_id, "timestamp": str(os.path.getmtime(file_path))}],
                "accuracy_metrics": {
                    "avg_confidence": sum(t["confidence"] for t in triplets) / len(triplets) if triplets else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"知识提取失败：{str(e)}")
            raise
    
    def _triplets_to_events(self, triplets: List[Dict]) -> List[Dict]:
        """
        将三元组转换为事件格式（兼容旧版前端）
        """
        events_map = {}
        
        for t in triplets:
            # 添加主语事件
            if t["subject_name"] not in events_map:
                events_map[t["subject_name"]] = {
                    "event_id": f"evt_{t['subject_name']}",
                    "event_name": t["subject_name"],
                    "event_type": self._map_event_type(t["subject_type"]),
                    "description": t.get("source", ""),
                    "probability": t["confidence"],
                    "metadata": {"source": t.get("source", "")}
                }
            
            # 添加宾语事件
            if t["object_name"] not in events_map:
                events_map[t["object_name"]] = {
                    "event_id": f"evt_{t['object_name']}",
                    "event_name": t["object_name"],
                    "event_type": self._map_event_type(t["object_type"]),
                    "description": t.get("source", ""),
                    "probability": t["confidence"],
                    "metadata": {"source": t.get("source", "")}
                }
        
        return list(events_map.values())
    
    def _triplets_to_gates(self, triplets: List[Dict]) -> List[Dict]:
        """
        将三元组转换为逻辑门格式（兼容旧版前端）
        """
        gates = []
        
        # 按目标节点分组
        target_sources = {}
        for t in triplets:
            obj = t["object_name"]
            if obj not in target_sources:
                target_sources[obj] = []
            target_sources[obj].append(t)
        
        # 为每个目标节点创建逻辑门
        gate_id = 0
        for target, sources in target_sources.items():
            # 检查是否存在 jointly_resultsIn 关系
            has_jointly = any(t["relation"] == "jointly_resultsIn" for t in sources)
            
            gates.append({
                "gate_id": f"gate_{gate_id}",
                "gate_type": "AND" if has_jointly else "OR",
                "input_events": [f"evt_{t['subject_name']}" for t in sources],
                "output_event": f"evt_{target}"
            })
            gate_id += 1
        
        return gates
    
    def _map_event_type(self, event_type: str) -> str:
        """
        映射事件类型到前端格式
        """
        type_mapping = {
            "TopEvent": "top",
            "IntermediateEvent": "middle",
            "BasicEvent": "bottom"
        }
        return type_mapping.get(event_type, "bottom")

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
        if self._owns_extraction:
            # 知识抽取服务不需要特殊关闭操作
            pass
