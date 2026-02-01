---
title: day04-学习节点可视化项目
date: 2025/08/04
tags:
  - 中电软件园
categories:
  - 实习
---
# day04

# day04-学习节点可视化项目

## 一.项目目录结构详细分析

### 📁 根目录文件

- .env.static : 静态环境配置文件，包含开发模式开关等全局配置
- .eslintrc.cjs : ESLint代码规范配置
- .gitignore : Git忽略文件配置
- .prettierrc : 代码格式化配置
- package.json : 项目依赖和脚本配置
- tsconfig.json : TypeScript配置
- vue.config.js : Vue项目构建配置

### 📁 src/ - 源代码核心目录 src/components/ - Vue组件

- 通用组件 : 加载动画、导航栏、通知系统、保存菜单等UI组件
- 主要组件 : Home.vue(主界面)、Settings.vue(设置)、Terminal.vue(终端) src/core/ - 核心逻辑层
- NodeFactory.js : 节点工厂，负责创建和管理节点类型
- EditorManager.js : 编辑器管理器，处理图编辑核心逻辑
- interfaceParser.js : 接口解析器，处理节点接口定义
- Specification.js : 规范处理器，管理节点规范文件
- History.ts : 操作历史管理
- stores.js : 状态管理 src/custom/ - 自定义实现
- CustomNode.js/.vue : 自定义节点组件实现
- Editor.js/.vue : 自定义编辑器
- CustomInterface.vue : 自定义接口组件
- nodepalette/ : 节点调色板相关功能
- panZoom.js : 画布缩放和平移 src/interfaces/ - 接口定义
- 各种Interface.js/.vue : 文本输入、滑块、十六进制、列表等不同类型的输入接口
- example01.js/.vue : 示例接口实现 src/icons/ - 图标组件
- 各种SVG图标组件，如箭头、齿轮、运行按钮等

### 📁 public/ - 静态资源 public/json/ - 节点规范

- sample-specification.json : 示例节点规范
- sample-dataflow.json : 示例数据流配置
- example01.json : 自定义示例 public/boards/ - 开发板配置
- 各种硬件开发板的可视化配置（如Kria K26、K410T等）
- 每个子目录包含对应开发板的节点和连接配置 public/data/data.js : 应用数据配置，包含示例项目和开发板列表

### 📁 resources/ - 资源文件 resources/schemas/ - JSON Schema定义

- dataflow_schema.json : 数据流验证模式
- graph_schema.json : 图结构验证模式
- metadata_schema.json : 元数据验证模式 resources/api_specification/ - API规范
- specification.json : 前端与后端通信的API定义

### 📁 styles/ - 样式文件

- SCSS样式文件 : 节点、连接、编辑器、调色板等样式定义
- 变量文件 : 颜色、尺寸等全局变量

### 📁 tests/ - 测试文件

- main.spec.ts : 主要功能测试
- subgraph.spec.ts : 子图功能测试
- history.spec.ts : 历史功能测试

### 📁 patches/ - 依赖补丁

- 用于修复第三方依赖的问题

### 📁 src/third-party/ - 第三方库

- hterm_all.js : 终端模拟器库

### 📁 src/plugins/ - Vue插件

- vuetify.js : Vuetify UI框架配置

### 📁 src/router/ - 路由配置

- router.js : Vue Router路由定义

### 📁 src/static/ - 静态图片

- 应用使用的静态图片资源

### 📁 src/view/ - 视图组件

- select-dataflow.vue : 数据流选择界面
- select-specification.vue : 规范选择界面

## 二.核心工作流程

1. 节点定义 : 在JSON规范中定义节点
2. 节点加载 : 通过Specification.js加载规范
3. 节点创建 : NodeFactory.js根据规范创建节点类
4. 界面渲染 : CustomNode.vue渲染节点界面
5. 交互处理 : Editor.js处理用户交互
6. 数据验证 : 使用JSON Schema验证数据完整性

这个架构设计清晰分离了数据层、逻辑层和表现层，使得添加新节点和功能变得简单直观。

## 三.业务流程

用户进入页面 > 选择组件库 或 组件 > 可以看到很多自定义的节点也就是单片机或者电路板 > 用户自由连接各种硬件的输入输出来达成模拟的目的

这样用户不用再花费成本购买真实硬件来进行连接测试
