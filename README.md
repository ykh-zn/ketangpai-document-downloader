# 课堂派文档下载器

下载课堂派上标记为"不允许下载"的文档。

## 工作原理

1. Selenium 打开浏览器，用户手动完成短信验证码登录
2. 从浏览器提取 localStorage 中的 token
3. 用 token 调用课堂派 API 获取文件信息
4. 从 API 响应中提取下载链接（即使页面显示"不允许下载"）
5. 下载文件保存到本地

## 快速开始

### 环境要求

- Python 3.8+
- Chrome 浏览器
- ChromeDriver（需与 Chrome 版本匹配）

### 安装

```bash
git clone https://github.com/yourusername/ketangpai-downloader.git
cd ketangpai-downloader
pip install -r requirements.txt
```

### 使用方法

```bash
# 方式一：直接传入 URL
python run.py "https://w.ketangpai.com/dataIndex?type=2&id=xxx&courseId=yyy"

# 方式二：交互式输入
python run.py
```

### 首次使用

1. 程序自动打开 Chrome 浏览器
2. 在浏览器中用短信验证码登录课堂派
3. 登录成功后，程序自动检测并提取认证信息
4. 文件下载到 `output/` 目录

### 后续使用

程序会自动使用 `cookies/session.pkl` 中保存的登录状态，无需重复登录。若 token 过期，程序会自动提示重新登录。

## 项目结构

```
课堂派文档下载器/
├── run.py                # 入口脚本
├── requirements.txt      # Python 依赖
├── ketangpai/            # 核心代码
│   ├── main.py           # 主流程编排
│   ├── auth.py           # 登录认证（Selenium）
│   ├── downloader.py     # API 调用与文件下载
│   └── config.py         # 配置项
├── cookies/              # 登录状态存储（自动生成）
├── output/               # 下载文件输出目录（自动生成）
└── docs/
    └── tutorial.md       # 爬虫开发教程
```

## 技术细节

**API 端点**

```
POST https://openapiv5.ketangpai.com/FutureV2/Courseware/query
```

**认证方式**

课堂派使用自定义 `token` header，token 来自用户登录后写入 localStorage 的值。

**关键发现**

页面显示 `candownload=0`（不允许下载），但 API 响应中的 `attachment.url` 仍然返回有效的下载链接。

**注意事项**

- URL 中 `courseId`（大写 C）在 API 请求中需转为 `courseid`（全小写）
- 下载链接有时效性，需实时从 API 获取

## 依赖

| 库 | 用途 |
|----|------|
| selenium | 浏览器自动化，模拟用户登录 |
| requests | 发送 HTTP 请求，调用 API |
| Pillow | 图片处理（预留） |

## 免责声明

本工具仅供学习交流使用。请遵守课堂派的使用条款，仅下载自己有权访问的内容。因使用本工具产生的任何问题，作者不承担责任。

## License

MIT
