# architecture_codes_optm

建筑设计标准规范与地区自定义条例的检索查询

## 项目简介

本项目是一个基于 RAG（检索增强生成）技术的建筑设计规范查询工具

- **核心痛点** : 建筑设计规范繁杂、地区条例各异、规范不定期更新、抽屉文件等所导致的前期查找消耗大、后期修改成本高、不同地域隐藏条款坑点多等问题。
- **设计思路** : 支持用户上传建筑标准规范文档，及自定义地方隐藏规范条款文件，通过AI智能问答系统快速检索和解答相关问题。达到尽量快速、全面掌握地方规范要求的作用。
- **文档支持** : 目前支持上传word\pdf格式。针对常见扫描版pdf文件，支持OCR识别。

功能持续优化中

## 核心功能

- **多格式文件上传**：支持 TXT、PDF（含扫描版）、DOC、DOCX 格式文档
- **智能文件解析**：自动识别文本内容，扫描版 PDF 支持 OCR 识别
- **向量知识库**：基于 ChromaDB 的向量存储，支持高效的语义检索
- **AI 智能问答**：基于通义千问大模型，提供专业、准确的规范解答
- **对话历史记录**：保存用户对话历史，支持上下文连续对话
- **文件管理**：支持查看已上传文件、打开文件、删除文件等操作

## 技术栈

- **前端框架**：Streamlit
- **RAG 框架**：LangChain
- **向量数据库**：ChromaDB
- **大语言模型**：阿里云通义千问（qwen3-max）
- **嵌入模型**：阿里云 text-embedding-v4
- **OCR 识别**：EasyOCR
- **文档处理**：PyMuPDF (fitz)、python-docx

## 项目结构

```
architecture_codes_optm/
├── app_qa.py              # Streamlit 主应用
├── rag.py                 # RAG 服务核心逻辑
├── knowledge_base.py      # 知识库管理服务
├── vector_stores.py       # 向量检索服务
├── file_parser.py         # 文件解析器
├── file_history_store.py  # 对话历史存储
├── config_data.py         # 配置文件
├── requirements.txt       # 依赖包列表
└── README.md             # 项目说明文档
```

## 安装部署

### 环境要求

- 建议使用 Python 3.11 版本运行
- 确保已在环境变量中配置阿里云 DASHSCOPE_API_KEY

启动应用
```bash
streamlit run app_qa.py
```

## 使用说明

### 上传文档

1. 点击文件上传区域，选择要上传的规范文件
2. 支持的文件格式：TXT、PDF、DOC、DOCX
3. 系统会自动解析文件内容并载入知识库

### 智能问答

1. 在底部输入框输入问题
2. AI 会基于上传的规范文档进行检索和回答
3. 支持连续对话，系统会记住上下文

### 文件管理

- 在侧边栏查看已上传的文件列表
- 点击"打开文件"按钮查看原始文件
- 点击"删除"按钮从知识库中移除文件

## 配置说明

主要配置项位于 `config_data.py` 文件中：

## 依赖包

详见 `requirements.txt` 文件：

- python==3.11.15
- easyocr==1.7.2
- fitz==0.0.1.dev2
- langchain_chroma==1.1.0
- langchain_community==0.4.1
- langchain_core==1.4.0
- langchain_text_splitters==1.1.2
- numpy==2.4.4
- Pillow==12.2.0
- python_docx==1.2.0
- streamlit==1.55.0

## 注意事项

- 首次运行会自动创建必要的目录和数据库
- 扫描版 PDF 的 OCR 识别可能需要较长时间
- 建议上传清晰的规范文档以获得更好的检索效果
- 请确保网络连接正常，需要访问阿里云 API

## 未竟

- 功能持续优化中
