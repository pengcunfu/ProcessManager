#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
界面组件模块
定义应用程序的所有UI组件和界面布局
"""

from typing import List, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QTextEdit, QProgressBar, QGroupBox, QHeaderView,
    QMessageBox, QLineEdit, QComboBox, QSplitter,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from system_monitor import SystemInfo, ProcessInfo, NetworkConnection, format_bytes, format_frequency
from styles import AppStyles, ProgressBarStyles, ButtonStyles, TableStyles


class InfoCard(QGroupBox):
    """信息卡片组件"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(AppStyles.GROUP_BOX)
        self.layout = QVBoxLayout(self)
        
    def add_info_label(self, text: str) -> QLabel:
        """添加信息标签"""
        label = QLabel(text)
        label.setStyleSheet(AppStyles.INFO_LABEL)
        self.layout.addWidget(label)
        return label
    
    def add_progress_bar(self, initial_value: int = 0) -> QProgressBar:
        """添加进度条"""
        progress = QProgressBar()
        progress.setValue(initial_value)
        self.layout.addWidget(progress)
        return progress


class SystemOverviewWidget(QWidget):
    """系统概览组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 实时信息区域
        realtime_group = QGroupBox("实时系统信息")
        realtime_group.setStyleSheet(AppStyles.GROUP_BOX)
        realtime_layout = QGridLayout(realtime_group)
        
        # CPU信息卡片
        self.cpu_card = InfoCard("CPU使用率")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet(ProgressBarStyles.get_cpu_style())
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_card.layout.addWidget(self.cpu_progress)
        self.cpu_card.layout.addWidget(self.cpu_label)
        
        # 内存信息卡片
        self.memory_card = InfoCard("内存使用率")
        self.memory_progress = QProgressBar()
        self.memory_progress.setStyleSheet(ProgressBarStyles.get_memory_style())
        self.memory_label = QLabel("内存: 0%")
        self.memory_card.layout.addWidget(self.memory_progress)
        self.memory_card.layout.addWidget(self.memory_label)
        
        # 磁盘信息卡片
        self.disk_card = InfoCard("磁盘使用率")
        self.disk_progress = QProgressBar()
        self.disk_progress.setStyleSheet(ProgressBarStyles.get_disk_style())
        self.disk_label = QLabel("磁盘: 0%")
        self.disk_card.layout.addWidget(self.disk_progress)
        self.disk_card.layout.addWidget(self.disk_label)
        
        # 添加到网格布局
        realtime_layout.addWidget(self.cpu_card, 0, 0)
        realtime_layout.addWidget(self.memory_card, 0, 1)
        realtime_layout.addWidget(self.disk_card, 1, 0, 1, 2)
        
        layout.addWidget(realtime_group)
        
        # 系统基本信息
        self.basic_info_card = InfoCard("系统基本信息")
        basic_info_layout = QGridLayout()
        
        import platform
        self.computer_name_label = QLabel(f"计算机名称: {platform.node()}")
        self.os_label = QLabel(f"操作系统: {platform.system()} {platform.release()}")
        self.architecture_label = QLabel(f"系统架构: {platform.architecture()[0]}")
        self.processor_label = QLabel(f"处理器: {platform.processor()}")
        
        basic_info_layout.addWidget(self.computer_name_label, 0, 0)
        basic_info_layout.addWidget(self.os_label, 0, 1)
        basic_info_layout.addWidget(self.architecture_label, 1, 0)
        basic_info_layout.addWidget(self.processor_label, 1, 1)
        
        # 清空原有布局并添加网格布局
        for i in reversed(range(self.basic_info_card.layout.count())):
            self.basic_info_card.layout.itemAt(i).widget().setParent(None)
        self.basic_info_card.layout.addLayout(basic_info_layout)
        
        layout.addWidget(self.basic_info_card)
    
    def update_system_info(self, info: SystemInfo):
        """更新系统信息显示"""
        # 更新CPU信息
        cpu_percent = int(info.cpu_percent)
        self.cpu_progress.setValue(cpu_percent)
        self.cpu_label.setText(f"CPU: {cpu_percent}% ({info.cpu_count}核心)")
        
        # 更新内存信息
        memory_percent = int(info.memory_percent)
        self.memory_progress.setValue(memory_percent)
        memory_used_gb = info.memory_used / (1024**3)
        memory_total_gb = info.memory_total / (1024**3)
        self.memory_label.setText(f"内存: {memory_percent}% ({memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB)")
        
        # 更新磁盘信息
        disk_percent = int(info.disk_percent)
        self.disk_progress.setValue(disk_percent)
        disk_used_gb = info.disk_used / (1024**3)
        disk_total_gb = info.disk_total / (1024**3)
        self.disk_label.setText(f"磁盘: {disk_percent}% ({disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB)")


class ProcessTableWidget(QWidget):
    """进程表格组件"""
    
    process_selected = Signal(int)  # 进程被选中信号
    kill_requested = Signal(int)   # 请求结束进程信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新进程列表")
        self.refresh_btn.setStyleSheet(ButtonStyles.get_primary_style())
        
        # 结束进程按钮
        self.kill_btn = QPushButton("结束选中进程")
        self.kill_btn.setStyleSheet(ButtonStyles.get_danger_style())
        self.kill_btn.clicked.connect(self._on_kill_clicked)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索进程名称...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        
        # 排序选择
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["CPU使用率", "内存使用率", "进程名", "PID"])
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        
        control_layout.addWidget(QLabel("搜索:"))
        control_layout.addWidget(self.search_edit)
        control_layout.addWidget(QLabel("排序:"))
        control_layout.addWidget(self.sort_combo)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.kill_btn)
        
        layout.addLayout(control_layout)
        
        # 进程表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "PID", "进程名", "CPU%", "内存%", "内存(MB)", "状态"
        ])
        self.table.setStyleSheet(TableStyles.get_default_style())
        
        # 设置表格属性
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table)
        
        # 存储当前进程数据
        self.current_processes = []
        self.current_filter = ""
        self.current_sort = "cpu_percent"
    
    def update_processes(self, processes: List[ProcessInfo]):
        """更新进程列表"""
        self.current_processes = processes
        self._apply_filter_and_sort()
    
    def _apply_filter_and_sort(self):
        """应用过滤和排序"""
        # 过滤
        filtered_processes = self.current_processes
        if self.current_filter:
            filtered_processes = [
                p for p in filtered_processes 
                if self.current_filter.lower() in p.name.lower()
            ]
        
        # 排序
        sort_key_map = {
            "CPU使用率": lambda x: x.cpu_percent,
            "内存使用率": lambda x: x.memory_percent,
            "进程名": lambda x: x.name.lower(),
            "PID": lambda x: x.pid
        }
        
        sort_key = sort_key_map.get(self.sort_combo.currentText(), lambda x: x.cpu_percent)
        reverse = self.sort_combo.currentText() in ["CPU使用率", "内存使用率"]
        filtered_processes.sort(key=sort_key, reverse=reverse)
        
        # 更新表格
        self.table.setRowCount(len(filtered_processes))
        
        for row, proc in enumerate(filtered_processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(proc.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(proc.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{proc.cpu_percent:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{proc.memory_percent:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{proc.memory_mb:.1f}"))
            self.table.setItem(row, 5, QTableWidgetItem(proc.status))
    
    def _on_search_changed(self, text: str):
        """搜索文本改变"""
        self.current_filter = text
        self._apply_filter_and_sort()
    
    def _on_sort_changed(self, text: str):
        """排序方式改变"""
        self._apply_filter_and_sort()
    
    def _on_selection_changed(self):
        """选择改变"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            pid_item = self.table.item(current_row, 0)
            if pid_item:
                pid = int(pid_item.text())
                self.process_selected.emit(pid)
    
    def _on_kill_clicked(self):
        """结束进程按钮点击"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            pid_item = self.table.item(current_row, 0)
            name_item = self.table.item(current_row, 1)
            
            if pid_item and name_item:
                pid = int(pid_item.text())
                name = name_item.text()
                
                reply = QMessageBox.question(
                    self, "确认", 
                    f"确定要结束进程 {name} (PID: {pid}) 吗？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.kill_requested.emit(pid)
        else:
            QMessageBox.information(self, "提示", "请先选择一个进程")


class NetworkTableWidget(QWidget):
    """网络连接表格组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新网络信息")
        self.refresh_btn.setStyleSheet(ButtonStyles.get_primary_style())
        
        # 协议过滤
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["全部", "TCP", "UDP"])
        self.protocol_combo.currentTextChanged.connect(self._on_protocol_changed)
        
        # 只显示监听端口
        self.listening_only_btn = QPushButton("仅监听端口")
        self.listening_only_btn.setStyleSheet(ButtonStyles.get_success_style())
        self.listening_only_btn.setCheckable(True)
        self.listening_only_btn.toggled.connect(self._on_listening_toggled)
        
        control_layout.addWidget(QLabel("协议:"))
        control_layout.addWidget(self.protocol_combo)
        control_layout.addWidget(self.listening_only_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(control_layout)
        
        # 网络连接表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "协议", "本地地址", "远程地址", "状态", "PID"
        ])
        self.table.setStyleSheet(TableStyles.get_default_style())
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # 存储当前连接数据
        self.current_connections = []
    
    def update_connections(self, connections: List[NetworkConnection]):
        """更新网络连接列表"""
        self.current_connections = connections
        self._apply_filters()
    
    def _apply_filters(self):
        """应用过滤器"""
        filtered_connections = self.current_connections
        
        # 协议过滤
        protocol_filter = self.protocol_combo.currentText()
        if protocol_filter != "全部":
            filtered_connections = [
                c for c in filtered_connections 
                if c.protocol == protocol_filter
            ]
        
        # 监听端口过滤
        if self.listening_only_btn.isChecked():
            filtered_connections = [
                c for c in filtered_connections 
                if c.status == "LISTEN"
            ]
        
        # 更新表格
        self.table.setRowCount(len(filtered_connections))
        
        for row, conn in enumerate(filtered_connections):
            self.table.setItem(row, 0, QTableWidgetItem(conn.protocol))
            self.table.setItem(row, 1, QTableWidgetItem(conn.local_addr))
            self.table.setItem(row, 2, QTableWidgetItem(conn.remote_addr))
            self.table.setItem(row, 3, QTableWidgetItem(conn.status))
            self.table.setItem(row, 4, QTableWidgetItem(str(conn.pid) if conn.pid else "N/A"))
    
    def _on_protocol_changed(self, text: str):
        """协议过滤改变"""
        self._apply_filters()
    
    def _on_listening_toggled(self, checked: bool):
        """监听端口过滤切换"""
        self._apply_filters()


