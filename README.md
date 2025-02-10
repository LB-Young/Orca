# Orca
Orca is a new agent language designed to decompose a complete task into multi-step agent actions. It combines the certainty of Ando workflow with the flexibility of a fully autonomous agent. The description of workflow in natural language can be adapted to the scenarios of tasks of different complexity, which increases the robustness of the agent system and improves the generalization of workflow.


在#Folder:backend文件夹下为Orca项目构建一个后端服务。构建的服务为对话形式，Orca项目的对话调用实例如，后端服务需要处理返回的message信息，并把message信息返回给前段服务。Orca返回的其他信息需要后端服务自己维护，当用户在当前会话下提出新的问题时，需要将新问题添加到会话message中请求Orca。如果用户开启了新的会话，则直接初始化参数并传递用户问题。

构建一个前端界面，如图所示，代码保存在frontend文件夹下。
用户启动前端服务会自动打开当前页面。页面初始状态默认任务下拉列表未选择任何内容。用户可以点击下拉列表选择对应任务，选择任务之后在下方的参数框中，由用户自行配置json参数，配置完成之后用户可以在问题输入框中输入问题，点击发送按钮之后，用户的问题会显示到对话框中，并等待返回结果。点击发送按钮时需要将配置的任务、参数、用户问题一起发送给后端服务，并且需要包括一个参数first_query标记当前问题是否为当前会话的第一个问题。后端服务会以流式的方式返回结果，前段需要以流式进行展示。