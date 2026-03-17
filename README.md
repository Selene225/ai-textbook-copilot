AI 教材学习助手（AI Textbook Copilot）

一个基于 OCR + 向量检索 + 大模型（RAG）的智能学习工具，支持上传教材 PDF，实现自动解析与问答。

项目简介

本项目旨在解决教材学习中的信息获取效率问题。传统教材内容检索依赖人工查找，效率较低。本项目通过构建一个基于检索增强生成（RAG）的系统，使教材内容可以被语义理解和调用，实现“可对话教材”。

主要能力包括：

PDF 教材自动解析（支持扫描版）

文本语义向量化存储

基于语义的相关内容检索

结合上下文的大模型问答

Demo 展示

核心功能
教材解析（OCR）

使用 PaddleOCR 对 PDF 进行逐页解析，支持扫描版教材内容提取，并进行基础图像预处理以提高识别准确率。

知识库构建

使用 LangChain 进行文本切分

使用 text2vec-base-chinese 生成文本向量

使用 FAISS 构建本地向量索引库

智能问答（RAG）

用户输入问题后，系统流程如下：

将问题向量化

在向量数据库中检索 Top-K 相关文本

将检索结果作为上下文输入大模型

生成基于教材内容的回答

技术架构
PDF教材
   ↓
OCR识别（PaddleOCR）
   ↓
文本切分（LangChain）
   ↓
向量化（text2vec）
   ↓
向量数据库（FAISS）
   ↓
语义检索（Top-K）
   ↓
LLM生成回答（DeepSeek）
技术栈
模块	技术
前端	Streamlit
OCR	PaddleOCR
向量模型	text2vec-base-chinese
向量数据库	FAISS
大模型	DeepSeek API
文本处理	LangChain
安装与运行
克隆项目
git clone https://github.com/yourname/ai-textbook-copilot.git
cd ai-textbook-copilot
安装依赖
pip install -r requirements.txt
配置 API Key

Linux / Mac：

export DEEPSEEK_API_KEY=your_api_key

Windows：

set DEEPSEEK_API_KEY=your_api_key
运行项目
streamlit run app.py
使用说明

上传 PDF 教材

系统自动进行 OCR 解析并构建知识库

输入问题

获取基于教材内容的回答

项目亮点

支持扫描版教材（OCR）

本地向量数据库（FAISS）

基于 RAG 架构降低模型幻觉

针对中文优化的向量模型

后续优化方向

支持多教材联合检索

引入重排序模型（Rerank）提升检索精度

增加答案来源定位（引用原文）

UI 进一步产品化优化

增加自动摘要与知识点整理功能

项目说明

本项目用于探索大模型在学习场景中的应用，重点在于 RAG（Retrieval-Augmented Generation）技术的实现路径与效果。

License

MIT License