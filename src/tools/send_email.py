from load_local_api_keys import load_local_api_keys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown2

async def dict_to_multiline_string(d, indent=0):
    result = ""
    for key, value in d.items():
        if isinstance(value, dict):  # 如果值是字典，递归处理
            inner = await dict_to_multiline_string(value, indent + 4)
            result += " " * indent + f"{key}:\n" + inner
        else:  # 否则直接添加键值对
            result += " " * indent + f"{key}: {value}\n"
    return result

async def send_email(content="", subject="", to="", params_format=False):
    if params_format:
        return ['content', 'subject', 'to']
    # Set up the SMTP server
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # 修改为SSL端口465
    smtp_username = "823707202@qq.com"
    # 需要使用应用专用密码而不是普通密码
    # 请在Google账户设置中生成应用专用密码: https://myaccount.google.com/security
    smtp_password = load_local_api_keys("qq_mail_shouquanma") # 替换为应用专用密码
    # Create the email message
    
    if isinstance(content, dict):
        content = await dict_to_multiline_string(content, 0)
    elif isinstance(content, list):
        content = "[" + "\n".join(content) + "\n]" 
    else:
        content = str(content).replace('\\n', '\n').replace("\n", "\n\n").replace("\n\n\n\n", "\n\n")
    
    # 创建纯文本版本（作为后备）
    text_part = MIMEText(content, 'plain', 'utf-8')
    
    # 转换 Markdown 为 HTML 并创建 HTML 版本
    html_content = markdown2.markdown(content, extras=['tables', 'code-friendly', 'fenced-code-blocks'])
    
    # 添加一些基本的 CSS 样式
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
    
    if isinstance(to, str):
        to_list = [to]
    elif isinstance(to, list):
        to_list = to
    else:
        raise ValueError("to must be a string or a list of strings")
    success_list = []
    fail_list = []
    for to in to_list:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = ""
            msg['Subject'] = subject
            msg.attach(html_part)

        # msg.attach(MIMEText(content, 'html', 'utf-8'))
        
            # 连接 SMTP 服务器
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用 SSL 加密
            server.login(smtp_username, smtp_password)  # 登录邮箱
            server.sendmail(from_addr=smtp_username, to_addrs=to, msg=msg.as_string())  # 发送邮件
            print("邮件发送成功！")
            success_list.append(to)
        except smtplib.SMTPException as e:
            print(f"邮件发送失败：{e}")
            fail_list.append(to)
            
    server.quit()
    return f"Send email to {success_list} successfully, fail to {fail_list}"
    

if __name__ == '__main__':
    import asyncio
    content = 'YoungL！\n我为您收集了最新的论文，并根据您的研究方向给出以下阅读建议：\n\n-----------------------------------------------------------------------------------------------------------------------------\n"{\n    "推荐阅读内容和顺序": [\n        {\n            "类别": "LLM",\n            "star数目": 3,\n            "标题": "The Stochastic Parrot on LLM\'s Shoulder: A Summative Assessment of Physical Concept Understanding",\n            "摘要总结": "研究通过设计物理概念理解任务PhysiCo，揭示了大型语言模型在理解核心物理现象上的局限性。",\n            "论文链接": "https://paperswithcode.com/paper/the-stochastic-parrot-on-llm-s-shoulder-a"\n        },\n        {\n            "类别": "多模态",\n            "star数目": 2,\n            "标题": "Spatio-temporal collaborative multiple-stream transformer network for liver lesion classification on multiple-sequence magnetic resonance imaging",\n            "摘要总结": "提出了一种时空协同多流Transformer网络，显著提升了多序列MRI肝脏病变分类的性能。",\n            "论文链接": "https://paperswithcode.com/paper/spatio-temporal-collaborative-multiple-stream"\n        },\n        {\n            "类别": "多模态",\n            "star数目": 1,\n            "标题": "Redistribute Ensemble Training for Mitigating Memorization in Diffusion Models",\n            "摘要总结": "提出一种减少扩散模型记忆行为的方法，有效降低了隐私风险并保持生成性能。",\n            "论文链接": "https://paperswithcode.com/paper/redistribute-ensemble-training-for-mitigating"\n        }\n    ],\n    "参考论文总结": {\n        "LLM": "LLM领域的论文主要探讨了大型语言模型对物理概念的理解能力。研究表明，尽管先进模型如GPT-4o和Gemini 2.0在自然语言处理任务中表现优异，但在涉及深层次推理的任务中仍存在明显不足，表明其可能存在“随机鹦鹉”现象。《The Stochastic Parrot on LLM\'s Shoulder: A Summative Assessment of Physical Concept Understanding》",\n        "RAG": "未收集到与RAG相关的最新前沿论文。",\n        "Agent": "未收集到与Agent相关的最新前沿论文。",\n        "多模态": "多模态领域的论文集中在医学影像分析和扩散模型优化上。前者提出了基于Transformer的网络用于肝脏病变分类，后者则关注减少扩散模型的记忆行为以保护隐私。两篇论文均展示了创新的技术解决方案，并在实验中取得了显著成果。《Spatio-temporal collaborative multiple-stream transformer network for liver lesion classification on multiple-sequence magnetic resonance imaging》、《Redistribute Ensemble Training for Mitigating Memorization in Diffusion Models》",\n        "音频": "未收集到与音频相关的最新前沿论文。",\n        "计算机视觉": "计算机视觉领域的论文探讨了伪装对象检测和激活函数优化。伪装对象检测的研究提出了一种结合脑机接口的人机协作框架，而激活函数优化则测试了一种新的自定义激活函数TAAF的性能。这些研究为提高模型效率和可靠性提供了新思路。《Evaluating the Performance of TAAF for image classification models》、《Uncertainty Aware Human-machine Collaboration in Camouflaged Object Detection》",\n        "其它": "其他领域的论文涵盖了图神经网络、灾难性遗忘、异常检测和注意力机制优化等主题。研究显示经典GNN在图级别任务中表现出色，Eidetic Learning解决了灾难性遗忘问题，AnomalyGFM提出了一种适用于零样本和少样本场景的图异常检测方法，Top-Theta Attention则优化了Transformer的计算效率。《Unlocking the Potential of Classic GNNs for Graph-level Tasks: Simple Architectures Meet Excellence》、《Eidetic Learning: an Efficient and Provable Solution to Catastrophic Forgetting》、《AnomalyGFM: Graph Foundation Model for Zero/Few-shot Anomaly Detection》、《Top-Theta Attention: Sparsifying Transformers by Compensated Thresholding》"\n    }\n}"'
    content = content.replace("\n", "\n\n").replace("\n\n\n\n", "\n\n")
    res = asyncio.run(send_email(content, "1", to=["lby15356@gmail.com", "xyzhang290@gmail.com"]))
    print(res)
