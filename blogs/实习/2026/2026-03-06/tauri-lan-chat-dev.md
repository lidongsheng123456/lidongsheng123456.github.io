---
title: Tauri + React + DeepSeek AI 打造内网智能聊天工具 LanChat
date: 2026-03-06
tags:
 - tauri
 - rust
 - react
 - deepseek
 - ai
 - mcp
 - websocket
 - 内网聊天
categories:
 - 实习
---

记录使用 Tauri 2 + React 19 + Rust + DeepSeek AI 开发内网智能聊天工具 **LanChat v2.0** 的完整过程。重点分享 AI 工具调用系统、MCP 协议服务、分层架构设计中的实现细节与踩坑经验。

## 1. 项目背景

公司内网环境下需要一个轻量级的局域网通讯工具，核心诉求：

- 不依赖外网，局域网内直连通信
- 不经过任何第三方服务器，消息完全私密
- 支持图片、视频、任意文件的高速传输
- **内置 AI 助手**，能浏览网页、操作文件、辅助编码

最终技术栈：

| 层级 | 技术 | 说明 |
|------|------|------|
| 桌面框架 | Tauri 2 | Rust 后端 + WebView 前端，包体约 8MB |
| 前端 | React 19 + TypeScript | Vite 构建，原生 CSS 设计系统 |
| 后端服务 | Rust + warp | 内嵌 HTTP + WebSocket + MCP 三合一服务 |
| AI | DeepSeek API | Function Calling 多轮工具调用 |
| MCP | JSON-RPC 2.0 + SSE | 标准化 AI 工具接口协议 |

## 2. 架构设计

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      LanChat v2.0                            │
│                                                              │
│  ┌─────────────────┐       ┌─────────────────────────────┐  │
│  │  React 19 前端   │◄─────►│  Tauri 2 (Rust) 后端        │  │
│  │  TypeScript      │       │                             │  │
│  │                  │       │  commands/    ← Controller   │  │
│  │  components/     │       │   ai_cmd / file / network   │  │
│  │  hooks/          │       │                             │  │
│  │  styles/         │       │  services/    ← Service     │  │
│  │  config.ts       │       │   ai/    chat_service       │  │
│  │                  │       │          tool_registry      │  │
│  │                  │       │          utility_tools       │  │
│  │                  │       │   web/   scraper / search   │  │
│  │                  │       │   file/  download / tools   │  │
│  │                  │       │   mcp_server                │  │
│  │                  │       │   network_service           │  │
│  │                  │       │                             │  │
│  │                  │       │  models/      ← Model       │  │
│  │                  │       │  server/      ← Infra       │  │
│  │                  │       │  utils/       ← Utils       │  │
│  │                  │       │  config.rs    ← Config      │  │
│  └─────────────────┘       └─────────────────────────────┘  │
└──────┬──────────────────────────────┬───────────────────┬────┘
       │ WebSocket + HTTP            │ JSON-RPC 2.0      │
       ▼                             ▼                   ▼
┌──────────────┐            ┌──────────────┐    ┌──────────────┐
│  局域网 LAN   │            │  MCP Server  │    │  DeepSeek AI │
│  :9120       │            │  :9121       │    │  (外网 API)   │
└──────────────┘            └──────────────┘    └──────────────┘
```

Tauri 启动时在后台同时启动两个服务：
- **聊天服务** (:9120)：warp HTTP + WebSocket，处理消息收发和文件传输
- **MCP 服务** (:9121)：JSON-RPC 2.0 over HTTP + SSE，暴露 AI 工具接口

### 2.2 后端分层（Java 解耦思想）

借鉴 Java 的 Controller / Service / Model 分层，对 Rust 后端做了严格解耦：

| 层级 | 目录 | 职责 | 规则 |
|------|------|------|------|
| Controller | `commands/` | Tauri IPC 命令 | 纯委托，不含业务逻辑 |
| Service | `services/ai/` | AI 对话、工具注册与调度 | 按业务领域分组 |
| | `services/web/` | 网页抓取、搜索引擎 | |
| | `services/file/` | 文件下载、文件系统 CRUD | |
| Model | `models/` | 数据结构定义 | 不引用 Service 层 |
| Infra | `server/` | HTTP / WebSocket 路由和处理器 | |
| Config | `config.rs` | 统一配置加载 | |

严格约束：**所有源文件 < 300 行**，最大文件 220 行。

## 3. AI 工具调用系统

这是整个项目的核心亮点，也是开发工作量最大的部分。

### 3.1 DeepSeek Function Calling

DeepSeek API 兼容 OpenAI 的 Function Calling 协议。核心流程：

```
用户消息 → 携带 tools 定义发送给 AI
         → AI 返回 tool_calls（要调用哪个工具、什么参数）
         → Rust 后端执行工具，拿到结果
         → 将结果作为 tool message 追加到对话
         → 再次发送给 AI（AI 根据结果决定继续调工具还是回复用户）
         → 最多循环 5 轮
