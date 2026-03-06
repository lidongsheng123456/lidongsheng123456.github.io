---
title: 基于 Tauri + React 开发内网聊天工具 LanChat 的实战经验
date: 2026-03-06
tags:
 - tauri
 - rust
 - react
 - websocket
 - 内网聊天
categories:
 - 实习
---

记录使用 Tauri 2 + React + TypeScript + Rust (warp) 开发内网聊天工具 **LanChat** 的完整过程，涵盖架构设计、核心功能实现、踩坑与解决方案。

## 1. 项目背景与技术选型

公司内网环境下需要一个轻量级的局域网即时通讯工具，要求：

- **零配置**：无需服务器部署，打开即用
- **文件传输**：支持图片、视频、任意文件的收发
- **跨设备**：同一局域网内任意 Windows 设备可互联
- **AI 聊天**：集成 LLM API 作为 AI 助手

最终选定技术栈：

| 层级 | 技术 | 说明 |
|------|------|------|
| 桌面框架 | Tauri 2 | Rust 后端 + WebView 前端，包体小 (~8MB) |
| 前端 | React + TypeScript | Vite 构建，Lucide 图标 |
| 后端服务 | Rust warp | 内嵌 HTTP + WebSocket 服务器 |
| 实时通信 | WebSocket | 消息推送、用户上下线 |
| AI 集成 | reqwest | Rust 端代理 LLM API 请求 |

### 为什么选 Tauri 而不是 Electron？

- Tauri 打包体积约 8MB，Electron 通常 150MB+
- Tauri 使用系统 WebView，内存占用低
- Rust 后端可以直接内嵌 warp 服务器，不需要额外进程
- Tauri 2 的 Command 机制让前后端通信非常简洁

## 2. 架构设计

```
┌─────────────────────────────────────────┐
│              Tauri Application           │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  React UI   │  │  Rust Backend    │  │
│  │  (WebView)  │◄─┤  ┌────────────┐  │  │
│  │             │  │  │ warp Server │  │  │
│  │  ChatWindow │  │  │  - /ws      │  │  │
│  │  UserList   │  │  │  - /upload  │  │  │
│  │  AiChat     │  │  │  - /files   │  │  │
│  │             │  │  └────────────┘  │  │
│  │             │  │  Tauri Commands  │  │
│  │             │──┤  - download_file │  │
│  │             │  │  - chat_with_ai  │  │
│  └─────────────┘  └──────────────────┘  │
└─────────────────────────────────────────┘
```

核心思路：**Tauri 启动时在后台启动一个 warp HTTP/WebSocket 服务器**，监听 `0.0.0.0:9120`。同局域网的其他设备通过 WebSocket 连接到这台机器，实现聊天和文件传输。

## 3. 核心功能实现

### 3.1 WebSocket 实时通信

服务端使用 warp 的 WebSocket 支持，维护一个全局客户端列表：

```rust
type Clients = Arc<Mutex<HashMap<String, Client>>>;

let ws_route = warp::path("ws")
    .and(warp::ws())
    .and(clients_filter.clone())
    .and(messages_filter.clone())
    .and(warp::addr::remote())
    .map(move |ws: warp::ws::Ws, clients, messages, addr| {
        ws.on_upgrade(move |socket| {
            handle_connection(socket, clients, messages, addr)
        })
    });
```

前端使用自定义 `useChat` Hook 管理 WebSocket 连接，实现了：

- **自动重连**：指数退避策略，断线后自动恢复
- **消息持久化**：聊天记录存储到 localStorage
- **历史合并**：重连后将服务端历史与本地消息合并去重

```typescript
const connect = useCallback(() => {
  const ws = new WebSocket(`ws://${serverUrl}/ws`);
  ws.onclose = () => {
    // 指数退避重连
    const delay = Math.min(
      BASE_RECONNECT_DELAY * Math.pow(1.5, reconnectAttempts.current),
      MAX_RECONNECT_DELAY
    );
    reconnectTimer.current = setTimeout(() => connect(), delay);
  };
}, [serverUrl, nickname]);
```

### 3.2 文件上传与传输

文件通过 HTTP POST 上传到服务器，存储在 `chat_files/` 目录：

```rust
let upload_route = warp::path("upload")
    .and(warp::post())
    .and(warp::body::bytes())
    .and(warp::header::<String>("x-file-name"))
    // ... 其他 header
    .and_then(handle_upload);
```

上传后文件名格式为 `{uuid}_{sanitized_name}.{ext}`，避免冲突和路径穿越攻击。

### 3.3 远程文件下载（踩坑重点）

本机下载直接从 `chat_files/` 目录复制到用户下载目录。远程机器则通过 HTTP 回落下载。

**踩坑：远程下载 502 Bad Gateway**

初始实现使用 `reqwest::get()` 下载文件，在远程机器上始终返回 502。排查后发现：

> **根因**：Windows 系统配置了 HTTP 代理，`reqwest` 默认使用系统代理设置。LAN 内部 IP 请求被代理服务器拦截，代理无法到达内网地址，返回 502。

**解决方案**：使用 `no_proxy()` 绕过系统代理：

```rust
let client = reqwest::Client::builder()
    .no_proxy()  // 关键！绕过系统代理
    .build()
    .map_err(|e| format!("Failed to create HTTP client: {}", e))?;

