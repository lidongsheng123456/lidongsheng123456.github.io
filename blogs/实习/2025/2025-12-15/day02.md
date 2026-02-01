---
title: PWA 实战指南 - LogicDrawer 项目总结
date: 2025/12/15
tags:
  - 中电软件园
categories:
  - 实习
---
# day02

# PWA 实战指南 - LogicDrawer 项目总结

## 📋 目录

- [项目概述](#项目概述)
- [PWA 核心功能实现](#pwa-核心功能实现)
- [Vite 开发环境缓存问题及解决方案](#vite-开发环境缓存问题及解决方案)
- [Service Worker 实现](#service-worker-实现)
- [PWA 管理器架构](#pwa-管理器架构)
- [Manifest 配置](#manifest-配置)
- [最佳实践与经验总结](#最佳实践与经验总结)

---

## 项目概述

**LogicDrawer** 是一个专业的数字电路设计与仿真工具,支持离线使用的 PWA 应用。

### 技术栈

- **构建工具**: Vite 5.0.10
- **前端框架**: 原生 TypeScript
- **PWA 核心**: Service Worker + Cache API + IndexedDB
- **版本管理**: 基于 package.json 的自动版本注入

---

## PWA 核心功能实现

### 1. Service Worker 注册策略

#### 开发环境 vs 生产环境

```typescript
// src/utils/PWAManager.ts
async registerServiceWorker(): Promise<void> {
    const isDevelopment = window.location.hostname === 'localhost';

    // 开发环境不使用 Service Worker
    if (isDevelopment) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        for (const registration of registrations) {
            await registration.unregister();
        }
        return;
    }

    // 生产环境注册 Service Worker
    this.registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/'
    });
}
```

**关键点**:

- ✅ 开发环境自动注销 Service Worker
- ✅ 避免缓存干扰开发调试
- ✅ 生产环境启用完整 PWA 功能

### 2. 版本管理系统

#### 自动版本注入机制

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [
    {
      name: 'inject-version-to-sw',
      apply: 'build',
      closeBundle() {
        const swPath = resolve(__dirname, 'dist/service-worker.js');
        let content = readFileSync(swPath, 'utf-8');
        content = content.replace(/__APP_VERSION__/g, `"${packageJson.version}"`);
        writeFileSync(swPath, content, 'utf-8');
      }
    },
    {
      name: 'dev-sw-injector',
      configureServer(server: ViteDevServer) {
        server.middlewares.use((req, res, next) => {
          if (req.url === '/service-worker.js') {
            const swPath = resolve(__dirname, 'public/service-worker.js');
            let content = readFileSync(swPath, 'utf-8');
            content = content.replace(/__APP_VERSION__/g, `"${packageJson.version}"`);
            res.setHeader('Content-Type', 'application/javascript');
            res.end(content);
            return;
          }
          next();
        });
      }
    }
  ]
});
```

**工作流程**:

1. 从 `package.json` 读取版本号
2. 构建时替换 Service Worker 中的 `__APP_VERSION__` 占位符
3. 开发环境通过中间件动态注入版本号
4. 版本号用于缓存命名和更新检测

### 3. 缓存策略

#### 多层缓存架构

```javascript
// public/service-worker.js
const CACHE_VERSION = `v${__APP_VERSION__}`;
const CACHE_NAME = `logicdrawer-${CACHE_VERSION}`;
const DATA_CACHE_NAME = `logicdrawer-data-${CACHE_VERSION}`;

// 预缓存静态资源
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/src/main.ts',
  '/src/styles/index.css',
  '/manifest.json',
  '/images/favicon.svg'
];

// 缓存模式匹配
const CACHE_PATTERNS = {
  static: /\.(js|ts|css|html|svg|png|jpg|jpeg|gif|webp|woff|woff2|ttf|eot)$/,
  api: /\/api\//,
  circuit: /\.json$/
};
```

#### 缓存优先策略 (Cache First)

```javascript
async function cacheFirstStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    console.log('[SW] Cache hit:', request.url);
    return cachedResponse;
  }
  
  // 缓存未命中,从网络获取
  const networkResponse = await fetch(request);
  
  if (networkResponse && networkResponse.status === 200) {
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}
```

**适用场景**:

- 静态资源 (JS, CSS, 图片)
- 电路配置文件
- 不常变化的内容

#### 网络优先策略 (Network First)

```javascript
async function networkFirstStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response('Offline - Network unavailable', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}
```

**适用场景**:

- API 请求
- 需要实时数据的资源
- 用户数据同步

### 4. 生命周期管理

#### 安装阶段

```javascript
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...', CACHE_VERSION);
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});
```

#### 激活阶段

```javascript
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...', CACHE_VERSION);
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // 删除旧版本缓存
            if (cacheName !== CACHE_NAME && cacheName !== DATA_CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
      .then(() => {
        // 通知客户端更新完成
        return self.clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({
              type: 'SW_UPDATED',
              version: CACHE_VERSION
            });
          });
        });
      })
  );
});
```

---

## Vite 开发环境缓存问题及解决方案

### ⚠️ 问题描述

在 Vite 开发环境中启用 Service Worker 会导致严重的缓存问题:

#### 1. **文件哈希值动态变化**

Vite 在开发模式下为每个模块生成动态哈希值:

```
开发环境请求示例:
http://localhost:4000/src/main.ts?t=1702345678901
http://localhost:4000/src/styles/index.css?t=1702345678902
http://localhost:4000/@vite/client?t=1702345678903
```

**问题**:

- 每次热更新 (HMR) 都会生成新的时间戳参数
- Service Worker 缓存的 URL 包含旧的时间戳
- 导致缓存永远无法命中
- 强制每次都从网络获取,失去缓存意义

#### 2. **CSS 预处理器问题**

```typescript
// 开发环境:Vite 动态编译 SCSS/LESS
import './styles/index.scss'  // Vite 实时编译为 CSS

