# PriAs
一个基于检索增强生成技术的大模型私人助理
## 项目开发计划
基础功能：
- [ ] Q&A
  - [x] 检索增强生成
  - [x] 添加聊天记录上下文逻辑
  - [x] 聊天记录持久化存储 - 基于redis ？ 主题编号问题未解决（mysql数据库）
  - [ ] 分库QA
  - [ ] 引用参考数据源
- [ ] load
  - [x] web
  - [ ] pdf
  - [ ] html
  - [x] markdown
  - [ ] csv
  - [ ] json
- [ ] llm
  - [x] gpt-3.5
  - [x] 百度千帆大模型
- [ ] 知识库 - 基于Chroma （mysql）
  - [x] 初始化知识库
  - [x] 知识存储持久化
  - [x] 知识库更新
  - [ ] 新建知识库
  - [ ] 知识库分库
- [ ] 前端
  - [x] 前端界面基本框架搭建
  - [x] 根据选择显示或隐藏新建数据库输入框？新建数据库重名问题未解决（mysql数据库）
  - [ ] 聊天记录前端叠加显示
  - [ ] 选中知识库后直接显示当前知识库已有文件
  - [ ] 提问界面左侧下方显示之前的提问主题及记录
- [ ] 发布
  - [ ] docker沙箱化

扩展功能(多模态)：
- [ ] 文本、图像、音频、视频互相搜索
- [ ] 接入图、文、视频生成

问题：
知识存储持久化问题
聊天记录存储持久化问题
嵌入维度问题