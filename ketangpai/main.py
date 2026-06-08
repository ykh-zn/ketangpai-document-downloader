"""
课堂派PDF/文档下载工具
"""

import sys

from .config import DEFAULT_URL
from .auth import Auth
from .downloader import Downloader


def main():
    # 获取URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入课堂派URL: ").strip()
        if not url:
            url = DEFAULT_URL
        if not url:
            print("未提供URL，退出")
            return

    print("=" * 50)
    print("课堂派文档下载工具")
    print("=" * 50)
    print(f"目标: {url}")

    # 初始化认证
    auth = Auth()

    # 尝试加载已有登录状态
    has_session = auth.load_session()

    # 初始化下载器
    downloader = Downloader(url, auth)

    try:
        # 通过API下载文件
        result = downloader.download_from_api()

        if result:
            print(f"\n完成！文件已保存到: {result}")
            return

        # 如果失败，可能需要重新登录
        print("\n下载失败，可能需要重新登录")
        auth.cleanup()

        # 重新登录
        auth = Auth()
        if not auth.login(url):
            print("登录失败")
            return

        # 重新初始化下载器
        downloader = Downloader(url, auth)

        # 重新下载
        result = downloader.download_from_api()

        if result:
            print(f"\n完成！文件已保存到: {result}")
        else:
            print("\n下载失败，请检查URL是否正确")

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        auth.cleanup()
        downloader.cleanup()


if __name__ == "__main__":
    main()