// Service Worker 缓存的是编译后的 CSS
// 但源文件修改后,缓存的 CSS 不会更新
```

**问题**:

- Vite 在开发时动态编译 CSS 预处理器文件
- Service Worker 缓存的是编译后的 CSS
- 源文件修改后,缓存返回旧的 CSS
- 导致样式不更新,开发体验极差

#### 3. **HMR (热模块替换) 失效**

```javascript
// Vite HMR 工作流程
1. 文件修改
2. Vite 检测变化
3. 发送 WebSocket 消息
4. 浏览器请求更新的模块 (带新的时间戳)
5. Service Worker 拦截请求
6. 缓存中找不到匹配的 URL (因为时间戳不同)
7. 从网络获取新模块 ✅
8. 但是缓存了带新时间戳的文件
9. 下次 HMR 又会生成新的时间戳
10. 导致缓存不断增长,永远无法复用 ❌
```

**问题**:

- Service Worker 拦截了 HMR 更新请求
- 由于时间戳参数不同,缓存无法命中
- 虽然能获取到新文件,但会缓存每个带时间戳的版本
- 导致缓存无限膨胀,浪费存储空间
- 缓存策略完全失效,失去了缓存的意义

#### 4. **开发服务器代理失效**

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:3000'
    }
  }
});

// Service Worker 拦截 /api 请求
// 返回缓存数据而不是代理到后端
// 导致开发时无法调试 API
```

### ✅ 解决方案

#### 方案 1: 开发环境禁用 Service Worker (推荐)

```typescript
// src/utils/PWAManager.ts
async registerServiceWorker(): Promise<void> {
    // 检测开发环境
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.port === '4000'; // Vite 默认端口

    if (isDevelopment) {
        console.log('[PWA] 开发环境:注销 Service Worker');
        
        // 注销所有已注册的 Service Worker
        const registrations = await navigator.serviceWorker.getRegistrations();
        for (const registration of registrations) {
            await registration.unregister();
            console.log('[PWA] 已注销:', registration.scope);
        }
        
        // 清除所有缓存
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(name => caches.delete(name)));
        console.log('[PWA] 已清除所有缓存');
        
        return;
    }

    // 生产环境正常注册
    this.registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/'
    });
}
```

