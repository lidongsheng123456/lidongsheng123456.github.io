import os
import requests
from pathlib import Path
from typing import List
import ollama
from langchain_chroma import Chroma

# --- 1. Ollama 嵌入类（必须与入库时一致） ---
class OllamaTextEmbeddings:
    def __init__(self, model: str):
        self.model = model

    def embed_query(self, text: str) -> List[float]:
        resp = ollama.embed(model=self.model, input=text)
        # 兼容处理返回的向量格式
        return resp.embeddings[0] if isinstance(resp.embeddings[0], list) else resp.embeddings

# --- 2. 配置 ---
LONGCAT_URL = "https://api.longcat.chat/openai/v1/chat/completions"
LONGCAT_API_KEY = "ak_10U5lH1mi4407FY5l61Jc4kE47H3f" 

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "vector_db_ollama"

# 使用 qwen3-embedding
embedding_model = OllamaTextEmbeddings(model="qwen3-embedding")

vectorstore = Chroma(
    persist_directory=str(DB_PATH),
    embedding_function=embedding_model
)

def call_longcat_llm(context: str, question: str):
    # 此处逻辑保持不变，依然调用 LongCat 或可根据需要改为调用 Ollama 的 Llama/Qwen 模型
    headers = {"Authorization": f"Bearer {LONGCAT_API_KEY}", "Content-Type": "application/json"}
    prompt = f"你是一个专业的博客助手。请根据提供的参考内容回答问题。\n\n参考内容：{context}\n\n问题：{question}"
    data = {
        "model": "LongCat-Flash-Chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    try:
        response = requests.post(LONGCAT_URL, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"LLM 调用失败: {e}"

def ask_blog(question: str):
    print(f"\n🔍 正在使用 Ollama 模型检索信息...")
    results = vectorstore.similarity_search(question, k=3)

    context_text = ""
    related_images = []

    for doc in results:
        if doc.metadata.get("type") == "text":
            context_text += f"\n[来源: {doc.metadata['source']}]\n{doc.page_content}\n"
        elif doc.metadata.get("type") == "image":
            related_images.append(doc.metadata['source'])

    print(f"🤖 正在组织语言...")
    answer = call_longcat_llm(context_text, question)

    print("\n✨ 回答：\n", answer)
    if related_images:
        print("\n🖼️  相关图片参考：")
        for img in related_images: print(f"- {BASE_DIR / img}")

if __name__ == "__main__":
    query = input("\n请输入问题: ")
    ask_blog(query)