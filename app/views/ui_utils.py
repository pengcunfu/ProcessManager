#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI工具函数和自定义样式组件
提供消息提示等辅助功能，以及可复用的样式组件
"""

from PySide6.QtWidgets import (
    QMessageBox, QTableWidget, QPushButton, QGroupBox,
    QDialog, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QTimer


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


class StyledTableWidget(QTableWidget):
    """自定义样式表格组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 优化表格样式
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)

        # 设置垂直表头
        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)
        vertical_header.setDefaultSectionSize(24)

        # 设置样式
        self._apply_styles()

    def _apply_styles(self):
        """应用表格样式"""
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #c0c0c0;
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #0078d4;
                selection-color: white;
                font-size: 9pt;
                outline: none;
            }
            QTableWidget::item {
                padding: 2px 4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333;
                padding: 4px;
                border: none;
                border-right: 1px solid #d0d0d0;
                border-bottom: 1px solid #d0d0d0;
                font-weight: bold;
                font-size: 9pt;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f0f0f0;
                border: none;
            }
        """)


class StyledButton(QPushButton):
    """自定义样式按钮组件"""

    # 按钮类型
    PRIMARY = "primary"
    DANGER = "danger"

    def __init__(self, text="", button_type=PRIMARY, parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setMinimumHeight(28)
        self._apply_styles()

    def _apply_styles(self):
        """应用按钮样式"""
        if self.button_type == self.PRIMARY:
            color = "#0078d4"
            hover_color = "#106ebe"
            pressed_color = "#005a9e"
        elif self.button_type == self.DANGER:
            color = "#d83b01"
            hover_color = "#a80000"
            pressed_color = "#8c0000"
        else:
            return

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)


class StyledGroupBox(QGroupBox):
    """自定义样式分组框组件"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self._apply_styles()

    def _apply_styles(self):
        """应用分组框样式"""
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
                font-size: 10pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px 0 4px;
            }
        """)