class HardwareInfoWidget(QWidget):
    """硬件信息组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新硬件信息")
        self.refresh_btn.setStyleSheet(ButtonStyles.get_primary_style())
        layout.addWidget(self.refresh_btn)
        
        # 硬件信息文本区域
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet(AppStyles.TEXT_EDIT)
        self.info_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.info_text)
    
    def update_hardware_info(self, hardware_info: dict):
        """更新硬件信息显示"""
        info_lines = []
        
        try:
            # CPU信息
            if 'cpu' in hardware_info:
                cpu_info = hardware_info['cpu']
                info_lines.append("=== CPU信息 ===")
                info_lines.append(f"物理核心数: {cpu_info.get('physical_cores', 'N/A')}")
                info_lines.append(f"逻辑核心数: {cpu_info.get('logical_cores', 'N/A')}")
                
                if cpu_info.get('frequency'):
                    freq = cpu_info['frequency']
                    info_lines.append(f"当前频率: {format_frequency(freq.get('current', 0))}")
                    info_lines.append(f"最大频率: {format_frequency(freq.get('max', 0))}")
                    info_lines.append(f"最小频率: {format_frequency(freq.get('min', 0))}")
                
                info_lines.append(f"处理器: {cpu_info.get('processor', 'N/A')}")
                info_lines.append("")
            
            # 内存信息
            if 'memory' in hardware_info:
                mem_info = hardware_info['memory']
                info_lines.append("=== 内存信息 ===")
                info_lines.append(f"总内存: {format_bytes(mem_info.get('total', 0))}")
                info_lines.append(f"可用内存: {format_bytes(mem_info.get('available', 0))}")
                info_lines.append(f"已使用内存: {format_bytes(mem_info.get('used', 0))}")
                info_lines.append(f"内存使用率: {mem_info.get('percent', 0):.1f}%")
                info_lines.append(f"交换内存总量: {format_bytes(mem_info.get('swap_total', 0))}")
                info_lines.append(f"交换内存使用: {format_bytes(mem_info.get('swap_used', 0))}")
                info_lines.append("")
            
            # 磁盘信息
            if 'disks' in hardware_info:
                info_lines.append("=== 磁盘信息 ===")
                for disk in hardware_info['disks']:
                    info_lines.append(f"设备: {disk.get('device', 'N/A')}")
                    info_lines.append(f"挂载点: {disk.get('mountpoint', 'N/A')}")
                    info_lines.append(f"文件系统: {disk.get('fstype', 'N/A')}")
                    
                    if 'error' in disk:
                        info_lines.append(f"  {disk['error']}")
                    else:
                        info_lines.append(f"  总空间: {format_bytes(disk.get('total', 0))}")
                        info_lines.append(f"  已使用: {format_bytes(disk.get('used', 0))}")
                        info_lines.append(f"  可用空间: {format_bytes(disk.get('free', 0))}")
                        info_lines.append(f"  使用率: {disk.get('percent', 0):.1f}%")
                    info_lines.append("")
            
            # 网络接口信息
            if 'network_interfaces' in hardware_info:
                info_lines.append("=== 网络接口 ===")
                for interface_name, addresses in hardware_info['network_interfaces'].items():
                    info_lines.append(f"接口: {interface_name}")
                    for addr in addresses:
                        if 'AF_INET' in addr['family']:
                            info_lines.append(f"  IP地址: {addr['address']}")
                            if addr['netmask']:
                                info_lines.append(f"  子网掩码: {addr['netmask']}")
                        elif 'AF_PACKET' in addr['family'] or 'AF_LINK' in addr['family']:
                            info_lines.append(f"  MAC地址: {addr['address']}")
                    info_lines.append("")
            
        except Exception as e:
            info_lines.append(f"显示硬件信息时出错: {e}")
        
        self.info_text.setPlainText("\n".join(info_lines))


class SystemDetailsWidget(QWidget):
    """系统详情组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新系统详情")
        self.refresh_btn.setStyleSheet(ButtonStyles.get_primary_style())
        layout.addWidget(self.refresh_btn)
        
        # 系统详情文本区域
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet(AppStyles.TEXT_EDIT)
        self.details_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.details_text)
    
    def update_system_details(self, details: dict):
        """更新系统详情显示"""
        info_lines = []
        
        try:
            # 系统基本信息
            if 'system' in details:
                sys_info = details['system']
                info_lines.append("=== 系统基本信息 ===")
                info_lines.append(f"计算机名称: {sys_info.get('computer_name', 'N/A')}")
                info_lines.append(f"操作系统: {sys_info.get('os_name', 'N/A')}")
                info_lines.append(f"系统版本: {sys_info.get('os_release', 'N/A')}")
                info_lines.append(f"系统详细版本: {sys_info.get('os_version', 'N/A')}")
                info_lines.append(f"系统架构: {sys_info.get('architecture', 'N/A')}")
                info_lines.append(f"处理器信息: {sys_info.get('processor', 'N/A')}")
                info_lines.append(f"Python版本: {sys_info.get('python_version', 'N/A')}")
                info_lines.append(f"系统启动时间: {sys_info.get('boot_time', 'N/A')}")
                info_lines.append("")
            
            # 用户信息
            if 'users' in details:
                info_lines.append("=== 用户信息 ===")
                for user in details['users']:
                    info_lines.append(f"用户: {user.get('name', 'N/A')}")
                    info_lines.append(f"终端: {user.get('terminal', 'N/A')}")
                    info_lines.append(f"主机: {user.get('host', 'N/A')}")
                    info_lines.append(f"登录时间: {user.get('started', 'N/A')}")
                    info_lines.append("")
            
            # 环境变量
            if 'environment' in details:
                info_lines.append("=== 重要环境变量 ===")
                for var, value in details['environment'].items():
                    info_lines.append(f"{var}: {value}")
                info_lines.append("")
            
        except Exception as e:
            info_lines.append(f"显示系统详情时出错: {e}")
        
        self.details_text.setPlainText("\n".join(info_lines))


class StatusBar(QWidget):
    """状态栏组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("就绪")
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0%")
        self.network_label = QLabel("网络: 0 KB/s")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.cpu_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.memory_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.network_label)
    
    def update_status(self, message: str):
        """更新状态消息"""
        self.status_label.setText(message)
    
    def update_system_status(self, info: SystemInfo):
        """更新系统状态"""
        self.cpu_label.setText(f"CPU: {info.cpu_percent:.1f}%")
        self.memory_label.setText(f"内存: {info.memory_percent:.1f}%")
        
        # 计算网络速度（简化版本）
        total_bytes = info.bytes_sent + info.bytes_recv
        self.network_label.setText(f"网络: {format_bytes(total_bytes)}")


# 工具函数
def show_error_message(parent, title: str, message: str):
    """显示错误消息"""
    QMessageBox.critical(parent, title, message)


def show_info_message(parent, title: str, message: str):
    """显示信息消息"""
    QMessageBox.information(parent, title, message)


def show_warning_message(parent, title: str, message: str):
    """显示警告消息"""
    QMessageBox.warning(parent, title, message)


def confirm_action(parent, title: str, message: str) -> bool:
    """确认操作"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No
    )
    return reply == QMessageBox.Yes
