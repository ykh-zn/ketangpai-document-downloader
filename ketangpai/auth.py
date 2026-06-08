"""登录认证模块"""

import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from .config import COOKIE_FILE, LOGIN_TIMEOUT


class Auth:
    def __init__(self):
        self.driver = None
        self.cookies = {}
        self.selenium_cookies = []

    def load_session(self):
        """加载保存的登录状态"""
        if not os.path.exists(COOKIE_FILE):
            return False

        try:
            with open(COOKIE_FILE, "rb") as f:
                data = pickle.load(f)

            if isinstance(data, dict) and "cookies" in data:
                self.cookies = data["cookies"]
                self.selenium_cookies = data.get("selenium_cookies", [])
            else:
                self.cookies = data
                self.selenium_cookies = []

            print(f"已加载 {len(self.cookies)} 个认证项")
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False

    def save_session(self):
        """保存登录状态"""
        data = {
            "cookies": self.cookies,
            "selenium_cookies": self.selenium_cookies
        }
        try:
            with open(COOKIE_FILE, "wb") as f:
                pickle.dump(data, f)
            print(f"登录状态已保存")
        except Exception as e:
            print(f"保存失败: {e}")

    def setup_driver(self):
        """初始化浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=options)

    def login(self, url):
        """打开浏览器等待用户登录"""
        print("\n" + "=" * 50)
        print("需要登录")
        print("=" * 50)
        print("即将打开浏览器，请用短信验证码登录")
        print("登录成功后会自动跳转，程序会自动检测...")
        print()

        self.setup_driver()
        self.driver.get(url)

        # 等待登录完成
        waited = 0
        while waited < LOGIN_TIMEOUT:
            time.sleep(2)
            waited += 2

            try:
                current_url = self.driver.current_url

                # 还在登录页
                if "login" in current_url.lower():
                    if waited % 10 == 0:
                        print(f"等待登录中... ({waited}秒)")
                    continue

                # 检测到页面加载完成
                page_source = self.driver.page_source
                if "Uploads" in page_source or "dataIndex" in current_url:
                    print("登录成功！")
                    break

            except Exception:
                pass

            if waited % 10 == 0:
                print(f"已等待 {waited} 秒...")

        if waited >= LOGIN_TIMEOUT:
            print("登录超时")
            self.driver.quit()
            return False

        # 等待页面完全加载
        time.sleep(5)

        # 获取认证信息
        self._extract_auth()

        # 保存
        self.save_session()
        return True

    def _extract_auth(self):
        """从浏览器提取认证信息"""
        # 获取Cookie
        self.selenium_cookies = self.driver.get_cookies()
        self.cookies = {}
        for c in self.selenium_cookies:
            self.cookies[c['name']] = c['value']

        # 获取localStorage
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
                self.cookies.update({f"ls_{k}": v for k, v in ls.items()})
        except:
            pass

        print(f"获取到 {len(self.cookies)} 个认证项")

    def setup_cookies_for_browser(self, driver, url):
        """为浏览器设置已保存的Cookie"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        driver.get(base_url)
        time.sleep(2)

        # 设置selenium格式的Cookie
        if self.selenium_cookies:
            for cookie in self.selenium_cookies:
                try:
                    c = {"name": cookie["name"], "value": cookie["value"]}
                    if "domain" in cookie:
                        c["domain"] = cookie["domain"]
                    if "path" in cookie:
                        c["path"] = cookie["path"]
                    driver.add_cookie(c)
                except:
                    pass

        # 设置localStorage中的token
        token = self.cookies.get("ls_token") or self.cookies.get("token")
        if token:
            try:
                driver.execute_script(f"localStorage.setItem('token', '{token}')")
            except:
                pass

    def get_token(self):
        """获取token"""
        return self.cookies.get("ls_token") or self.cookies.get("token")

    def cleanup(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
