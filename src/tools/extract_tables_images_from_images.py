import os
import time
import numpy as np
import onnxruntime as ort
import cv2
import json
from .vl_model import vl_model


CLASS_MAPPING = {
    0: "Text Title",
    1: "Body Text",
    2: "Header/Footer", 
    3: "Image",
    4: "Image Caption",
    5: "Table",
    6: "Table Title",
    7: "Table Footer Unit"
}

def resize_boxes(boxes, old_size, new_size):
    old_width,old_height = old_size
    new_width,new_height = new_size
    scale_x, scale_y = (
        old_width / new_width,
        old_height / new_height,
    )
    if not isinstance(boxes, np.ndarray):
        boxes = np.array(boxes)
    boxes[:, 0::2] *= scale_x
    boxes[:, 1::2] *= scale_y
    x1 = np.clip(boxes[:, 0], a_min=0, a_max=old_width)
    y1 = np.clip(boxes[:, 1], a_min=0, a_max=old_height)
    x2 = np.clip(boxes[:, 2], a_min=0, a_max=old_width)
    y2 = np.clip(boxes[:, 3], a_min=0, a_max=old_height)
    return np.stack((x1, y1, x2, y2), axis=-1)

def resize_image(image, min_size=800, max_size=1333):
    height, width = image.shape[:2]
    if height >= min_size and width >= min_size and width <= max_size and height <= max_size:
        return image
    else:
        scale_w = min_size / width
        scale_h = min_size / height
        scale = min(scale_w, scale_h)
        if width * scale > max_size or height * scale > max_size:
            scale = max_size / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

def get_img_inputs(sample_image, min_size=800, max_size=1333):
    original_image = cv2.imread(sample_image)
    height, width = original_image.shape[:2]
    image = resize_image(original_image, min_size, max_size)
    image = image.transpose(2, 0, 1)
    inputs = {"image": image, "height": height, "width": width}
    sample_inputs = [inputs]
    return sample_inputs


def find_title_for_content(boxes, labels, scores, content_box, content_type):
    # 计算内容框的中心点坐标
    content_center = [(content_box[0] + content_box[2])/2, (content_box[1] + content_box[3])/2]
    
    # 根据内容类型确定标题类型
    title_type = "Table Title" if content_type == "Table" else "Image Caption"
    
    # 初始化最小距离为无穷大
    min_distance = float('inf')
    # 初始化最近的标题框为None
    closest_title = None
    # 初始化最近标题的置信度分数
    closest_score = 0
    
    # 遍历所有检测到的框
    for box, label, score in zip(boxes, labels, scores):
        # 如果置信度大于0.5且标签匹配目标标题类型
        if box[2] < content_box[0] or box[0] > content_box[2]:
            continue
        if score > 0.5 and label == title_type:
            # 计算当前标题框的中心点
            title_center = [(box[0] + box[2])/2, (box[1] + box[3])/2]
            # 计算标题中心点和内容中心点的垂直距离
            distance = abs(title_center[1] - content_center[1])
            # 如果找到更近的标题框
            if distance < min_distance:
                min_distance = distance
                closest_title = box
                closest_score = score
    
    # 返回找到的最近的标题框
    return closest_title

async def extract_tables_images_from_images(images_dir="", tables_images_outdir="", params_format=False):
    if params_format:
        return ['images_dir', 'tables_images_outdir']
    
    if not images_dir or not tables_images_outdir:
        raise Exception("图片目录和保存目录不能为空")
    
    if not os.path.exists(images_dir):
        raise Exception("图片目录不存在")
    
    os.makedirs(tables_images_outdir, exist_ok=True)
    
    model_path = "/Users/liubaoyang/Documents/YoungL/models/jockerK/layoutlmv3-onnx/jockerK/layoutlmv3-onnx/quantize_model.onnx"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ONNX模型文件不存在: {model_path}")
    
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    
    processed_images = 0
    extracted_tables = 0
    extracted_images = 0
    failed_images = 0
    tmp_dir = "/Users/liubaoyang/Desktop/flowchart/tmp/"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    try:
        for image in os.listdir(images_dir):
            if image.startswith(".DS_Store"):
                continue
                
            image_path = os.path.join(images_dir, image)
            
            try:
                inputs = get_img_inputs(image_path)
                ori_height, ori_width = inputs[0]["height"], inputs[0]["width"]
                image_data = inputs[0]['image']
                image_data = image_data.astype("float32")
                
                outputs = session.run(['pred_boxes', 'labels', 'scores'], {
                    "image": image_data
                })
                
                height, width = image_data.shape[1:3]
                boxes = resize_boxes(outputs[0], (ori_width, ori_height), (width, height))
                tmp_labels = outputs[1]
                labels = [CLASS_MAPPING[label] for label in tmp_labels]
                scores = outputs[2]
                
                original_image = cv2.imread(image_path)
                content_count = 0
                
                for box, label, score in zip(boxes, labels, scores):
                    if score > 0.5 and label in ["Table", "Image"]:
                        x1, y1, x2, y2 = map(int, box)
                        content_image = original_image[y1:y2, x1:x2]
                        
                        title_box = find_title_for_content(boxes, labels, scores, box, label)
                        title = ""
                        if title_box is not None:
                            tx1, ty1, tx2, ty2 = map(int, title_box)
                            # 创建临时目录用于保存标题框图片

                            title_image = original_image[ty1:ty2, tx1:tx2]

                            # 保存标题图片到临时目录
                            title_image_path = os.path.join(tmp_dir, f"title_{content_count}.png")
                            cv2.imwrite(title_image_path, title_image)

                            try:
                                title = await vl_model(title_image_path, "提取图片中的文本内容，直接返回提取的结果，不要返回其他内容。")
                                title = title.replace("/", "")
                                print(title)
                                # 删除临时标题图片文件
                                os.remove(title_image_path)

                            except:
                                title = str(content_count)
                        
                        prefix = "table" if label == "Table" else "image"
                        output_filename = f"{prefix}_{title}.png"
                        output_path = os.path.join(tables_images_outdir, output_filename)
                        
                        cv2.imwrite(output_path, content_image)
                        content_count += 1
                        
                        if label == "Table":
                            extracted_tables += 1
                        else:
                            extracted_images += 1
                
                processed_images += 1
                
            except Exception as e:
                print(f"处理图片 {image} 时出错: {str(e)}")
                failed_images += 1
                continue
        # 删除tmp_dir目录
        if os.path.exists(tmp_dir):
            for file in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {str(e)}")
            try:
                os.rmdir(tmp_dir)
            except Exception as e:
                print(f"删除目录 {tmp_dir} 时出错: {str(e)}")

        return f"完成内容提取：成功处理 {processed_images} 张图片，提取 {extracted_tables} 个表格和 {extracted_images} 张图片，失败 {failed_images} 张。提取结果保存在 {tables_images_outdir} 目录下。"
        
    except Exception as e:
        raise Exception(f"内容提取过程中出错: {str(e)}")

async def ut():
    images_dir = "/Users/liubaoyang/Desktop/flowchart/pdf_page_images_path/"
    tables_images_outdir = "/Users/liubaoyang/Desktop/flowchart/extract_out/"
    result = await extract_tables_images_from_images(images_dir, tables_images_outdir)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(ut())
    