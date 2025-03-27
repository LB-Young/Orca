import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown2
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
from Orca.tools.load_local_api_keys import load_local_api_keys

class SendEmailTool(Tool):
    """邮件发送工具"""
    
    name = "send_email"  # 工具名称
    description = "发送邮件"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "content": {
            "type": "string",
            "description": "邮件内容",
            "required": True
        },
        "subject": {
            "type": "string",
            "description": "邮件主题",
            "required": True
        },
        "to": {
            "type": "array",
            "description": "收件人邮箱地址列表",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "邮件发送结果"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        content = inputs.get("content", "")
        subject = inputs.get("subject", "")
        to = inputs.get("to", [])
        
        # 参数校验
        if not content:
            raise Exception("邮件内容不能为空")
        if not subject:
            raise Exception("邮件主题不能为空")
        if not to:
            raise Exception("收件人列表不能为空")
        
        try:
            # 发送邮件
            result = await self._send_email(content, subject, to)
            return result
        except Exception as e:
            raise Exception(f"发送邮件失败: {str(e)}")
    
    async def _dict_to_multiline_string(self, d, indent=0):
        """将字典转换为多行字符串
        
        Args:
            d: 字典对象
            indent: 缩进量
            
        Returns:
            str: 格式化的多行字符串
        """
        result = ""
        for key, value in d.items():
            if isinstance(value, dict):  # 如果值是字典，递归处理
                inner = await self._dict_to_multiline_string(value, indent + 4)
                result += " " * indent + f"{key}:\n" + inner
            else:  # 否则直接添加键值对
                result += " " * indent + f"{key}: {value}\n"
        return result
    
    async def _send_email(self, content, subject, to):
        """发送邮件
        
        Args:
            content: 邮件内容
            subject: 邮件主题
            to: 收件人列表
            
        Returns:
            str: 发送结果
        """
        # 设置SMTP服务器
        smtp_server = "smtp.qq.com"
        smtp_port = 465  # SSL端口
        smtp_username = "823707202@qq.com"
        # 使用应用专用密码
        smtp_password = load_local_api_keys("qq_mail_shouquanma")
        
        # 处理邮件内容
        if isinstance(content, dict):
            content = await self._dict_to_multiline_string(content, 0)
        elif isinstance(content, list):
            content = "[" + "\n".join(content) + "\n]" 
        else:
            content = str(content).replace('\\n', '\n').replace("\n", "\n\n").replace("\n\n\n\n", "\n\n")
        
        # 创建纯文本版本（作为后备）
        text_part = MIMEText(content, 'plain', 'utf-8')
        
        # 转换 Markdown 为 HTML 并创建 HTML 版本
        html_content = markdown2.markdown(content, extras=['tables', 'code-friendly', 'fenced-code-blocks'])
        
        # 添加基本的 CSS 样式
        styled_html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
                    pre {{ background: #f4f4f4; padding: 1em; border-radius: 4px; overflow-x: auto; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f4f4f4; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """
        html_part = MIMEText(styled_html, 'html', 'utf-8')
        
        # 处理收件人
        if isinstance(to, str):
            to_list = [to]
        elif isinstance(to, list):
            to_list = to
        else:
            raise ValueError("to必须是字符串或字符串列表")
        
        success_list = []
        fail_list = []
        server = None
        
        try:
            # 连接 SMTP 服务器
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用 SSL 加密
            server.login(smtp_username, smtp_password)  # 登录邮箱
            
            for recipient in to_list:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = smtp_username
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    msg.attach(html_part)
                    
                    server.sendmail(from_addr=smtp_username, to_addrs=recipient, msg=msg.as_string())  # 发送邮件
                    success_list.append(recipient)
                except Exception as e:
                    print(f"向 {recipient} 发送邮件失败：{e}")
                    fail_list.append(recipient)
        
        finally:
            if server:
                server.quit()
                
        return f"成功发送邮件至 {success_list}，发送失败的收件人 {fail_list}" 