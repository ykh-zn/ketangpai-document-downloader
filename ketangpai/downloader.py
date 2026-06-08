"""
PDF/文档下载模块

本模块负责通过课堂派API获取文件下载链接并下载文件。

核心原理：
- 课堂派页面上显示"不允许下载"的文件，实际上API仍返回有效下载链接
- 通过逆向分析API接口，直接调用接口获取下载URL
- 使用requests库下载文件到本地

API关键点：
- 端点：POST https://openapiv5.ketangpai.com/FutureV2/Courseware/query
- 认证：使用自定义token header（非标准Bearer）
- 参数：courseid全小写，但URL中是courseId（大写C），需注意转换
"""

import os
import time
import requests
from io import BytesIO
from urllib.parse import urlparse, unquote
from PIL import Image

# 导入配置常量
from .config import (
    OUTPUT_DIR, REQUEST_TIMEOUT,
    MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT
)


class Downloader:
    """
    文件下载器类

    负责：
    1. 解析URL提取课程和课件ID
    2. 调用API获取文件元信息和下载链接
    3. 下载文件并保存到本地
    """

    def __init__(self, url, auth):
        """
        初始化下载器

        Args:
            url: 课堂派页面URL，包含courseId和id参数
            auth: Auth实例，提供认证token和cookies
        """
        self.url = url
        self.auth = auth

        # 创建requests会话，复用TCP连接和headers
        self.session = requests.Session()

        # 设置通用请求头，模拟浏览器行为
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://w.ketangpai.com/",      # 来源页面，防止跨域请求被拒
            "Content-Type": "application/json",          # 请求体格式为JSON
        })

        # 设置认证token
        # 课堂派使用自定义的token header，不是标准的Authorization Bearer
        token = auth.get_token()
        if token:
            self.session.headers["token"] = token

    def _extract_ids(self):
        """
        从URL中提取courseId和课件id

        URL格式示例：
        https://w.ketangpai.com/dataIndex?type=2&id=xxx&courseId=yyy

        注意：URL中是courseId（大写C），但API参数要求courseid（全小写）

        Returns:
            dict: 包含id和courseid的字典，提取失败返回空字符串
        """
        try:
            # 解析URL
            parsed = urlparse(self.url)

            # 将查询字符串解析为字典
            # 格式："type=2&id=xxx&courseId=yyy" -> {"type":"2", "id":"xxx", "courseId":"yyy"}
            params = dict(p.split("=") for p in parsed.query.split("&") if "=" in p)

            return {
                "id": params.get("id", ""),              # 课件ID
                "courseid": params.get("courseId", ""),   # 课程ID（注意大小写转换）
            }
        except:
            # URL格式不匹配或解析失败
            return {"id": "", "courseid": ""}

    def get_file_info(self):
        """
        通过API获取课件的文件信息

        调用课堂派的Courseware/query接口，获取：
        - 文件名
        - 文件大小
        - 下载链接
        - 预览链接

        Returns:
            dict: API返回的data字段，包含文件详细信息；失败返回None
        """
        print("\n获取文件信息...")

        # 从URL提取必要的ID参数
        ids = self._extract_ids()
        if not ids["id"] or not ids["courseid"]:
            print("无法从URL提取ID")
            return None

        # API端点
        api_url = "https://openapiv5.ketangpai.com/FutureV2/Courseware/query"

        # 构建请求体
        data = {
            "id": ids["id"],                           # 课件ID
            "courseid": ids["courseid"],                # 课程ID（全小写）
            "contenttype": "2",                        # 内容类型：2表示文档
            "reqtimestamp": int(time.time() * 1000)    # 请求时间戳（毫秒）
        }

        try:
            # 发送POST请求
            resp = self.session.post(api_url, json=data, timeout=REQUEST_TIMEOUT)

            if resp.status_code == 200:
                result = resp.json()

                # 检查API响应状态
                # status=1 表示成功
                if result.get("status") == 1 and result.get("data"):
                    return result["data"]
                else:
                    # API返回业务错误
                    print(f"API返回错误: {result.get('message', '未知错误')}")
            else:
                # HTTP状态码非200
                print(f"HTTP错误: {resp.status_code}")
        except Exception as e:
            # 网络异常、JSON解析失败等
            print(f"请求失败: {e}")

        return None

    def download_from_api(self):
        """
        通过API获取文件信息并执行下载

        完整流程：
        1. 调用get_file_info()获取文件元数据
        2. 从响应中提取下载链接
        3. 下载文件到本地

        Returns:
            str: 下载成功返回文件路径；失败返回None
        """
        # 获取文件信息
        file_info = self.get_file_info()
        if not file_info:
            return None

        # 提取附件列表
        attachments = file_info.get("attachment", [])
        if not attachments:
            print("未找到附件")
            return None

        # 使用第一个附件（通常只有一个）
        attachment = attachments[0]

        # 提取文件元信息
        file_name = attachment.get("name", "unknown.docx")     # 文件名
        download_url = attachment.get("url", "")                # 下载链接
        file_size = attachment.get("orgin_size", "0")           # 文件大小（字节）

        # 打印文件信息
        print(f"文件名: {file_name}")
        print(f"文件大小: {int(file_size) / 1024:.2f} KB")
        print(f"下载链接: {download_url[:80]}...")  # 只显示前80个字符

        # 检查下载链接是否存在
        if not download_url:
            print("未找到下载链接")
            return None

        # 执行下载
        return self._download_file(download_url, file_name)

    def _download_file(self, url, filename):
        """
        下载文件并保存到本地

        Args:
            url: 文件下载链接
            filename: 原始文件名

        Returns:
            str: 保存成功返回文件完整路径；失败返回None
        """
        print(f"\n下载文件...")

        try:
            # 发送GET请求下载文件
            # allow_redirects=True 允许跟随重定向（CDN下载通常会重定向）
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

            # 验证响应：状态码200且内容长度大于1000字节（过滤错误页面）
            if resp.status_code == 200 and len(resp.content) > 1000:
                # 清理文件名中的非法字符
                filename = self._clean_filename(filename)

                # 构建输出路径
                output_path = os.path.join(OUTPUT_DIR, filename)

                # 写入文件（二进制模式）
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
        """
        清理文件名，移除或替换Windows文件系统不允许的字符

        Windows禁止的字符：< > : " / \ | ? *

        Args:
            filename: 原始文件名

        Returns:
            str: 清理后的安全文件名
        """
        import re

        # 将非法字符替换为下划线
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # 限制文件名长度（Windows最大255字符，留一些余量）
        if len(filename) > 200:
            # 分离文件名和扩展名，只截断文件名部分
            name, ext = os.path.splitext(filename)
            filename = name[:190] + ext

        return filename

    def find_images_from_preview(self):
        """
        从预览页面查找图片（备用下载方法）

        当直接下载链接不可用时，可以尝试从文档预览页面提取图片。
        预览页面会将文档渲染为图片序列。

        Returns:
            list: 图片URL列表（当前未完整实现，返回空列表）
        """
        print("\n查找预览图片...")

        # 获取文件信息
        file_info = self.get_file_info()
        if not file_info:
            return []

        # 获取附件列表
        attachments = file_info.get("attachment", [])
        if not attachments:
            return []

        # 获取预览URL
        playurl = attachments[0].get("playurl", "")
        if not playurl:
            print("未找到预览链接")
            return []

        print(f"预览链接: {playurl[:80]}...")

        # TODO: 这里可以进一步实现从预览页面提取图片的逻辑
        # 可能需要解析HTML或调用预览API获取图片列表
        # 目前先返回空列表
        return []

    def cleanup(self):
        """
        清理资源

        关闭requests会话，释放连接池资源。
        当前为空实现，因为requests会话会自动管理连接。
        """
        pass
