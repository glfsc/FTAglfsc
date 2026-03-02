"""
文件解析服务
"""
from typing import List

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

class FileParser:
    """文件解析器"""
    
    def parse(self, file_path: str, file_ext: str) -> List[str]:
        """
        解析文件内容
        返回文本列表
        """
        if file_ext == ".docx":
            return self._parse_docx(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            return self._parse_excel(file_path)
        elif file_ext == ".csv":
            return self._parse_csv(file_path)
        elif file_ext == ".txt":
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式：{file_ext}")
    
    def _parse_docx(self, file_path: str) -> List[str]:
        """解析DOCX文件"""
        if not HAS_DOCX:
            raise ValueError("需要安装python-docx: pip install python-docx")
        doc = Document(file_path)
        texts = []
        for para in doc.paragraphs:
            if para.text.strip():
                texts.append(para.text.strip())
        return texts
    
    def _parse_excel(self, file_path: str) -> List[str]:
        """解析Excel文件"""
        if not HAS_PANDAS:
            raise ValueError("需要安装pandas和openpyxl: pip install pandas openpyxl")
        import pandas as pd
        df = pd.read_excel(file_path)
        texts = []
        for _, row in df.iterrows():
            row_text = " ".join([str(val) for val in row.values if pd.notna(val)])
            if row_text.strip():
                texts.append(row_text.strip())
        return texts
    
    def _parse_csv(self, file_path: str) -> List[str]:
        """解析CSV文件"""
        if not HAS_PANDAS:
            raise ValueError("需要安装pandas: pip install pandas")
        import pandas as pd
        df = pd.read_csv(file_path)
        texts = []
        for _, row in df.iterrows():
            row_text = " ".join([str(val) for val in row.values if pd.notna(val)])
            if row_text.strip():
                texts.append(row_text.strip())
        return texts
    
    def _parse_txt(self, file_path: str) -> List[str]:
        """解析TXT文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip()]
