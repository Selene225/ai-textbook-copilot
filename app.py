import os
import gc
import tempfile

import streamlit as st
import cv2
import numpy as np
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss

from openai import OpenAI


# ===============================
# 页面设置
# ===============================
st.set_page_config(page_title="AI教材学习助手", layout="wide")
st.title("AI教材学习助手")


# ===============================
# API KEY
# ===============================
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ===============================
# OCR初始化
# ===============================
@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=True, lang="ch")

ocr = load_ocr()


# ===============================
# 向量模型
# ===============================
@st.cache_resource
def load_embedding():
    return SentenceTransformer("shibing624/text2vec-base-chinese")

embed_model = load_embedding()


# ===============================
# OCR PDF
# ===============================
def ocr_pdf(pdf_path, progress_bar):

    texts = []
    page_count = 0

    images = convert_from_path(
        pdf_path,
        dpi=150,
        poppler_path=r"D:\poppler\poppler-23.11.0\Library\bin"
    )

    total_pages = len(images)

    for i, img in enumerate(images):

        progress_bar.progress((i + 1) / total_pages)

        img = np.array(img)

        # RGB转BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # 自动缩放大图
        h, w = img.shape[:2]

        if w > 2000:
            scale = 2000 / w
            img = cv2.resize(img, (int(w * scale), int(h * scale)))

        result = ocr.ocr(img)

        page_text = ""

        if result:
            for line in result[0]:
                page_text += line[1][0] + "\n"

        texts.append(page_text)

        page_count += 1

        # 释放内存
        del img
        gc.collect()

    return texts


# ===============================
# 构建向量数据库
# ===============================
def build_vector_store(texts):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.create_documents(texts)

    corpus = [doc.page_content for doc in docs]

    embeddings = embed_model.encode(corpus)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))

    return index, corpus


# ===============================
# 检索
# ===============================
def search(query, index, corpus):

    q_emb = embed_model.encode([query])

    D, I = index.search(np.array(q_emb), 3)

    results = []

    for idx in I[0]:
        results.append(corpus[idx])

    return "\n".join(results)


# ===============================
# AI回答
# ===============================
def ask_llm(context, question):

    prompt = f"""
你是一个教材学习助手，请根据教材内容回答问题。

教材内容：
{context}

问题：
{question}

请根据教材内容回答。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# ===============================
# 左侧上传
# ===============================
st.sidebar.header("课程设置")

course = st.sidebar.text_input("课程名称")

uploaded_file = st.sidebar.file_uploader(
    "上传教材",
    type=["pdf"]
)


# ===============================
# 主流程
# ===============================
if uploaded_file:

    if "vector_store" not in st.session_state:

        st.info("第一次解析教材，正在OCR，请耐心等待...")

        progress = st.progress(0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        texts = ocr_pdf(pdf_path, progress)

        st.success("OCR完成，正在构建知识库...")

        index, corpus = build_vector_store(texts)

        st.session_state.vector_store = index
        st.session_state.corpus = corpus

        st.success("教材知识库构建完成！")


# ===============================
# 提问
# ===============================
if "vector_store" in st.session_state:

    question = st.text_input("请输入你的问题")

    if question:

        with st.spinner("思考中..."):

            context = search(
                question,
                st.session_state.vector_store,
                st.session_state.corpus
            )

            answer = ask_llm(context, question)

        st.markdown("### AI回答")
        st.write(answer)