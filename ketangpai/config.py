"""
配置文件

集中管理所有可配置的常量，包括：
- 文件路径配置
- 超时时间配置
- 图片过滤配置
- 其他运行时参数
"""

import os

# ========== 路径配置 ==========
# 项目根目录：当前文件的上两级目录（ketangpai/config.py -> ketangpai -> 项目根目录）
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cookie存储目录：保存登录状态的序列化文件
COOKIE_DIR = os.path.join(PROJECT_DIR, "cookies")

# 输出目录：下载的文件保存位置
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# Session文件路径：pickle格式的认证数据
COOKIE_FILE = os.path.join(COOKIE_DIR, "session.pkl")

# ========== 超时配置（单位：秒） ==========
# 登录等待超时：用户完成短信验证码登录的最大等待时间（5分钟）
LOGIN_TIMEOUT = 300

# 页面加载等待：等待页面DOM渲染和异步请求完成的时间
PAGE_LOAD_WAIT = 5

# HTTP请求超时：API调用和文件下载的超时时间
REQUEST_TIMEOUT = 30

# ========== 图片过滤配置 ==========
# 下载图片时，过滤掉尺寸过小的图片（可能是图标、缩略图等）
MIN_IMAGE_WIDTH = 100    # 最小宽度（像素）
MIN_IMAGE_HEIGHT = 100   # 最小高度（像素）

# ========== 默认URL ==========
# 如果不通过命令行传入URL，可以在这里设置默认值
DEFAULT_URL = ""

# ========== 目录初始化 ==========
# 程序启动时自动创建必要的目录
os.makedirs(COOKIE_DIR, exist_ok=True)  # exist_ok=True：目录已存在时不报错
os.makedirs(OUTPUT_DIR, exist_ok=True)
