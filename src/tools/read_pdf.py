import os
import PyPDF2


async def pdf_reader(file_path, params_format=False):
    if params_format:
        return ['file_path']

    if not os.path.exists(file_path):
        raise Exception("PDF文件不存在")

    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"PDF读取失败: {str(e)}")