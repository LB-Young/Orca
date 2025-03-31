import os
import time
import numpy as np
import onnxruntime as ort
import cv2
import json
from typing import Dict, Any, Iterator, Union, List
from .tool import Tool
from .vl_model import VLModelTool

class ExtractTablesImagesFromImagesTool(Tool):
    """从图片中提取表格和图片工具"""
    
    name = "extract_tables_images_from_images"  # 工具名称
    description = "从图片中提取表格和图片内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "images_dir": {
            "type": "string",
            "description": "图片目录",
            "required": True
        },
        "tables_images_outdir": {
            "type": "string",
            "description": "提取的表格和图片保存目录",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "提取结果信息"
        }
    }
    
    # 工具属性
    properties = {}
    
    # 类别映射
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
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        images_dir = inputs.get("images_dir", "")
        tables_images_outdir = inputs.get("tables_images_outdir", "")
        
        # 参数校验
        if not images_dir:
            raise Exception("图片目录不能为空")
        if not tables_images_outdir:
            raise Exception("提取的表格和图片保存目录不能为空")
        
        if not os.path.exists(images_dir):
            raise Exception("图片目录不存在")
        
        try:
            result = await self._extract_contents(images_dir, tables_images_outdir)
            return result
        except Exception as e:
            raise Exception(f"从图片中提取表格和图片失败: {str(e)}")
    
    async def _extract_contents(self, images_dir, tables_images_outdir):
        """从图片中提取表格和图片
        
        Args:
            images_dir: 图片目录
            tables_images_outdir: 提取的表格和图片保存目录
            
        Returns:
            str: 提取结果信息
        """
        # 确保保存目录存在
        os.makedirs(tables_images_outdir, exist_ok=True)
        
        # 模型路径
        model_path = "/Users/liubaoyang/Documents/YoungL/models/jockerK/layoutlmv3-onnx/jockerK/layoutlmv3-onnx/quantize_model.onnx"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ONNX模型文件不存在: {model_path}")
        
        # 创建ONNX运行时会话
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        # 创建视觉语言模型工具实例
        vl_model_tool = VLModelTool()
        
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
                    # 准备输入数据
                    inputs = self._get_img_inputs(image_path)
                    ori_height, ori_width = inputs[0]["height"], inputs[0]["width"]
                    image_data = inputs[0]['image']
                    image_data = image_data.astype("float32")
                    
                    # 模型推理
                    outputs = session.run(['pred_boxes', 'labels', 'scores'], {
                        "image": image_data
                    })
                    
                    # 处理输出结果
                    height, width = image_data.shape[1:3]
                    boxes = self._resize_boxes(outputs[0], (ori_width, ori_height), (width, height))
                    tmp_labels = outputs[1]
                    labels = [self.CLASS_MAPPING[label] for label in tmp_labels]
                    scores = outputs[2]
                    
                    # 读取原始图像
                    original_image = cv2.imread(image_path)
                    content_count = 0
                    
                    # 处理每个检测到的内容框
                    for box, label, score in zip(boxes, labels, scores):
                        if score > 0.5 and label in ["Table", "Image"]:
                            x1, y1, x2, y2 = map(int, box)
                            content_image = original_image[y1:y2, x1:x2]
                            
                            # 查找对应的标题框
                            title_box = self._find_title_for_content(boxes, labels, scores, box, label)
                            title = ""
                            if title_box is not None:
                                tx1, ty1, tx2, ty2 = map(int, title_box)
                                title_image = original_image[ty1:ty2, tx1:tx2]

                                # 保存标题图片到临时目录
                                title_image_path = os.path.join(tmp_dir, f"title_{content_count}.png")
                                cv2.imwrite(title_image_path, title_image)

                                try:
                                    # 使用视觉语言模型提取标题文本
                                    vl_inputs = {
                                        "pic_path": title_image_path,
                                        "query": "提取图片中的文本内容，直接返回提取的结果，不要返回其他内容。"
                                    }
                                    title_result = await vl_model_tool.run(vl_inputs, {})
                                    title = title_result.replace("/", "")
                                    print(title)
                                    # 删除临时标题图片文件
                                    os.remove(title_image_path)
                                except:
                                    title = str(content_count)
                            
                            # 确定输出文件名前缀
                            prefix = "table" if label == "Table" else "image"
                            output_filename = f"{prefix}_{title}.png"
                            output_path = os.path.join(tables_images_outdir, output_filename)
                            
                            # 保存提取的内容
                            cv2.imwrite(output_path, content_image)
                            content_count += 1
                            
                            # 更新统计信息
                            if label == "Table":
                                extracted_tables += 1
                            else:
                                extracted_images += 1
                    
                    processed_images += 1
                    
                except Exception as e:
                    print(f"处理图片 {image} 时出错: {str(e)}")
                    failed_images += 1
                    continue
                    
            # 清理临时目录
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
    
    def _resize_boxes(self, boxes, old_size, new_size):
        """调整框的大小
        
        Args:
            boxes: 框坐标
            old_size: 原始尺寸
            new_size: 新尺寸
            
        Returns:
            numpy.ndarray: 调整后的框坐标
        """
        old_width, old_height = old_size
        new_width, new_height = new_size
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
    
    def _resize_image(self, image, min_size=800, max_size=1333):
        """调整图像大小
        
        Args:
            image: 图像
            min_size: 最小尺寸
            max_size: 最大尺寸
            
        Returns:
            numpy.ndarray: 调整后的图像
        """
        height, width = image.shape[:2]
        if height >= min_size and width >= min_size and width <= max_size and height <= max_size:
            return image
        else:
            # 计算缩放比例
            scale_w = min_size / width
            scale_h = min_size / height
            scale = min(scale_w, scale_h)
            if width * scale > max_size or height * scale > max_size:
                scale = max_size / max(width, height)
            # 缩放
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized_image = cv2.resize(image, (new_width, new_height))
        return resized_image
    
    def _get_img_inputs(self, sample_image, min_size=800, max_size=1333):
        """获取图像输入
        
        Args:
            sample_image: 图像路径
            min_size: 最小尺寸
            max_size: 最大尺寸
            
        Returns:
            list: 输入数据列表
        """
        original_image = cv2.imread(sample_image)
        height, width = original_image.shape[:2]
        image = self._resize_image(original_image, min_size, max_size)
        image = image.transpose(2, 0, 1)
        inputs = {"image": image, "height": height, "width": width}
        # 样本准备完成
        sample_inputs = [inputs]
        return sample_inputs
    
    def _find_title_for_content(self, boxes, labels, scores, content_box, content_type):
        """查找内容对应的标题框
        
        Args:
            boxes: 框坐标列表
            labels: 标签列表
            scores: 置信度分数列表
            content_box: 内容框坐标
            content_type: 内容类型
            
        Returns:
            numpy.ndarray: 标题框坐标，如果没有找到则返回None
        """
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
            # 如果水平方向上框不重叠则跳过
            if box[2] < content_box[0] or box[0] > content_box[2]:
                continue
            # 如果置信度大于0.5且标签匹配目标标题类型
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