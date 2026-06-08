"""PDF/文档下载模块"""

import os
import time
import requests
from io import BytesIO
from urllib.parse import urlparse, unquote
from PIL import Image

from .config import (
    OUTPUT_DIR, REQUEST_TIMEOUT,
    MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT
)


class Downloader:
    def __init__(self, url, auth):
        self.url = url
        self.auth = auth
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://w.ketangpai.com/",
            "Content-Type": "application/json",
        })

        # 设置token header
        token = auth.get_token()
        if token:
            self.session.headers["token"] = token

    def _extract_ids(self):
        """从URL提取courseId和id"""
        try:
            parsed = urlparse(self.url)
            params = dict(p.split("=") for p in parsed.query.split("&") if "=" in p)
            return {
                "id": params.get("id", ""),
                "courseid": params.get("courseId", ""),
            }
        except:
            return {"id": "", "courseid": ""}

    def get_file_info(self):
        """通过API获取文件信息"""
        print("\n获取文件信息...")

        ids = self._extract_ids()
        if not ids["id"] or not ids["courseid"]:
            print("无法从URL提取ID")
            return None

        api_url = "https://openapiv5.ketangpai.com/FutureV2/Courseware/query"
        data = {
            "id": ids["id"],
            "courseid": ids["courseid"],
            "contenttype": "2",
            "reqtimestamp": int(time.time() * 1000)
        }

        try:
            resp = self.session.post(api_url, json=data, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("status") == 1 and result.get("data"):
                    return result["data"]
                else:
                    print(f"API返回错误: {result.get('message', '未知错误')}")
            else:
                print(f"HTTP错误: {resp.status_code}")
        except Exception as e:
            print(f"请求失败: {e}")

        return None

    def download_from_api(self):
        """通过API获取文件信息并下载"""
        file_info = self.get_file_info()
        if not file_info:
            return None

        # 提取文件信息
        attachments = file_info.get("attachment", [])
        if not attachments:
            print("未找到附件")
            return None

        attachment = attachments[0]
        file_name = attachment.get("name", "unknown.docx")
        download_url = attachment.get("url", "")
        file_size = attachment.get("orgin_size", "0")

        print(f"文件名: {file_name}")
        print(f"文件大小: {int(file_size) / 1024:.2f} KB")
        print(f"下载链接: {download_url[:80]}...")

        if not download_url:
            print("未找到下载链接")
            return None

        # 下载文件
        return self._download_file(download_url, file_name)

    def _download_file(self, url, filename):
        """下载文件"""
        print(f"\n下载文件...")

        try:
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 1000:
                # 清理文件名
                filename = self._clean_filename(filename)
                output_path = os.path.join(OUTPUT_DIR, filename)

                with open(output_path, 'wb') as f:
                    f.write(resp.content)

                print(f"下载成功！文件已保存到: {output_path}")
                return output_path
            else:
                print(f"下载失败: HTTP {resp.status_code}")
                return None
        except Exception as e:
            print(f"下载失败: {e}")
            return None

    def _clean_filename(self, filename):
        """清理文件名，移除非法字符"""
        import re
        # 移除或替换非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制长度
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:190] + ext
        return filename

    def find_images_from_preview(self):
        """从预览页面查找图片（备用方法）"""
        print("\n查找预览图片...")

        file_info = self.get_file_info()
        if not file_info:
            return []

        attachments = file_info.get("attachment", [])
        if not attachments:
            return []

        # 获取预览URL
        playurl = attachments[0].get("playurl", "")
        if not playurl:
            print("未找到预览链接")
            return []

        print(f"预览链接: {playurl[:80]}...")

        # 这里可以进一步实现从预览页面提取图片的逻辑
        # 目前先返回空列表
        return []

    def cleanup(self):
        """清理资源"""
        pass
