---
title: day03-实现IC可视化项目拆除到自己的项目
date: 2025/07/21
tags:
  - 中电软件园
categories:
  - 实习
---
# day03

# day03-实现IC可视化项目拆除到自己的项目

## 一.概述

1. 为什么不是原项目改，因为局限性，界面丑且功能少，将项目拆分为组件后嵌入到自己的项目，就能实现随看和个性化配置。

## 二.实现思路

1. 更改环境，查看原项目的package.json将依赖的各种库以及框架使用的组件版本号全部移植到要整合的项目中，然后重新执行安装依赖命令：**npm install**​ **；**
2. 深入分析IC项目的目录结构以及业务实现的逻辑，找到切入点，开始移植，将import导入的与我选择的切入点代码块需要的库移植到自己项目进行分类管理；
3. 切入点需要的依赖以及子组件导入完毕后，解决业务逻辑报错，根据页面显示的error依次解决，不要怕麻烦，解决过程中可能需要对拆过来的代码块进行调整，这些调整需要根据实际情况。
4. 报错解决完后，可以尝试优化我们拆过来的模块跟我们自己项目的适配度.

## 三.总结

不骄不躁，脚踏实地，心态放好，仔细梳理代码逻辑。

# 关于Rust语言

## 一.概述

### 1.Rust语言是一门系统编程语言，专注于安全速度和并发，她的特点主要包括

1. 内存安全：无需垃圾回器即可防止内存泄漏；
2. 零成本抽象：高级特性不会影响运行是性能；
3. 并发安全：防止数据竞争；
4. 跨平台：支持多种操作系统和架构。

### 2.常用工具

1. rustc：Rust编译器；
2. cargo：包管理器和构建工具；
3. rustfmt：代码格式化工具；
4. clippy：代码检查工具。

### 3.基础语法

#### 3.1变量和数据类型

1. 不可变数据类型：let x = 5;
2. 可变变量：let mut y =10; y = 15;
3. 常量：const MAX_POINTS: u32 = 10_0000;
4. 整数：let integer：i32 = 42;
5. 浮点：let float：f64 = 3.14;
6. 布尔：let boolean：bool = true;
7. 字符：let char：char = 'A';
8. 字符串：let string：&str = "Hello Ruse!"。

#### 3.2函数

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b // 表达式，无需 return 关键字
}

fn main(){
    println!("Hello World")
    let result = add(5,3)
    println!("5+3={}",result)
}
```

#### 3.控制流

1. if/else；
2. loop；
3. while；
4. for
5. match；
6. if let；
7. while let。

## 二.所有权系统

### 1.所有权规则

1. Rust 中的每个值都有一个被称为其**所有者**的变量；
2. 值在任一时刻只能有一个所有者；
3. 当所有者离开作用域，这个值将被丢弃。

### 2.借用和引用

1. 创建引用的行为称为借用borrowing。引用默认是不可变的，如果我们尝试修改借用的值，会得到错误

```rust
fn main() {
    let s = String::from("hello");
    change(&s);
}

fn change(some_string: &String) {
    some_string.push_str(", world"); // 错误：不能修改借用的值
}
```

1. 如果每次传递值都转移所有权，代码会变得非常繁琐。Rust 提供了引用机制，允许我们使用值而不获取所有权

```rust
fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1); // 传递 s1 的引用
    
    println!("'{}' 的长度是 {}", s1, len); // s1 仍然可用
}

fn calculate_length(s: &String) -> usize { // s 是 String 的引用
    s.len()
} // s 离开作用域，但它不拥有引用值的所有权，所以不会释放任何东西
```

## 三.结构体和枚举

### 1.结构体

```rust
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}
 
fn main() {}
```

### 2.枚举

```rust
enum IpAddrKind {
    V4,
    V6,
}
 
fn main() {
    let four = IpAddrKind::V4;
    let six = IpAddrKind::V6;
 
    route(IpAddrKind::V4);
    route(IpAddrKind::V6);
}
 
fn route(ip_kind: IpAddrKind) {}
```

## 三.错误处理

### 1.Result类型

1. 在Rust编程中，Resu1t<T，E>是一个极其重要的枚举类型，用于处理可能成功或失败的操作。它有两个变体；
2. 0k(T):表示操作成功，包含成功的值；
3. Err(E):表示操作失败，包含错误信息!；
4. 这种设计强制开发者显式处理可能的错误情况，避免了其他语言中常见的未处理异常问题。
5. 让我们看一个简单的字符串解析为整数的例子:
6. 在这个例子中，parse方法返回一个Resu1t类型，?操作符会在遇到错误时提前返回错误，否则继续执行。

```rust
use std::num::ParseIntError;
 
fn multiply(n1_str: &str, n2_str: &str) -> Result<i32, ParseIntError> {
    let n1 = n1_str.parse::<i32>()?;  // 使用?操作符简化错误处理
    let n2 = n2_str.parse::<i32>()?;
    Ok(n1 * n2)
}
```

### 2.操作符

1. ?操作符是Rust错误处理的一大亮点，它相当于

```rust
法更加简洁。使用?可以大大减少样板代码，使错误处理更加优雅。
match result {
    Ok(v) => v,
    Err(e) => return Err(e),
}
```

1. 但语法更加简洁。使用?可以大大减少样板代码，使错误处理更加优雅。

## 四.并发编程（**待后续补充**)
