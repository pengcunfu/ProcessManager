#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI工具函数
提供消息提示等辅助功能
"""

from PySide6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition


def show_success_message(parent, message: str):
    """显示成功消息"""
    InfoBar.success(
        title="成功",
        content=message,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=3000,
        parent=parent
    )


def show_error_message(parent, message: str):
    """显示错误消息"""
    InfoBar.error(
        title="错误",
        content=message,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=5000,
        parent=parent
    )


def show_warning_message(parent, message: str):
    """显示警告消息"""
    InfoBar.warning(
        title="警告",
        content=message,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=4000,
        parent=parent
    )


def show_info_message(parent, message: str):
    """显示信息消息"""
    InfoBar.info(
        title="信息",
        content=message,
        orient=Qt.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=3000,
        parent=parent
    )

