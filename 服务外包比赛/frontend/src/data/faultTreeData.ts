export interface EventData {
  id: string;
  name: string;
  probability: string;
  rules: Record<string, any>;
}

export interface NodeData {
  id: string;
  name: string;
  type: string; // "1" (Top), "2" (Intermediate), "3" (Basic)
  x: number;
  y: number;
  gate: string; // "1" (AND), "2" (OR), "" (None)
  event: EventData;
}

export interface LinkData {
  sourceId: string;
  targetId: string;
  isCondition: boolean;
  traceability: {
    evidence: string;
    confidence: number;
  };
}

export interface FaultTreeData {
  attr: {
    background: string;
    color: string;
    width: number;
    height: number;
    containerX: number;
    containerY: number;
    eventCode: boolean;
    eventProbability: boolean;
    linkColor: string;
  };
  nodeList: NodeData[];
  linkList: LinkData[];
}

export const initialData: FaultTreeData = {
    "attr": {
        "background": "#fff",
        "color": "#000",
        "width": 1920,
        "height": 1080,
        "containerX": -50,
        "containerY": -50,
        "eventCode": true,
        "eventProbability": false,
        "linkColor": "#456"
    },
    "nodeList": [
        {
            "id": "node-e67cec1d9b644c37abd96a82e97939f8",
            "name": "气路压力不足",
            "type": "3",
            "x": 150,
            "y": 150,
            "gate": "",
            "event": {
                "id": "1347789",
                "name": "气路压力不足",
                "probability": "1e-8",
                "rules": {}
            }
        },
        {
            "id": "node-9bc8a0cd345c4f6db3409d6737de55c9",
            "name": "回收故障",
            "type": "2",
            "x": 350,
            "y": 150,
            "gate": "2",
            "event": {
                "id": "1907116",
                "name": "回收故障",
                "probability": "1e-8",
                "rules": {}
            }
        },
        {
            "id": "node-c97760ca7bcc47e1b808c24c400ab509",
            "name": "机械锁未释放",
            "type": "3",
            "x": 550,
            "y": 150,
            "gate": "",
            "event": {
                "id": "5665282",
                "name": "机械锁未释放",
                "probability": "1e-8",
                "rules": {}
            }
        },
        {
            "id": "node-cb9dd77400bf47d58083d266a9182f67",
            "name": "释放故障",
            "type": "2",
            "x": 750,
            "y": 150,
            "gate": "2",
            "event": {
                "id": "2932350",
                "name": "释放故障",
                "probability": "1e-8",
                "rules": {}
            }
        },
        {
            "id": "node-2cf5d76ce788463cad74c4b2bb500526",
            "name": "登机梯故障",
            "type": "1",
            "x": 950,
            "y": 150,
            "gate": "2",
            "event": {
                "id": "1322269",
                "name": "登机梯故障",
                "probability": "1e-8",
                "rules": {}
            }
        }
    ],
    "linkList": [
        {
            "sourceId": "node-e67cec1d9b644c37abd96a82e97939f8",
            "targetId": "node-9bc8a0cd345c4f6db3409d6737de55c9",
            "isCondition": false,
            "traceability": {
                "evidence": "《通用型驱动系统故障手册》P12",
                "confidence": 0.95
            }
        },
        {
            "sourceId": "node-e67cec1d9b644c37abd96a82e97939f8",
            "targetId": "node-cb9dd77400bf47d58083d266a9182f67",
            "isCondition": false,
            "traceability": {
                "evidence": "《通用型驱动系统故障手册》P12",
                "confidence": 0.95
            }
        },
        {
            "sourceId": "node-9bc8a0cd345c4f6db3409d6737de55c9",
            "targetId": "node-2cf5d76ce788463cad74c4b2bb500526",
            "isCondition": false,
            "traceability": {
                "evidence": "《系统原理定义》",
                "confidence": 0.99
            }
        },
        {
            "sourceId": "node-c97760ca7bcc47e1b808c24c400ab509",
            "targetId": "node-9bc8a0cd345c4f6db3409d6737de55c9",
            "isCondition": false,
            "traceability": {
                "evidence": "维修工单 -202305A",
                "confidence": 0.88
            }
        },
        {
            "sourceId": "node-cb9dd77400bf47d58083d266a9182f67",
            "targetId": "node-2cf5d76ce788463cad74c4b2bb500526",
            "isCondition": false,
            "traceability": {
                "evidence": "《系统原理定义》",
                "confidence": 0.99
            }
        }
    ]
};
