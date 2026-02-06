---
title: 用 Gitea Actions 实现 CI/CD：从构建到阿里云部署
date: 2026-02-06
tags:
 - gitea
 - ci/cd
 - vuepress
 - bun
categories:
 - 实习
---

这篇记录基于当前仓库的 `deploy.yml`，完整走一遍 Gitea Actions 的 CI/CD 思路：拉代码 → 安装依赖 → 构建 → 上传到服务器 → 执行部署后命令。

## ✅ 1. 工作流入口与触发方式

这个 workflow 放在 `.gitea/workflows/deploy.yml`，触发条件是：

- 推送到 `main` 分支时自动构建部署
- 也支持在 Gitea Web 手动触发（`workflow_dispatch`）

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
```

---

## ✅ 2. Runner 运行环境

本仓库的 workflow 使用 `bun` 作为 runner 环境：

```yaml
jobs:
  build-and-deploy:
    runs-on: bun
```

如果你的 Gitea Runner 是自建的，需要确保该 runner 能识别 `bun` 标签，并且机器上已安装 Bun。

---

## ✅ 3. 核心流程拆解

### ① 检出代码

```yaml
- name: 📋 检出代码仓库
  uses: http://192.168.192.1:3000/git/checkout@main
  with:
    fetch-depth: 0
    ref: main
```

### ② 安装依赖

```yaml
- name: 📦 安装依赖
  run: bun install --force
```

### ③ 构建项目

```yaml
- name: 🔨 构建项目
  run: bun run build
```

VuePress 构建产物输出到：

```
.vuepress/dist/
```

### ④ 上传构建产物到阿里云

```yaml
- name: 📤 上传到阿里云服务器
  uses: http://192.168.192.1:3000/git/scp-action@master
  with:
    host: ${{ secrets.ALIYUN_HOST }}
    username: ${{ secrets.ALIYUN_USERNAME }}
    password: ${{ secrets.ALIYUN_PASSWORD }}
    port: ${{ secrets.ALIYUN_PORT }}
    source: ".vuepress/dist/*"
    target: /home/server/lds_blog
```

### ⑤ 执行部署后命令（可选）

```yaml
- name: ✅ 执行部署后命令
  uses: http://192.168.192.1:3000/git/ssh-action@master
  with:
    host: ${{ secrets.ALIYUN_HOST }}
    username: ${{ secrets.ALIYUN_USERNAME }}
    password: ${{ secrets.ALIYUN_PASSWORD }}
    port: ${{ secrets.ALIYUN_PORT }}
    script: |
      echo "Deployment completed at $(date)"
```

---

## ✅ 4. 必须配置的 Secrets

在 Gitea 仓库里添加以下 Secrets：

- `ALIYUN_HOST`
- `ALIYUN_USERNAME`
- `ALIYUN_PASSWORD`
- `ALIYUN_PORT`

这些值会在 `scp-action` / `ssh-action` 中被自动注入。

---

## ✅ 5. 常见踩坑

- **Runner 没有 bun**：构建步骤直接失败，Runner 需要提前装好 Bun
- **没有配置 Secrets**：上传和 SSH 步骤会报错
- **构建路径不对**：VuePress 构建默认产物是 `.vuepress/dist`，上传路径一定要对齐

---

## ✅ 6. 最终效果

推送代码 → 自动构建 → 构建产物上传到服务器目录 `/home/server/lds_blog` → 页面更新完成。

---