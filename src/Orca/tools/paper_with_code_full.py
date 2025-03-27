import aiohttp
import json
from lxml import html
import asyncio
import PyPDF2
import requests
import os
from tqdm import tqdm
import hashlib
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool

class PaperWithCodeFullTool(Tool):
    """论文代码搜索工具（含全文）"""
    
    name = "paper_with_code_search_full"  # 工具名称
    description = "从Papers with Code网站搜索论文并获取全文内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "type": {
            "type": "string",
            "description": "读取类型，'top'表示读取最受欢迎的论文，'latest'表示读取最新的论文",
            "required": True
        },
        "nums": {
            "type": "integer",
            "description": "需要读取的论文数目",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "papers": {
            "type": "array",
            "description": "论文信息列表，包含标题、作者、发表时间、摘要、star数和全文内容"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        type_param = inputs.get("type", "top")
        nums = inputs.get("nums", 10)
        
        try:
            papers = await self._fetch_papers(type_param, nums)
            return papers
        except Exception as e:
            raise Exception(f"获取论文失败: {str(e)}")
    
    async def _fetch_papers(self, type_param: str, nums: int) -> List[Dict[str, Any]]:
        """
        获取 Papers with Code 网站的论文信息
        
        Args:
            type_param: 读取类型，'top'表示最受欢迎的论文，'latest'表示最新的论文
            nums: 需要读取的论文数目
        
        Returns:
            list: 论文信息列表
        """
        try:
            papers = []
            page = (nums-1) // 10 + 1
            cur_page = 1
            if type_param == "top":
                base_url = "https://paperswithcode.com"
                source_url = "https://paperswithcode.com"
                url = f"{base_url}"
            else:
                base_url = "https://paperswithcode.com/latest"
                source_url = "https://paperswithcode.com"
                url = f"{base_url}"
                
            while True:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise Exception(f"HTTP错误: {response.status}")
                            
                        html_content = await response.text()
                        tree = html.fromstring(html_content)
                        
                        # 获取论文列表
                        for i in range(1, nums + 1):
                            try:
                                # 获取标题和链接
                                title_xpath = f'/html/body/div[3]/div[2]/div[{i}]/div[2]/div/div[1]/h1/a'
                                title_elem = tree.xpath(title_xpath)
                                if not title_elem:
                                    continue
                                    
                                title = title_elem[0].text.strip()

                                # 获取发布日期
                                # 尝试获取第三个span元素下的日期
                                date_xpath_3 = f'/html/body/div[3]/div[2]/div[{i}]/div[2]/div/div[1]/p[1]/span[3]'
                                date_elem = tree.xpath(date_xpath_3)
                                if (not date_elem) or len(date_elem[0].text.strip()) == 0:
                                    # 如果第三个span没有日期，尝试获取第二个span元素下的日期
                                    date_xpath_2 = f'/html/body/div[3]/div[2]/div[{i}]/div[2]/div/div[1]/p[1]/span[2]'
                                    date_elem = tree.xpath(date_xpath_2)
                                
                                published_date = date_elem[0].text.strip() if date_elem else "未知日期"

                                paper_url = source_url + title_elem[0].get('href')
                                
                                # 获取作者团队信息
                                team_xpath = f'/html/body/div[3]/div[2]/div[{i}]/div[2]/div/div[1]/p[1]/span[1]/a'
                                team_elem = tree.xpath(team_xpath)
                                team = team_elem[0].text.strip() if team_elem else "未知团队"
                                
                                # 获取详细信息
                                detail_info = await self._get_paper_detail(session, source_url, paper_url)
                                if detail_info:
                                    papers.append({
                                        'title': title,
                                        'url': detail_info['url'],
                                        'team': team,  # 添加团队信息到返回结果中
                                        'abstract': detail_info['abstract'],
                                        'published_date': published_date,
                                        'stars': detail_info['stars'],
                                        'authors': detail_info['authors'],
                                        'content': detail_info['paper_content']
                                    })
                                    
                            except Exception as e:
                                print(f"处理第{i}篇论文时出错: {str(e)}")
                                continue
                                
                if cur_page == page:
                    break
                if cur_page < page:
                    cur_page += 1
                    url = f"{base_url}/?page={cur_page}"
                    
            return papers
                    
        except Exception as e:
            raise Exception(f"获取论文列表失败: {str(e)}")
    
    async def _get_paper_detail(self, session, source_url, paper_url):
        """获取论文详细信息"""
        try:
            async with session.get(paper_url) as response:
                if response.status != 200:
                    return None
                detail_html = await response.text()
                tree = html.fromstring(detail_html)
                
                # 获取摘要              
                abstract = tree.xpath('/html/body/div[3]/main/div[2]/div/div/p/text()')
                abstract = abstract[0].strip() if abstract else "无摘要"
                
                # 获取作者信息
                # 尝试第一个xpath路径获取作者
                authors = tree.xpath('/html/body/div[3]/main/div[1]/div/div/div/p/span/a/text()')
                if not authors:
                    # 如果第一个路径失败，尝试第二个xpath路径
                    authors = tree.xpath('/html/body/div[3]/main/div[1]/div/div/div/p/span/text()')
                
                # 处理作者列表，去除空白字符并过滤掉空字符串
                authors = [author.strip() for author in authors[1:] if author.strip()] if authors else ["未知作者"]

                # 获取star数
                stars = tree.xpath('/html/body/div[3]/main/div[3]/div[1]/div[2]/div[1]/div/div[2]/div/text()')
                
                stars_num = ""
                for item in stars:
                    stars_num += item.strip().replace(",", "")
                    if stars_num:
                        break
                stars = int(stars_num) if stars_num else 0

                # 获取论文下载链接
                pdf_link = tree.xpath('/html/body/div[3]/main/div[2]/div/div/a[1]/@href')
                paper_content = ""
                if pdf_link:
                    # 获取PDF URL
                    pdf_url = pdf_link[0] if pdf_link[0].startswith('http') else source_url + pdf_link[0]
                    save_dir = '/Users/liubaoyang/Documents/YoungL/logs/orca/output/paper_recommend/download_pdf/'
                    # 检查是否已缓存
                    cached_path = self._get_cached_pdf_path(pdf_url, save_dir)
                    if os.path.exists(cached_path):
                        paper_content = await self._read_pdf(cached_path)  # 从缓存读取内容
                    else:
                        # 下载论文
                        file_path = await self._download_pdf(pdf_url, save_dir)
                        if file_path:
                            paper_content = await self._read_pdf(file_path)
                return {
                    'url': paper_url,
                    'authors': authors,
                    'abstract': abstract,
                    'stars': stars,
                    "paper_content": paper_content
                }
                
        except Exception as e:
            print(f"获取论文详情失败: {str(e)}")
            return None
    
    def _get_cached_pdf_path(self, url, output_dir):
        """获取PDF文件的缓存路径

        Args:
            url (str): PDF文件的URL
            output_dir (str): 缓存目录

        Returns:
            str: 缓存文件的完整路径
        """
        # 使用URL的MD5值作为文件名
        filename = hashlib.md5(url.encode()).hexdigest() + '.pdf'
        return os.path.join(output_dir, filename)
    
    async def _download_pdf(self, url, output_dir="."):
        """从给定URL下载PDF文件并保存到指定目录，支持缓存

        Args:
            url (str): PDF文件的URL
            output_dir (str, optional): 保存文件的目录. Defaults to "."

        Returns:
            str: 保存的文件路径，如果下载失败则返回None
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 检查缓存
            cached_path = self._get_cached_pdf_path(url, output_dir)
            if os.path.exists(cached_path):
                print(f"使用缓存的PDF文件: {cached_path}")
                return cached_path

            # 发送GET请求获取PDF文件
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            # 获取文件大小（字节）
            file_size = int(response.headers.get('content-length', 0))

            # 使用tqdm创建进度条
            progress = tqdm(total=file_size, unit='iB', unit_scale=True)

            # 以二进制写入模式打开文件
            with open(cached_path, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    progress.update(size)

            progress.close()
            print(f"PDF文件已成功下载并缓存到: {cached_path}")
            return cached_path

        except requests.exceptions.RequestException as e:
            print(f"下载PDF文件时发生错误: {str(e)}")
            return None
        except IOError as e:
            print(f"保存PDF文件时发生错误: {str(e)}")
            return None
    
    async def _read_pdf(self, path):
        """读取PDF文件内容

        Args:
            path (str): PDF文件路径

        Returns:
            str: 提取的文本内容
        """
        with open(path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            if len(text) > 30000:
                text = text[:30000] + "..."
            
            return text 