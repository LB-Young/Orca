# Orca

<div align="center">
  <img src="https://via.placeholder.com/200x200.png?text=Orca" alt="Orca Logo" width="200" height="200">
  <h3>一种新型的智能体语言，用于分解复杂任务</h3>
</div>

## 项目简介

Orca 是一种新型的智能体语言，专为分解复杂任务设计。它将完整任务分解为多步智能体操作，结合了 Ando 工作流的确定性和完全自主智能体的灵活性。使用自然语言描述的工作流可以适应不同复杂度的任务场景，提高智能体系统的鲁棒性并改善工作流的泛化能力。

## 主要特性

- **任务分解**：将复杂任务自动分解为多个可管理的步骤
- **工作流灵活性**：使用自然语言描述工作流，适应不同复杂度的任务
- **多工具集成**：内置丰富的工具集，包括网页搜索、PDF处理、视频分析等
- **多智能体协作**：支持多个智能体协同工作，各司其职
- **流式处理**：支持流式输出，提供实时反馈
- **可扩展性**：易于添加新工具和智能体

## 安装指南

### 环境要求

- Python >= 3.10

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/Orca.git
cd Orca
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 安装 Orca 包

```bash
pip install -e .
```

## 使用示例

### 使用 Orca 语言文件
```
python example/chat.py

python example/workflow.py
```

## Orca 语言示例

```
default_agent:False
variabes:
{}
orca:

@agent_init(system_prompt="需要分析用户问题，然后使用工具收集尽量多的网页信息，最后基于收集的信息回答用户问题。", tools=["browser_use"])->new_agent
@new_agent($query) -> answer
```

## 支持的工具

Orca 内置了丰富的工具集，包括但不限于：

- **网页搜索**：DuckDuckGo、Jina 等搜索引擎
- **学术研究**：Arxiv 论文搜索、Paper with Code 等
- **内容分析**：PDF 处理、图像分析、表格提取
- **多媒体处理**：YouTube 字幕提取、视频分析
- **数据可视化**：流程图生成、Mermaid 图表
- **通信工具**：邮件发送

## 项目结构

```
Orca/
├── src/                    # 源代码
│   ├── Orca/               # 核心代码
│   │   ├── agents/         # 智能体实现
│   │   ├── executor.py     # 执行器
│   │   ├── Orca.py         # 主类
│   │   └── ...
│   └── tools/              # 工具集
├── examples/               # 使用示例
│   ├── chat.py             # 聊天示例
│   ├── workflow.py         # 工作流示例
│   └── ...
├── docs/                   # 文档
├── tests/                  # 测试
├── requirements.txt        # 依赖列表
└── setup.py                # 安装脚本
```

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 报告问题和提出建议
- 提交代码改进
- 改进文档
- 添加新工具和功能

## 许可证

本项目采用 [LICENSE](LICENSE) 许可证。未经许可不得用于商业用途。

## 联系方式

- 作者：YoungL
- 邮箱：[lby15356@gmail.com](mailto:lby15356@gmail.com)
- GitHub：[https://github.com/LB-Young/Orca](https://github.com/LB-Young/Orca)