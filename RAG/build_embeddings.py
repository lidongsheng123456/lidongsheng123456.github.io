import os
from pathlib import Path
from typing import List
import ollama  # 引入 ollama 库
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# --- 1. 定义 Ollama 嵌入类 ---
class OllamaTextEmbeddings:
    def __init__(self, model: str):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量处理文本嵌入"""
        # 调用 ollama.embed 接口
        resp = ollama.embed(model=self.model, input=texts)
        return resp.embeddings

    def embed_query(self, text: str) -> List[float]:
        """处理单条查询嵌入"""
        resp = ollama.embed(model=self.model, input=text)
        return resp.embeddings[0] if isinstance(resp.embeddings[0], list) else resp.embeddings

# --- 2. 配置与初始化 ---
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIRS = [BASE_DIR / "blogs", BASE_DIR / "docs"]
DB_PATH = BASE_DIR / "vector_db_ollama" # 建议更换路径以区分原多模态库
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

# 使用用户指定的 qwen3-embedding 模型
embedding_model = OllamaTextEmbeddings(model="qwen3-embedding")
header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")])
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

texts, metadatas = [], []

print("🚀 开始本地 Ollama 知识库构建...")

# --- 3. 扫描并处理文档 ---
for source_dir in SOURCE_DIRS:
    if not source_dir.exists(): continue
    for file_path in source_dir.rglob("*"):
        try:
            rel_path = str(file_path.relative_to(BASE_DIR))

            # 情况 A: 处理图片 (注意：qwen3-embedding 不支持图片向量化，此处仅存入路径信息)
            if file_path.suffix.lower() in IMAGE_EXTENSIONS:
                print(f"  🖼️  记录图片路径 (跳过向量化): {rel_path}")
                # 由于模型限制，我们不为图片生成向量，或者你可以选择存入文件名作为文本进行向量化
                texts.append(f"Image reference: {file_path.name}") 
                metadatas.append({"source": rel_path, "type": "image"})

            # 情况 B: 处理 Markdown
            elif file_path.suffix.lower() == ".md":
                print(f"  📄 处理文档: {rel_path}")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                header_splits = header_splitter.split_text(content)
                chunks = text_splitter.split_documents(header_splits)

                for chunk in chunks:
                    texts.append(chunk.page_content)
                    meta = chunk.metadata.copy()
                    meta.update({"source": rel_path, "type": "text"})
                    metadatas.append(meta)

        except Exception as e:
            print(f"  ❌ 出错 {file_path.name}: {e}")

# --- 4. 存入数据库 ---
if texts:
    print(f"\n📦 正在存入本地 ChromaDB (共 {len(texts)} 个知识点)...")
    # 让 Chroma 内部调用 embedding_model 的 embed_documents
    vectorstore = Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embedding_model,
        persist_directory=str(DB_PATH)
    )
    print(f"✨ Ollama RAG 知识库构建完成！")