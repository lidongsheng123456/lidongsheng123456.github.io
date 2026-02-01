---
title: day05-Langium通过ts定义DSL和状态机的框架
date: 2025/07/21
tags:
  - 中电软件园
categories:
  - 实习
---
# day05

# day05-Langium通过ts定义DSL和状态机的框架

## 一.概述

1. 一个语言工程框架，采用TypeScript编写并在node.js环境下运行，它的主要目标是降低创建领域专用语言（DSL）或低代码平台的门槛。

## 二.应用场景

1. 领域专用语言（DSL）开发，包括：软件开发，数据建模，领域专用编程语言；
2. 多平台语言支持；
3. 命令行工具开发：可以将Langium的DSL打包成命令行界面创建丰富的互联工具集：验证器，解释器，代码生成器，服务适配器...。

## 三.优势

1. 代码生成：支持将DSL代码自动转换为多种编程语言（java，python，c++，...）；
2. 类型安全：生成类型安全的抽象语法树（AST）。

## 四.开发DSL

1. 搭建好Langium项目之后，开始我们自己定义领域编程语言的第一步，编写语法，多种编程语言也有着属于自己的语法；
2. 语法文件通常只需要一个，例如：src/language/hello-world.langium，语法定义好之后一般在/example下面编写DSL实例文件，文件后缀由langium-config.json中的fileExtensions决定。
