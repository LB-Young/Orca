import arxiv
import PyPDF2
import requests
from typing import Dict, Any, Iterator, Union
from .tool import Tool

async def read_pdf(path):
    # 读取PDF文件内容的辅助函数
    with open(path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


class ArxivSearchTool(Tool):
    """Arxiv论文搜索工具"""
    
    name = "arxiv_search"  # 工具名称
    description = "搜索arxiv上相关主题的论文"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "string",
            "description": "搜索的关键词",
            "required": True
        },
        "nums": {
            "type": "integer",
            "description": "搜索的论文数目",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "papers": {
            "type": "array",
            "description": "搜索到的论文列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        keyword = inputs.get("keyword", "")
        nums = inputs.get("nums", 1)
        
        # 限制结果数量
        if nums > 20:
            nums = 20
            
        # 创建Arxiv客户端
        client = arxiv.Client()
        search = arxiv.Search(
            query = keyword,
            max_results = nums,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        
        # 获取并处理搜索结果
        papers = []
        for r in client.results(search):
            try:
                down_load_path = r.download_pdf("/Users/liubaoyang/Documents/YoungL/logs/orca/output/paper_recommend/download_pdf/")
                pdf_text = await read_pdf(down_load_path)
                papers.append(
                    {
                        "title": r.title,
                        "authors": r.authors,
                        "published": r.published,
                        "summary": r.summary,
                        "pdf_text": pdf_text,
                        "down_load_path": down_load_path
                    }
                )
            except Exception as e:
                print(e)
                
        return papers 