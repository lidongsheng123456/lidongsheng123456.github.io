---
title: IndexedDB 与 MySQL 对比详解
date: 2025/12/08
tags:
  - 中电软件园
categories:
  - 实习
---
# day01

# IndexedDB 与 MySQL 对比详解

## 📚 目录

- [IndexedDB 的结构层次](#indexeddb-的结构层次)
- [数据存储方式](#数据存储方式)
- [IndexedDB vs MySQL 核心区别](#indexeddb-vs-mysql-核心区别)
- [项目中的实际应用](#项目中的实际应用)
- [总结](#总结)

---

## IndexedDB 的结构层次

IndexedDB 采用以下层次结构：

```
Database (数据库)
  └── Object Store (对象存储，类似表)
        ├── Key Path (主键路径)
        ├── Index (索引)
        └── Data (数据对象)
```

### 1. Database（数据库）

- **作用**：最顶层的容器，对应项目中的 `LogicDrawerDB`
- **特点**：

  - 一个域名下可以创建多个数据库
  - 通过版本号管理结构变更
  - 每个数据库有独立的存储空间

**代码示例**：

```typescript
const dbName = 'LogicDrawerDB';
const version = 2;
const request = indexedDB.open(dbName, version);
```

### 2. Object Store（对象存储）

- **作用**：类似 MySQL 的表，但更灵活
- **项目中的 Object Store**：

  - ​`circuits`：存储电路数据
  - ​`settings`：存储用户设置
  - ​`recent`：存储最近文件
  - ​`cache`：存储缓存数据

**代码示例**：

```typescript
// 创建 Object Store
if (!db.objectStoreNames.contains('circuits')) {
    const circuitStore = db.createObjectStore('circuits', { keyPath: 'id' });
    circuitStore.createIndex('name', 'name', { unique: false });
    circuitStore.createIndex('timestamp', 'timestamp', { unique: false });
    circuitStore.createIndex('synced', 'synced', { unique: false });
}
```

### 3. Key Path（主键路径）

- **作用**：指定对象中的某个字段作为主键
- **特点**：

  - 可以是对象的任意属性
  - 支持自动生成（`autoIncrement: true`）
  - 主键值必须唯一

**代码示例**：

```typescript
// 使用 id 字段作为主键
db.createObjectStore('circuits', { keyPath: 'id' });

// 使用 key 字段作为主键
db.createObjectStore('settings', { keyPath: 'key' });
```

### 4. Index（索引）

- **作用**：为对象的非主键字段创建索引，用于快速查询
- **特点**：

  - 可以创建多个索引
  - 支持唯一索引（`unique: true`）
  - 支持复合索引（多个字段组合）

**代码示例**：

```typescript
// 为 name 字段创建索引
circuitStore.createIndex('name', 'name', { unique: false });

// 为 timestamp 字段创建索引
circuitStore.createIndex('timestamp', 'timestamp', { unique: false });
```

### 5. Transaction（事务）

- **作用**：所有操作必须在事务中进行
- **模式**：

  - ​`readonly`：只读事务，性能更好
  - ​`readwrite`：读写事务，可以修改数据
- **特点**：

  - 自动管理事务生命周期
  - 支持跨多个 Object Store 的事务

**代码示例**：

```typescript
// 创建读写事务
const transaction = db.transaction(['circuits'], 'readwrite');
const store = transaction.objectStore('circuits');
const request = store.put(circuitData);
```

---

## 数据存储方式

### IndexedDB 存储的是 JavaScript 对象

IndexedDB 直接存储 JavaScript 对象，不需要序列化（除了 Blob 等特殊类型）。

**存储示例**：

```typescript
const circuitData = {
    id: "circuit-001",
    name: "我的电路",
    data: {
        nodes: [
            { id: "node1", type: "input", position: { x: 100, y: 200 } },
            { id: "node2", type: "output", position: { x: 300, y: 200 } }
        ],
        edges: [
            { source: "node1", target: "node2" }
        ],
        config: {
            theme: "dark",
            grid: true
        }
    },
    timestamp: 1234567890,
    synced: false,
    version: "1.0"
};

// 直接存储整个对象
await store.put(circuitData);
```

### 支持的数据类型

IndexedDB 支持以下数据类型：

|类型|说明|示例|
| ------| -------------------------------| ------------------|
|**基本类型**|String, Number, Boolean, Date|​`"hello"`​, `123`​, `true`​, `new Date()`|
|**复杂类型**|Object, Array|​`{ key: "value" }`​, `[1, 2, 3]`|
|**二进制类型**|Blob, File, ImageData|​`new Blob()`​, `file object`|
|**不支持**|Function, Symbol, undefined|❌ 不能存储|

### 数据检索方式

```typescript
// 1. 通过主键获取
const circuit = await store.get("circuit-001");

// 2. 通过索引获取
const index = store.index('name');
const circuits = await index.getAll(IDBKeyRange.only('我的电路'));

// 3. 获取所有数据
const allCircuits = await store.getAll();

// 4. 使用游标遍历
const request = store.openCursor();
request.onsuccess = (event) => {
    const cursor = event.target.result;
    if (cursor) {
        console.log(cursor.value);
        cursor.continue();
    }
};
```

---

## IndexedDB vs MySQL 核心区别

### 对比表格

|特性|IndexedDB|MySQL|
| ------| --------------------------| --------------------|
|**存储位置**|浏览器本地（客户端）|服务器（服务端）|
|**数据格式**|JavaScript 对象（NoSQL）|关系型数据（SQL）|
|**查询语言**|JavaScript API|SQL 语句|
|**数据结构**|灵活的对象结构|固定的表结构（列）|
|**事务模型**|自动事务管理|手动事务控制|
|**数据类型**|支持 Blob、File 等|基本类型 + BLOB|
|**索引方式**|基于对象属性|基于列|
|**数据同步**|单机存储|多客户端共享|
|**容量限制**|浏览器配额（通常几GB）|服务器磁盘限制|
|**网络需求**|不需要网络|需要网络连接|
|**并发控制**|浏览器单线程|支持多用户并发|

### 详细对比

#### 1. 数据模型差异

**IndexedDB（NoSQL 风格）**

```typescript
// 存储的是完整的对象，结构灵活
const circuit = {
    id: "1",
    name: "电路1",
    data: {
        nodes: [...],
        edges: [...],
        config: {...}
    },
    timestamp: 1234567890,
    synced: false
};

// 直接存储整个对象
await store.put(circuit);
```

**MySQL（关系型）**

```sql
-- 需要拆分成多个表
CREATE TABLE circuits (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP,
    synced BOOLEAN DEFAULT FALSE
);

CREATE TABLE circuit_data (
    circuit_id VARCHAR(50),
    data JSON,  -- 或者拆分成更多表
    FOREIGN KEY (circuit_id) REFERENCES circuits(id)
);

-- 插入数据需要多步操作
INSERT INTO circuits (id, name, created_at, synced) 
VALUES ('1', '电路1', NOW(), FALSE);
INSERT INTO circuit_data (circuit_id, data) 
VALUES ('1', '{"nodes":[...],"edges":[...]}');
```

#### 2. 查询方式差异

**IndexedDB**

```typescript
// 使用 JavaScript API，通过索引查询
const transaction = db.transaction(['circuits'], 'readonly');
const store = transaction.objectStore('circuits');
const index = store.index('name');
const request = index.getAll(IDBKeyRange.only('电路1'));

request.onsuccess = () => {
    const circuits = request.result;
    console.log(circuits);
};
```

**MySQL**

```sql
-- 使用 SQL 语句
SELECT * FROM circuits WHERE name = '电路1';

-- 复杂查询
SELECT c.*, cd.data 
FROM circuits c 
LEFT JOIN circuit_data cd ON c.id = cd.circuit_id 
WHERE c.name LIKE '%电路%' 
ORDER BY c.created_at DESC 
LIMIT 10;
```

#### 3. 事务处理差异

**IndexedDB**

```typescript
// 自动管理事务，操作完成后自动提交或回滚
const transaction = db.transaction(['circuits'], 'readwrite');
const store = transaction.objectStore('circuits');

// 所有操作在事务中
store.put(data1);
store.put(data2);
store.delete(id);

// 事务自动管理，出错自动回滚
transaction.onerror = () => {
    console.error('事务失败，自动回滚');
};
```

**MySQL**

```sql
-- 需要手动控制事务
START TRANSACTION;

INSERT INTO circuits VALUES (...);
UPDATE circuits SET synced = TRUE WHERE id = '1';
DELETE FROM circuits WHERE id = '2';

-- 手动提交或回滚
COMMIT;  -- 或 ROLLBACK;
```

#### 4. 数据同步差异

**IndexedDB**

- ✅ 单机存储，不同浏览器/设备间不共享
- ✅ 适合离线应用、缓存、本地配置
- ✅ 数据存储在用户本地，隐私性好
- ❌ 无法跨设备同步（需要额外实现）

**MySQL**

- ✅ 服务器存储，多客户端共享
- ✅ 适合需要数据一致性的场景
- ✅ 支持多用户并发访问
- ❌ 需要网络连接，无法离线使用

#### 5. 性能特点

**IndexedDB**

- ✅ 本地访问，速度快
- ✅ 异步操作，不阻塞 UI
- ✅ 支持大量数据存储（GB 级别）
- ❌ 查询能力有限（无复杂 SQL）

**MySQL**

- ✅ 强大的查询能力（SQL）
- ✅ 支持复杂的关系查询
- ✅ 支持聚合函数、分组等
- ❌ 需要网络传输，有延迟

---

## 项目中的实际应用

### 使用场景

从 `IndexedDBManager.ts` 代码可以看到，IndexedDB 在项目中用于：

#### 1. 离线存储（Circuits）

```typescript
// 存储电路数据，支持离线编辑
async saveCircuit(circuit: Circuit): Promise<void> {
    const db = await this.ensureDB();
    const transaction = db.transaction(['circuits'], 'readwrite');
    const store = transaction.objectStore('circuits');
    await store.put(circuit);
}
```

**优势**：

- 用户可以在离线状态下编辑电路
- 数据保存在本地，加载速度快
- 支持同步标记，便于后续同步到服务器

#### 2. 缓存机制（Cache）

```typescript
// 带过期时间的缓存
async setCache(key: string, value: any, ttl: number = 3600000): Promise<void> {
    const cacheData = {
        key,
        value,
        expiry: Date.now() + ttl
    };
    await store.put(cacheData);
}
```

**优势**：

- 减少网络请求
- 支持过期时间管理
- 自动清理过期缓存

#### 3. 用户设置（Settings）

```typescript
// 存储用户偏好设置
async saveSetting(key: string, value: any): Promise<void> {
    await store.put({ key, value });
}
```

**优势**：

- 设置保存在本地，无需每次从服务器获取
- 隐私性好，用户数据不离开本地

#### 4. 最近文件（Recent Files）

```typescript
// 记录最近访问的文件
async addRecentFile(file: RecentFile): Promise<void> {
    const fileData = {
        ...file,
        timestamp: Date.now()
    };
    await store.put(fileData);
}
```

**优势**：

- 快速访问最近使用的文件
- 支持按时间排序
- 自动限制数量，避免占用过多空间

### 为什么选择 IndexedDB？

这些场景适合使用 IndexedDB，因为：

1. ✅ **数据主要在客户端使用**：电路数据、设置、缓存都是客户端本地使用
2. ✅ **需要离线访问**：PWA 应用需要离线功能
3. ✅ **不需要多用户共享**：每个用户的数据独立存储
4. ✅ **存储复杂对象**：电路数据是嵌套的 JavaScript 对象
5. ✅ **性能要求高**：本地存储访问速度快

### 典型工作流程

```typescript
// 1. 用户编辑电路（离线）
await indexedDBManager.saveCircuit(circuit);

// 2. 标记为未同步
circuit.synced = false;

// 3. 网络恢复后，同步到服务器
const unsyncedCircuits = await indexedDBManager.getUnsyncedCircuits();
for (const circuit of unsyncedCircuits) {
    await syncToServer(circuit);
    await indexedDBManager.markCircuitAsSynced(circuit.id);
}
```

---

## 总结

### IndexedDB 的定位

IndexedDB 是**浏览器的 NoSQL 数据库**，专门为客户端本地存储设计：

- 🎯 **适用场景**：离线应用、本地缓存、用户设置、PWA 应用
- 🎯 **核心优势**：本地存储、离线访问、支持复杂对象、性能好
- 🎯 **使用限制**：单机存储、查询能力有限、需要手动同步

### MySQL 的定位

MySQL 是**服务端关系型数据库**，用于持久化存储和共享数据：

- 🎯 **适用场景**：多用户系统、数据持久化、复杂查询、数据一致性
- 🎯 **核心优势**：强大的 SQL 查询、多用户并发、数据共享、事务支持
- 🎯 **使用限制**：需要网络、有延迟、不适合离线场景

### 最佳实践：两者配合使用

在实际项目中，通常**两者配合使用**：

```
┌─────────────────┐
│   用户操作      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│   IndexedDB     │◄────►│      MySQL       │
│  (本地缓存)     │ 同步  │   (服务器存储)   │
│                 │       │                 │
│ • 离线编辑      │       │ • 数据持久化    │
│ • 快速访问      │       │ • 多用户共享    │
│ • 用户设置      │       │ • 数据备份      │
└─────────────────┘      └─────────────────┘
```

**工作流程**：

1. 用户操作 → 先保存到 IndexedDB（快速响应）
2. 后台同步 → 将数据同步到 MySQL（持久化）
3. 离线场景 → 使用 IndexedDB 数据
4. 在线场景 → 从 MySQL 获取最新数据

### 关键区别总结

|维度|IndexedDB|MySQL|
| ------| ------------------| --------------------|
|**存储位置**|浏览器本地|服务器|
|**数据模型**|NoSQL（对象）|关系型（表）|
|**查询方式**|JavaScript API|SQL|
|**适用场景**|离线、缓存、本地|持久化、共享、查询|
|**数据同步**|单机|多客户端|
|**网络需求**|不需要|需要|

---

## 📖 参考资料

- [MDN - IndexedDB API](https://developer.mozilla.org/zh-CN/docs/Web/API/IndexedDB_API)
- [W3C IndexedDB Specification](https://www.w3.org/TR/IndexedDB/)
- [MySQL Official Documentation](https://dev.mysql.com/doc/)

---

*文档生成时间：2024年*  
*项目：LogicDrawer*  
*文件：IndexedDBManager.ts*
