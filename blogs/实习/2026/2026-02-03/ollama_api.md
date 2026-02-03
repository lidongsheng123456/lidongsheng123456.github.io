---
title: ollama暴露的API
date: 2026-02-03
tags:
 - ollama
categories:
 - 实习
---

使用 `curl` 是测试本地 Ollama 接口最快的方式。以下是针对最常用 API 的具体指令示例：

> Base URL（本地默认）：`http://localhost:11434`  
> 说明：推理接口默认是流式（NDJSON），加 `"stream": false` 可一次性返回完整 JSON。

### 1. 基础文本生成 (`/api/generate`)

如果你只需要 AI 针对一个问题给出回答，使用这个接口。

```bash
curl http://localhost:11434/api/generate ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "deepseek-r1:7b",
  "prompt": "为什么天空是蓝色的？",
  "stream": false
}'

```

* **`stream: false`**: 一次性返回完整结果。如果设为 `true`（默认），你会看到一连串 JSON 数据块。

---

### 2. 对话补全 (`/api/chat`)

如果你想模拟类似 ChatGPT 的**多轮对话**，需要使用这个接口并传入消息历史。

```bash
curl http://localhost:11434/api/chat ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "llama3.2",
  "messages": [
    { "role": "user", "content": "你好，请记住我的名字叫小明。" },
    { "role": "assistant", "content": "你好小明！很高兴认识你。" },
    { "role": "user", "content": "我刚才说我叫什么？" }
  ],
  "stream": false
}'

```

---

### 3. 多模态视觉识别 (`/api/generate`)

对于支持 Vision 的模型（如 `llava`），你可以发送图片的 **Base64** 编码。

```bash
curl http://localhost:11434/api/generate ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "llava",
  "prompt": "这张图片里有什么？",
  "images": ["iVBORw0KGgoAAAANSUhEUgAA..."]
}'

```

> *注：`images` 参数是一个包含 Base64 字符串的数组。*

---

### 4. 获取本地模型列表 (`/api/tags`)

查看你电脑里已经下载了哪些模型。

```bash
curl http://localhost:11434/api/tags

```

---

### 5. 生成向量嵌入 (`/api/embed`)

用于 RAG 或语义搜索，将文字转为一串高维数组。

```bash
curl http://localhost:11434/api/embed ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "qwen3-embedding",
  "input": "机器学习是人工智能的一个子集"
}'

```

补充：历史上也见过 `POST /api/embeddings`，目前常见实现以 `/api/embed` 为主。

---

### 6. 查看当前运行中的模型 (`/api/ps`)

用于确认有哪些模型常驻在内存（以及占用情况）。

```bash
curl http://localhost:11434/api/ps
```

---

### 7. 查看某个模型的详细信息 (`/api/show`)

返回模型的元信息（参数、template、license 等）。

```bash
curl http://localhost:11434/api/show ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "llama3.2"
}'
```

---

### 8. 拉取模型 (`/api/pull`)

等价于 `ollama pull`，支持流式进度输出。

```bash
curl http://localhost:11434/api/pull ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "qwen3-embedding",
  "stream": false
}'
```

---

### 9. 删除模型 (`/api/delete`)

等价于 `ollama rm`。

```bash
curl -X DELETE http://localhost:11434/api/delete ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "llama3.2"
}'
```

---

### 10. 复制模型 (`/api/copy`)

把一个本地模型拷贝成新名字（例如做不同参数/提示词版本管理）。

```bash
curl http://localhost:11434/api/copy ^
  -H "Content-Type: application/json" ^
  -d '{
  "source": "llama3.2",
  "destination": "llama3.2-copy"
}'
```

---

### 11. 创建模型 (`/api/create`)

把 Modelfile + 基础模型组合成一个新模型（等价于 `ollama create`，通常用于自定义 system/template、附加文件等）。

```bash
curl http://localhost:11434/api/create ^
  -H "Content-Type: application/json" ^
  -d '{
  "name": "my-llama3.2",
  "modelfile": "FROM llama3.2\nSYSTEM 你是一个中文助手\n"
}'
```

---

### 12. 推送模型 (`/api/push`)

把本地模型推送到远端仓库（等价于 `ollama push`，一般配合鉴权/仓库权限）。

```bash
curl http://localhost:11434/api/push ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "my-llama3.2",
  "stream": false
}'
```

---

### 13. 查看版本 (`/api/version`)

```bash
curl http://localhost:11434/api/version
```

---

## OpenAI 兼容接口（`/v1/*`）

Ollama 提供 OpenAI 风格的兼容层，便于直接用 OpenAI SDK/工具链接入。

### 1) Chat Completions (`/v1/chat/completions`)

```bash
curl http://localhost:11434/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "llama3.2",
  "messages": [
    { "role": "user", "content": "用三句话解释什么是 RAG" }
  ]
}'
```

### 2) Embeddings (`/v1/embeddings`)

```bash
curl http://localhost:11434/v1/embeddings ^
  -H "Content-Type: application/json" ^
  -d '{
  "model": "qwen3-embedding",
  "input": "RAG 的核心是什么"
}'
```

### 3) Models (`/v1/models`)

```bash
curl http://localhost:11434/v1/models
```

---

参考：

- https://docs.ollama.com/api/introduction
- https://github.com/ollama/ollama/blob/main/docs/api.md
