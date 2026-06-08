"""
课堂派PDF/文档下载工具 - 主流程编排模块

本模块负责整个下载流程的编排：
1. 获取用户输入的URL
2. 加载或创建登录认证
3. 调用下载器获取文件
4. 失败时重新登录并重试
"""

import sys

# 导入配置和功能模块
from .config import DEFAULT_URL        # 默认URL配置
from .auth import Auth                 # 认证模块：处理登录和session管理
from .downloader import Downloader     # 下载模块：处理API调用和文件下载


def main():
    """
    主函数 - 编排整个下载流程

    流程：
    1. 从命令行参数或用户输入获取URL
    2. 尝试使用已保存的session进行下载
    3. 如果失败，提示用户重新登录
    4. 登录成功后重试下载
    """

    # ========== 第一步：获取目标URL ==========
    # 优先从命令行参数获取，否则提示用户输入
    if len(sys.argv) > 1:
        # 如果命令行传入了参数，直接使用第一个参数作为URL
        url = sys.argv[1]
    else:
        # 交互式输入：提示用户粘贴URL
        url = input("请输入课堂派URL: ").strip()
        if not url:
            # 如果用户没有输入，尝试使用默认URL
            url = DEFAULT_URL
        if not url:
            # 既没有输入也没有默认值，退出程序
            print("未提供URL，退出")
            return

    # 打印程序标题和目标信息
    print("=" * 50)
    print("课堂派文档下载工具")
    print("=" * 50)
    print(f"目标: {url}")

    # ========== 第二步：初始化认证系统 ==========
    auth = Auth()

    # 尝试加载之前保存的登录状态（cookies和token）
    # 这样可以避免每次都要求用户重新登录
    has_session = auth.load_session()

    # ========== 第三步：初始化下载器 ==========
    # 下载器需要URL和认证信息来调用API
    downloader = Downloader(url, auth)

    try:
        # ========== 第四步：尝试下载文件 ==========
        # 调用下载器的API下载方法
        result = downloader.download_from_api()

        if result:
            # 下载成功，打印结果路径并退出
            print(f"\n完成！文件已保存到: {result}")
            return

        # ========== 第五步：下载失败，尝试重新登录 ==========
        # 可能是session过期或token失效
        print("\n下载失败，可能需要重新登录")
        auth.cleanup()  # 清理旧的浏览器实例

        # 创建新的认证实例并执行登录流程
        # 这会打开浏览器，等待用户手动登录
        auth = Auth()
        if not auth.login(url):
            # 登录失败（超时或用户取消）
            print("登录失败")
            return

        # 登录成功，重新初始化下载器使用新的认证信息
        downloader = Downloader(url, auth)

        # ========== 第六步：重试下载 ==========
        result = downloader.download_from_api()

        if result:
            print(f"\n完成！文件已保存到: {result}")
        else:
            print("\n下载失败，请检查URL是否正确")

    except KeyboardInterrupt:
        # 用户按 Ctrl+C 中断程序
        print("\n用户中断")
    except Exception as e:
        # 捕获其他异常并打印详细错误信息
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的调用堆栈
    finally:
        # ========== 清理资源 ==========
        # 无论成功失败，都要关闭浏览器和清理资源
        auth.cleanup()
        downloader.cleanup()


# 当直接运行此模块时执行主函数
if __name__ == "__main__":
    main()