let url = format!("http://{}/files/{}", server_url, stored_name);
let response = client.get(&url).send().await?;
```

这是一个在企业内网环境中非常常见的坑，值得记住。

### 3.4 AI 聊天集成

通过 Tauri Command 在 Rust 端代理 LLM API 请求，绕过 WebView 的 CORS 限制：

```rust
#[tauri::command]
async fn chat_with_ai(api_key: String, messages: Vec<AiChatMessage>) -> Result<String, String> {
    let client = reqwest::Client::builder()
        .no_proxy()
        .build()?;

    let response = client
        .post("https://api.longcat.chat/openai/v1/chat/completions")
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&body)
        .send()
        .await?;
    // ...
}
```

前端通过 `useAiChat` Hook 管理 AI 聊天状态，消息持久化到 localStorage。

### 3.5 全局传输状态管理

**问题**：上传/下载状态存在组件本地 state 中，切换聊天频道后状态丢失，用户不知道传输还在进行中。

**解决方案**：创建全局 `TransferContext`，在 App 顶层提供传输状态，配合浮动指示器组件：

```typescript
// TransferProvider 管理所有传输任务
export interface TransferItem {
  id: string;
  type: "upload" | "download";
  fileName: string;
  status: "active" | "success" | "error";
}

// 浮动指示器固定在右下角，跨页面持久显示
<div className="transfer-indicator">
  {transfers.map(t => (
    <div className={`transfer-item transfer-item--${t.status}`}>
      {/* spinner / 文件名 / 状态 */}
    </div>
  ))}
</div>
```

完成的传输任务 3 秒后自动移除，错误任务可手动关闭。

## 4. UI/UX 优化经验

### 4.1 拖拽上传覆盖层定位

**问题**：拖拽覆盖层放在 `chat-messages`（可滚动区域）内部，使用 `position: absolute`。当消息多时滚动到底部，覆盖层在顶部不可见。

**解决方案**：将覆盖层移到 `chat-window` 级别（不可滚动），确保始终覆盖整个聊天区域。

### 4.2 深色背景上的 UI 元素

绿色消息气泡（自己发的消息）上的下载旋转器使用了默认的绿色边框，在绿色背景上几乎不可见。

**解决方案**：为 `isMine` 状态添加白色变体：

```css
.chat-upload-spinner--white {
  border-color: white;
  border-top-color: transparent;
}
```

### 4.3 图片预览 Portal

图片预览弹窗如果渲染在消息气泡内部，会被父元素的 `overflow: hidden` 裁剪。使用 `ReactDOM.createPortal` 将预览弹窗渲染到 `document.body`，确保全屏覆盖。

## 5. 关键踩坑总结

| 问题 | 根因 | 解决方案 |
|------|------|----------|
| 远程下载 502 | reqwest 走系统 HTTP 代理 | `Client::builder().no_proxy()` |
| 拖拽覆盖层不可见 | `position: absolute` 在滚动容器内 | 移到不可滚动的父容器 |
| 上传/下载状态丢失 | 状态在组件 local state | 提升到全局 Context |
| 图片预览被裁剪 | 父元素 `overflow: hidden` | `ReactDOM.createPortal` |
| WebView CORS 限制 | 浏览器跨域策略 | Rust 端代理 API 请求 |
| 文件名路径穿越 | 用户可构造恶意文件名 | `sanitize_filename` + 路径校验 |

## 6. 项目结构

```
tauri-chat/
├── src/                          # React 前端
│   ├── App.tsx                   # 主应用（登录/聊天路由）
│   ├── components/
│   │   ├── ChatWindow.tsx        # 聊天窗口（消息列表、输入、文件上传）
│   │   ├── AiChatWindow.tsx      # AI 聊天窗口
│   │   ├── MessageBubble.tsx     # 消息气泡（文本/图片/视频/文件）
│   │   ├── UserList.tsx          # 侧边栏用户列表
│   │   ├── LoginScreen.tsx       # 登录界面
│   │   ├── ImagePreview.tsx      # 图片预览 Portal
│   │   └── TransferIndicator.tsx # 浮动传输进度指示器
│   ├── hooks/
│   │   ├── useChat.ts            # WebSocket 聊天 Hook
│   │   ├── useAiChat.ts          # AI 聊天 Hook
│   │   ├── useTransfers.tsx      # 全局传输状态 Context
│   │   └── useLocalStorage.ts    # localStorage Hook
│   └── index.css                 # 全局样式
├── src-tauri/
│   ├── src/
│   │   ├── lib.rs                # Tauri Commands（下载、AI 聊天）
│   │   └── server.rs             # warp HTTP/WebSocket 服务器
│   ├── Cargo.toml
│   └── tauri.conf.json
└── package.json
```

## 7. 总结

这个项目的核心价值在于 **Tauri 的双层架构**：

- **前端**：React 负责 UI 渲染和用户交互，开发效率高
- **后端**：Rust 负责网络服务、文件操作、API 代理，性能和安全性好

Tauri 2 的 Command 机制让两者之间的通信非常自然。遇到 WebView 无法处理的场景（CORS、文件系统操作、系统代理），都可以通过 Rust Command 绕过。

最大的收获是理解了**企业内网环境的特殊性**：系统代理、防火墙、不同机器间的网络差异，这些在开发环境中很难复现，需要在实际部署中反复测试。