**优点**:

- ✅ 完全避免缓存干扰
- ✅ HMR 正常工作
- ✅ 开发体验最佳
- ✅ 实现简单

**缺点**:

- ❌ 无法在开发环境测试 PWA 功能

#### 方案 2: 条件性缓存策略

```javascript
// public/service-worker.js
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // 跳过 Vite 开发服务器的特殊请求
  if (url.searchParams.has('t') ||           // 时间戳参数
      url.pathname.includes('/@vite/') ||    // Vite 内部模块
      url.pathname.includes('/@fs/') ||      // 文件系统访问
      url.pathname.includes('/@id/') ||      // 模块 ID
      url.pathname.includes('node_modules')) { // 依赖模块
    return; // 不拦截,直接走网络
  }
  
  // 其他请求正常缓存
  event.respondWith(cacheFirstStrategy(event.request, CACHE_NAME));
});
```

**优点**:

- ✅ 可以在开发环境测试部分 PWA 功能
- ✅ 不影响 Vite HMR

**缺点**:

- ❌ 配置复杂
- ❌ 可能遗漏某些 Vite 特殊路径
- ❌ 仍然可能出现缓存问题

#### 方案 3: 使用环境变量控制

```typescript
// vite.config.ts
export default defineConfig({
  define: {
    __ENABLE_SW__: process.env.NODE_ENV === 'production'
  }
});

// src/main.ts
if (__ENABLE_SW__) {
  pwaManager.init();
}
```

**优点**:

- ✅ 灵活控制
- ✅ 可以通过环境变量切换

**缺点**:

- ❌ 需要额外的构建配置
- ❌ 代码中有条件判断

### 🎯 最佳实践建议

1. **开发环境完全禁用 Service Worker**

    ```bash
    npm run dev  # 自动禁用 SW
    ```
2. **使用预览模式测试 PWA**

    ```bash
    npm run build
    npm run preview  # 启用 SW 测试
    ```
3. **生产环境构建验证**

    ```bash
    npm run build
    # 部署到测试服务器验证 PWA 功能
    ```
4. **添加开发提示**

    ```typescript
    if (isDevelopment) {
      console.warn('⚠️  开发环境:Service Worker 已禁用');
      console.info('💡 提示:使用 npm run preview 测试 PWA 功能');
    }
    ```

### 📊 性能对比

|场景|无 Service Worker|有 Service Worker (开发)|有 Service Worker (生产)|
| --------| -----------------| ------------------------| ------------------------|
|首次加载|正常|正常|快速 (预缓存)|
|HMR 更新|即时|延迟/失败|N/A|
|样式更新|即时|缓存旧样式|即时 (版本更新)|
|离线访问|❌|✅ (但数据可能旧)|✅|
|开发体验|⭐⭐⭐⭐⭐|⭐⭐|N/A|

---

## Service Worker 实现

### 完整功能清单

#### 1. 网络请求拦截

```javascript
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 跳过非 HTTP(S) 请求
  if (!request.url.startsWith('http')) {
    return;
  }

  // API 请求 - 网络优先
  if (CACHE_PATTERNS.api.test(url.pathname)) {
    event.respondWith(networkFirstStrategy(request, DATA_CACHE_NAME));
    return;
  }

  // 电路文件 - 缓存优先
  if (CACHE_PATTERNS.circuit.test(url.pathname)) {
    event.respondWith(cacheFirstStrategy(request, DATA_CACHE_NAME));
    return;
  }

  // 静态资源 - 缓存优先
  if (CACHE_PATTERNS.static.test(url.pathname)) {
    event.respondWith(cacheFirstStrategy(request, CACHE_NAME));
    return;
  }

  // 其他请求 - 网络优先
  event.respondWith(networkFirstStrategy(request, CACHE_NAME));
});
```

#### 2. 后台同步 (Background Sync)

