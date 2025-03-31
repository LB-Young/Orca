from graphviz import Source
from typing import Dict, Any, Iterator, Union
from .tool import Tool

class FlowChartTool(Tool):
    """流程图生成工具"""
    
    name = "flow_chart"  # 工具名称
    description = "根据Mermaid格式的字符串生成流程图"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "mermaid_string": {
            "type": "string",
            "description": "Mermaid格式的流程图字符串",
            "required": True
        },
        "output_path": {
            "type": "string",
            "description": "输出图片的保存路径",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "result": {
            "type": "string",
            "description": "流程图生成结果信息"
        }
    }
    
    # 工具属性
    properties = {}
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        # 异步运行方法实现
        return await self.run(inputs, properties)
    
    async def run(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Union[str, Any]:
        # 从输入中提取参数
        mermaid_string = inputs.get("mermaid_string", "")
        output_path = inputs.get("output_path", "")
        
        # 参数校验
        if not mermaid_string:
            raise Exception("Mermaid字符串不能为空")
        if not output_path:
            raise Exception("输出路径不能为空")
            
        try:
            output_path = eval(output_path)
        except:
            pass
        
        try:
            result = await self._generate_flow_chart(mermaid_string, output_path)
            return result
        except Exception as e:
            raise Exception(f"生成流程图失败: {str(e)}")
    
    async def _generate_flow_chart(self, mermaid_string, output_path):
        """根据Mermaid格式字符串生成流程图
        
        Args:
            mermaid_string: Mermaid格式的流程图字符串
            output_path: 输出图片的保存路径
            
        Returns:
            str: 流程图生成结果信息
        """
        map = {}
        # 首先构建完整的节点映射
        for line in mermaid_string.split("\n"):
            if "-->" in line:
                parts = line.strip().split('-->')
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    # 处理源节点
                    if "[" in source:
                        key = source.split("[")[0].strip()
                        map[key] = source
                    # 处理目标节点（需要先处理边标签）
                    if "|" in target:
                        target = target.split('|')[-1].strip()
                    if "[" in target:
                        key = target.split("[")[0].strip()
                        map[key] = target
                        
        # 提取mermaid代码部分
        if "```mermaid" in mermaid_string:
            mermaid_string = mermaid_string.split("```mermaid")[-1].split("```")[0].strip()
        if "graph TD" in mermaid_string:
            mermaid_string = mermaid_string.split("graph TD")[-1].strip()
            
        # 将mermaid格式转换为DOT格式
        dot_code = "digraph G {\n"
        dot_code += "    node [shape=box];\n"
        dot_code += "    graph [dpi=300];\n"
        
        # 处理每一行连接关系
        for line in mermaid_string.split('\n'):
            if '-->' in line:
                parts = line.strip().split('-->')
                if len(parts) == 2:
                    source = parts[0].strip()
                    if "[" not in source:
                        source = map.get(source, source)
                    target = parts[1].strip()
                    
                    # 处理边标签
                    edge_label = ""
                    if "|" in target:
                        edge_parts = target.split('|')
                        if len(edge_parts) >= 2:
                            edge_label = edge_parts[0].strip().strip('|')
                            target = edge_parts[-1].strip()
                    
                    if "[" not in target:
                        target = map.get(target, target)
                    
                    # 检查是否为图片节点
                    source_is_image = 'image:' in source
                    target_is_image = 'image:' in target
                    
                    # 提取节点ID
                    source_id = source.split('[')[0].strip()
                    target_id = target.split('[')[0].strip()
                    
                    # 处理源节点
                    if source_is_image:
                        image_path = source[source.find('image:')+6:].strip().strip('[]').strip('"')
                        dot_code += f'    {source_id} [image="{image_path}", label="", shape=none, imagescale=true];\n'
                    else:
                        source_label = source[source.find('[')+1:source.find(']')] if '[' in source else source
                        dot_code += f'    {source_id} [label="{source_label}"];\n'
                    
                    # 处理目标节点
                    if target_is_image:
                        image_path = target[target.find('image:')+6:].strip().strip('[]').strip('"')
                        dot_code += f'    {target_id} [image="{image_path}", label="", shape=none, imagescale=true];\n'
                    else:
                        target_label = target[target.find('[')+1:target.find(']')] if '[' in target else target
                        dot_code += f'    {target_id} [label="{target_label}"];\n'
                    
                    # 添加连接关系，如果有边标签则包含标签
                    if edge_label:
                        dot_code += f'    {source_id} -> {target_id} [label="{edge_label}"];\n'
                    else:
                        dot_code += f'    {source_id} -> {target_id};\n'
        
        dot_code += "}"
        
        # 使用graphviz渲染流程图
        s = Source(dot_code, filename=output_path.rsplit(".", 1)[0], format=output_path.split(".")[-1])
        s.render(cleanup=True)
        
        return f"流程图保存至：{output_path}" 