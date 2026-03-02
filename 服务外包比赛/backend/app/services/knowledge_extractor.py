"""
知识提取服务 - 基于大模型的工业知识智能提取
核心功能：
1. 从设备手册、维修工单等文本中提取故障事件
2. 识别事件类型（顶事件、中间事件、底事件）
3. 提取事件关联关系和逻辑门规则
4. 生成结构化知识用于故障树构建
"""
from app.models.schemas import FaultEvent, LogicGate
from typing import Dict, List
import re

class KnowledgeExtractor:
    """
    知识提取器（基于大模型）
    支持开源模型：Llama 3、GLM-4、ChatGLM3等
    """
    
    def __init__(self):
        # TODO: 加载大模型
        # 示例：from transformers import AutoModelForCausalLM, AutoTokenizer
        # self.model = AutoModelForCausalLM.from_pretrained("THUDM/chatglm3-6b")
        # self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm3-6b")
        self.model = None
        self.tokenizer = None
    
    def extract_from_text(self, text: str, top_event: str = None) -> Dict:
        """
        从文本中提取故障知识
        
        Args:
            text: 工业文本内容（设备手册、维修记录等）
            top_event: 用户指定的顶事件（可选）
        
        Returns:
            包含故障事件和逻辑门的字典
        """
        if self.model:
            return self._extract_with_llm(text, top_event)
        else:
            # 使用规则方法模拟（实际应使用大模型）
            return self._extract_with_rules(text, top_event)
    
    def _extract_with_llm(self, text: str, top_event: str) -> Dict:
        """
        使用大模型提取知识
        Prompt工程：指导模型识别故障事件和逻辑关系
        """
        prompt = f"""
你是一个工业设备故障分析专家。请从以下文本中提取故障树相关信息：

文本内容：
{text}

顶事件（用户指定）：{top_event or "请自动识别"}

请按以下格式提取：
1. 故障事件列表（包括顶事件、中间事件、底事件）
2. 事件之间的逻辑关系（AND门、OR门）
3. 每个事件的描述和发生概率（如果有）

输出格式：JSON
"""
        
        # TODO: 调用大模型生成
        # response = self.model.generate(prompt)
        # parsed_result = self._parse_llm_output(response)
        
        return self._extract_with_rules(text, top_event)
    
    def _extract_with_rules(self, text: str, top_event: str) -> Dict:
        """
        基于规则的知识提取（用于演示和备用）
        实际生产环境应使用大模型
        """
        # 关键词匹配识别故障事件
        fault_keywords = ['故障', '失效', '损坏', '异常', '错误', '失灵']
        cause_keywords = ['由于', '因为', '导致', '引起', '造成']
        
        events = []
        gates = []
        
        # 提取顶事件
        if top_event:
            events.append(FaultEvent(
                event_id="E1",
                event_name=top_event,
                event_type="top",
                description=f"系统级故障：{top_event}",
                probability=0.01
            ))
        
        # 简单规则提取中间事件和底事件
        sentences = text.split('。')
        event_id_counter = 2
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in fault_keywords):
                # 提取事件名称
                event_name = self._extract_event_name(sentence)
                if event_name:
                    event_type = "bottom" if any(kw in sentence for kw in cause_keywords) else "middle"
                    events.append(FaultEvent(
                        event_id=f"E{event_id_counter}",
                        event_name=event_name,
                        event_type=event_type,
                        description=sentence.strip(),
                        probability=0.05 if event_type == "middle" else 0.1
                    ))
                    event_id_counter += 1
        
        # 生成逻辑门关系
        if len(events) >= 3:
            gates.append(LogicGate(
                gate_id="G1",
                gate_type="OR",
                input_events=[e.event_id for e in events[1:3]],
                output_event=events[0].event_id
            ))
        
        return {
            "events": events,
            "gates": gates,
            "extraction_method": "rule_based",
            "accuracy_estimate": 0.75
        }
    
    def _extract_event_name(self, sentence: str) -> str:
        """从句子中提取事件名称"""
        # 简单规则：提取包含故障关键词的短语
        fault_keywords = ['故障', '失效', '损坏', '异常', '错误']
        for keyword in fault_keywords:
            if keyword in sentence:
                # 提取关键词前后的词语
                idx = sentence.find(keyword)
                start = max(0, idx - 10)
                end = min(len(sentence), idx + 10)
                return sentence[start:end].strip()
        return "未知故障"
    
    def extract_with_traceability(self, text: str, top_event: str) -> Dict:
        """
        带溯源的知识提取
        记录每个提取结果的来源位置，便于专家验证
        
        Returns:
            包含events、gates和traceability信息
        """
        result = self.extract_from_text(text, top_event)
        
        # 添加溯源信息
        traceability = []
        for event in result["events"]:
            traceability.append({
                "event_id": event.event_id,
                "source_text": event.description,
                "confidence": 0.85,  # 提取置信度
                "extraction_method": "LLM" if self.model else "Rule-based"
            })
        
        result["traceability"] = traceability
        return result
    
    def batch_extract(self, file_paths: List[str], top_event: str) -> Dict:
        """
        批量提取多个文件的知识
        支持多数据集同时上传作为单故障树生成依据
        """
        all_events = []
        all_gates = []
        all_traceability = []
        
        for file_path in file_paths:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 提取知识
            result = self.extract_with_traceability(text, top_event)
            all_events.extend(result["events"])
            all_gates.extend(result["gates"])
            all_traceability.extend(result.get("traceability", []))
        
        # 去重和合并
        unique_events = self._deduplicate_events(all_events)
        merged_gates = self._merge_gates(all_gates)
        
        return {
            "events": unique_events,
            "gates": merged_gates,
            "traceability": all_traceability,
            "source_count": len(file_paths)
        }
    
    def _deduplicate_events(self, events: List[FaultEvent]) -> List[FaultEvent]:
        """去重事件"""
        seen = set()
        unique = []
        for event in events:
            if event.event_name not in seen:
                seen.add(event.event_name)
                unique.append(event)
        return unique
    
    def _merge_gates(self, gates: List[LogicGate]) -> List[LogicGate]:
        """合并逻辑门"""
        # 简单去重
        seen = set()
        unique = []
        for gate in gates:
            key = f"{gate.gate_type}_{gate.output_event}"
            if key not in seen:
                seen.add(key)
                unique.append(gate)
        return unique
