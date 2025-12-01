#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式定义
原生PySide6样式
"""


def get_app_stylesheet():
    """获取应用程序样式表"""
    return """
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    QWidget {
        font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
        font-size: 10pt;
    }
    
    /* 卡片样式 */
    QGroupBox {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-top: 10px;
        padding: 15px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: #333333;
    }
    
    /* 按钮样式 */
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #106ebe;
    }
    
    QPushButton:pressed {
        background-color: #005a9e;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    QPushButton#secondaryButton {
        background-color: #f3f3f3;
        color: #333333;
        border: 1px solid #d0d0d0;
    }
    
    QPushButton#secondaryButton:hover {
        background-color: #e8e8e8;
    }
    
    QPushButton#dangerButton {
        background-color: #d13438;
    }
    
    QPushButton#dangerButton:hover {
        background-color: #a80000;
    }
    
    /* 表格样式 */
    QTableWidget {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        gridline-color: #f0f0f0;
    }
    
    QTableWidget::item {
        padding: 5px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    QTableWidget::item:selected {
        background-color: #e3f2fd;
        color: #000000;
    }
    
    QHeaderView::section {
        background-color: #fafafa;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #e0e0e0;
        font-weight: bold;
        color: #333333;
    }
    
    /* 输入框样式 */
    QLineEdit {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 6px 10px;
    }
    
    QLineEdit:focus {
        border: 2px solid #0078d4;
        padding: 5px 9px;
    }
    
    /* 下拉框样式 */
    QComboBox {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 6px 10px;
        min-width: 100px;
    }
    
    QComboBox:hover {
        border: 1px solid #0078d4;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: url(none);
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #666666;
        margin-right: 5px;
    }
    
    QComboBox QAbstractItemView {
        background-color: white;
        border: 1px solid #d0d0d0;
        selection-background-color: #e3f2fd;
        selection-color: #000000;
    }
    
    /* 进度条样式 */
    QProgressBar {
        background-color: #f0f0f0;
        border: none;
        border-radius: 4px;
        text-align: center;
        height: 20px;
    }
    
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 4px;
    }
    
    /* 标签页样式 */
    QTabWidget::pane {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: white;
    }
    
    QTabBar::tab {
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 16px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 2px solid #0078d4;
    }
    
    QTabBar::tab:hover {
        background-color: #e8e8e8;
    }
    
    /* 滚动条样式 */
    QScrollBar:vertical {
        background-color: #f5f5f5;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #f5f5f5;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* 文本编辑器样式 */
    QTextEdit, QPlainTextEdit {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px;
    }
    
    /* 菜单样式 */
    QMenuBar {
        background-color: #f5f5f5;
        border-bottom: 1px solid #e0e0e0;
    }
    
    QMenuBar::item {
        padding: 6px 12px;
        background-color: transparent;
    }
    
    QMenuBar::item:selected {
        background-color: #e8e8e8;
    }
    
    QMenu {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 6px 24px 6px 12px;
        border-radius: 3px;
    }
    
    QMenu::item:selected {
        background-color: #e3f2fd;
    }
    
    /* 状态栏样式 */
    QStatusBar {
        background-color: #f5f5f5;
        border-top: 1px solid #e0e0e0;
    }
    
    /* 工具提示样式 */
    QToolTip {
        background-color: #333333;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 10px;
    }
    """


def get_dark_stylesheet():
    """获取深色主题样式表"""
    return """
    QMainWindow {
        background-color: #202020;
    }
    
    QWidget {
        font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
        font-size: 10pt;
        color: #e0e0e0;
    }
    
    QGroupBox {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        margin-top: 10px;
        padding: 15px;
        font-weight: bold;
        color: #e0e0e0;
    }
    
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #106ebe;
    }
    
    QPushButton#secondaryButton {
        background-color: #3d3d3d;
        color: #e0e0e0;
        border: 1px solid #505050;
    }
    
    QTableWidget {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        color: #e0e0e0;
        gridline-color: #404040;
    }
    
    QTableWidget::item:selected {
        background-color: #0078d4;
    }
    
    QHeaderView::section {
        background-color: #353535;
        color: #e0e0e0;
        border-bottom: 2px solid #505050;
    }
    
    QLineEdit, QComboBox {
        background-color: #2d2d2d;
        border: 1px solid #505050;
        color: #e0e0e0;
    }
    
    QProgressBar {
        background-color: #353535;
    }
    
    QTabWidget::pane {
        background-color: #2d2d2d;
        border: 1px solid #404040;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        color: #e0e0e0;
    }
    
    QTabBar::tab:selected {
        background-color: #353535;
        border-bottom: 2px solid #0078d4;
    }
    """