```

Rust 端实现的核心循环：

```rust
pub async fn chat_with_tools(api_key: &str, messages: Vec<AiChatMessage>) -> Result<String, String> {
    let client = build_http_client()?;
    let tools = tool_registry::build_tool_definitions();
    let mut conversation = messages;

    for _round in 0..config::get().ai.max_tool_rounds {
        let ai_resp = call_ai_api(&client, api_key, &conversation, Some(&tools)).await?;
        let choice = ai_resp.choices.first().ok_or("No response")?;

        if let Some(tool_calls) = &choice.message.tool_calls {
            // AI 要求调用工具
            conversation.push(/* assistant message with tool_calls */);
            for tc in tool_calls {
                let result = tool_registry::execute_tool(&tc.function.name, args).await;
                conversation.push(AiChatMessage::tool_result(&tc.id, &tc.function.name, &result));
            }
        } else {
            // AI 直接返回文本回复
            return Ok(choice.message.content.clone().unwrap_or_default());
        }
    }
    // 超过最大轮次，不带 tools 做最终总结
    let final_resp = call_ai_api(&client, api_key, &conversation, None).await?;
    Ok(final_resp.choices.first().and_then(|c| c.message.content.clone()).unwrap_or_default())
}
```

### 3.2 工具注册表（tool_registry）

所有 14 个工具的定义和执行调度集中在 `tool_registry.rs`，同时为 AI Service 和 MCP Server 提供统一接口，避免代码重复：

```rust
fn all_tools() -> Vec<(&'static str, &'static str, Value)> {
    vec![
        ("browse_website", "抓取并解析网页内容", json!({...})),
        ("web_search", "搜索互联网", json!({...})),
        ("read_file", "读取文件文本内容", json!({...})),
        ("write_file", "创建或覆盖写入文件", json!({...})),
        // ... 共 14 个工具
    ]
}

