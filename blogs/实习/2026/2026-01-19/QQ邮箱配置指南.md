---
title: QQ邮箱配置指南
date: 2026/01/19
tags:
  - 中电软件园
categories:
  - 实习
---
# QQ邮箱配置指南

# QQ 邮箱发送邮件配置指南

## 📋 目录

- [功能说明](#功能说明)
- [前置准备](#前置准备)
- [QQ 邮箱配置步骤](#qq-邮箱配置步骤)
- [环境变量配置](#环境变量配置)
- [安装依赖](#安装依赖)
- [启动服务](#启动服务)
- [测试配置](#测试配置)
- [常见问题](#常见问题)

---

## 功能说明

本服务使用 Node.js + Express + Nodemailer 实现邮件发送功能，支持：

- ✅ 联系表单邮件发送
- ✅ 请求频率限制（防止邮件轰炸）
- ✅ 邮件格式验证
- ✅ HTML 格式邮件
- ✅ 配置健康检查

---

## 前置准备

### 1. 安装 Node.js

确保已安装 Node.js（建议 v16 或更高版本）

```bash
node --version
npm --version
```

### 2. 准备 QQ 邮箱

- 一个可用的 QQ 邮箱账号
- 开启 SMTP 服务并获取授权码

---

## QQ 邮箱配置步骤

### 步骤 1：登录 QQ 邮箱

访问 [QQ 邮箱](https://mail.qq.com/) 并登录

### 步骤 2：开启 SMTP 服务

1. 点击顶部 **设置** → **账户**
2. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务** 部分
3. 找到 **SMTP服务**，点击 **开启**

### 步骤 3：获取授权码

1. 开启 SMTP 服务时，系统会要求验证（通常是发送短信）
2. 验证成功后，QQ 邮箱会生成一个 **授权码**
3. **重要：**  复制并保存这个授权码（不是你的 QQ 密码！）

授权码格式示例：`abcdefghijklmnop`（16位字符）

### 步骤 4：记录 SMTP 配置信息

QQ 邮箱 SMTP 配置：

- **SMTP 服务器：**  `smtp.qq.com`
- **SMTP 端口：**  `465`（SSL）或 `587`（TLS）
- **用户名：**  你的 QQ 邮箱地址（如：`123456789@qq.com`）
- **密码：**  刚才获取的授权码（不是 QQ 密码）

---

## 环境变量配置

### 1. 创建 .env 文件

在 `server` 目录下创建 `.env` 文件：

```bash
cd server
```

### 2. 填写配置信息

在 `.env` 文件中添加以下内容：

```env
# 服务器端口
PORT=3001

# SMTP 邮件服务器配置（QQ 邮箱）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=你的QQ邮箱@qq.com
SMTP_PASS=你的授权码
SMTP_FROM=你的QQ邮箱@qq.com

# 接收邮件的地址（可以是同一个邮箱）
TO_EMAIL=接收邮件的邮箱@qq.com
```

### 3. 配置示例

```env
# 示例配置
PORT=3001

SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=123456789@qq.com
SMTP_PASS=abcdefghijklmnop
SMTP_FROM=123456789@qq.com

TO_EMAIL=987654321@qq.com
```

**注意事项：**

- `SMTP_USER` 和 `SMTP_FROM` 通常填写同一个邮箱
- `SMTP_PASS` 填写的是授权码，不是 QQ 密码
- `TO_EMAIL` 是接收表单邮件的邮箱，可以和发送邮箱相同
- 不要将 `.env` 文件提交到 Git（已在 `.gitignore` 中）

---

## 安装依赖

在 `server` 目录下安装依赖：

```bash
cd server
npm install
```

依赖包说明：

- `express` - Web 服务器框架
- `nodemailer` - 邮件发送库
- `cors` - 跨域支持
- `dotenv` - 环境变量管理
- `express-rate-limit` - 请求频率限制

---

## 启动服务

### 开发模式（自动重启）

```bash
npm run dev
```

### 生产模式

```bash
npm start
```

启动成功后，你会看到：

```
服务器运行在 http://localhost:3001
API 端点:
  POST /api/send-email - 发送邮件
  GET  /api/health - 健康检查
  GET  /api/test-config - 测试邮件配置
```

---

## 测试配置

### 1. 测试邮件配置

在浏览器中访问：

```
http://localhost:3001/api/test-config
```

成功响应：

```json
{
  "success": true,
  "message": "邮件配置正确"
}
```

### 2. 测试健康检查

```
http://localhost:3001/api/health
```

响应：

```json
{
  "status": "ok",
  "timestamp": "2026-01-19T...",
  "service": "pilot-sim-home-server"
}
```

### 3. 测试发送邮件

使用 Postman 或 curl 测试：

```bash
curl -X POST http://localhost:3001/api/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "phone": "13800138000",
    "email": "test@example.com",
    "industry": "互联网",
    "message": "这是一条测试消息"
  }'
```

成功响应：

```json
{
  "success": true,
  "message": "邮件发送成功",
  "messageId": "<...>"
}
```

---

## 常见问题

### Q1: 提示 "邮件配置错误"

**原因：**  环境变量未正确配置

**解决：**

1. 检查 `.env` 文件是否存在
2. 确认所有必填字段都已填写
3. 重启服务器

### Q2: 提示 "Invalid login" 或 "Authentication failed"

**原因：**  授权码错误或 SMTP 服务未开启

**解决：**

1. 确认使用的是授权码，不是 QQ 密码
2. 检查 QQ 邮箱是否已开启 SMTP 服务
3. 重新生成授权码并更新 `.env`

### Q3: 邮件发送失败，提示连接超时

**原因：**  端口或网络问题

**解决：**

1. 尝试更换端口（465 或 587）
2. 检查防火墙设置
3. 确认网络可以访问 `smtp.qq.com`

### Q4: 提示 "请求过于频繁"

**原因：**  触发了频率限制（15分钟内超过5次）

**解决：**

- 等待 15 分钟后重试
- 或修改 `server.js` 中的 `emailLimiter` 配置

### Q5: 收不到邮件

**检查项：**

1. 查看垃圾邮件箱
2. 确认 `TO_EMAIL` 配置正确
3. 检查服务器日志是否有错误
4. 使用 `/api/test-config` 验证配置

### Q6: 端口 465 和 587 的区别

- **465 端口：**  使用 SSL 加密（推荐）
- **587 端口：**  使用 TLS 加密

两者都可以使用，如果一个不行可以尝试另一个。

---

## API 接口说明

### POST /api/send-email

发送邮件接口

**请求体：**

```json
{
  "name": "姓名（必填）",
  "phone": "电话（必填）",
  "email": "邮箱（必填）",
  "industry": "行业（可选）",
  "message": "需求描述（必填）"
}
```

**限流规则：**  15分钟内最多 5 次请求

**响应：**

```json
{
  "success": true,
  "message": "邮件发送成功",
  "messageId": "..."
}
```

---

## 安全建议

1. ✅ 不要将 `.env` 文件提交到版本控制
2. ✅ 定期更换授权码
3. ✅ 使用环境变量管理敏感信息
4. ✅ 启用请求频率限制
5. ✅ 在生产环境中使用 HTTPS
6. ✅ 验证用户输入，防止注入攻击

---

## 生产部署建议

1. 使用 PM2 管理进程：

    ```bash
    npm install -g pm2
    pm2 start server.js --name pilot-sim-server
    ```
2. 配置反向代理（Nginx）
3. 使用 HTTPS
4. 设置日志记录
5. 配置监控和告警

---

## 技术支持

如有问题，请检查：

1. Node.js 版本是否符合要求
2. 依赖是否正确安装
3. 环境变量是否正确配置
4. QQ 邮箱 SMTP 服务是否开启
5. 授权码是否正确

---

**最后更新：**  2026-01-19
