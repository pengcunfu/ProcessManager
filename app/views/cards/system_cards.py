#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控相关卡片组件
"""

from PySide6.QtWidgets import QLabel, QGridLayout, QProgressBar, QVBoxLayout
from PySide6.QtCore import Qt

from app.models import SystemInfo
from app.views.ui_utils import StyledGroupBox


class SystemOverviewCard(StyledGroupBox):
    """系统概览卡片"""

    def __init__(self, parent=None):
        super().__init__("系统概览", parent)
        self.setFixedHeight(180)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 资源使用情况网格
        grid_layout = QGridLayout()

        # CPU
        cpu_label = QLabel("CPU使用率")
        self.cpu_value = QLabel("0%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setFixedHeight(10)

        grid_layout.addWidget(cpu_label, 0, 0)
        grid_layout.addWidget(self.cpu_value, 0, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.cpu_progress, 1, 0, 1, 2)

        # 内存
        memory_label = QLabel("内存使用率")
        self.memory_value = QLabel("0%")
        self.memory_progress = QProgressBar()
        self.memory_progress.setFixedHeight(10)

        grid_layout.addWidget(memory_label, 2, 0)
        grid_layout.addWidget(self.memory_value, 2, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.memory_progress, 3, 0, 1, 2)

        # 磁盘
        disk_label = QLabel("磁盘使用率")
        self.disk_value = QLabel("0%")
        self.disk_progress = QProgressBar()
        self.disk_progress.setFixedHeight(10)

        grid_layout.addWidget(disk_label, 4, 0)
        grid_layout.addWidget(self.disk_value, 4, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.disk_progress, 5, 0, 1, 2)

        layout.addLayout(grid_layout)

    def update_system_info(self, info: SystemInfo):
        """更新系统信息"""
        # CPU
        cpu_percent = int(info.cpu_percent)
        self.cpu_value.setText(f"{cpu_percent}%")
        self.cpu_progress.setValue(cpu_percent)

        # 内存
        memory_percent = int(info.memory_percent)
        memory_gb = info.memory_used / (1024**3)
        self.memory_value.setText(f"{memory_percent}% ({memory_gb:.1f}GB)")
        self.memory_progress.setValue(memory_percent)

        # 磁盘
        disk_percent = int(info.disk_percent)
        disk_gb = info.disk_used / (1024**3)
        self.disk_value.setText(f"{disk_percent}% ({disk_gb:.1f}GB)")
        self.disk_progress.setValue(disk_percent)


class SystemStatsCard(StyledGroupBox):
    """系统统计卡片"""

    def __init__(self, parent=None):
        super().__init__("系统统计", parent)
        self.setFixedHeight(100)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QGridLayout(self)

        # 启动时间
        self.boot_time_label = QLabel("启动时间: --")
        layout.addWidget(self.boot_time_label, 0, 0)

        # 运行时间
        self.uptime_label = QLabel("运行时间: --")
        layout.addWidget(self.uptime_label, 0, 1)

        # 进程数
        self.process_count_label = QLabel("进程数: --")
        layout.addWidget(self.process_count_label, 1, 0)

        # CPU核心数
        self.cpu_count_label = QLabel("CPU核心: --")
        layout.addWidget(self.cpu_count_label, 1, 1)

    def update_system_info(self, info: SystemInfo):
        """更新系统统计信息"""
        self.boot_time_label.setText(f"启动时间: {info.boot_time}")
        self.uptime_label.setText(f"运行时间: {info.uptime}")
        self.process_count_label.setText(f"进程数: {info.process_count}")
        self.cpu_count_label.setText(f"CPU核心: {info.cpu_count}")


class SystemInfoCard(StyledGroupBox):
    """系统详细信息卡片"""

    def __init__(self, parent=None):
        super().__init__("系统信息", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QGridLayout(self)

        row = 0

        # 操作系统
        self.system_label = QLabel("操作系统: --")
        layout.addWidget(self.system_label, row, 0)

        # 节点名
        self.node_label = QLabel("节点名: --")
        layout.addWidget(self.node_label, row, 1)
        row += 1

        # 发行版本
        self.release_label = QLabel("发行版本: --")
        layout.addWidget(self.release_label, row, 0)

        # 版本号
        self.version_label = QLabel("版本号: --")
        layout.addWidget(self.version_label, row, 1)
        row += 1

        # 架构
        self.machine_label = QLabel("架构: --")
        layout.addWidget(self.machine_label, row, 0)

        # 处理器
        self.processor_label = QLabel("处理器: --")
        layout.addWidget(self.processor_label, row, 1)
        row += 1

        # 主机名
        self.hostname_label = QLabel("主机名: --")
        layout.addWidget(self.hostname_label, row, 0)

        # 当前用户
        self.username_label = QLabel("当前用户: --")
        layout.addWidget(self.username_label, row, 1)
        row += 1

        # Python版本
        self.python_version_label = QLabel("Python版本: --")
        layout.addWidget(self.python_version_label, row, 0)

        # Python编译器
        self.python_compiler_label = QLabel("Python编译器: --")
        layout.addWidget(self.python_compiler_label, row, 1)
        row += 1

        # Python构建信息
        self.python_build_label = QLabel("Python构建: --")
        layout.addWidget(self.python_build_label, row, 0, 1, 2)

    def update_system_info(self, info: SystemInfo):
        """更新系统信息"""
        self.system_label.setText(f"操作系统: {info.system or 'N/A'}")
        self.node_label.setText(f"节点名: {info.node or 'N/A'}")
        self.release_label.setText(f"发行版本: {info.release or 'N/A'}")

        # 版本号可能很长，截断显示
        version = info.version or 'N/A'
        if len(version) > 50:
            version = version[:47] + "..."
        self.version_label.setText(f"版本号: {version}")

        self.machine_label.setText(f"架构: {info.machine or 'N/A'}")
        self.processor_label.setText(f"处理器: {info.processor or 'N/A'}")
        self.hostname_label.setText(f"主机名: {info.hostname or 'N/A'}")
        self.username_label.setText(f"当前用户: {info.username or 'N/A'}")
        self.python_version_label.setText(f"Python版本: {info.python_version or 'N/A'}")
        self.python_compiler_label.setText(f"Python编译器: {info.python_compiler or 'N/A'}")
        self.python_build_label.setText(f"Python构建: {info.python_build or 'N/A'}")