pub async fn execute_tool(name: &str, args: Value) -> String {
    match name {
        "browse_website" => web_scraper::browse_website(&a.url).await,
        "read_file" => file_tools::read_file(&a.path),
        "write_file" => file_tools::write_file(&a.path, &a.content),
        // ...
    }
}
```

这个设计的好处：
- `ai_service.rs` 和 `mcp_server.rs` 都通过 `tool_registry` 获取工具定义和执行工具
- 新增工具只需在 `all_tools()` 加一条记录 + 在对应 service 中实现函数
- 两个入口的工具列表和行为始终一致

### 3.3 14 项工具实现

| 类别 | 工具 | 实现要点 |
|------|------|----------|
| **Web** | `browse_website` | `scraper` crate 解析 HTML，提取标题/正文/链接，跳过 script/style/nav |
| | `fetch_url_raw` | 获取原始文本，适用于 API / JSON 请求 |
| | `web_search` | 请求 DuckDuckGo HTML 版，解析 `.result` 元素 |
| | `extract_webpage_images` | 提取所有 `img[src]`，解析相对 URL 为绝对 URL |
| **文件** | `read_file` | 路径校验 + 读取文本 + 超长截断 (100K 字符) |
| | `write_file` | 路径校验 + 自动创建父目录 + 写入 |
| | `list_directory` | 分别收集目录和文件，按类型排序展示 |
| | `create_directory` | `fs::create_dir_all` 递归创建 |
| | `delete_path` | 区分文件/目录，分别调用 `remove_file`/`remove_dir_all` |
| | `search_files` | 递归遍历，按文件名关键词匹配，最多 100 条 |
| **工具** | `get_current_datetime` | `chrono::Local::now()`，含星期中文 |
| | `encode_decode` | Base64 / URL / Hex 双向转换 |
| | `get_ip_geolocation` | 调 ip-api.com 免费接口 |
| | `text_stats` | 统计字符/词/行/字节/中文字符数 |

### 3.4 安全防护

文件系统工具涉及直接操作用户磁盘，必须做安全校验：

```rust
fn validate_path(path: &str) -> Result<PathBuf, String> {
    let canonical = p.canonicalize()?; // 解析符号链接和 ..

    let blocked = ["\\windows\\", "\\system32", "/etc/", "/usr/", "\\program files"];
    for b in &blocked {
        if path_str.contains(b) {
            return Err(format!("禁止访问系统目录: {}", b));
        }
    }
    Ok(canonical)
}
```

Web 工具同样做了 SSRF 防护，拒绝 `localhost` / `127.0.0.1` / 内网网段的请求。

### 3.5 前端工具状态提示

AI 调用工具时前端不能只显示 "思考中..."，需要让用户知道 AI 在做什么。通过正则匹配用户消息内容来预判：

```typescript
function detectToolHint(content: string): string | null {
  if (/网址|网页|url|http|浏览/i.test(lower)) return "正在浏览网页...";
  if (/搜索|搜一下|查一下|search|百度|谷歌/i.test(lower)) return "正在搜索...";
  if (/读取文件|查看文件|read.*file/i.test(lower)) return "正在读取文件...";
  if (/写入文件|创建文件|write.*file|改.*bug/i.test(lower)) return "正在操作文件...";
  // ...
  return null;
}
```

## 4. MCP 协议服务

### 4.1 什么是 MCP

[Model Context Protocol](https://modelcontextprotocol.io/) 是 Anthropic 提出的标准协议，让 AI 模型通过统一接口调用外部工具。LanChat 内置 MCP Server 意味着：

- 任何支持 MCP 的 AI 客户端（Claude Desktop、Cursor 等）都可以连接 LanChat 使用其 14 项工具
- LanChat 自身的 AI 助手也通过同一套工具定义工作

### 4.2 实现

MCP Server 基于 warp 实现 JSON-RPC 2.0 协议，只需处理三个方法：

```rust
async fn handle_rpc(req: JsonRpcRequest) -> JsonRpcResponse {
    match req.method.as_str() {
        "initialize" => /* 返回协议版本和能力 */,
        "tools/list" => /* 调 tool_registry::build_mcp_tool_list() */,
        "tools/call" => /* 调 tool_registry::execute_tool(name, args) */,
        _ => JsonRpcResponse::error(req.id, -32601, "Method not found"),
    }
}
```

同时提供 SSE 端点（`/mcp/sse`）用于服务端推送通知。

## 5. 聊天核心实现

### 5.1 WebSocket 实时通信

服务端使用 warp WebSocket，维护全局客户端列表 `Arc<RwLock<HashMap<String, Client>>>`：

```rust
let ws_route = warp::path("ws")
    .and(warp::ws())
    .and(clients_filter)
    .and(messages_filter)
    .and(warp::addr::remote())
    .map(|ws: warp::ws::Ws, clients, messages, addr| {
        ws.on_upgrade(move |socket| {
            ws_handler::handle_connection(socket, clients, messages, addr)
        })
    });
```

WebSocket 事件类型：
- `join`：客户端注册昵称，返回 welcome + 历史消息
- `message`：广播聊天消息（公共/私聊）
- `users`：用户列表变更推送

前端 `useChat` Hook 实现了指数退避自动重连和 localStorage 消息持久化。

### 5.2 文件传输

文件通过 HTTP POST 上传，文件名格式 `{uuid}_{sanitized_name}.{ext}` 防止冲突和路径穿越。

远程下载文件时必须绕过系统代理：

```rust
let client = reqwest::Client::builder()
    .no_proxy()  // 企业内网环境关键配置
    .build()?;
