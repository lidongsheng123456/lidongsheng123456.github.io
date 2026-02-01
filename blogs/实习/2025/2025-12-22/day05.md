---
title: Day05 - Python创建MCP服务器项目总结
date: 2025/12/22
tags:
  - 中电软件园
categories:
  - 实习
---
# day05

# Day05 - Python创建MCP服务器项目总结

## 🎯 项目概述

本项目是一个基于Python的MCP（Model Context Protocol）服务器，名为`web-manage-mcp`，主要功能包括豆瓣API调用和通用Java API的CRUD操作。

## 📁 项目结构

```
web_manage_mcp/
├── web_manage_mcp_server/          # 主代码包
│   ├── apis/                       # API调用模块
│   │   ├── douban_api.py          # 豆瓣API实现
│   │   └── java_api.py            # Java API通用客户端
│   ├── tools/                      # MCP工具模块
│   │   ├── douban_tools.py        # 豆瓣MCP工具
│   │   └── java_tools.py          # Java API MCP工具
│   └── utils/                      # 工具模块
│       └── config.py              # 配置管理
├── scripts/                        # 脚本目录
├── tests/                          # 测试目录
├── main.py                         # MCP服务器主程序
├── run_server.py                   # 启动脚本
├── pyproject.toml                  # 项目配置
└── config.json                     # 服务器配置文件
```

## 🛠️ 技术栈

- **MCP协议**: Model Context Protocol - AI系统与外部工具的标准连接协议
- **HTTP客户端**: httpx - 现代异步HTTP客户端
- **数据验证**: pydantic - Python数据验证库
- **异步编程**: asyncio - Python异步编程框架
- **请求限流**: asyncio-throttle - 异步请求限流
- **项目管理**: uv - 现代Python包管理工具

## 🚀 MCP服务器创建步骤

### 1. 项目初始化

```bash
# 创建项目目录
mkdir web_manage_mcp
cd web_manage_mcp

# 初始化Python项目
uv init
```

### 2. 依赖配置 (pyproject.toml)

```toml
[project]
name = "web-manage-mcp"
version = "0.1.0"
description = "Douban API MCP Server"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.24.0", 
    "pydantic>=2.0.0",
    "asyncio-throttle>=1.0.0"
]
```

### 3. 核心MCP服务器实现 (main.py)

```python
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

# 创建MCP服务器实例
server = Server("web-manage-mcp")

@server.list_tools()
async def handle_list_tools():
    """列出可用工具"""
    return [...]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """处理工具调用"""
    # 工具调用逻辑
    pass

async def main():
    """启动MCP服务器"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, ...)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 CRUD操作实现

### 豆瓣API工具 (增删改查)

#### 增 - 添加收藏

```python
@tool("add_favorite")
async def add_favorite(item_type: str, item_id: str, title: str, rating: str = None, comment: str = None):
    """添加收藏到豆瓣"""
    favorite = Favorite(
        item_type=item_type,
        item_id=item_id, 
        title=title,
        rating=rating,
        comment=comment
    )
    return await douban_api.add_favorite(favorite)
```

#### 删 - 删除收藏

```python
@tool("delete_favorite")
async def delete_favorite(favorite_id: str):
    """删除豆瓣收藏"""
    return await douban_api.delete_favorite(favorite_id)
```

#### 改 - 更新收藏

```python
@tool("update_favorite")
async def update_favorite(favorite_id: str, rating: str = None, comment: str = None):
    """更新豆瓣收藏"""
    return await douban_api.update_favorite(favorite_id, rating, comment)
```

#### 查 - 查询收藏

```python
@tool("get_favorite")
async def get_favorite(favorite_id: str):
    """获取收藏详情"""
    return await douban_api.get_favorite(favorite_id)

@tool("list_favorites") 
async def list_favorites(item_type: str = None):
    """列出收藏列表"""
    return await douban_api.list_favorites(item_type)
```

### Java API工具 (通用CRUD)

#### 增 - 创建资源

```python
@tool("java_create_item")
async def java_create_item(api_name: str, endpoint: str, data: dict):
    """创建资源 (POST)"""
    api_client = api_manager.get_api(api_name)
    return await api_client.post(endpoint, json=data)
```

#### 删 - 删除资源

```python
@tool("java_delete_item")
async def java_delete_item(api_name: str, endpoint: str, item_id: str):
    """删除资源 (DELETE)"""
    api_client = api_manager.get_api(api_name)
    return await api_client.delete(f"{endpoint}/{item_id}")
```

#### 改 - 更新资源

```python
@tool("java_update_item")
async def java_update_item(api_name: str, endpoint: str, item_id: str, data: dict):
    """更新资源 (PUT)"""
    api_client = api_manager.get_api(api_name)
    return await api_client.put(f"{endpoint}/{item_id}", json=data)

@tool("java_patch_item")
async def java_patch_item(api_name: str, endpoint: str, item_id: str, data: dict):
    """部分更新 (PATCH)"""
    api_client = api_manager.get_api(api_name)
    return await api_client.patch(f"{endpoint}/{item_id}", json=data)
```

#### 查 - 查询资源

```python
@tool("java_get_item")
async def java_get_item(api_name: str, endpoint: str, item_id: str = None, params: dict = None):
    """获取资源 (GET)"""
    api_client = api_manager.get_api(api_name)
    url = f"{endpoint}/{item_id}" if item_id else endpoint
    return await api_client.get(url, params=params)

