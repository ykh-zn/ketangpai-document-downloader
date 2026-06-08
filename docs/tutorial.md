# Python爬虫系统教程

## 目录
1. [爬虫基础概念](#1-爬虫基础概念)
2. [HTTP协议详解](#2-http协议详解)
3. [爬虫工具介绍](#3-爬虫工具介绍)
4. [认证与鉴权](#4-认证与鉴权)
5. [逆向工程实战](#5-逆向工程实战)
6. [课堂派案例详解](#6-课堂派案例详解)

---

## 1. 爬虫基础概念

### 什么是爬虫？

爬虫（Web Crawler/Spider）是一个自动访问网页并提取数据的程序。

**工作原理：**
```
你的程序  →  发送请求  →  服务器
你的程序  ←  返回数据  ←  服务器
```

**类比：**
- 你在浏览器输入网址 → 浏览器帮你发请求 → 服务器返回网页
- 爬虫就是用代码代替浏览器，自动完成这个过程

### 爬虫能做什么？

| 场景 | 例子 |
|------|------|
| 数据采集 | 抓取商品价格、新闻内容 |
| 文件下载 | 下载图片、PDF、视频 |
| 信息监控 | 监控股票价格、航班信息 |
| 自动化测试 | 测试网站功能是否正常 |

### 爬虫的法律与道德

**可以做的：**
- 公开数据
- 自己账号有权访问的内容
- 不违反网站robots.txt的规定

**不可以做的：**
- 爬取他人隐私数据
- 高频请求导致服务器压力
- 绕过付费机制

---

## 2. HTTP协议详解

### 什么是HTTP？

HTTP（超文本传输协议）是浏览器和服务器之间通信的规则。

**类比：**
- HTTP就像你去餐厅点餐
- 你（客户端）告诉服务员（服务器）你要什么
- 服务员把菜（数据）端给你

### 请求（Request）

当你访问一个网页时，浏览器会发送一个HTTP请求：

```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0 ...
Cookie: session=abc123
```

**请求的组成部分：**

| 部分 | 说明 | 例子 |
|------|------|------|
| 方法（Method） | 你要做什么 | GET（获取）、POST（提交） |
| 路径（URL） | 你要访问什么 | /api/user/info |
| 请求头（Headers） | 附加信息 | Cookie、User-Agent |
| 请求体（Body） | POST时携带的数据 | {"username": "xxx"} |

### 响应（Response）

服务器收到请求后会返回响应：

```
HTTP/1.1 200 OK
Content-Type: application/json

{"name": "张三", "age": 20}
```

**响应的组成部分：**

| 部分 | 说明 | 例子 |
|------|------|------|
| 状态码（Status Code） | 请求是否成功 | 200（成功）、404（未找到） |
| 响应头（Headers） | 附加信息 | Content-Type、Set-Cookie |
| 响应体（Body） | 返回的数据 | HTML、JSON、图片 |

### 常见状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 301/302 | Redirect | 重定向到新地址 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未登录/认证失败 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器错误 |

### 请求方法

| 方法 | 用途 | 特点 |
|------|------|------|
| GET | 获取数据 | 参数在URL中，如 ?id=123 |
| POST | 提交数据 | 参数在请求体中，更安全 |
| PUT | 更新数据 | 替换整个资源 |
| DELETE | 删除数据 | 删除指定资源 |

---

## 3. 爬虫工具介绍

### requests库（最常用）

用于发送HTTP请求：

```python
import requests

# GET请求
response = requests.get("https://api.example.com/data")
print(response.text)  # 返回的文本内容
print(response.json())  # 如果是JSON，直接解析

# POST请求
data = {"username": "admin", "password": "123456"}
response = requests.post("https://api.example.com/login", json=data)

# 带Cookie的请求
cookies = {"session": "abc123"}
response = requests.get("https://api.example.com/profile", cookies=cookies)

# 带Header的请求
headers = {"Authorization": "Bearer token123"}
response = requests.get("https://api.example.com/data", headers=headers)
```

### Selenium库（浏览器自动化）

用于控制真实浏览器，处理JavaScript渲染的页面：

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

# 启动浏览器
driver = webdriver.Chrome()

# 访问网页
driver.get("https://www.example.com")

# 查找元素
element = driver.find_element(By.ID, "username")
element = driver.find_element(By.CSS_SELECTOR, ".login-btn")
element = driver.find_element(By.XPATH, "//button[@type='submit']")

# 操作元素
element.click()  # 点击
element.send_keys("admin")  # 输入文本

# 获取页面内容
html = driver.page_source  # 获取整个页面HTML
text = element.text  # 获取元素文本

# 执行JavaScript
result = driver.execute_script("return document.title;")

# 关闭浏览器
driver.quit()
```

### BeautifulSoup库（解析HTML）

用于从HTML中提取数据：

```python
from bs4 import BeautifulSoup

html = """
<html>
<body>
    <h1>标题</h1>
    <div class="content">
        <p>第一段</p>
        <p>第二段</p>
    </div>
    <a href="https://example.com">链接</a>
</body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

# 查找元素
title = soup.find("h1").text  # "标题"
paragraphs = soup.find_all("p")  # 所有<p>标签
link = soup.find("a")["href"]  # "https://example.com"

# 按class查找
content = soup.find("div", class_="content")
```

---

## 4. 认证与鉴权

### 什么是认证？

认证就是证明"你是你"。网站需要知道你是谁，才能决定你能访问什么。

### Cookie认证

**原理：**
```
1. 你登录网站，输入用户名密码
2. 服务器验证通过，给你一个"通行证"（Cookie）
3. 你之后每次请求都带上这个"通行证"
4. 服务器看到"通行证"就知道是你
```

**类比：**
- 登录 = 进入公司打卡
- Cookie = 你的工牌
- 之后每次请求 = 带着工牌进出各个房间

**代码实现：**
```python
import requests

# 方式1：手动设置Cookie
cookies = {"session_id": "abc123", "user_id": "12345"}
response = requests.get("https://example.com/profile", cookies=cookies)

# 方式2：使用Session自动管理Cookie
session = requests.Session()

# 登录，Cookie会自动保存
login_data = {"username": "admin", "password": "123456"}
session.post("https://example.com/login", json=login_data)

# 后续请求会自动带上Cookie
response = session.get("https://example.com/profile")
```

### Token认证

**原理：**
```
1. 你登录网站
2. 服务器给你一个Token（一串字符）
3. 你之后每次请求在Header中带上Token
4. 服务器验证Token
```

**与Cookie的区别：**
| 特点 | Cookie | Token |
|------|--------|-------|
| 存储位置 | 浏览器自动管理 | 开发者手动存储 |
| 传输方式 | 自动附加在Cookie header | 手动放在Authorization header |
| 跨域 | 受同源策略限制 | 可以跨域 |
| 安全性 | 较低（容易被CSRF攻击） | 较高 |

**代码实现：**
```python
import requests

# Token通常放在Authorization header中
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
response = requests.get("https://api.example.com/data", headers=headers)

# 有些网站用自定义header，比如课堂派用的是token
headers = {
    "token": "882e0f5cf088ab3ee74e4132d5ad2e4a..."
}
response = requests.post("https://api.example.com/data", headers=headers)
```

### 课堂派的认证机制

通过抓包发现，课堂派使用的是**Token认证**，而且Token放在自定义的`token` header中：

```python
# 课堂派的请求头
headers = {
    "token": "882e0f5cf088ab3ee74e4132d5ad2e4a37d58174fafafd4c3550a45275c1fb9f"
}
```

**Token的来源：**
- 用户登录后，服务器返回Token
- 前端把Token存入`localStorage`
- 后续请求从`localStorage`读取Token并放在header中

---

## 5. 逆向工程实战

### 什么是逆向工程？

逆向工程就是通过分析网站的行为，找出它是怎么工作的。

### 步骤1：打开开发者工具

**Chrome浏览器按F12，打开开发者工具**

开发者工具有几个重要标签：

| 标签 | 功能 |
|------|------|
| Elements | 查看和修改HTML/CSS |
| Console | 执行JavaScript代码 |
| Network | 查看网络请求（最重要！） |
| Sources | 查看JavaScript源代码 |
| Application | 查看Cookie、LocalStorage等存储 |

### 步骤2：分析网络请求

**Network面板是爬虫开发的核心！**

1. **筛选请求类型：**
   - XHR：API请求（通常是我们要找的）
   - JS：JavaScript文件
   - CSS：样式文件
   - Img：图片
   - Doc：HTML文档

2. **查看请求详情：**
   - Headers：请求头、请求参数
   - Preview：响应预览
   - Response：响应原始内容

3. **实战技巧：**
   - 勾选"Preserve log"保留所有请求
   - 勾选"Disable cache"禁用缓存
   - 使用筛选器搜索关键词

### 步骤3：找到API端点

**课堂派案例：**

1. 打开课堂派页面，按F12
2. 切换到Network标签
3. 点击"XHR"筛选
4. 刷新页面
5. 看到一个请求：`FutureV2/Courseware/query`

**分析这个请求：**
- 方法：POST
- URL：`https://openapiv5.ketangpai.com/FutureV2/Courseware/query`
- 请求头：包含`token`字段
- 请求体：包含`id`、`courseid`等参数

### 步骤4：复制请求为代码

**Chrome可以自动生成代码：**

1. 右键点击请求
2. 选择"Copy" → "Copy as cURL"
3. 粘贴到 https://curlconverter.com/
4. 自动生成Python代码

### 步骤5：测试和调试

```python
# 先用浏览器的请求参数测试
import requests

headers = {
    "token": "从浏览器复制的token"
}

data = {
    "id": "从浏览器复制的id",
    "courseid": "从浏览器复制的courseid",
    "contenttype": "2",
    "reqtimestamp": 1234567890
}

response = requests.post(
    "https://openapiv5.ketangpai.com/FutureV2/Courseware/query",
    headers=headers,
    json=data
)

print(response.json())  # 查看响应
```

---

## 6. 课堂派案例详解

### 完整流程

```
1. 分析网页结构
   ↓
2. 找到API端点
   ↓
3. 分析认证方式
   ↓
4. 提取必要参数
   ↓
5. 模拟API调用
   ↓
6. 下载文件
```

### 详细步骤

#### 步骤1：分析网页结构

访问课堂派页面，F12查看HTML：

```html
<!-- 页面结构 -->
<div class="views_course-dataDetail">
    <h1>期末题库</h1>
    <div class="enclosure">
        <li>
            <img src="docx图标">
            <span>4_机考题库（2021版）知识竞赛.docx</span>
            <span>106.31KB</span>
        </li>
    </div>
    <span>不允许下载</span>
</div>
```

**发现：**
- 文件名：4_机考题库（2021版）知识竞赛.docx
- 文件大小：106.31KB
- 状态：不允许下载

#### 步骤2：找到API端点

F12 → Network → XHR，看到请求：

```
POST https://openapiv5.ketangpai.com/FutureV2/Courseware/query
```

**请求参数：**
```json
{
    "id": "MDAwMDAwMDAwMLOcpZmH39FshqiGoQ",
    "courseid": "MDAwMDAwMDAwMLOcuZeIqb-whdtyoQ",
    "contenttype": "2",
    "reqtimestamp": 1780914690773
}
```

#### 步骤3：分析认证方式

查看请求头，发现：
```
token: 882e0f5cf088ab3ee74e4132d5ad2e4a37d58174fafafd4c3550a45275c1fb9f
```

**Token的来源：**
- 登录后存入localStorage
- 前端代码从localStorage读取
- 放入请求头

#### 步骤4：提取必要参数

从URL中提取参数：
```
https://w.ketangpai.com/dataIndex?type=2&id=xxx&courseId=yyy
                                    ↑          ↑
                                   id      courseid（注意小写）
```

**踩坑：** API要求`courseid`是小写，但URL中是`courseId`（大写C）

#### 步骤5：模拟API调用

```python
import requests
import time

# 构造请求
headers = {
    "token": "882e0f5cf088ab3ee74e4132d5ad2e4a...",
    "Content-Type": "application/json"
}

data = {
    "id": "MDAwMDAwMDAwMLOcpZmH39FshqiGoQ",
    "courseid": "MDAwMDAwMDAwMLOcuZeIqb-whdtyoQ",  # 小写！
    "contenttype": "2",
    "reqtimestamp": int(time.time() * 1000)
}

# 发送请求
response = requests.post(
    "https://openapiv5.ketangpai.com/FutureV2/Courseware/query",
    headers=headers,
    json=data
)

# 解析响应
result = response.json()
print(result)
```

**响应结果：**
```json
{
    "status": 1,
    "data": {
        "attachment": [{
            "name": "4_机考题库.docx",
            "url": "https://downloadv5.ketangpai.com/File/download/id/xxx..."
        }],
        "candownload": "0"  // 页面显示"不允许下载"
    }
}
```

#### 步骤6：下载文件

**关键发现：** 虽然`candownload=0`，但API仍然返回了下载链接！

```python
# 提取下载链接
attachment = result["data"]["attachment"][0]
download_url = attachment["url"]

# 下载文件
response = requests.get(download_url)
with open("机考题库.docx", "wb") as f:
    f.write(response.content)

print("下载完成！")
```

### 踩坑记录

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| API返回"登录过期" | 使用了Cookie认证 | 改用token header |
| API返回403 | courseid大小写错误 | 改为小写courseid |
| 下载链接404 | URL过期（有expires参数） | 实时从API获取 |
| iframe不加载 | 需要点击触发 | 通过API直接获取 |

---

## 总结

**爬虫开发的核心流程：**

1. **抓包分析** - 用F12的Network面板
2. **找到API** - 筛选XHR请求
3. **分析认证** - 看请求头中的Cookie/Token
4. **提取参数** - 从URL或请求体中获取
5. **模拟请求** - 用requests库发送
6. **处理响应** - 提取需要的数据

**最重要的技能：**
- 会用F12开发者工具
- 能看懂HTTP请求
- 会用requests库
- 能分析JSON数据

**学习建议：**
1. 先学会用F12抓包
2. 再学requests库的基本用法
3. 然后尝试模拟简单的API
4. 最后挑战复杂的网站
