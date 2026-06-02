"""
简历文件解析工具

提供 LangChain @tool，供 Agent 调用以提取 PDF/DOCX/TXT 文件内容。
"""

from pathlib import Path

from langchain_core.tools import tool
from pypdf import PdfReader
from docx import Document


@tool
def read_resume_file(file_path: str) -> str:
    """
    读取简历文件内容。

    支持 PDF、DOCX、TXT 格式。传入文件路径，返回提取的纯文本内容。
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
        return text.strip()

    elif suffix == ".docx":
        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs)
        return text.strip()

    elif suffix == ".txt":
        return path.read_text(encoding="utf-8").strip()

    else:
        return f"不支持的文件格式: {suffix}，仅支持 PDF、DOCX、TXT"
