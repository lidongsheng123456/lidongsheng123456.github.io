---
title: Langium脚手架核心工作流程学习指南
date: 2025/08/11
tags:
  - 中电软件园
categories:
  - 实习
---
# Langium脚手架核心工作流程学习指南

# Langium 脚手架核心工作流程学习指南

本指南基于 MiniLogo 项目，详细介绍 Langium 开发的完整工作流程和具体命令。

## 目录

1. [项目概述](#项目概述)
2. [步骤3: 编写语法](#步骤3-编写语法)
3. [步骤4: 生成AST](#步骤4-生成ast)
4. [步骤5: 解决交叉引用](#步骤5-解决交叉引用)
5. [步骤6: 创建验证](#步骤6-创建验证)
6. [步骤7: 生成工件](#步骤7-生成工件)
7. [完整开发流程](#完整开发流程)
8. [项目结构说明](#项目结构说明)
9. [常用命令速查](#常用命令速查)

## 项目概述

MiniLogo 是一个基于 Langium 框架开发的简单绘图语言，支持：

- 基本绘图命令（移动、画笔控制、颜色设置）
- 函数定义和调用
- 循环控制结构
- 表达式计算

## 步骤3: 编写语法

### 3.1 创建语法文件

语法文件位置：`packages/language/src/minilogo.langium`

### 3.2 安装开发工具

```bash
# 安装 Langium VS Code 扩展
# 在 VS Code 扩展市场搜索 "Langium" 并安装
```

### 3.3 语法文件结构

```langium
// 语法声明
grammar MinLogo

// 入口点定义
entry Model:(stmts+=Stmt | defs+=Def)*;

// 语句类型
Stmt: Cmd | Macro;

// 基本命令
Cmd: Pen | Move | Color | For;

// 函数调用（交叉引用）
Macro: def=[Def:ID] '(' (args+=Expr (',' args+=Expr)*)? ')';

// 函数定义
Def: 'def' name=ID '(' (params+=Param (','  params+=Param)*)? ')' Block;

// 词法规则
terminal ID returns string: /[_a-zA-Z][\w_]*/;
terminal INT returns number: /-?[0-9]+/;
terminal HEX returns string: /#(\d|[a-fA-F])+/;
```

### 3.4 关键语法概念

- **entry**: 定义语言的入口点
- **terminal**: 词法规则，定义基本的词法单元
- **fragment**: 可重用的语法片段
- **交叉引用**: `def=[Def:ID]` 用于引用其他语言元素
-  **+=** : 表示可以有多个元素的列表
-  **?** : 表示可选元素
-  **|** : 表示选择（或）

### 3.5 语法验证

保存 `.langium` 文件时，VS Code 扩展会自动检查语法错误并提供：

- 语法高亮
- 代码补全
- 错误提示
- 语法验证

## 步骤4: 生成AST

### 4.1 核心命令

```bash
# 在项目根目录执行
# 生成 AST 和相关文件（一次性生成）
npm run langium:generate

# 或者在 language 包目录下直接运行
cd packages/language
langium generate

# 监听模式（文件变化时自动重新生成）
npm run langium:watch
```

### 4.2 配置文件

`packages/language/langium-config.json`:

```json
{
    "projectName": "MiniLogo",
    "languages": [
        {
            "id": "minilogo",
            "grammar": "src/minilogo.langium",
            "fileExtensions": ["minilogo"],
            "textMate": {
                "out": "syntaxes/minilogo.tmLanguage.json"
            }
        }
    ],
    "out": "src/generated"
}
```

### 4.3 生成的文件

生成过程会在 `src/generated/` 目录下创建：

- `ast.ts` - AST 类型定义和接口
- `grammar.ts` - 语法解析器实现
- `module.ts` - 语言模块配置
- `index.ts` - 导出文件

### 4.4 AST 结构示例

```typescript
// 生成的 AST 接口示例
export interface Model extends AstNode {
    readonly $type: 'Model';
    defs: Def[];
    stmts: Stmt[];
}

export interface Def extends AstNode {
    readonly $type: 'Def';
    name: string;
    params: Param[];
    body: Stmt[];
}
```

## 步骤5: 解决交叉引用

### 5.1 自动处理机制

Langium 会自动处理语法中定义的交叉引用：

```langium
// 函数调用引用函数定义
Macro: def=[Def:ID] '(' (args+=Expr (',' args+=Expr)*)? ')';

// 变量引用参数定义
Ref: val=[Param:ID];
```

### 5.2 交叉引用类型

1. **本地引用**: 同一文件内的引用
2. **全局引用**: 跨文件的引用
3. **作用域引用**: 特定作用域内的引用

### 5.3 验证交叉引用

```bash
# 构建项目以验证交叉引用解析
npm run build

# 如果有交叉引用错误，会在构建时报告
```

### 5.4 自定义作用域提供者

如需自定义引用解析逻辑，可以实现 `ScopeProvider`：

```typescript
export class MiniLogoScopeProvider extends DefaultScopeProvider {
    override getScope(context: ReferenceInfo): Scope {
        // 自定义作用域解析逻辑
        return super.getScope(context);
    }
}
```

## 步骤6: 创建验证

### 6.1 验证器结构

在 `src/validation/` 目录下创建验证规则：

```typescript
// minilogo-validator.ts
import { ValidationAcceptor, ValidationChecks } from 'langium';
import { Def, Ref, MiniLogoAstType } from '../generated/ast.js';

export function registerValidationChecks(services: MiniLogoServices) {
    const registry = services.validation.ValidationRegistry;
    const validator = services.validation.MiniLogoValidator;
    const checks: ValidationChecks<MiniLogoAstType> = {
        Def: validator.checkUniqueDefNames,
        Ref: validator.checkParameterUsage
    };
    registry.register(checks, validator);
}

export class MiniLogoValidator {
    checkUniqueDefNames(def: Def, accept: ValidationAcceptor): void {
        // 检查函数名是否唯一
        const model = def.$container;
        if (model && model.$type === 'Model') {
            const duplicates = model.defs.filter(d => d.name === def.name);
            if (duplicates.length > 1) {
                accept('error', `函数名 '${def.name}' 重复定义`, {
                    node: def,
                    property: 'name'
                });
            }
        }
    }

    checkParameterUsage(ref: Ref, accept: ValidationAcceptor): void {
        // 检查参数是否在作用域内
        if (!ref.val || ref.val.$refText === undefined) {
            accept('error', `未定义的参数引用`, {
                node: ref,
                property: 'val'
            });
        }
    }
}
```

### 6.2 注册验证器

在语言模块中注册验证器：

```typescript
// module.ts
import { registerValidationChecks } from './validation/minilogo-validator.js';

export const MiniLogoModule: Module<MiniLogoServices, PartialLangiumServices> = {
    validation: {
        MiniLogoValidator: () => new MiniLogoValidator()
    }
};

export function createMiniLogoServices(context: DefaultSharedModuleContext): MiniLogoServices {
    const shared = inject(createDefaultSharedModule(context), MiniLogoGeneratedSharedModule);
    const MiniLogo = inject(createDefaultModule({ shared }), MiniLogoGeneratedModule, MiniLogoModule);
    shared.ServiceRegistry.register(MiniLogo);
    registerValidationChecks(MiniLogo);
    return MiniLogo;
}
```

### 6.3 测试验证

```bash
# 运行验证测试
npm run test

# 创建测试文件
# test/validation.test.ts
```

## 步骤7: 生成工件

### 7.1 CLI 工具开发

项目的 CLI 包用于代码生成，位于 `packages/cli/`：

```bash
# 构建 CLI 工具
npm run build

# 使用 CLI 生成代码
node packages/cli/bin/cli.js generate example/test.minilogo
```

### 7.2 代码生成器实现

在 `packages/cli/src/generator.ts` 中实现：

```typescript
import { CompositeGeneratorNode, toString } from 'langium';
import { Model } from 'minilogo-language';

export function generateJavaScript(model: Model): string {
    const fileNode = new CompositeGeneratorNode();
    
    fileNode.append('// Generated JavaScript code', NL);
    fileNode.append('const canvas = document.getElementById("canvas");', NL);
    fileNode.append('const ctx = canvas.getContext("2d");', NL, NL);
    
    // 生成函数定义
    model.defs.forEach(def => {
        generateFunction(def, fileNode);
    });
    
    // 生成主程序
    model.stmts.forEach(stmt => {
        generateStatement(stmt, fileNode);
    });
    
    return toString(fileNode);
}

function generateFunction(def: Def, fileNode: CompositeGeneratorNode): void {
    fileNode.append(`function ${def.name}(`, ...def.params.map(p => p.name).join(', '), ') {', NL);
    fileNode.indent(body => {
        def.body.forEach(stmt => generateStatement(stmt, body));
    });
    fileNode.append('}', NL, NL);
}
```

### 7.3 HTML 生成器

```typescript
export function generateHTML(model: Model): string {
    return `<!DOCTYPE html>
<html>
<head>
    <title>MiniLogo Output</title>
</head>
<body>
    <canvas id="canvas" width="800" height="600"></canvas>
    <script>
${generateJavaScript(model)}
    </script>
</body>
</html>`;
}
```

## 完整开发流程

### 开发环境设置

```bash
# 1. 克隆或创建项目
git clone <repository-url>
cd hello-world

# 2. 安装依赖
npm install

# 3. 初始构建
npm run build:clean
```

### 日常开发命令

```bash
# 开发模式（推荐开启两个终端）
# 终端1：监听语法文件变化
npm run langium:watch

# 终端2：监听 TypeScript 文件变化
npm run watch

# 单次构建
npm run build

# 清理重建
npm run build:clean

# 运行测试
npm run test

# 生成代码
node packages/cli/bin/cli.js generate example/test.minilogo
```

### 调试流程

1. **语法错误**: 检查 `.langium` 文件语法
2. **生成错误**: 运行 `npm run langium:generate` 查看错误信息
3. **构建错误**: 运行 `npm run build` 查看 TypeScript 编译错误
4. **运行时错误**: 检查生成的代码和验证逻辑

## 项目结构说明

```
hello-world/
├── packages/
│   ├── language/              # 语言核心包
│   │   ├── src/
│   │   │   ├── minilogo.langium      # 语法定义
│   │   │   ├── generated/            # 生成的文件
│   │   │   ├── validation/           # 验证规则
│   │   │   └── index.ts              # 入口文件
│   │   ├── test/                     # 测试文件
│   │   └── langium-config.json       # Langium 配置
│   ├── cli/                   # 命令行工具包
│   │   ├── src/
│   │   │   ├── cli.ts               # CLI 入口
│   │   │   ├── generator.ts         # 代码生成器
│   │   │   └── main.ts              # 主逻辑
│   │   └── bin/
│   │       └── cli.js               # 可执行文件
│   └── extension/             # VS Code 扩展包
│       ├── src/
│       └── package.json
├── example/
│   └── test.minilogo          # 示例文件
├── generated/                 # 生成的输出文件
├── package.json               # 根包配置
└── tsconfig.json              # TypeScript 配置
```

### 包的职责分工

- **language**: 语言的核心实现（语法、AST、验证、服务）
- **cli**: 命令行工具，用于代码生成和文件处理
- **extension**: VS Code 扩展，提供编辑器支持

## 常用命令速查

### 构建相关

```bash
npm run build                  # 构建所有包
npm run build:clean            # 清理后构建
npm run clean                  # 清理构建文件
npm run watch                  # 监听模式构建
```

### Langium 相关

```bash
npm run langium:generate       # 生成 AST 文件
npm run langium:watch          # 监听语法文件变化
langium generate               # 直接调用 Langium CLI
langium generate --watch       # Langium CLI 监听模式
```

### 测试相关

```bash
npm run test                   # 运行所有测试
npm run test --workspace packages/language  # 运行特定包的测试
```

### 代码生成

```bash
# 使用 CLI 生成代码
node packages/cli/bin/cli.js generate <input-file>

# 示例
node packages/cli/bin/cli.js generate example/test.minilogo
```

### 开发工具

```bash
# 安装 VS Code 扩展开发依赖
npm install --workspace packages/extension

# 打包扩展
npm run package --workspace packages/extension
```

## 最佳实践

### 1. 语法设计

- 保持语法简洁明了
- 合理使用交叉引用
- 注意运算符优先级
- 添加充分的注释

### 2. 验证规则

- 提供清晰的错误信息
- 覆盖常见的语义错误
- 性能优化（避免重复计算）

### 3. 代码生成

- 生成可读的目标代码
- 处理边界情况
- 提供调试信息
- 支持多种输出格式

### 4. 测试策略

- 单元测试覆盖核心功能
- 集成测试验证端到端流程
- 性能测试确保扩展性