@tool("java_list_items")
async def java_list_items(api_name: str, endpoint: str, params: dict = None):
    """列出资源列表"""
    api_client = api_manager.get_api(api_name)
    return await api_client.get(endpoint, params=params)
```

## 🔌 MCP客户端配置

### Claude Desktop配置

```json
{
  "mcpServers": {
    "web-manage-mcp": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "D:/idea_project/my_project/web_manage_mcp"
    }
  }
}
```

### Cursor配置

```json
{
  "mcpServers": {
    "web-manage-mcp": {
      "command": "python",
      "args": ["D:/idea_project/my_project/web_manage_mcp/main.py"],
      "cwd": "D:/idea_project/my_project/web_manage_mcp",
      "env": {
        "PYTHONPATH": "D:/idea_project/my_project/web_manage_mcp"
      }
    }
  }
}
```

## 📋 可用工具列表

### 豆瓣API工具

|工具名称|操作类型|描述|参数|
| ----------| ----------| --------------| ----------------------|
|​`search_movies`|查|搜索电影|​`query`​, `count?`|
|​`get_movie_detail`|查|获取电影详情|​`movie_id`|
|​`search_books`|查|搜索图书|​`query`​, `count?`|
|​`add_favorite`|增|添加收藏|​`item_type`​, `item_id`​, `title`​, `rating?`​, `comment?`|
|​`get_favorite`|查|获取收藏详情|​`favorite_id`|
|​`list_favorites`|查|列出收藏列表|​`item_type?`|
|​`update_favorite`|改|更新收藏|​`favorite_id`​, `rating?`​, `comment?`|
|​`delete_favorite`|删|删除收藏|​`favorite_id`|

### Java API工具

|工具名称|操作类型|描述|参数|
| ----------| ----------| -------------------| ----------------------|
|​`java_add_api`|配置|添加API配置|​`name`​, `base_url`​, `auth_token?`​, `timeout?`​, `headers?`|
|​`java_create_item`|增|创建资源 (POST)|​`api_name`​, `endpoint`​, `data`|
|​`java_get_item`|查|获取资源 (GET)|​`api_name`​, `endpoint`​, `item_id?`​, `params?`|
|​`java_update_item`|改|更新资源 (PUT)|​`api_name`​, `endpoint`​, `item_id`​, `data`|
|​`java_patch_item`|改|部分更新 (PATCH)|​`api_name`​, `endpoint`​, `item_id`​, `data`|
|​`java_delete_item`|删|删除资源 (DELETE)|​`api_name`​, `endpoint`​, `item_id`|
|​`java_list_items`|查|列出资源列表|​`api_name`​, `endpoint`​, `params?`|
|​`java_search_items`|查|搜索资源|​`api_name`​, `endpoint`​, `query`​, `params?`|
|​`java_batch_operation`|批量|批量操作|​`api_name`​, `endpoint`​, `operation`​, `items`|
|​`java_list_apis`|查|列出已配置的API|无|

## 🚀 启动和使用

### 1. 安装依赖

```bash
uv sync
```

### 2. 启动服务器

```bash
# 方式1: 直接运行
python main.py

# 方式2: 使用启动脚本
python run_server.py

# 方式3: 使用uv脚本
uv run start-server
```

### 3. 测试API

```bash
python tests/test_apis.py
```

## 💡 使用示例

### 豆瓣API使用

```javascript
// 搜索电影
search_movies({
  "query": "肖申克的救赎",
  "count": 5
})

// 添加收藏
add_favorite({
  "item_type": "movie",
  "item_id": "1292052", 
  "title": "肖申克的救赎",
  "rating": "9.7",
  "comment": "经典电影"
})
```

### Java API使用

```javascript
// 添加API配置
java_add_api({
  "name": "my_api",
  "base_url": "https://api.example.com",
  "auth_token": "your_token_here"
})

// 创建资源
java_create_item({
  "api_name": "my_api",
  "endpoint": "users",
  "data": {
    "name": "张三",
    "email": "zhangsan@example.com"
  }
})
```

## 🔧 配置管理

服务器配置文件 `config.json`:

```json
{
  "server": {
    "name": "web-manage-mcp",
    "version": "1.0.0",
    "debug": false
  },
  "apis": {
    "douban": {
      "enabled": true,
      "rate_limit": 10
    },
    "java": {
      "enabled": true,
      "rate_limit": 30
    }
  },
  "storage": {
    "type": "memory",
    "file_path": "data.json"
  }
}
```

## 📈 扩展开发

### 添加新的API模块

1. 在 `web_manage_mcp_server/apis/` 创建新的API客户端
2. 在 `web_manage_mcp_server/tools/` 创建对应的MCP工具
3. 在 `main.py` 中注册新工具
4. 更新配置文件支持新API

## 🎯 总结

通过Python创建MCP服务器的关键步骤：

1. **项目结构设计** - 模块化设计，分离API调用和MCP工具
2. **MCP协议实现** - 使用mcp库实现标准协议
3. **CRUD操作封装** - 将HTTP API封装为MCP工具
4. **异步编程** - 使用asyncio提高性能
5. **配置管理** - 动态配置支持多API
6. **客户端集成** - 支持多种AI编辑器

这个项目展示了如何将传统的REST API转换为MCP工具，让AI助手能够直接调用外部服务进行数据操作。
