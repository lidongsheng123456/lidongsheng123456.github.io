---
title: 网页父子窗口 postMessage 通信机制解析
date: 2025/11/10
tags:
  - 中电软件园
categories:
  - 实习
---
# day05

# 网页父子窗口 postMessage 通信机制解析

## 核心问题

子窗口调用 `window.parent.postMessage(message, '*')`​ 发送消息时，多个注册了 `window.addEventListener('message', handleMessage)` 的“父窗口”能否全部接收？

**结论：不能。仅直接父窗口会接收，不会多播给多个窗口。**

## 一、窗口层级关系的核心规则

浏览器中窗口/iframe 的层级为 **树形结构**，每个子窗口（含 iframe）有且仅有一个 `window.parent`（直接父窗口），层级关系唯一且不可逆：

- 层级示例：A（顶层窗口）→ B（A 的 iframe 子窗口）→ C（B 的 iframe 子窗口）

  - C 的 `window.parent` = B（直接父窗口）
  - B 的 `window.parent` = A（直接父窗口）
  - A 为顶层窗口（`window.parent === window`）

### 关键机制

​`window.parent.postMessage`​ 的消息接收者严格限定为 **当前子窗口的直接父窗口**，而非所有祖先窗口或无关联窗口。

## 二、消息传递效果（案例验证）

### 场景 1：直接父窗口接收（默认行为）

- 结构：A（顶层）→ B（A 的 iframe）→ C（B 的 iframe）
- 操作：C 执行 `window.parent.postMessage('test', '*')`
- 结果：

  - 仅 B 窗口的 `message` 事件触发（B 是 C 的直接父窗口）
  - A 窗口（祖父窗口）不会接收

### 场景 2：多层级转发（实现祖父窗口接收）

若需顶层窗口 A 接收 C 的消息，需通过中间层 B 转发：

#### B 窗口代码（转发逻辑）

```javascript
// B 窗口监听 C 的消息并转发给 A
window.addEventListener('message', (e) => {
  // 验证消息来源（仅接收 C 窗口的消息）
  if (e.source === document.querySelector('iframe').contentWindow) {
    // 转发给直接父窗口 A
    window.parent.postMessage(e.data, 'https://your-domain.com'); // 指定目标域名
  }
});
```

#### A 窗口代码（接收转发消息）

```javascript
window.addEventListener('message', (e) => {
  // 安全校验：限定来源域名和发送窗口
  if (e.origin === 'https://trusted-domain.com' && e.source === document.querySelector('iframe').contentWindow) {
    console.log('A 收到转发消息：', e.data);
  }
});
```

## 三、“多个父窗口”的误解澄清

### 误解 1：一个子窗口嵌入多个父窗口

- 实际：不可能。一个子窗口无法同时嵌入多个父窗口，`window.parent` 始终唯一。

### 误解 2：兄弟窗口接收消息

- 场景：顶层窗口 A 打开两个子窗口 B 和 C（兄弟关系）
- 操作：B 执行 `window.parent.postMessage('test', '*')`
- 结果：仅 A（共同父窗口）接收，C （兄弟窗口）不会接收（无直接层级关联）

## 四、安全最佳实践

### 1. 避免使用 `targetOrigin: '*'`

指定具体目标域名，防止消息被恶意窗口拦截：

```javascript
// 错误写法（不安全）
window.parent.postMessage(message, '*');

// 正确写法（限定域名）
window.parent.postMessage(message, 'https://your-top-domain.com');
```

### 2. 接收消息时严格校验

必须验证 `e.source`​（发送窗口）和[ ]()​[`e.origin`]()​[（发送域名）]()，防止跨域恶意注入：

```javascript
window.addEventListener('message', (e) => {
  // 校验条件：仅接收指定域名、指定窗口的消息
  const trustedOrigin = 'https://trusted-domain.com';
  const trustedSource = document.querySelector('#target-iframe').contentWindow;
  
  if (e.origin === trustedOrigin && e.source === trustedSource) {
    console.log('安全接收消息：', e.data);
  }
});
```

## 五、总结

1. **消息传递范围**：`window.parent.postMessage`​ 仅发送给 **直接父窗口**，无多播能力。
2. **多层级接收**：需通过“子窗口 → 直接父窗口 → 祖父窗口”的转发机制实现。
3. **层级唯一性**：每个子窗口的 `window.parent` 唯一，不存在“多个父窗口同时接收”的场景。
4. **安全优先**：始终指定 `targetOrigin` 并校验消息来源，避免跨域安全风险。

‍
