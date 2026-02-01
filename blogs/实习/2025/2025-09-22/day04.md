---
title: Promise 静态方法使用指南
date: 2025/09/22
tags:
  - 中电软件园
categories:
  - 实习
---
# day04

# Promise 静态方法使用指南

## 概述

Promise 是 JavaScript 中处理异步操作的重要机制。本文档详细介绍三个核心静态方法：`Promise.resolve`​、`Promise.reject`​ 和 `Promise.all` 的应用场景和使用方法。

## 1. Promise.resolve()

### 基本语法

```javascript
Promise.resolve(value)
```

### 功能说明

- 返回一个以给定值解析后的 Promise 对象
- 如果参数本身就是 Promise 对象，则直接返回该对象
- 如果参数是 thenable 对象，会执行其 then 方法

### 应用场景

#### 1.1 将普通值转换为 Promise

```javascript
// 将普通值包装成 Promise
const resolvedPromise = Promise.resolve(42);
resolvedPromise.then(value => {
    console.log(value); // 输出: 42
});

// 将字符串转换为 Promise
Promise.resolve("Hello World")
    .then(message => console.log(message)); // 输出: Hello World
```

#### 1.2 统一异步和同步操作的返回类型

```javascript
function getData(useCache = false) {
    if (useCache) {
        // 同步返回缓存数据，但包装成 Promise
        return Promise.resolve(cachedData);
    } else {
        // 异步获取数据
        return fetch('/api/data').then(res => res.json());
    }
}

// 调用方可以统一使用 .then() 处理
getData(true).then(data => console.log(data));
getData(false).then(data => console.log(data));
```

#### 1.3 链式调用的起点

```javascript
Promise.resolve()
    .then(() => {
        console.log('第一步');
        return '数据1';
    })
    .then(data => {
        console.log('第二步:', data);
        return '数据2';
    })
    .then(data => {
        console.log('第三步:', data);
    });
```

## 2. Promise.reject()

### 基本语法

```javascript
Promise.reject(reason)
```

### 功能说明

- 返回一个带有拒绝原因的 Promise 对象
- 参数通常是 Error 对象或错误信息

### 应用场景

#### 2.1 主动抛出错误

```javascript
function validateUser(user) {
    if (!user.name) {
        return Promise.reject(new Error('用户名不能为空'));
    }
    if (!user.email) {
        return Promise.reject(new Error('邮箱不能为空'));
    }
    return Promise.resolve(user);
}

validateUser({ name: '', email: 'test@example.com' })
    .then(user => console.log('验证通过:', user))
    .catch(error => console.error('验证失败:', error.message));
```

#### 2.2 条件性错误处理

```javascript
function processData(data) {
    if (data.length === 0) {
        return Promise.reject(new Error('数据为空'));
    }
    
    if (data.some(item => item.invalid)) {
        return Promise.reject(new Error('包含无效数据'));
    }
    
    return Promise.resolve(data.map(item => item.value));
}
```

#### 2.3 错误传播

```javascript
function apiCall() {
    return fetch('/api/data')
        .then(response => {
            if (!response.ok) {
                return Promise.reject(new Error(`HTTP ${response.status}: ${response.statusText}`));
            }
            return response.json();
        });
}
```

## 3. Promise.all()

### 基本语法

```javascript
Promise.all(iterable)
```

### 功能说明

- 接收一个可迭代对象（通常是数组）
- 当所有 Promise 都成功时，返回包含所有结果的数组
- 如果任何一个 Promise 失败，立即返回失败的 Promise

### 应用场景

#### 3.1 并行执行多个异步操作

```javascript
// 同时获取多个 API 数据
const userPromise = fetch('/api/user/123').then(res => res.json());
const postsPromise = fetch('/api/posts').then(res => res.json());
const commentsPromise = fetch('/api/comments').then(res => res.json());

Promise.all([userPromise, postsPromise, commentsPromise])
    .then(([user, posts, comments]) => {
        console.log('用户信息:', user);
        console.log('文章列表:', posts);
        console.log('评论列表:', comments);
        // 所有数据都获取完成后的处理逻辑
    })
    .catch(error => {
        console.error('获取数据失败:', error);
    });
```