```javascript
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-circuits') {
    event.waitUntil(syncCircuits());
  }
});

async function syncCircuits() {
  const db = await openIndexedDB();
  const pendingCircuits = await getPendingCircuits(db);
  
  for (const circuit of pendingCircuits) {
    try {
      const response = await fetch('/api/circuits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(circuit)
      });
      
      if (response.ok) {
        await markCircuitAsSynced(db, circuit.id);
      }
    } catch (error) {
      console.error('[SW] Failed to sync circuit:', circuit.id, error);
    }
  }
}
```

#### 3. 推送通知 (Push Notifications)

```javascript
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/images/icon-192.png',
    badge: '/images/badge-72.png',
    vibrate: [200, 100, 200],
    actions: [
      { action: 'open', title: '打开应用' },
      { action: 'close', title: '关闭' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('LogicDrawer', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'open') {
    event.waitUntil(clients.openWindow('/'));
  }
});
```

#### 4. 消息通信 (postMessage)

```javascript
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_VERSION':
      event.ports[0].postMessage({
        type: 'VERSION',
        version: CACHE_VERSION
      });
      break;
      
    case 'CLEAR_CACHE':
      event.waitUntil(clearAllCaches());
      break;
      
    case 'CACHE_CIRCUIT':
      event.waitUntil(cacheCircuit(data));
      break;
  }
});
```

#### 5. IndexedDB 集成

```javascript
function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('LogicDrawerDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      if (!db.objectStoreNames.contains('circuits')) {
        const circuitStore = db.createObjectStore('circuits', { keyPath: 'id' });
        circuitStore.createIndex('synced', 'synced', { unique: false });
        circuitStore.createIndex('timestamp', 'timestamp', { unique: false });
      }
      
      if (!db.objectStoreNames.contains('settings')) {
        db.createObjectStore('settings', { keyPath: 'key' });
      }
    };
  });
}
```

---

## PWA 管理器架构

### 核心功能模块

#### 1. 初始化流程

```typescript
class PWAManager {
  async init(): Promise<void> {
    // 1. 检查浏览器支持
    if (!this.checkSupport()) {
      console.warn('[PWA] 浏览器不支持 PWA 功能');
      return;
    }

    // 2. 注册 Service Worker
    await this.registerServiceWorker();

    // 3. 初始化 IndexedDB
    await indexedDBManager.init();

    // 4. 监听安装提示
    this.listenForInstallPrompt();

    // 5. 监听 Service Worker 消息
    this.listenForSWMessages();

    // 6. 监听在线/离线状态
    this.listenForOnlineStatus();

    // 7. 定期清理过期缓存
    this.scheduleCleanup();
  }
}
```

#### 2. 更新检测与通知

```typescript
private async notifyUpdateAvailable(): Promise<void> {
  // 获取新版本号
  const waitingWorker = this.registration?.waiting || this.registration?.installing;
  const messageChannel = new MessageChannel();
  
  const versionPromise = new Promise<string>((resolve) => {
    messageChannel.port1.onmessage = (event) => {
      if (event.data.type === 'VERSION') {
        resolve(event.data.version);
      }
    };
    setTimeout(() => resolve('新版本'), 1000);
  });

  waitingWorker.postMessage({ type: 'GET_VERSION' }, [messageChannel.port2]);
  const newVersion = await versionPromise;

  // 显示更新横幅
  const updateBanner = document.createElement('div');
  updateBanner.className = 'pwa-update-banner';
  updateBanner.innerHTML = `
    <div class="pwa-update-content">
      <span>🎉 ${newVersion} 可用!</span>
      <div>
        <button id="pwa-update-btn">立即更新</button>
        <button id="pwa-dismiss-btn">稍后</button>
      </div>
    </div>
  `;
  document.body.appendChild(updateBanner);
}
```

#### 3. 安装提示