```

### 5.3 全局传输状态

上传/下载状态通过 React Context 全局管理，配合浮动指示器组件跨页面持久显示：

```typescript
export interface TransferItem {
  id: string;
  type: "upload" | "download";
  fileName: string;
  status: "active" | "success" | "error";
}
```

## 6. 统一配置系统

为避免配置散落在代码各处，设计了前后端统一的配置方案：

```
lanchat.config.json (项目根目录)
       │
       ├─► config.rs (Rust: include_str! 编译时嵌入，OnceLock 全局访问)
       │
       └─► config.ts (前端: 通过 Tauri Command 从后端获取，缓存后同步访问)
```

Rust 端关键实现：

```rust
const CONFIG_JSON: &str = include_str!("../../lanchat.config.json");
static CONFIG: OnceLock<AppConfig> = OnceLock::new();

pub fn get() -> &'static AppConfig {
    CONFIG.get_or_init(|| serde_json::from_str(CONFIG_JSON).expect("Invalid config"))
}
```

好处：
- 修改配置只需编辑一个 JSON 文件
- 编译时嵌入，运行时零 IO
- 前后端配置值来源一致

## 7. API Key 安全方案

DeepSeek API Key 不能出现在前端代码或配置文件中。最终方案：

```rust
// 编译时通过环境变量嵌入二进制
const EMBEDDED_KEY: Option<&str> = option_env!("DEEPSEEK_API_KEY");

