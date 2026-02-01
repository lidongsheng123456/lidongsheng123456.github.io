---
title: d
date: 2025/08/25
tags:
  - 中电软件园
categories:
  - 实习
---
# day01

## 一.PlatformIO共有模块

1. 顶部菜单
2. 控制上下页
3. 个人中心
4. 首页
5. 创建新项目
6. 导入Arduino项目
7. 打开项目
8. 项目示例
9. 最新资讯
10. 最近的项目
11. 项目
12. 添加现有项目
13. 创建新项目
14. 搜索项目
15. 配置项目
16. 项目检查
17. 选择已有项目和环境进行检查
18. 检查后的报告包含内存使用信息，并以可视化的方式详细呈现内存利用率，有助于定位和改进应用程序中占用大量内存的部分，例如符号或函数
19. 静态代码分析报告有助于在调试之前发现并修复软件缺陷。
20. 图书馆
22. 开发板资源管理器
23. 显示平台收集的1545块开发板
24. 平台
25. 显示已安装的平台
26. 嵌入式平台
27. 桌面平台
28. 框架平台
29. 设备
30. 串行设备
31. 本地硬盘设备
32. 多播DNS

顶部、底部、侧边栏固定组件，以上八个工作区路由跳转实现

## 二.FUXA：HMI-SCADA-Dashboard 基于Web的可视化平台

**简介**

**项目结构分析**

| 目录/文件 | 描述 |

|----------|------|

|

| client/src/app/ | Angular应用主要源代码 |

| client/src/app/alarms/ | 报警管理模块 |

| client/src/app/device/ | 设备管理模块 |

| client/src/app/editor/ | 编辑器模块 |

| client/src/app/fuxa-view/ | FUXA视图组件 |

| client/src/app/gauges/ | 仪表盘组件 |

|

| server/api/ | REST API接口 |

| server/runtime/ | 运行时环境 |

| server/runtime/devices/ | 设备驱动和连接 |

| server/runtime/alarms/ | 报警处理逻辑 |

| server/runtime/storage/ | 数据存储模块 |

|

|

|

|

**技术栈：**

| 层级 | 技术 | 版本 |

|-----|------|------|

| 前端框架 | Angular | 16.2.12 |

| UI组件库 | Angular Material | 16.2.13 |

| 图表库 | Chart.js | 3.9.1 |

| 状态管理 | RxJS | 7.8.0 |

| 后端框架 | Node.js + Express | 4.21.2 |

| 实时通信 | Socket.IO | 4.5.0 |

| 数据库 | SQLite3 | 5.1.5 |

| 设备协议 | OPC UA, Modbus, MQTT | - |

| 报表生成 | PDFMake | 0.2.5/0.2.7 |

**主要功能模块**

| 模块 | 功能描述 |

|-----|---------|

| 设备管理 | 支持多种工业协议(OPC UA, Modbus, MQTT等)的设备连接和管理 |

| 编辑器 | 可视化HMI/SCADA界面设计工具 |

| 报警系统 | 报警配置、监控和通知 |

| 数据采集 | 实时数据采集和历史数据存储 |

| 图表展示 | 数据可视化和趋势分析 |

| 用户管理 | 用户权限和认证系统 |

| 脚本引擎 | 自定义脚本执行 |

| 报表系统 | 自定义报表生成 |

**项目特点：**

- 跨平台支持(Windows, Linux, macOS)
- 支持多种工业通信协议
- 可视化编辑器设计HMI/SCADA界面
- 实时数据监控和历史数据趋势分析
- 报警管理和通知系统
- 用户权限管理
- 可作为Web应用或桌面应用部署

**连接的设备可选通信方式如下： **

- OPCUA
- BACnet
- ModbusRTU
- ModbusTCP
- WebAPI
- MQTTclient
- internal
- ODBC
- ADSclent
