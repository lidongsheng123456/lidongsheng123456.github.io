---
title: day02-Tauri桌面端框架基础
date: 2025/07/28
tags:
  - 中电软件园
categories:
  - 实习
---
# day02

# day02-Tauri桌面端框架基础

## 一.概述

1. 一个用于为所有主流桌面和移动平台构建小型快速二进制文件的框架，开发者可以集成任何人可以编译为HTML，javascript和css的前端框架来构建用户体验，用户在需要时利用Rust，Swift和Kotlin等语言实现后端逻辑。

## 二.搭建项目

1. 创建新的前后端项目：npm create tauri-app @latest ... 后续根据提示操作；
2. 在已有前端项目创建，使用Tauri Cli为项目单独初始化后端；
3. 具体流程参照官方文档：

## 三.应用场景

1. Tauri相当于一个Web主机在我们的应用程序中，可以集成任何可以编译为前端三剑客的前端框架来构建用户体验，同时使用Rust等后端语言实现后端逻辑；
2. 利用Rust可以实现操作系统开发，并与前端页面通信，从而构建出一个可视化应用程序；
3. electron的平替。

## 四.Tauri的前后端通信（后端调用前端）

1. 后端使用Rust在二进制程序中定义一个函数调用前端函数并传值，例：

```rust
#[tauri:command]
fn greet(app: AppHandle,name: &str){
    app.emit("test-event",name).unwrap(); // 调用前端自定义事件
}
```

b.前端使用Tauri提供的函数监听事件，例：

```javascript
listen("test-event",(payload)=>{
    console.log(payload);
})
// 注意：后端要导入Tauri的包，例：use tauri::{AppHandle,Emitter};
//       前端要导Tauri的包，例：import{listen} from "@tauri-apps/api/event";
```

## 五.Tauri的前后端通信（前端调后端）

1. 前端示例

```javascript
import {invoke} from "@/tauri-apps/api/core";

async greet()=>{
    let data await invoke("greet",{name:"Hello"});
    console.log(data) // Hello Hello
}
```

b.后端示例

```rust
fn greet(name: &str)->String{
    format!("Hello,{}",name)
}
```

## 六.Tauri前后端是如何通信的

1. 通过全局事件系统和API桥接实现双向通信；
2. 全局事件通信：Rust代码可通过发送全局事件（如：app.emit）将消息传给前端，前端通过listen函数监听这个事件并调用回调函数；
3. API桥接交互：前端通过Tauri提供的invoke函数调用Rust代码（如：invoke（"test",{message:"Hello Rust"}）），Rust通过test函数接收消息并回传响应。
