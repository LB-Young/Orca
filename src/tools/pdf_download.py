import requests
import os
from tqdm import tqdm

def download_pdf(url, output_dir="."):
    """从给定URL下载PDF文件并保存到指定目录

    Args:
        url (str): PDF文件的URL
        output_dir (str, optional): 保存文件的目录. Defaults to "."

    Returns:
        str: 保存的文件路径，如果下载失败则返回None
    """
    try:
        # 发送GET请求获取PDF文件
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 从URL中提取文件名，如果没有则使用默认名称
        filename = url.split('/')[-1]
        if not filename.endswith('.pdf'):
            filename = 'downloaded.pdf'

        # 构建完整的文件保存路径
        file_path = os.path.join(output_dir, filename)

        # 获取文件大小（字节）
        file_size = int(response.headers.get('content-length', 0))

        # 使用tqdm创建进度条
        progress = tqdm(total=file_size, unit='iB', unit_scale=True)

        # 以二进制写入模式打开文件
        with open(file_path, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                progress.update(size)

        progress.close()
        print(f"PDF文件已成功下载到: {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        print(f"下载PDF文件时发生错误: {str(e)}")
        return None
    except IOError as e:
        print(f"保存PDF文件时发生错误: {str(e)}")
        return None

if __name__ == "__main__":
    # 示例使用
    pdf_url = "https://arxiv.org/pdf/2408.00203v1.pdf"
    download_pdf(pdf_url)