#### 3.2 批量文件处理

```javascript
function processFiles(fileList) {
    const processPromises = fileList.map(file => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve({
                name: file.name,
                content: reader.result,
                size: file.size
            });
            reader.onerror = () => reject(new Error(`读取文件 ${file.name} 失败`));
            reader.readAsText(file);
        });
    });

    return Promise.all(processPromises);
}

// 使用示例
processFiles(selectedFiles)
    .then(results => {
        console.log('所有文件处理完成:', results);
        results.forEach(file => {
            console.log(`${file.name}: ${file.size} bytes`);
        });
    })
    .catch(error => {
        console.error('文件处理失败:', error);
    });
```

#### 3.3 数据验证场景

```javascript
function validateAllInputs(formData) {
    const validations = [
        validateEmail(formData.email),
        validatePassword(formData.password),
        validatePhone(formData.phone),
        checkUsernameAvailability(formData.username)
    ];

    return Promise.all(validations)
        .then(results => {
            console.log('所有验证通过:', results);
            return { valid: true, data: formData };
        })
        .catch(error => {
            console.error('验证失败:', error);
            return { valid: false, error: error.message };
        });
}
```

#### 3.4 资源预加载

```javascript
function preloadResources() {
    const imagePromises = [
        '/images/logo.png',
        '/images/banner.jpg',
        '/images/background.png'
    ].map(src => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(src);
            img.onerror = () => reject(new Error(`加载图片失败: ${src}`));
            img.src = src;
        });
    });

    const scriptPromises = [
        '/js/analytics.js',
        '/js/charts.js'
    ].map(src => {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.onload = () => resolve(src);
            script.onerror = () => reject(new Error(`加载脚本失败: ${src}`));
            script.src = src;
            document.head.appendChild(script);
        });
    });

    return Promise.all([...imagePromises, ...scriptPromises]);
}

preloadResources()
    .then(resources => {
        console.log('所有资源加载完成:', resources);
        // 初始化应用
        initializeApp();
    })
    .catch(error => {
        console.error('资源加载失败:', error);
        // 显示错误提示
        showErrorMessage('应用初始化失败，请刷新页面重试');
    });
```

## 4. 综合应用示例

### 4.1 用户注册流程

```javascript
class UserRegistration {
    /**
     * 用户注册主流程
     * @param {Object} userData 用户数据
     * @returns {Promise} 注册结果
     */
    static async register(userData) {
        try {
            // 1. 数据验证（并行执行）
            await Promise.all([
                this.validateEmail(userData.email),
                this.validatePassword(userData.password),
                this.validatePhone(userData.phone)
            ]);

            // 2. 检查用户名和邮箱是否已存在（并行执行）
            const [usernameAvailable, emailAvailable] = await Promise.all([
                this.checkUsernameAvailability(userData.username),
                this.checkEmailAvailability(userData.email)
            ]);

            if (!usernameAvailable) {
                return Promise.reject(new Error('用户名已存在'));
            }
            if (!emailAvailable) {
                return Promise.reject(new Error('邮箱已被注册'));
            }

            // 3. 创建用户
            const user = await this.createUser(userData);
            
            // 4. 发送欢迎邮件和短信（并行执行，但不阻塞主流程）
            Promise.all([
                this.sendWelcomeEmail(user.email),
                this.sendWelcomeSMS(user.phone)
            ]).catch(error => {
                console.warn('发送欢迎消息失败:', error);
            });

            return Promise.resolve({
                success: true,
                user: user,
                message: '注册成功'
            });

        } catch (error) {
            return Promise.reject(error);
        }
    }

    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return Promise.reject(new Error('邮箱格式不正确'));
        }
        return Promise.resolve(true);
    }

    static validatePassword(password) {
        if (password.length < 8) {
            return Promise.reject(new Error('密码长度至少8位'));
        }
        return Promise.resolve(true);
    }

    static validatePhone(phone) {
        const phoneRegex = /^1[3-9]\d{9}$/;
        if (!phoneRegex.test(phone)) {
            return Promise.reject(new Error('手机号格式不正确'));
        }
        return Promise.resolve(true);
    }
}
```