fn read_api_key() -> Result<String, String> {
    if let Some(key) = EMBEDDED_KEY {
        if !key.is_empty() { return Ok(key.to_string()); }
    }
    // 回退：OS 凭据管理器 (keyring)
    let entry = keyring::Entry::new("lanchat", "deepseek_api_key")?;
    entry.get_password()
}
```

打包时只需设置环境变量：

```bash
$env:DEEPSEEK_API_KEY = "sk-xxx"
npm run tauri build
```

Key 嵌入 Rust 编译后的二进制文件中，前端代码和配置文件里完全不可见。

## 8. 踩坑与解决方案

| 问题 | 根因 | 解决方案 |
|------|------|----------|
| 远程文件下载 502 | reqwest 默认走系统 HTTP 代理，代理无法到达内网 IP | `Client::builder().no_proxy()` |
| `ai_service.rs` 超 300 行 | 工具定义和执行逻辑与 AI 调用逻辑耦合 | 提取 `tool_registry.rs` 集中管理 |
| `handlers.rs` 超 300 行 | WebSocket + 上传 + 下载三种职责混在一起 | 拆分为 `ws_handler.rs` + `file_handler.rs` |
| `network_cmd.rs` 混入业务逻辑 | Command 层直接调 `local_ip_address` 和 `hostname` | 下沉到 `network_service.rs` |
| 聊天输入框跑到窗口顶部 | 组件拆分后渲染顺序错误 | `<ChatInput />` 移到 `chat-messages` div 之后 |
| 图片预览被裁剪 | 父元素 `overflow: hidden` | `ReactDOM.createPortal` 渲染到 body |
| 拖拽覆盖层不可见 | `position: absolute` 在滚动容器内 | 移到不可滚动的父容器 |
| CSS 文件 1855 行 | 所有样式堆在 `index.css` | 拆分为 9 个模块化 CSS 文件 |
| WebView CORS | 浏览器跨域策略限制 AI API 请求 | Rust 端代理 API 请求 |
| 文件名路径穿越 | 用户可构造恶意文件名 | `sanitize_filename` + `canonicalize` 校验 |

## 9. 项目结构

```
tauri-chat/
├── lanchat.config.json              # 统一配置文件
├── src/                             # React 前端
│   ├── App.tsx                      # 主应用入口
│   ├── config.ts                    # 前端配置加载
│   ├── components/
│   │   ├── ChatWindow.tsx           # 聊天窗口
│   │   ├── ChatInput.tsx            # 输入框组件
│   │   ├── AiChatWindow.tsx         # AI 聊天窗口
│   │   ├── MarkdownRenderer.tsx     # Markdown 渲染
│   │   ├── MessageBubble.tsx        # 消息气泡
│   │   ├── UserList.tsx             # 侧边栏用户列表
│   │   ├── LoginScreen.tsx          # 登录界面
│   │   ├── ImagePreview.tsx         # 图片预览
│   │   └── TransferIndicator.tsx    # 传输进度指示器
│   ├── hooks/
│   │   ├── useChat.ts               # WebSocket 聊天
│   │   ├── useAiChat.ts             # AI 聊天（工具提示、上下文管理）
│   │   ├── useTransfers.tsx         # 全局传输状态
│   │   └── useLocalStorage.ts       # localStorage
│   └── styles/                      # 模块化 CSS（9 个文件）
│       ├── base.css                 # 全局变量、重置、布局
│       ├── chat.css                 # 聊天窗口
│       ├── chat-input.css           # 输入区域
│       ├── message.css              # 消息气泡
│       ├── ai.css                   # AI 动画
│       ├── markdown.css             # Markdown 样式
│       └── ...
├── src-tauri/src/                   # Rust 后端
│   ├── lib.rs                       # Tauri 入口
│   ├── config.rs                    # 配置加载（include_str! + OnceLock）
│   ├── commands/                    # Controller 层
│   │   ├── ai_cmd.rs                # AI 聊天 + API Key 管理
│   │   ├── file_cmd.rs              # 文件下载
│   │   ├── network_cmd.rs           # 网络信息
│   │   └── config_cmd.rs            # 前端配置
│   ├── services/                    # Service 层（按领域分组）
│   │   ├── ai/
│   │   │   ├── chat_service.rs      # DeepSeek API 调用 + 多轮工具循环
│   │   │   ├── tool_registry.rs     # 14 项工具定义 + 统一调度
│   │   │   └── utility_tools.rs     # 时间/编码/IP/文本工具
│   │   ├── web/
│   │   │   ├── scraper.rs           # 网页抓取与解析
│   │   │   └── search.rs            # DuckDuckGo 搜索 + 图片提取
│   │   ├── file/
│   │   │   ├── download.rs          # 聊天文件下载
│   │   │   └── tools.rs             # 文件系统 CRUD（AI 工具）
│   │   ├── mcp_server.rs            # MCP JSON-RPC 2.0 服务
│   │   └── network_service.rs       # 网络信息
│   ├── models/                      # Model 层
│   │   ├── ai.rs                    # AI 消息、工具参数结构体
│   │   ├── chat.rs                  # 聊天消息、WebSocket 类型
│   │   └── network.rs               # 网络接口类型
│   ├── server/                      # 基础设施层
│   │   ├── routes.rs                # warp 路由定义
│   │   ├── ws_handler.rs            # WebSocket 连接和消息处理
│   │   ├── file_handler.rs          # 文件上传和下载处理
│   │   └── state.rs                 # 共享状态
│   └── utils/
│       └── filename.rs              # 文件名清洗
└── package.json
```

## 10. 总结

这个项目经历了从单文件到分层架构、从简单问答到 14 项工具调用的完整演进。几个核心收获：

**Tauri 的双层架构优势**：WebView 无法处理的问题（CORS、系统代理、文件系统操作、密钥保护），Rust Command 都能优雅解决。

**AI Function Calling 的工程化**：不只是拼接 prompt，而是设计工具注册表、统一调度、安全校验、前端状态提示的完整闭环。同一套工具同时服务 AI 对话和 MCP 协议，代码复用率高。

**分层解耦的价值**：将后端从扁平结构重构为 `commands → services/{ai,web,file} → models` 三层后，新增工具只需在对应 service 写实现 + registry 加一行，不需要改动 AI 调用逻辑或 MCP 服务代码。

**企业内网的特殊性**：系统代理、防火墙、不同机器间的网络差异，这些在开发环境中很难复现，`no_proxy()` 这类看似简单的配置在实际部署中至关重要。
