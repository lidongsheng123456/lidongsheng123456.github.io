---
title: day01-将自己的web服务集成在Vscode中和PWA的学习
date: 2025/07/28
tags:
  - 中电软件园
categories:
  - 实习
---
# day01

# day01-将自己的web服务集成在Vscode中和PWA的学习

## 一.vscode插件制作

### 1.概述

1. 为了集成VsCode内部自带的API，而无需去找库来整合，例（文件，终端...）。

### 2.集成步骤

2.1.可以在自己的项目下搭一个Vscode的扩展项目，可以用命令：

2.2.项目搭好之后，整理项目结构：

vscode - extension /

|-- package.json 					vscode插件配置

|-- src /

|	|-- extension.ts 				插件主入口（编写index.html入口，命令启动插件的命令）

|	|-- webview /

|		|-- index.tsx 				React应用入口

|		|-- components / 			React组件

|-- build /							编译后的React应用

|-- dist / 							编译后的插件代码

|-- chip-generator-extension-0.1.0.vsix  	打包后的插件，vscode直接安装vsix类型的扩展就可以用了

2.3.修改package.json中的配置，例如：displayName（插件名称），version（版本号）；

2.4.创建插件的入口文件：src/extension.ts，并写入对应的插件配置；

2.5.修改我们原有的组件以便支持Vscode的窗口正常显示；

2.6.在React原项目中创建：src/VsCode-api.ts相当于适配器用于React应用于Vscode插件之间的通信（调用Vscode的文件系统API，窗口提示API）；

2.7.构建和打包流程；

2.8.可以写个构建插件的脚本，例：build-extension.js；

2.9.插件打成之后，会出现在vscode-extension/chip-generator-extension-0.1.0.vsix，打包的文件根据当前Vscode插件下的package.json里面的配置决定；

2.10.打开Vscode，按ctrl + shift + p打开命令面板，选择我们vsix后缀的文件，重启Vscode按chip Generator开始使用，其他命令可以点击插件详细信息查看命令。

## 二.pwa渐进式网页应用

### 1.概述

1. 可以在浏览器上运行，还可以安装到设备上提供离线访问，推送通知等功能，浏览器内置API。

### 2.核心技术

1. Service Worker：在后台运行的脚本，可以拦截网络请求缓存资源，并实现离线功能（别人看不到你离线）；
2. Manifest：json配置文件，让web服务可以被电脑下载成桌面应用，手机可以下载成APP，定义了下载后的应用图标、名称、启动页面等元数据，使网页像应用一样被安装和显示；
3. HTTPS；为确保安全，pwa网页应用必须通过https提供服务。

### 3.使用步骤

1. 创建service-worker.js，并在其中写缓存逻辑，通过self给这个上下文全局对象注册事件监听和处理后台任务，例如我们网页发起一次网络请求，需要将获取的资源缓存到本地，例：

```javascript
self.addEventListener('fetch',(event)=>{
    // 例如拦截GET请求
    if(event.request.method !== 'GET'){
        return    
    }
    // 下面写入程序，如果有缓存，直接返回缓存，没有则发起请求，再回写到缓存中
})
```

b.注册Service Worker在index.html下注册；

```javascript
// 例
if('serviceWorker' in navigator){
    Window.addEventListener('load',()=>{
        navigator.serviceWorker.register('service-worker.js')
        .then(registration=>{
            // 成功回调        
        })
        .catch(error=>{
            // 失败回调        
        })
    })
}
```

c.创建manifest.json文件并添加必要的元数据（json格式）；

d.在inde.html引入manifest（作用：1.可安装到主屏幕，2.自定义外观，3.独立窗口，4.被应用商店识别，5.右键菜单快捷方式）。

### 4.pwa的高级功能

1. 离线功能：例如动态缓存用户在离线时访问的页面，并在用户重新上线时同步数据；
2. 推送功能：例如通过Web push API发送通知，即使用户处于离线状态；
3. 后台同步：例如通过Background Sync API 在用户重新联网时自动同步数据；
4. 添加到主屏幕：用户可以将应用添加到主屏幕，像应用商店下载应用一样使用。

### 5.小结

1. 重点文件：manifest.json（配置当前web服务下载成应用程序的图标，名称，描述，可以下载成手机上的APP）；
2. Progressive Web App（PWA）渐进式网页应用的出现和发展，让网页应用更加灵活和强大，为开发者提供新的机会和挑战。无论是简化用户的安装过程，实现离线访问，还是发送推送通知，PWA都展示了其独特的优势。
