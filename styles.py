#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式模块
定义应用程序的所有样式和主题
"""

class AppStyles:
    """应用程序样式类"""
    
    # 主窗口样式
    MAIN_WINDOW = """
        QMainWindow {
            background-color: #f0f0f0;
        }
    """
    
    # 标签页样式
    TAB_WIDGET = """
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #0078d4;
        }
        QTabBar::tab:hover {
            background-color: #d0d0d0;
        }
    """
    
    # 分组框样式
    GROUP_BOX = """
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #333333;
        }
    """
    
    # 按钮样式
    BUTTON = """
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 100px;
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
    """
    
    # 危险按钮样式（如删除、结束进程等）
    DANGER_BUTTON = """
        QPushButton {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #c82333;
        }
        QPushButton:pressed {
            background-color: #bd2130;
        }
    """
    
    # 进度条样式
    PROGRESS_BAR_CPU = """
        QProgressBar {
            border: 2px solid #cccccc;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            background-color: #f8f9fa;
        }
        QProgressBar::chunk {
            background-color: #05B8CC;
            border-radius: 3px;
        }
    """
    
    PROGRESS_BAR_MEMORY = """
        QProgressBar {
            border: 2px solid #cccccc;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            background-color: #f8f9fa;
        }
        QProgressBar::chunk {
            background-color: #FFA500;
            border-radius: 3px;
        }
    """
    
    PROGRESS_BAR_DISK = """
        QProgressBar {
            border: 2px solid #cccccc;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            background-color: #f8f9fa;
        }
        QProgressBar::chunk {
            background-color: #32CD32;
            border-radius: 3px;
        }
    """
    
    # 表格样式
    TABLE = """
        QTableWidget {
            gridline-color: #d0d0d0;
            background-color: white;
            alternate-background-color: #f8f9fa;
            selection-background-color: #0078d4;
            selection-color: white;
        }
        QTableWidget::item {
            padding: 5px;
            border: none;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background-color: #e9ecef;
            padding: 8px;
            border: 1px solid #dee2e6;
            font-weight: bold;
        }
    """
    
    # 文本编辑器样式
    TEXT_EDIT = """
        QTextEdit {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
        }
    """
    
    # 标签样式
    LABEL = """
        QLabel {
            color: #333333;
            font-size: 11pt;
        }
    """
    
    # 信息标签样式
    INFO_LABEL = """
        QLabel {
            color: #495057;
            font-size: 10pt;
            padding: 4px;
            background-color: #f8f9fa;
            border-radius: 3px;
        }
    """
    
    @classmethod
    def get_complete_stylesheet(cls):
        """获取完整的样式表"""
        return f"""
            {cls.MAIN_WINDOW}
            {cls.TAB_WIDGET}
            {cls.GROUP_BOX}
            {cls.BUTTON}
            {cls.TABLE}
            {cls.TEXT_EDIT}
            {cls.LABEL}
        """
    
    @classmethod
    def get_theme_colors(cls):
        """获取主题颜色"""
        return {
            'primary': '#0078d4',
            'primary_hover': '#106ebe',
            'primary_pressed': '#005a9e',
            'danger': '#dc3545',
            'danger_hover': '#c82333',
            'success': '#28a745',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#f0f0f0',
            'surface': '#ffffff',
            'border': '#cccccc',
            'text': '#333333',
            'text_muted': '#6c757d'
        }


class ProgressBarStyles:
    """进度条专用样式类"""
    
    @staticmethod
    def get_cpu_style():
        return AppStyles.PROGRESS_BAR_CPU
    
    @staticmethod
    def get_memory_style():
        return AppStyles.PROGRESS_BAR_MEMORY
    
    @staticmethod
    def get_disk_style():
        return AppStyles.PROGRESS_BAR_DISK
    
    @staticmethod
    def get_custom_style(color: str):
        """获取自定义颜色的进度条样式"""
        return f"""
            QProgressBar {{
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                background-color: #f8f9fa;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """


class ButtonStyles:
    """按钮专用样式类"""
    
    @staticmethod
    def get_primary_style():
        return AppStyles.BUTTON
    
    @staticmethod
    def get_danger_style():
        return AppStyles.DANGER_BUTTON
    
    @staticmethod
    def get_success_style():
        return """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """
    
    @staticmethod
    def get_warning_style():
        return """
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """


class TableStyles:
    """表格专用样式类"""
    
    @staticmethod
    def get_default_style():
        return AppStyles.TABLE
    
    @staticmethod
    def get_compact_style():
        """紧凑型表格样式"""
        return """
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 3px;
                border: none;
                font-size: 9pt;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 6px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                font-size: 9pt;
            }
        """


# 预定义的主题
class Themes:
    """主题类"""
    
    LIGHT_THEME = {
        'name': 'Light',
        'background': '#f0f0f0',
        'surface': '#ffffff',
        'primary': '#0078d4',
        'text': '#333333'
    }
    
    DARK_THEME = {
        'name': 'Dark',
        'background': '#2b2b2b',
        'surface': '#3c3c3c',
        'primary': '#4fc3f7',
        'text': '#ffffff'
    }
    
    @classmethod
    def get_dark_stylesheet(cls):
        """获取暗色主题样式"""
        return """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3c3c3c;
                border-bottom: 2px solid #4fc3f7;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #555555;
                background-color: #3c3c3c;
            }
            QTableWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                gridline-color: #555555;
                alternate-background-color: #404040;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QLabel {
                color: #ffffff;
            }
        """
