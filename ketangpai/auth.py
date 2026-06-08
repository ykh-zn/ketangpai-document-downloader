"""
登录认证模块

本模块负责处理课堂派的登录认证，包括：
1. 使用Selenium打开浏览器让用户手动登录
2. 从浏览器提取cookies和localStorage中的token
3. 将认证信息持久化保存到本地文件
4. 恢复已保存的登录状态

认证原理：
- 课堂派使用自定义的token认证机制（非标准Bearer token）
- token存储在浏览器的localStorage中
- 同时需要浏览器cookies来维持会话状态
"""

import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# 导入配置常量
from .config import COOKIE_FILE, LOGIN_TIMEOUT


class Auth:
    """
    认证管理类

    负责管理课堂派的登录状态，包括：
    - 浏览器自动化登录
    - 认证信息提取与保存
    - 登录状态恢复
    """

    def __init__(self):
        """初始化认证管理器"""
        self.driver = None              # Selenium WebDriver实例
        self.cookies = {}               # 扁平化的cookie字典，用于requests库
        self.selenium_cookies = []      # Selenium格式的cookie列表，用于浏览器恢复

    def load_session(self):
        """
        加载之前保存的登录状态

        从本地pickle文件读取之前保存的cookies和token。
        如果文件存在且格式正确，恢复登录状态，避免重复登录。

        Returns:
            bool: 是否成功加载了session
        """
        # 检查session文件是否存在
        if not os.path.exists(COOKIE_FILE):
            return False

        try:
            # 从pickle文件反序列化认证数据
            with open(COOKIE_FILE, "rb") as f:
                data = pickle.load(f)

            # 兼容新旧两种数据格式
            if isinstance(data, dict) and "cookies" in data:
                # 新格式：包含cookies和selenium_cookies
                self.cookies = data["cookies"]
                self.selenium_cookies = data.get("selenium_cookies", [])
            else:
                # 旧格式：直接就是cookies字典
                self.cookies = data
                self.selenium_cookies = []

            print(f"已加载 {len(self.cookies)} 个认证项")
            return True
        except Exception as e:
            # 文件损坏或格式不匹配
            print(f"加载失败: {e}")
            return False

    def save_session(self):
        """
        保存当前登录状态

        将cookies和Selenium格式的cookies序列化到本地文件，
        下次启动时可以直接恢复登录状态。
        """
        # 组织要保存的数据结构
        data = {
            "cookies": self.cookies,                    # 用于requests库的扁平cookie
            "selenium_cookies": self.selenium_cookies   # 用于浏览器恢复的完整cookie
        }

        try:
            # 序列化到pickle文件
            with open(COOKIE_FILE, "wb") as f:
                pickle.dump(data, f)
            print(f"登录状态已保存")
        except Exception as e:
            print(f"保存失败: {e}")

    def setup_driver(self):
        """
        初始化Selenium WebDriver

        配置并启动Chrome浏览器实例，用于：
        - 打开课堂派登录页面
        - 等待用户手动登录
        - 提取登录后的认证信息
        """
        options = webdriver.ChromeOptions()
        # 最大化浏览器窗口，方便用户操作
        options.add_argument("--start-maximized")
        # 隐藏自动化标志，避免被网站检测
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # 创建Chrome浏览器实例
        self.driver = webdriver.Chrome(options=options)

    def login(self, url):
        """
        执行登录流程

        打开浏览器访问目标URL，等待用户完成短信验证码登录。
        登录成功后自动提取认证信息并保存。

        Args:
            url: 课堂派页面URL

        Returns:
            bool: 登录是否成功
        """
        # 打印登录提示信息
        print("\n" + "=" * 50)
        print("需要登录")
        print("=" * 50)
        print("即将打开浏览器，请用短信验证码登录")
        print("登录成功后会自动跳转，程序会自动检测...")
        print()

        # 启动浏览器并访问目标页面
        self.setup_driver()
        self.driver.get(url)

        # ========== 等待用户登录 ==========
        # 轮询检测登录状态，最多等待LOGIN_TIMEOUT秒
        waited = 0
        while waited < LOGIN_TIMEOUT:
            # 每2秒检测一次
            time.sleep(2)
            waited += 2

            try:
                current_url = self.driver.current_url

                # 判断1：如果URL中包含"login"，说明还在登录页
                if "login" in current_url.lower():
                    # 每10秒打印一次等待提示
                    if waited % 10 == 0:
                        print(f"等待登录中... ({waited}秒)")
                    continue

                # 判断2：检查页面内容是否包含登录成功的标志
                page_source = self.driver.page_source
                # "Uploads"或"dataIndex"表示已进入课程资料页面
                if "Uploads" in page_source or "dataIndex" in current_url:
                    print("登录成功！")
                    break

            except Exception:
                # 浏览器可能已关闭或其他异常，继续等待
                pass

            # 每10秒打印一次等待时间
            if waited % 10 == 0:
                print(f"已等待 {waited} 秒...")

        # 检查是否超时
        if waited >= LOGIN_TIMEOUT:
            print("登录超时")
            self.driver.quit()
            return False

        # 等待页面完全加载（包括异步请求）
        time.sleep(5)

        # ========== 提取并保存认证信息 ==========
        self._extract_auth()
        self.save_session()
        return True

    def _extract_auth(self):
        """
        从浏览器提取认证信息

        提取两类认证数据：
        1. 浏览器cookies - 维持HTTP会话状态
        2. localStorage中的token - 用于API调用认证
        """
        # 获取所有浏览器cookies
        self.selenium_cookies = self.driver.get_cookies()

        # 转换为扁平字典格式，方便requests库使用
        self.cookies = {}
        for c in self.selenium_cookies:
            self.cookies[c['name']] = c['value']

        # 通过JavaScript获取localStorage中的所有数据
        # 课堂派的token就存储在这里
        try:
            ls = self.driver.execute_script("""
                var items = {};
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            """)
            if ls:
                # 给localStorage的key加上"ls_"前缀，避免与cookie冲突
                self.cookies.update({f"ls_{k}": v for k, v in ls.items()})
        except:
            pass

        print(f"获取到 {len(self.cookies)} 个认证项")

    def setup_cookies_for_browser(self, driver, url):
        """
        为新浏览器实例恢复已保存的登录状态

        将之前保存的cookies和token注入到新的浏览器中，
        实现免登录直接访问页面。

        Args:
            driver: 新的Selenium WebDriver实例
            url: 目标URL，用于确定cookie的域
        """
        from urllib.parse import urlparse

        # 先访问基础域名，这样才能设置cookie
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        driver.get(base_url)
        time.sleep(2)

        # 恢复Selenium格式的cookies
        if self.selenium_cookies:
            for cookie in self.selenium_cookies:
                try:
                    # 只保留必要的字段，避免兼容性问题
                    c = {"name": cookie["name"], "value": cookie["value"]}
                    if "domain" in cookie:
                        c["domain"] = cookie["domain"]
                    if "path" in cookie:
                        c["path"] = cookie["path"]
                    driver.add_cookie(c)
                except:
                    pass

        # 恢复localStorage中的token
        # 优先从"ls_token"获取（新格式），其次从"token"获取（旧格式）
        token = self.cookies.get("ls_token") or self.cookies.get("token")
        if token:
            try:
                # 通过JavaScript注入token到localStorage
                driver.execute_script(f"localStorage.setItem('token', '{token}')")
            except:
                pass

    def get_token(self):
        """
        获取API调用所需的token

        Returns:
            str: 认证token，如果不存在则返回None
        """
        # 优先从"ls_token"获取（localStorage提取的），其次从"token"获取
        return self.cookies.get("ls_token") or self.cookies.get("token")

    def cleanup(self):
        """
        清理资源

        关闭Selenium WebDriver浏览器实例，释放系统资源。
        使用try-except避免浏览器已关闭时的异常。
        """
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
