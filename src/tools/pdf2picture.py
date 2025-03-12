import os
from pdf2image import convert_from_path


async def pdf2pictures(pdf_path="", picture_save_path="", params_format=False):
    if params_format:
        return ['file_path', "picture_save_path"]
    
    if not pdf_path or not picture_save_path:
        raise Exception("PDF路径和保存路径不能为空")
    
    if not os.path.exists(pdf_path):
        raise Exception("PDF文件不存在")
    
    # 确保保存路径存在
    os.makedirs(picture_save_path, exist_ok=True)
    
    try:
        # 将PDF文件转换为图片
        images = convert_from_path(pdf_path)
        
        # 保存每一页为单独的图片
        for i, image in enumerate(images):
            image_path = os.path.join(picture_save_path, f'page_{i + 1}.png')
            image.save(image_path, 'PNG')
            
        return f"{pdf_path}文件已经转位图片，图片保存在{picture_save_path}文件夹下。"
    except Exception as e:
        raise Exception(f"PDF转换图片失败: {str(e)}")
    
async def ut():
    pdf_path = "/Users/liubaoyang/Desktop/flowchart/难选高钙白钨矿选矿技术研究.pdf"
    picture_save_path = "/Users/liubaoyang/Desktop/flowchart/output_pic"
    res = await pdf2pictures(pdf_path, picture_save_path)
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(ut())