# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

课堂派文档下载工具 — 通过逆向课堂派 API，下载页面上标记为"不允许下载"的文档。核心原理：Selenium 模拟登录获取 token，再用 requests 调用 API 拿到下载链接。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行（传入课堂派 URL）
python run.py "https://w.ketangpai.com/dataIndex?type=2&id=xxx&courseId=yyy"

# 运行（交互式输入 URL）
python run.py
```

## 架构

```
run.py                  → 入口，调用 ketangpai.main.main()
ketangpai/
  main.py               → 主流程编排：加载 session → 尝试下载 → 失败则重新登录 → 重试
  auth.py               → Auth 类：Selenium 打开浏览器等待用户短信登录，提取 cookie + localStorage token，序列化到 cookies/session.pkl
  downloader.py          → Downloader 类：从 URL 解析 id/courseid，POST openapiv5.ketangpai.com/FutureV2/Courseware/query 获取附件信息，下载文件到 output/
  config.py              → 路径、超时、图片过滤等常量
```

## 关键技术细节

- **认证方式**：课堂派使用自定义 `token` header（非标准 Authorization Bearer），token 来自 localStorage 的 `token` 键
- **URL 参数映射**：URL 中 `courseId`（大写 C）→ API 参数 `courseid`（全小写），不一致需注意
- **API 端点**：`POST https://openapiv5.ketangpai.com/FutureV2/Courseware/query`
- **绕过机制**：页面显示 `candownload=0`，但 API 响应中仍包含有效下载链接
- **Session 持久化**：cookie 和 localStorage 用 pickle 序列化到 `cookies/session.pkl`，支持免重复登录
- **依赖**：selenium（浏览器自动化登录）、requests（API 调用）、Pillow（图片过滤，当前未重度使用）
