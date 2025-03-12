from graphviz import Source


async def flow_chart(mermaid_string="", output_path="", params_format=False):
    if params_format:
        return ['mermaid_string']
    try:
        output_path = eval(output_path)
    except:
        pass
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
    # 创建完整的DOT格式图表代码
    mermaid_string = mermaid_string.split("graph TD")[-1].split("```")[0].strip()
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
                    source = map[source]
                target = parts[1].strip()
                
                # 处理边标签
                edge_label = ""
                if "|" in target:
                    edge_parts = target.split('|')
                    if len(edge_parts) >= 2:
                        edge_label = edge_parts[0].strip().strip('|')
                        target = edge_parts[-1].strip()
                
                if "[" not in target:
                    target = map[target]
                
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
    mermaid_code = dot_code
    
    # 使用graphviz渲染流程图
    s = Source(mermaid_code, filename=output_path.rsplit(".", 1)[0], format=output_path.split(".")[-1])
    s.render(cleanup=True)
    
    return f"流程图保存至：{output_path}"
    
    
async def ut():
    string = """
```mermaid
graph TD
A[高钙白钨矿选矿技术的流程] --> B[表2 原矿中钨化学物相分析结果]
B -->|黑钨矿中WO3含量0.019，分布率4.42%| C[白钨矿中WO3含量0.41，分布率95.35%]
C -->|钨华中WO3含量0.001，分布率0.23%| D[合计WO3含量0.43，分布率100.00%]

B --> table_2[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/table_表2原矿中钨化学物相分析结果.png"]

A --> E[试验方法、试验设备及药剂]
E --> F[选矿原设计流程：一粗一精两扫浮硫，浮硫尾矿经一粗一精一扫得到钨粗精矿，钨粗精矿经浓缩、“彼德洛夫法”高温解吸后一粗五精三扫精得到钨精矿产品]
F --> G[磨矿细度与钨、硫精矿品位与回收率关系（图2）]
G --> H[-0.075mm粒级占80%时WO3回收率达到82.83%，继续增加磨矿细度对提高钨回收率效果不显著；同时硫回收率随磨矿细度增加变化不大（仅71%左右）]

G --> image_2[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/image_图2磨矿细度与钨、硫精矿品位与回收率关系.png"]

A --> I[3.2 浮硫条件试验]
I --> J[3.2.1 浮硫调整剂试验]
J --> K[表3 脱硫调整剂种类试验结果]
K --> L[空白试验、只加碳酸钠或水玻璃或两者都加时，硫与银回收率均低于70%；硫酸作调整剂时硫回收率75.26%，且S品位最高(9.97%)；硫酸铜作调整剂时，硫回收率提高到81.95%；CN作调整剂时浮硫和银效果均较好，硫、银回收率分别达到88.84%和74.80%。选择CN作为浮硫调整剂，用量200g/t]

K --> table_3[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/table_表3脱硫调整剂种类试验结果.png"]

I --> M[3.2.2 浮硫起泡剂种类试验]
M --> N[表4 起泡剂种类试验结果]
N --> O[MIBC比松醇油的上浮产率降低了4.51个百分点，硫精矿提高了2.37个品位、银含量提高了33.35g/t，浮选效率较高。选择MIBC作为浮硫起泡剂]

N --> table_4[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/table_表4一起泡剂种类试验结果.png"]

A --> P[3.3 浮钨条件试验]
P --> Q[3.3.1 高效抑制剂种类及用量试验]
Q --> R[表5 浮钨抑制剂种类试验结果]
R --> S[FS作为浮钨抑制剂，精矿品位达到了1.78%，分选效率达到66.23%。选择FS作为浮钨抑制剂]

R --> table_5[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/table_表5浮钨抑制剂种类试验结果.png"]

P --> T[3.3.2 水玻璃用量试验]
T --> U[表7 浮钨水玻璃用量试验结果]
U --> V[水玻璃用量选择4000~4500g/t为宜，该条件下精矿富集比高]

U --> table_7[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/table_表7浮钨水玻璃用量试验结果.png"]

P --> W[3.3.3 捕收剂种类及用量试验]
W --> X[表8 浮钨捕收剂种类试验结果]
X --> Y[捕收剂CY-88*分选效果较好，精矿品位达到2.67%，回收率也比较理想]

X --> table_8[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/table_表8浮钨捕收剂种类试验结果.png"]

A --> Z[3.4 闭路试验]
Z --> AA[图3 脱硫浮钨粗选段闭路试验质量流程]
AA --> AB[粗选段采用一粗二精一扫浮硫可以得到硫精矿产率5.27%S品位21.87%的硫精矿（银含量244g/t），硫回收率90.17%（银回收率69.20%），钨在硫精矿中损失1.72%；一粗二精二扫浮钨闭路试验可得到产率12.97%WO3品位2.96%的钨粗精矿，钨回收率89.25%]

AA --> image_3[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/image_图3脱硫浮铜粗选段闭路试验数质量流程.png"]

Z --> AC[图4 钨精选段闭路试验质量流程]
AC --> AD[钨粗精矿高温解吸后，经过一粗四精三扫闭路试验可以得到产率0.51%WO3品位65.56%的钨精矿产品，回收率77.98%；精选段尾矿WO3品位0.39%，钨损失率11.27%]

AC --> image_4[image: "/Users/liubaoyang/Desktop/flowchart/extract_out/image_图4钨精选段闭路试验数质量流程.png"]
```
"""
    out_path = "'res.jpg'"
    res = await flow_chart(mermaid_string=string, output_path=out_path)
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(ut())