```typescript
private listenForInstallPrompt(): void {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    this.deferredPrompt = e;
    console.log('[PWA] 应用可以安装');
  });

  window.addEventListener('appinstalled', () => {
    console.log('[PWA] 应用已安装');
    this.deferredPrompt = null;
  });
}

async promptInstall(): Promise<void> {
  if (!this.deferredPrompt) {
    return;
  }

  this.deferredPrompt.prompt();
  const { outcome } = await this.deferredPrompt.userChoice;
  
  if (outcome === 'accepted') {
    console.log('[PWA] 用户接受安装');
  }
  
  this.deferredPrompt = null;
}
```

#### 4. 离线/在线状态管理

```typescript
private listenForOnlineStatus(): void {
  window.addEventListener('online', () => {
    console.log('[PWA] 网络已连接');
    this.showNotification('网络已连接', '正在同步数据...');
    this.syncData();
  });

  window.addEventListener('offline', () => {
    console.log('[PWA] 网络已断开');
    this.showNotification('离线模式', '您可以继续使用应用,数据将在联网后同步');
  });
}
```

#### 5. 数据同步

```typescript
async syncData(): Promise<void> {
  if (!navigator.onLine) {
    return;
  }

  const unsyncedCircuits = await indexedDBManager.getUnsyncedCircuits();
  
  if (unsyncedCircuits.length === 0) {
    return;
  }

  // 使用后台同步 API
  if (this.registration && 'sync' in this.registration) {
    await (this.registration as any).sync.register('sync-circuits');
  } else {
    // 降级方案:直接同步
    await this.syncCircuitsDirectly(unsyncedCircuits);
  }
}
```

---

## Manifest 配置

### 完整配置示例

```json
{
  "name": "PiLoTSim-LogicDrawer",
  "short_name": "LogicDrawer",
  "description": "专业的数字电路设计与仿真工具，支持离线使用",
  "start_url": "/?source=pwa",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4CAF50",
  "orientation": "any",
  "scope": "/",
  "lang": "zh-CN",
  "dir": "ltr",
  "icons": [
    {
      "src": "/images/favicon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    },
    {
      "src": "/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    }
  ],
  "screenshots": [
    {
      "src": "/images/screenshot-wide.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    },
    {
      "src": "/images/screenshot-narrow.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],
  "categories": [
    "education",
    "productivity",
    "utilities"
  ],
  "shortcuts": [
    {
      "name": "新建电路",
      "short_name": "新建",
      "description": "创建新的数字电路",
      "url": "/?action=new",
      "icons": [
        {
          "src": "/images/shortcut-new.png",
          "sizes": "96x96"
        }
      ]
    }
  ],
  "share_target": {
    "action": "/share",
    "method": "POST",
    "enctype": "multipart/form-data",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url",
      "files": [
        {
          "name": "circuit",
          "accept": ["application/json", ".json"]
        }
      ]
    }
  },
  "prefer_related_applications": false
}
```

### HTML 集成

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- PWA Manifest -->
  <link rel="manifest" href="/manifest.json">
  
  <!-- iOS 支持 -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="LogicDrawer">
  <link rel="apple-touch-icon" href="/images/favicon.svg">
  
  <!-- 主题颜色 -->
  <meta name="theme-color" content="#4CAF50">
