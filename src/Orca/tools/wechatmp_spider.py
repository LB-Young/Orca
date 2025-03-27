from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
import os

class WechatmpSpiderTool(Tool):
    """微信公众号内容搜索工具"""
    
    name = "wechatmp_spider"  # 工具名称
    description = "微信公众号内容搜索器"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "string",
            "description": "搜索的关键词",
            "required": True
        },
        "nums": {
            "type": "integer",
            "description": "搜索文章数目",
            "required": False
        }
    }
    
    # 工具输出定义
    outputs = {
        "paths": {
            "type": "array",
            "description": "搜索结果保存的路径列表"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        """
        执行微信公众号搜索
        
        注意：此方法依赖selenium和Chrome WebDriver，需要确保环境中已安装
        """
        try:
            # 导入可能依赖的模块
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from lxml import etree
            import time
            
            # 从输入中提取参数
            keyword = inputs.get("keyword", "")
            nums = inputs.get("nums", 3)
            
            # 参数校验
            if not keyword:
                raise Exception("搜索关键词不能为空")
            
            # 定义输出目录
            output_dir = '/Users/liubaoyang/Documents/YoungL/logs/orca/output/wechatmp'
            os.makedirs(output_dir, exist_ok=True)
            
            # 创建Chrome浏览器实例
            driver = webdriver.Chrome()
            wait = WebDriverWait(driver, 10)
            
            try:
                # 打开搜索页面
                driver.get("https://weixin.sogou.com/")
                time.sleep(1)
                
                # 定位搜索框并输入内容
                search_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/div[2]/div[2]/div[2]/form/div/span[1]/input[2]")))
                search_input.send_keys(keyword)
                time.sleep(2)
                
                # 点击搜索按钮
                search_button = driver.find_element(By.XPATH, 
                    "/html/body/div/div[2]/div[2]/div[2]/form/div/span[2]/input")
                search_button.click()
                
                # 等待搜索结果加载
                time.sleep(3)
                
                # 创建保存结果的目录
                res_dir = os.path.join(output_dir, keyword)
                os.makedirs(res_dir, exist_ok=True)
                
                # 结果列表
                results = []
                
                # 提取搜索结果
                for i in range(nums):
                    try:
                        # 获取当前页面的HTML
                        page = etree.HTML(driver.page_source)
                        
                        # 提取基本信息
                        url = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a/@href')
                        url = url[0] if url else ""
                        
                        title = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a/text()')
                        title = title[0] if title else ""
                        
                        time_str = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/div/span[2]/text()')
                        time_str = time_str[0] if time_str else ""
                        
                        abstract = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/p/text()')
                        abstract = abstract[0] if abstract else ""
                        
                        user_id = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/div/span[1]/text()')
                        user_id = user_id[0] if user_id else ""
                        
                        # 处理标题，移除特殊字符
                        title = title.replace('\\', ' ').replace('/', ' ')[:15]
                        
                        # 点击链接打开新页面
                        article_link = driver.find_element(By.XPATH, 
                            f"/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a")
                        article_link.click()
                        time.sleep(2)
                        
                        # 切换到新窗口
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(2)
                        
                        # 等待内容加载并提取
                        content_element = wait.until(EC.presence_of_element_located(
                            (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div[1]/div[2]")))
                        content = content_element.text
                        
                        # 保存结果
                        result = {
                            'url': url,
                            'title': title,
                            'time': time_str,
                            'abstract': abstract,
                            'user_id': user_id,
                            'content': content
                        }
                        
                        # 将结果保存到文件
                        file_path = os.path.join(res_dir, f"{user_id or f'article_{i+1}'}.txt")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            for key, value in result.items():
                                f.write(f"{key}: {value}\n")
                        
                        results.append(result)
                        
                        # 关闭当前窗口，切回主窗口
                        driver.close()
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[0])
                    except Exception as e:
                        print(f"处理第{i+1}个搜索结果时出错: {str(e)}")
                        # 尝试切回主窗口
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
            
            finally:
                # 关闭浏览器
                driver.quit()
            
            # 返回结果目录路径
            return [res_dir]
            
        except Exception as e:
            raise Exception(f"微信公众号搜索失败: {str(e)}") 