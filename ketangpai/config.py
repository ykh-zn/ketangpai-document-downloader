"""配置文件"""

import os

# 目录配置（项目根目录）
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE_DIR = os.path.join(PROJECT_DIR, "cookies")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
COOKIE_FILE = os.path.join(COOKIE_DIR, "session.pkl")

# 超时配置（秒）
LOGIN_TIMEOUT = 300        # 登录等待超时
PAGE_LOAD_WAIT = 5         # 页面加载等待
REQUEST_TIMEOUT = 30       # 请求超时

# 图片过滤配置
MIN_IMAGE_WIDTH = 100      # 最小图片宽度
MIN_IMAGE_HEIGHT = 100     # 最小图片高度

# 默认URL（可选）
DEFAULT_URL = ""

# 确保目录存在
os.makedirs(COOKIE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