</head>
</html>
```

---

## 最佳实践与经验总结

### ✅ 成功经验

#### 1. **环境分离策略**

- 开发环境禁用 Service Worker,避免缓存干扰
- 生产环境启用完整 PWA 功能
- 使用 `npm run preview` 测试 PWA 功能

#### 2. **版本管理自动化**

- 基于 `package.json` 自动注入版本号
- Vite 插件在构建时替换占位符
- 开发环境中间件动态注入版本号

#### 3. **缓存策略分层**

- 静态资源使用缓存优先策略
- API 请求使用网络优先策略
- 用户数据使用 IndexedDB 持久化

#### 4. **优雅的更新机制**

- 检测到新版本时显示更新提示
- 用户确认后应用更新并刷新页面
- 自动清理旧版本缓存

#### 5. **离线功能完善**

- 监听在线/离线状态变化
- 离线时提示用户,数据本地保存
- 恢复在线后自动同步数据

### ⚠️ 常见陷阱

#### 1. **Vite 开发环境缓存问题**

- ❌ 不要在开发环境启用 Service Worker
- ✅ 使用环境检测自动禁用

#### 2. **缓存更新不及时**

- ❌ 不要使用固定的缓存名称
- ✅ 使用版本号动态生成缓存名称

#### 3. **Service Worker 作用域**

- ❌ 不要将 Service Worker 放在子目录
- ✅ 放在根目录,scope 设置为 `/`

#### 4. **HTTPS 要求**

- ❌ 生产环境必须使用 HTTPS
- ✅ 开发环境 localhost 可以使用 HTTP

#### 5. **iOS Safari 兼容性**

- ❌ 不要依赖某些 PWA API (如 Background Sync)
- ✅ 提供降级方案

### 🎯 性能优化建议

#### 1. **预缓存优化**

```javascript
// 只预缓存关键资源
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/src/main.ts',
  '/manifest.json'
];
// 避免预缓存过多资源,影响首次加载
```

#### 2. **缓存大小控制**

```javascript
// 定期清理过期缓存
async function cleanExpiredCache() {
  const cacheNames = await caches.keys();
  const now = Date.now();
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const requests = await cache.keys();
    
    for (const request of requests) {
      const response = await cache.match(request);
      const cacheTime = response.headers.get('sw-cache-time');
      
      if (cacheTime && now - parseInt(cacheTime) > 7 * 24 * 60 * 60 * 1000) {
        await cache.delete(request);
      }
    }
  }
}
```

#### 3. **网络请求优化**

```javascript
// 使用 stale-while-revalidate 策略
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    cache.put(request, networkResponse.clone());
    return networkResponse;
  });
  
  return cachedResponse || fetchPromise;
}
```

### 📊 监控与调试

#### 1. **Chrome DevTools**

```
Application -> Service Workers
- 查看 Service Worker 状态
- 手动更新 Service Worker
- 模拟离线模式

Application -> Cache Storage
- 查看缓存内容
- 清除特定缓存

Application -> IndexedDB
- 查看本地数据
```

#### 2. **Lighthouse 审计**

```bash
# 使用 Lighthouse 检查 PWA 质量
npm install -g lighthouse
lighthouse https://your-app.com --view
```

#### 3. **日志记录**

```javascript
// Service Worker 中添加详细日志
console.log('[SW] Cache hit:', request.url);
console.log('[SW] Network response:', response.status);
console.error('[SW] Fetch failed:', error);
```

### 🔒 安全建议

#### 1. **HTTPS 强制**

```javascript
// 检测 HTTPS
if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
  location.replace(`https:${location.href.substring(location.protocol.length)}`);
}
```

#### 2. **内容安全策略 (CSP)**

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline'">
```

#### 3. **缓存敏感数据处理**

```javascript
// 不要缓存敏感数据
if (request.url.includes('/api/user') || 
    request.url.includes('/api/auth')) {
  return fetch(request); // 直接走网络,不缓存
}
```

---

## 总结

### 核心要点

1. **开发环境禁用 Service Worker** - 避免 Vite 缓存问题
2. **版本管理自动化** - 基于 package.json 自动注入版本号
3. **分层缓存策略** - 静态资源缓存优先,API 网络优先
4. **优雅的更新机制** - 检测更新并提示用户
5. **完善的离线支持** - IndexedDB + Background Sync

### 项目收益

- ✅ **离线可用**: 用户可以在无网络环境下使用应用
- ✅ **快速加载**: 静态资源从缓存加载,首屏时间显著减少
- ✅ **数据同步**: 离线操作的数据在联网后自动同步
- ✅ **原生体验**: 可安装到桌面,类似原生应用
- ✅ **自动更新**: 检测到新版本自动提示用户更新

### 参考资源

- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google - PWA 指南](https://web.dev/progressive-web-apps/)
- [Vite 官方文档](https://vitejs.dev/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache)
- [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)

---

**文档版本**: 1.0.0
**最后更新**: 2024-12-16
**项目**: LogicDrawer
**作者**: FrontEndTechPro
