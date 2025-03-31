import os
import time
import numpy as np
import onnxruntime as ort
import cv2
import json
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class ImagesLayoutAnalysisTool(Tool):
    """图像布局分析工具"""
    
    name = "images_layout_analysis"  # 工具名称
    description = "分析图片布局，识别图片中的标题、正文、表格等元素"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "images_dir": {
            "type": "string",
            "description": "图片目录",
            "required": True
        },
        "layout_save_dir": {
            "type": "string",
            "description": "布局分析结果保存目录",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "布局分析结果信息"
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
        layout_save_dir = inputs.get("layout_save_dir", "")
        
        # 参数校验
        if not images_dir:
            raise Exception("图片目录不能为空")
        if not layout_save_dir:
            raise Exception("布局分析结果保存目录不能为空")
        
        if not os.path.exists(images_dir):
            raise Exception("图片目录不存在")
        
        try:
            result = await self._analyze_layout(images_dir, layout_save_dir)
            return result
        except Exception as e:
            raise Exception(f"分析图片布局失败: {str(e)}")
    
    async def _analyze_layout(self, images_dir, layout_save_dir):
        """分析图片布局
        
        Args:
            images_dir: 图片目录
            layout_save_dir: 布局分析结果保存目录
            
        Returns:
            str: 布局分析结果信息
        """
        # 确保保存目录存在
        os.makedirs(layout_save_dir, exist_ok=True)
        
        # 模型路径
        model_path = "/Users/liubaoyang/Documents/YoungL/models/jockerK/layoutlmv3-onnx/jockerK/layoutlmv3-onnx/quantize_model.onnx"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ONNX模型文件不存在: {model_path}")
        
        # 创建ONNX运行时会话
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        processed_images = 0
        failed_images = 0
        
        try:
            for image in os.listdir(images_dir):
                if image.startswith(".DS_Store"):
                    continue
                    
                image_path = os.path.join(images_dir, image)
                output_path = os.path.join(layout_save_dir, f"layout_{image}")
                
                try:
                    # 准备输入数据
                    inputs = self._get_img_inputs(image_path)
                    ori_height, ori_width = inputs[0]["height"], inputs[0]["width"]
                    image_data = inputs[0]['image']
                    image_data = image_data.astype("float32")
                    
                    # 模型推理
                    start = time.time()
                    outputs = session.run(['pred_boxes', 'labels', 'scores'], {
                        "image": image_data
                    })
                    end = time.time()
                    
                    # 处理输出结果
                    height, width = image_data.shape[1:3]
                    boxes = self._resize_boxes(outputs[0], (ori_width, ori_height), (width, height))
                    tmp_labels = outputs[1]
                    labels = [self.CLASS_MAPPING[label] for label in tmp_labels]
                    scores = outputs[2]
                    
                    # 可视化结果
                    original_image = cv2.imread(image_path)
                    color = (0, 255, 0)  # 绿色
                    thickness = 2
                    for box, label, score in zip(boxes, labels, scores):
                        if score > 0.5:  # 只处理置信度大于0.5的检测结果
                            x1, y1, x2, y2 = map(int, box)
                            cv2.rectangle(original_image, (x1, y1), (x2, y2), color, thickness)
                            
                            # 添加标签和置信度文本
                            label_text = f"Class: {label}, Score: {score:.2f}"
                            cv2.putText(original_image, label_text, (x1, y1-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
                    
                    # 保存结果图像
                    cv2.imwrite(output_path, original_image)
                    processed_images += 1
                    
                    # 保存预测数据到layout_save_dir文件夹下的json文件中
                    layout_data = {
                        'image_name': image,
                        'predictions': [
                            {
                                'box': box.tolist(),
                                'label': label,
                                'score': float(score)
                            }
                            for box, label, score in zip(boxes, labels, scores)
                            if score > 0.5
                        ]
                    }
                    file_name = image.rsplit(".", 1)[0] + ".json"
                    json_path = os.path.join(layout_save_dir, file_name)
                        
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(layout_data, f, ensure_ascii=False, indent=4)

                except Exception as e:
                    print(f"处理图片 {image} 时出错: {str(e)}")
                    failed_images += 1
                    continue
            
            return f"完成布局分析：成功处理 {processed_images} 张图片，失败 {failed_images} 张。分析结果保存在 {layout_save_dir} 目录下。"
            
        except Exception as e:
            raise Exception(f"布局分析过程中出错: {str(e)}")
    
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