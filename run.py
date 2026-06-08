"""
课堂派文档下载工具 - 入口脚本

本脚本是程序的启动入口，负责调用主流程函数。

使用方法：
  python run.py <URL>      # 直接传入课堂派URL
  python run.py            # 交互式输入URL
"""

# 导入主流程函数
from ketangpai.main import main

# 当直接运行此脚本时执行主函数
if __name__ == "__main__":
    main()
