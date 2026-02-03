---
title: 从零实现本地 RAG 博客助手（Ollama + Chroma）的深度代码拆解
date: 2026-02-03
tags:
 - RAG
 - Python
 - 向量数据库
categories:
 - 实习
---

# 从零实现本地 RAG 博客助手（Ollama + Chroma）的深度代码拆解

🌱 **前言**：昨天初步跑通了 RAG，今天把整个流程的代码实现细节复盘一遍。核心目标是把工作区里的 `blogs/`、`docs/` 笔记转成可检索的“外挂大脑”，并用 **本地 Ollama** 的 `qwen3-embedding` 做向量化，落盘到 **ChromaDB**。

说明：当前实现以“文本检索”为主。图片不会做真正的多模态向量化（`qwen3-embedding` 不支持图像输入），但会把图片作为“引用条目”写入库里，便于回答时输出相关图片路径供你打开查看。

---

## 🏗️ 步骤一：文档加载与元数据提取 (Loading)

为了处理 `blogs/` 和 `docs/` 目录下的笔记，我们不能只把内容塞进向量库，还要保留文件路径、标题层级等元数据，方便回答时“溯源”。

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIRS = [BASE_DIR / "blogs", BASE_DIR / "docs"]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

for source_dir in SOURCE_DIRS:
    for file_path in source_dir.rglob("*"):
        rel_path = str(file_path.relative_to(BASE_DIR))
        if file_path.suffix.lower() in IMAGE_EXTENSIONS:
            texts.append(f"Image reference: {file_path.name}")
            metadatas.append({"source": rel_path, "type": "image"})
        elif file_path.suffix.lower() == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 继续走“切分 -> 入库”的流程

```

---

## 🔪 步骤二：逻辑切分 (Smart Splitting)
直接按字符切分容易把一段代码块或一个小节切碎。这里采用 **Markdown 标题层级切分 + 超长段落二次微切** 的混合策略：

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# 1. 按照 Markdown 标题层级切分，保留 H1 和 H2 的语义
headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

# 2. 对超长段落进行二次微切
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

def get_chunks(raw_text, path):
    # 逻辑切分
    header_splits = header_splitter.split_text(raw_text)
    # 微切分并注入元数据
    final_chunks = text_splitter.split_documents(header_splits)
    for chunk in final_chunks:
        chunk.metadata["source"] = path
        chunk.metadata["type"] = "text"
    return final_chunks

```

---
## 🧠 步骤三：向量化 (Embedding)

向量化用的是 **本地 Ollama** 的 `qwen3-embedding`。为了让 Chroma 能直接调用嵌入能力，这里封装一个最小 Embeddings 类，提供 `embed_documents` / `embed_query` 两个方法（入库和查询必须一致）。

```python
import ollama

class OllamaTextEmbeddings:
    def __init__(self, model: str):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        resp = ollama.embed(model=self.model, input=texts)
        return resp.embeddings

    def embed_query(self, text: str) -> list[float]:
        resp = ollama.embed(model=self.model, input=text)
        return resp.embeddings[0] if isinstance(resp.embeddings[0], list) else resp.embeddings
```

---

## 📦 步骤四：向量存储 (Vector Storage)
使用 **ChromaDB** 进行本地持久化存储，数据落在工作区根目录的 `vector_db_ollama/`。这里不手动传 embeddings，而是让 Chroma 在内部批量调用 `embed_documents`。

```python
from langchain_chroma import Chroma

DB_PATH = BASE_DIR / "vector_db_ollama"

vectorstore = Chroma.from_texts(
    texts=texts,
    metadatas=metadatas,
    embedding=embedding_model,
    persist_directory=str(DB_PATH)
)

```

---

## 🔍 步骤五：检索与长文本对话 (Retrieval & LLM)
当用户提问（例如 “Nginx 404 怎么解？”）时，系统先从 Chroma 检索最相关的 `k=3` 条记录，拼成“参考内容”，再交给 **LongCat** 组织成最终回答；如果召回里包含图片条目，会在回答后输出图片路径，方便你打开查看。

```python
results = vectorstore.similarity_search(question, k=3)

context_text = ""
related_images = []

for doc in results:
    if doc.metadata.get("type") == "text":
        context_text += f"\n[来源: {doc.metadata['source']}]\n{doc.page_content}\n"
    elif doc.metadata.get("type") == "image":
        related_images.append(doc.metadata["source"])

answer = call_longcat_llm(context_text, question)
```

---

## 📊 总结：RAG 流程全景图

| 环节 | 关键技术 | 作用 |
| --- | --- | --- |
| **数据源** | Markdown + 图片文件 | 原始知识资产（图片仅做“引用条目”） |
| **切分器** | MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter | 结构化切分 + 超长段落兜底 |
| **嵌入** | Ollama `qwen3-embedding` | 本地生成文本向量（入库/查询一致） |
| **向量库** | ChromaDB（本地持久化） | 保存 chunks、元数据与向量 |
| **对话** | LongCat-Flash-Chat | 将检索结果组织成答案 |

---

💻 **代码如诗 | 每日进步 1%**

