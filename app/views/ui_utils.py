#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI工具函数
提供消息提示等辅助功能
"""

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer


def show_success_message(parent, message: str):
    """显示成功消息"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("成功")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    # 3秒后自动关闭
    QTimer.singleShot(3000, msg_box.close)
    msg_box.exec()


def show_error_message(parent, message: str):
    """显示错误消息"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("错误")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


def show_warning_message(parent, message: str):
    """显示警告消息"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("警告")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


def show_info_message(parent, message: str):
    """显示信息消息"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("信息")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()
