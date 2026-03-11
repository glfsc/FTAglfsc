"""
知识抽取模块集成测试脚本

用于测试从文件上传到知识提取的完整流程

使用方法:
    python test_knowledge_extraction.py

前提条件:
    1. 已配置 .env 文件（包含 DASHSCOPE_API_KEY 和 Neo4j 连接信息）
    2. 已安装所有依赖包
    3. Neo4j 数据库正在运行
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.knowledge_extraction_service import KnowledgeExtractionService
from app.services.fault_tree_service import FaultTreeService
from app.models.schemas import KnowledgeExtractRequest


def test_basic_extraction():
    """Test basic file extraction functionality"""
    print("=" * 60)
    print("Test 1: Basic File Extraction")
    print("=" * 60)
    
    # 创建测试文件
    test_content = """
    设备故障分析文档
    
    若电源模块 A 失效，则会导致系统宕机。
    若控制板 B 失效，也会导致系统宕机。
    电源模块 A 和控制板 B 同时失效时，系统必然宕机。
    
    线缆老化会导致电源模块故障。
    温度过高会导致控制板 B 失效。
    """
    
    test_file = "test_document.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        # 测试知识抽取服务
        service = KnowledgeExtractionService(mode="multimodal")
        result = service.extract_and_save(file_path=test_file, output_dir="data/output")
        
        if result["success"]:
            print(f"[OK] Extraction successful!")
            print(f"   - Triplets count: {len(result['triplets'])}")
            print(f"   - Output file: {result.get('output_path', 'N/A')}")
            
            # Display first 3 triplets
            print("\n   Sample triplets:")
            for i, triplet in enumerate(result['triplets'][:3], 1):
                print(f"   {i}. {triplet['subject_name']} --[{triplet['relation']}]--> {triplet['object_name']}")
                print(f"      Type: {triplet['subject_type']} -> {triplet['object_type']}")
                print(f"      Confidence: {triplet['confidence']}")
                print()
        else:
            print(f"[FAIL] Extraction failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"[CLEAN] Test file removed")


def test_fault_tree_service():
    """Test complete fault tree service (requires Neo4j)"""
    print("\n" + "=" * 60)
    print("Test 2: Complete Fault Tree Service (Requires Neo4j)")
    print("=" * 60)
    
    # 创建测试文件
    test_content = """
    液压系统故障分析
    
    若[液压泵损坏]或[油管破裂]，均会导致[系统压力不足]。
    若[系统压力不足]且[控制阀卡滞]同时发生，会导致[执行机构失效]。
    
    电机故障会导致液压泵损坏。
    油液污染会导致控制阀卡滞。
    外力撞击会导致油管破裂。
    """
    
    test_file = "test_hydraulic.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        # 创建故障树服务
        service = FaultTreeService()
        
        # 创建提取请求
        request = KnowledgeExtractRequest(
            file_id=test_file,
            mode="multimodal"
        )
        
        # 执行提取
        result = service.extract_knowledge(request)
        
        print(f"[OK] Extraction task completed!")
        print(f"   - Task ID: {result['task_id']}")
        print(f"   - Triplets count: {len(result['triplets'])}")
        print(f"   - Events count: {len(result['events'])}")
        print(f"   - Gates count: {len(result['gates'])}")
        print(f"   - Inserted count: {result['inserted']}")
        print(f"   - Skipped count: {result['skipped']}")
        print(f"   - Duplicates count: {result['duplicates']}")
        print(f"   - Avg confidence: {result['accuracy_metrics']['avg_confidence']:.2f}")
        print(f"   - Output file: {result.get('output_file', 'N/A')}")
        
        # Display event samples
        if result['events']:
            print("\n   Event samples:")
            for event in result['events'][:3]:
                print(f"   - {event['event_name']} ({event['event_type']})")
        
        # Display gate samples
        if result['gates']:
            print("\n   Gate samples:")
            for gate in result['gates'][:2]:
                inputs = " AND ".join(gate['input_events']) if gate['gate_type'] == 'AND' else " OR ".join(gate['input_events'])
                print(f"   - {inputs} --> {gate['output_event']} ({gate['gate_type']})")
        
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n[CLEAN] Test file removed")


def test_api_format():
    """Test API response format"""
    print("\n" + "=" * 60)
    print("Test 3: API Response Format")
    print("=" * 60)
    
    # 模拟 API 响应结构
    mock_response = {
        "task_id": "extract_test123",
        "triplets": [
            {
                "subject_name": "测试故障 A",
                "subject_type": "BasicEvent",
                "relation": "resultsIn",
                "object_name": "测试故障 B",
                "object_type": "IntermediateEvent",
                "confidence": 0.95,
                "source": "测试文档"
            }
        ],
        "events": [
            {
                "event_id": "evt_测试故障 A",
                "event_name": "测试故障 A",
                "event_type": "bottom",
                "description": "测试文档",
                "probability": 0.95,
                "metadata": {"source": "测试文档"}
            }
        ],
        "gates": [
            {
                "gate_id": "gate_0",
                "gate_type": "OR",
                "input_events": ["evt_测试故障 A"],
                "output_event": "evt_测试故障 B"
            }
        ],
        "status": "completed",
        "progress": 1.0,
        "output_file": "data/output/test_triplets.json",
        "traceability": [{"file": "test.txt", "timestamp": "1234567890"}],
        "accuracy_metrics": {"avg_confidence": 0.95}
    }
    
    print("[OK] API Response Format Example:")
    print(json.dumps(mock_response, indent=2, ensure_ascii=False))


def main():
    """Run all tests"""
    print("\n[START] Knowledge Extraction Module Integration Test\n")
    
    # Test 1: Basic extraction
    test_basic_extraction()
    
    # Test 2: Complete service (requires Neo4j)
    print("\n[NOTE] Test 2 requires Neo4j database running")
    response = input("Continue to Test 2? (y/n): ")
    if response.lower() == 'y':
        try:
            test_fault_tree_service()
        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] User cancelled test")
    else:
        print("[SKIPPED] Test 2")
    
    # Test 3: API format
    test_api_format()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All tests completed!")
    print("=" * 60)
    print("\n[TIPS]")
    print("   - Check data/output/ directory for generated JSON files")
    print("   - If Neo4j is connected, query extracted knowledge in database")
    print("   - Test actual API with curl or Postman")
    print()


if __name__ == "__main__":
    main()
