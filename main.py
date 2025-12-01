#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控与进程管理工具 - 主入口文件（MVC架构）
使用PySide6-Fluent-Widgets的现代化界面
"""

import sys
import signal
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from app.views.main_window import main


def signal_handler(signum, frame):
    """信号处理函数，用于处理Ctrl+C等中断信号"""
    print("\n接收到中断信号，正在安全退出...")
    QApplication.quit()


if __name__ == "__main__":
    try:
        # 设置信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 启动应用程序
        sys.exit(main())

    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"启动应用程序时出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