### 4.2 数据同步系统

```javascript
class DataSyncManager {
    /**
     * 同步多个数据源
     * @param {Array} dataSources 数据源配置
     * @returns {Promise} 同步结果
     */
    static syncAllData(dataSources) {
        const syncPromises = dataSources.map(source => {
            return this.syncSingleSource(source)
                .catch(error => {
                    // 单个数据源失败不影响其他数据源
                    console.warn(`数据源 ${source.name} 同步失败:`, error);
                    return { 
                        source: source.name, 
                        success: false, 
                        error: error.message 
                    };
                });
        });

        return Promise.all(syncPromises)
            .then(results => {
                const successful = results.filter(r => r.success !== false);
                const failed = results.filter(r => r.success === false);
                
                return {
                    total: results.length,
                    successful: successful.length,
                    failed: failed.length,
                    results: results
                };
            });
    }

    static syncSingleSource(source) {
        return fetch(source.url)
            .then(response => {
                if (!response.ok) {
                    return Promise.reject(new Error(`HTTP ${response.status}`));
                }
                return response.json();
            })
            .then(data => {
                return this.processData(data, source.processor);
            })
            .then(processedData => {
                return this.saveData(processedData, source.storage);
            })
            .then(() => {
                return { 
                    source: source.name, 
                    success: true, 
                    timestamp: new Date().toISOString() 
                };
            });
    }
}
```

## 5. 最佳实践

### 5.1 错误处理

```javascript
// ✅ 推荐：明确的错误类型
function fetchUserData(userId) {
    if (!userId) {
        return Promise.reject(new Error('用户ID不能为空'));
    }
    
    return fetch(`/api/users/${userId}`)
        .then(response => {
            if (!response.ok) {
                return Promise.reject(new Error(`获取用户数据失败: ${response.status}`));
            }
            return response.json();
        })
        .catch(error => {
            if (error.name === 'TypeError') {
                return Promise.reject(new Error('网络连接失败'));
            }
            return Promise.reject(error);
        });
}
```

### 5.2 性能优化

```javascript
// ✅ 推荐：合理使用 Promise.all 进行并行处理
async function loadDashboardData() {
    try {
        // 并行加载独立的数据
        const [userInfo, notifications, statistics] = await Promise.all([
            fetchUserInfo(),
            fetchNotifications(),
            fetchStatistics()
        ]);

        // 基于用户信息加载相关数据
        const relatedData = await fetchRelatedData(userInfo.id);

        return {
            userInfo,
            notifications,
            statistics,
            relatedData
        };
    } catch (error) {
        console.error('加载仪表板数据失败:', error);
        throw error;
    }
}
```

### 5.3 超时处理

```javascript
function withTimeout(promise, timeoutMs) {
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
            reject(new Error(`操作超时 (${timeoutMs}ms)`));
        }, timeoutMs);
    });

    return Promise.race([promise, timeoutPromise]);
}

// 使用示例
withTimeout(fetch('/api/data'), 5000)
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => {
        if (error.message.includes('操作超时')) {
            console.error('请求超时，请检查网络连接');
        } else {
            console.error('请求失败:', error);
        }
    });
```

## 6. 总结

- **Promise.resolve()** : 用于将值转换为 Promise，统一异步处理接口
- **Promise.reject()** : 用于主动抛出错误，实现错误流程控制
- **Promise.all()** : 用于并行执行多个异步操作，提高性能

这三个方法是 Promise 编程的基础工具，合理使用可以让异步代码更加清晰、高效和可维护。

## 7. 参考资源

- [MDN Promise 文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [JavaScript Promise 最佳实践](https://javascript.info/promise-basics)
- [异步编程模式](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/async-performance/README.md)
