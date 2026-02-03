# RAG 启动方式

在本目录执行：

```bash
uv venv --python 3.12
uv sync
ollama pull qwen3-embedding
```

构建向量库（首次运行或更新笔记后执行）：

```bash
uv run build_embeddings.py
```

启动查询：

```bash
uv run query_rag.py
```
