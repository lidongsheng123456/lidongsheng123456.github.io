---
title: day02-实现web显示文件树结构
date: 2025/07/21
tags:
  - 中电软件园
categories:
  - 实习
---
# day02

# day02-实现web显示文件树结构

## 一.概念

Web File就是使Web应用可以访问文件和其中的内容。

## 二.文件系统树形结构实现步骤

### 1.通过File System Access API ，这是浏览器提供的原生API

### 2.代码逻辑流程

1. 通过Window.showDirctoryPicker()获取到一个FileSystemDirectoryHandle的对象，该对象具有选择文件夹的所有文件夹以及文件；
2. 此时我们需对获取到的句柄（FileSystemDirectoryHandle）进行处理，构建树形结构，句柄就是指一个对象的标识；
3. 调用句柄的.entries()方法拿到异步迭代器，使用for循环遍历迭代器，因为是异步的所以我们要用async和await暂停函数执行，等待结果，此时我们就拿到了数个FileSystemDirectoryHandle或FileSystemFileHandle区别是文件夹和文件；
4. 问题来了我们拿到的并不是一个完整的嵌套关系文件树结构，解决方案：递归处理，当这个文件夹对象调用自己时类型时文件直接push进当前文件夹的children，不是则递归调用自己直到遍历的不是文件夹才停止；
5. 疑问：怎么清楚我们push进去的是当前文件夹的，而不是其他文件夹的，经过分析得出递归的始终是自己的子节点，所以不会出错；
6. 拿到树状结构对象后，再渲染页面，页面也是递归渲染。
