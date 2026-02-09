#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件
使用原生PySide6创建界面组件
"""

from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QPushButton, QLineEdit, QComboBox, QProgressBar,
    QTextEdit, QDialog, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QBrush

from app.models import SystemInfo, ProcessInfo, NetworkConnection, format_bytes, format_frequency
from app.controllers.traffic_controller import ProcessTrafficInfo
from app.views.ui_utils import StyledTableWidget, StyledButton, StyledGroupBox


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
        grid_layout.addWidget(self.cpu_value, 0, 1, Qt.AlignRight)
        grid_layout.addWidget(self.cpu_progress, 1, 0, 1, 2)
        
        # 内存
        memory_label = QLabel("内存使用率")
        self.memory_value = QLabel("0%")
        self.memory_progress = QProgressBar()
        self.memory_progress.setFixedHeight(10)
        
        grid_layout.addWidget(memory_label, 2, 0)
        grid_layout.addWidget(self.memory_value, 2, 1, Qt.AlignRight)
        grid_layout.addWidget(self.memory_progress, 3, 0, 1, 2)
        
        # 磁盘
        disk_label = QLabel("磁盘使用率")
        self.disk_value = QLabel("0%")
        self.disk_progress = QProgressBar()
        self.disk_progress.setFixedHeight(10)
        
        grid_layout.addWidget(disk_label, 4, 0)
        grid_layout.addWidget(self.disk_value, 4, 1, Qt.AlignRight)
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


class ProcessTableCard(StyledGroupBox):
    """进程表格卡片"""

    # 信号定义
    refresh_requested = Signal()
    kill_requested = Signal(int, bool)  # pid, force

    def __init__(self, parent=None):
        super().__init__("进程管理", parent)
        self.current_processes = []
        self.filtered_processes = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索进程...")
        self.search_box.setFixedWidth(200)
        self.search_box.textChanged.connect(self._on_search_changed)
        control_layout.addWidget(self.search_box)
        
        # 排序选择
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["CPU使用率", "内存使用率", "进程名", "PID"])
        self.sort_combo.setFixedWidth(120)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        control_layout.addWidget(self.sort_combo)

        control_layout.addStretch()

        # 刷新按钮
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        control_layout.addWidget(refresh_btn)
        
        layout.addLayout(control_layout)

        # 进程表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "PID", "进程名", "CPU%", "内存%", "内存(MB)", "状态"
        ])
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # 选择变化
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table)
        
        # 操作按钮栏
        button_layout = QHBoxLayout()
        
        self.kill_btn = StyledButton("结束进程", StyledButton.PRIMARY)
        self.kill_btn.clicked.connect(self._on_kill_clicked)
        self.kill_btn.setEnabled(False)

        self.force_kill_btn = StyledButton("强制结束", StyledButton.DANGER)
        self.force_kill_btn.clicked.connect(self._on_force_kill_clicked)
        self.force_kill_btn.setEnabled(False)

        self.details_btn = StyledButton("详细信息", StyledButton.PRIMARY)
        self.details_btn.clicked.connect(self._on_details_clicked)
        self.details_btn.setEnabled(False)
        
        button_layout.addWidget(self.kill_btn)
        button_layout.addWidget(self.force_kill_btn)
        button_layout.addWidget(self.details_btn)
        button_layout.addStretch()
        
        # 进程统计标签
        self.stats_label = QLabel("进程数: 0")
        button_layout.addWidget(self.stats_label)
        
        layout.addLayout(button_layout)
    
    def update_processes(self, processes: List[ProcessInfo]):
        """更新进程列表"""
        self.current_processes = processes
        self._apply_filter_and_sort()
        self.stats_label.setText(f"进程数: {len(processes)}")
    
    def _apply_filter_and_sort(self):
        """应用过滤和排序"""
        # 过滤
        search_text = self.search_box.text().lower()
        if search_text:
            self.filtered_processes = [
                p for p in self.current_processes 
                if search_text in p.name.lower()
            ]
        else:
            self.filtered_processes = self.current_processes.copy()
        
        # 排序
        sort_key_map = {
            "CPU使用率": lambda x: x.cpu_percent,
            "内存使用率": lambda x: x.memory_percent,
            "进程名": lambda x: x.name.lower(),
            "PID": lambda x: x.pid
        }
        
        sort_key = sort_key_map.get(self.sort_combo.currentText(), lambda x: x.cpu_percent)
        reverse = self.sort_combo.currentText() in ["CPU使用率", "内存使用率"]
        self.filtered_processes.sort(key=sort_key, reverse=reverse)
        
        # 更新表格
        self.table.setRowCount(len(self.filtered_processes))
        
        for row, proc in enumerate(self.filtered_processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(proc.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(proc.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{proc.cpu_percent:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{proc.memory_percent:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{proc.memory_mb:.1f}"))
            self.table.setItem(row, 5, QTableWidgetItem(proc.status))
    
    def _on_search_changed(self):
        """搜索文本改变"""
        self._apply_filter_and_sort()
    
    def _on_sort_changed(self):
        """排序方式改变"""
        self._apply_filter_and_sort()
    
    def _on_selection_changed(self):
        """选择改变"""
        has_selection = len(self.table.selectedItems()) > 0
        self.kill_btn.setEnabled(has_selection)
        self.force_kill_btn.setEnabled(has_selection)
        self.details_btn.setEnabled(has_selection)
    
    def _on_kill_clicked(self):
        """结束进程"""
        self._kill_process(force=False)
    
    def _on_force_kill_clicked(self):
        """强制结束进程"""
        self._kill_process(force=True)
    
    def _kill_process(self, force: bool):
        """结束进程"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            pid_item = self.table.item(current_row, 0)
            name_item = self.table.item(current_row, 1)
            
            if pid_item and name_item:
                pid = int(pid_item.text())
                name = name_item.text()
                
                action_text = "强制结束" if force else "结束"
                reply = QMessageBox.question(
                    self, "确认操作", 
                    f"确定要{action_text}进程 {name} (PID: {pid}) 吗？",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.kill_requested.emit(pid, force)
    
    def _on_details_clicked(self):
        """显示进程详情"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_processes):
            process = self.filtered_processes[current_row]
            self._show_process_details(process)
    
    def _show_process_details(self, process: ProcessInfo):
        """显示进程详细信息"""
        details = f"""进程详细信息:

PID: {process.pid}
进程名称: {process.name}
状态: {process.status}
创建时间: {process.create_time}
CPU使用率: {process.cpu_percent:.1f}%
内存使用率: {process.memory_percent:.2f}%
内存使用量: {process.memory_mb:.2f} MB
"""
        
        QMessageBox.information(self, "进程详情", details)


class NetworkTableCard(StyledGroupBox):
    """网络连接表格卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("网络连接", parent)
        self.current_connections = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 协议过滤
        control_layout.addWidget(QLabel("协议:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["全部", "TCP", "UDP"])
        self.protocol_combo.setFixedWidth(100)
        self.protocol_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.protocol_combo)
        
        # 状态过滤
        control_layout.addWidget(QLabel("状态:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "LISTEN", "ESTABLISHED", "TIME_WAIT"])
        self.status_combo.setFixedWidth(120)
        self.status_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.status_combo)

        control_layout.addStretch()

        # 刷新按钮
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        control_layout.addWidget(refresh_btn)
        
        layout.addLayout(control_layout)

        # 网络连接表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "协议", "本地地址", "远程地址", "状态", "PID"
        ])
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # 统计信息
        self.stats_label = QLabel("连接数: 0")
        layout.addWidget(self.stats_label)
    
    def update_connections(self, connections: List[NetworkConnection]):
        """更新网络连接列表"""
        self.current_connections = connections
        self._apply_filters()
        self.stats_label.setText(f"连接数: {len(connections)}")
    
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
        
        # 状态过滤
        status_filter = self.status_combo.currentText()
        if status_filter != "全部":
            filtered_connections = [
                c for c in filtered_connections 
                if c.status == status_filter
            ]
        
        # 更新表格
        self.table.setRowCount(len(filtered_connections))
        
        for row, conn in enumerate(filtered_connections):
            self.table.setItem(row, 0, QTableWidgetItem(conn.protocol))
            self.table.setItem(row, 1, QTableWidgetItem(conn.local_addr))
            self.table.setItem(row, 2, QTableWidgetItem(conn.remote_addr))
            self.table.setItem(row, 3, QTableWidgetItem(conn.status))
            self.table.setItem(row, 4, QTableWidgetItem(str(conn.pid) if conn.pid else "N/A"))
    
    def _on_filter_changed(self):
        """过滤器改变"""
        self._apply_filters()


class HardwareInfoCard(StyledGroupBox):
    """硬件信息卡片"""

    refresh_requested = Signal()
    detail_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("硬件信息", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 刷新按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        detail_btn = StyledButton("查看详情", StyledButton.PRIMARY)
        detail_btn.clicked.connect(self.detail_requested.emit)
        button_layout.addWidget(detail_btn)
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 硬件信息文本区域
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
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


class TrafficMonitorCard(StyledGroupBox):
    """网络流量监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("实时流量监控", parent)
        self.setFixedHeight(220)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 实时速率显示
        speed_layout = QHBoxLayout()
        
        # 上传速度
        upload_box = QVBoxLayout()
        upload_label = QLabel("上传速度")
        upload_label.setAlignment(Qt.AlignCenter)
        self.upload_speed = QLabel("0 B/s")
        self.upload_speed.setAlignment(Qt.AlignCenter)
        upload_box.addWidget(upload_label)
        upload_box.addWidget(self.upload_speed)
        
        # 下载速度
        download_box = QVBoxLayout()
        download_label = QLabel("下载速度")
        download_label.setAlignment(Qt.AlignCenter)
        self.download_speed = QLabel("0 B/s")
        self.download_speed.setAlignment(Qt.AlignCenter)
        download_box.addWidget(download_label)
        download_box.addWidget(self.download_speed)
        
        speed_layout.addLayout(upload_box)
        speed_layout.addLayout(download_box)
        layout.addLayout(speed_layout)
        
        # 分隔线
        line = QLabel()
        line.setFrameStyle(QLabel.HLine | QLabel.Sunken)
        layout.addWidget(line)
        
        # 总流量统计
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("总上传:"), 0, 0)
        self.total_sent = QLabel("0 B")
        stats_layout.addWidget(self.total_sent, 0, 1)
        
        stats_layout.addWidget(QLabel("总下载:"), 0, 2)
        self.total_recv = QLabel("0 B")
        stats_layout.addWidget(self.total_recv, 0, 3)
        
        stats_layout.addWidget(QLabel("发送包:"), 1, 0)
        self.packets_sent = QLabel("0")
        stats_layout.addWidget(self.packets_sent, 1, 1)
        
        stats_layout.addWidget(QLabel("接收包:"), 1, 2)
        self.packets_recv = QLabel("0")
        stats_layout.addWidget(self.packets_recv, 1, 3)
        
        layout.addLayout(stats_layout)
    
    def update_traffic(self, traffic_data: dict):
        """更新流量信息"""
        # 更新实时速度
        upload_speed = traffic_data.get('upload_speed', 0)
        download_speed = traffic_data.get('download_speed', 0)
        
        self.upload_speed.setText(f"{format_bytes(int(upload_speed))}/s")
        self.download_speed.setText(f"{format_bytes(int(download_speed))}/s")
        
        # 更新总流量
        total_sent = traffic_data.get('total_sent', 0)
        total_recv = traffic_data.get('total_recv', 0)
        
        self.total_sent.setText(format_bytes(total_sent))
        self.total_recv.setText(format_bytes(total_recv))
        
        # 更新包统计
        packets_sent = traffic_data.get('packets_sent', 0)
        packets_recv = traffic_data.get('packets_recv', 0)
        
        self.packets_sent.setText(f"{packets_sent:,}")
        self.packets_recv.setText(f"{packets_recv:,}")


class ProcessTrafficCard(StyledGroupBox):
    """进程流量统计卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("进程流量统计", parent)
        self.current_traffic = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        info_label = QLabel("💡 提示: 需要管理员权限才能查看详细的进程流量")
        control_layout.addWidget(info_label)
        
        control_layout.addStretch()

        # 刷新按钮
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        control_layout.addWidget(refresh_btn)

        layout.addLayout(control_layout)

        # 进程流量表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "PID", "进程名", "连接数", "读取", "写入"
        ])
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # 统计信息
        self.stats_label = QLabel("进程数: 0")
        layout.addWidget(self.stats_label)
    
    def update_process_traffic(self, traffic_list: List[ProcessTrafficInfo]):
        """更新进程流量列表"""
        self.current_traffic = traffic_list
        
        # 只显示前50个（性能考虑）
        display_list = traffic_list[:50]
        
        self.table.setRowCount(len(display_list))
        
        for row, traffic in enumerate(display_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(traffic.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(traffic.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(traffic.connections_count)))
            self.table.setItem(row, 3, QTableWidgetItem(format_bytes(traffic.bytes_recv)))
            self.table.setItem(row, 4, QTableWidgetItem(format_bytes(traffic.bytes_sent)))

        self.stats_label.setText(f"显示进程: {len(display_list)} / 总计: {len(traffic_list)}")


class HardwareInfoDialog(QDialog):
    """硬件信息对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("硬件信息")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # CPU信息标签页
        self.cpu_text = self.create_tab("CPU信息", "cpu")
        # 内存信息标签页
        self.memory_text = self.create_tab("内存信息", "memory")
        # 磁盘信息标签页
        self.disk_text = self.create_tab("磁盘信息", "disk")
        # 网络接口标签页
        self.network_text = self.create_tab("网络接口", "network")

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_info)
        button_layout.addWidget(refresh_btn)

        close_btn = StyledButton("关闭", StyledButton.PRIMARY)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def create_tab(self, title, key):
        """创建标签页"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        scroll_area.setWidget(text_edit)
        self.tab_widget.addTab(scroll_area, title)

        return text_edit

    def update_hardware_info(self, hardware_info: dict):
        """更新硬件信息显示"""

        # 更新CPU信息
        self.update_cpu_info(hardware_info.get('cpu', {}))

        # 更新内存信息
        self.update_memory_info(hardware_info.get('memory', {}))

        # 更新磁盘信息
        self.update_disk_info(hardware_info.get('disks', []))

        # 更新网络接口信息
        self.update_network_info(hardware_info.get('network_interfaces', {}))

    def update_cpu_info(self, cpu_info: dict):
        """更新CPU信息"""
        info_lines = []

        try:
            info_lines.append("<h2>CPU 处理器信息</h2>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

            if cpu_info.get('processor'):
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>处理器型号</b></td><td>{cpu_info['processor']}</td></tr>")

            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>物理核心数</b></td><td>{cpu_info.get('physical_cores', 'N/A')}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>逻辑核心数</b></td><td>{cpu_info.get('logical_cores', 'N/A')}</td></tr>")

            if cpu_info.get('frequency'):
                freq = cpu_info['frequency']
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>当前频率</b></td><td>{format_frequency(freq.get('current', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最大频率</b></td><td>{format_frequency(freq.get('max', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最小频率</b></td><td>{format_frequency(freq.get('min', 0))}</td></tr>")

            info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示CPU信息时出错: {e}</p>")

        self.cpu_text.setHtml("".join(info_lines))

    def update_memory_info(self, mem_info: dict):
        """更新内存信息"""
        info_lines = []

        try:
            info_lines.append("<h2>内存信息</h2>")

            # 物理内存
            info_lines.append("<h3>物理内存</h3>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>总内存</b></td><td>{format_bytes(mem_info.get('total', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>可用内存</b></td><td>{format_bytes(mem_info.get('available', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用内存</b></td><td>{format_bytes(mem_info.get('used', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>内存使用率</b></td><td>{mem_info.get('percent', 0):.1f}%</td></tr>")
            info_lines.append("</table>")

            # 交换内存
            info_lines.append("<h3>交换内存</h3>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>交换内存总量</b></td><td>{format_bytes(mem_info.get('swap_total', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用交换内存</b></td><td>{format_bytes(mem_info.get('swap_used', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>空闲交换内存</b></td><td>{format_bytes(mem_info.get('swap_free', 0))}</td></tr>")
            info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示内存信息时出错: {e}</p>")

        self.memory_text.setHtml("".join(info_lines))

    def update_disk_info(self, disks: list):
        """更新磁盘信息"""
        info_lines = []

        try:
            info_lines.append("<h2>磁盘信息</h2>")

            for idx, disk in enumerate(disks, 1):
                info_lines.append(f"<h3>磁盘 {idx}</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>设备</b></td><td>{disk.get('device', 'N/A')}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>挂载点</b></td><td>{disk.get('mountpoint', 'N/A')}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>文件系统类型</b></td><td>{disk.get('fstype', 'N/A')}</td></tr>")

                if 'error' in disk:
                    info_lines.append(f"<tr><td colspan='2' style='color: red;'>{disk['error']}</td></tr>")
                else:
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>总空间</b></td><td>{format_bytes(disk.get('total', 0))}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用</b></td><td>{format_bytes(disk.get('used', 0))}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>可用空间</b></td><td>{format_bytes(disk.get('free', 0))}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>使用率</b></td><td>{disk.get('percent', 0):.1f}%</td></tr>")

                info_lines.append("</table><br>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示磁盘信息时出错: {e}</p>")

        self.disk_text.setHtml("".join(info_lines))

    def update_network_info(self, interfaces: dict):
        """更新网络接口信息"""
        info_lines = []

        try:
            info_lines.append("<h2>网络接口信息</h2>")

            for idx, (interface_name, addresses) in enumerate(interfaces.items(), 1):
                info_lines.append(f"<h3>{interface_name}</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                for addr in addresses:
                    if 'AF_INET' in addr['family']:
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>IP地址</b></td><td>{addr['address']}</td></tr>")
                        if addr.get('netmask'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>子网掩码</b></td><td>{addr['netmask']}</td></tr>")
                        if addr.get('broadcast'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>广播地址</b></td><td>{addr['broadcast']}</td></tr>")
                    elif 'AF_INET6' in addr['family']:
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>IPv6地址</b></td><td>{addr['address']}</td></tr>")
                    elif 'AF_PACKET' in addr['family'] or 'AF_LINK' in addr['family']:
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>MAC地址</b></td><td>{addr['address']}</td></tr>")

                info_lines.append("</table><br>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示网络信息时出错: {e}</p>")

        self.network_text.setHtml("".join(info_lines))

    def refresh_info(self):
        """刷新硬件信息（由主窗口调用）"""
        # 这个方法会被主窗口重写或者通过信号连接
        pass


class TemperatureMonitorCard(StyledGroupBox):
    """温度监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("温度监控", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 温度信息显示
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(300)
        layout.addWidget(self.info_text)

    def update_temperature(self, temp_info: dict):
        """更新温度信息"""
        info_lines = []

        try:
            if 'error' in temp_info:
                info_lines.append(f"<p style='color: red;'>{temp_info['error']}</p>")
            else:
                for sensor_name, temps in temp_info.items():
                    info_lines.append(f"<h3 style='color: #E65100;'>{sensor_name}</h3>")
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%; border: 1px solid #FFB74D;'>")

                    for temp in temps:
                        label = temp.get('label', 'N/A')
                        current = temp.get('current', 0)
                        high = temp.get('high')
                        critical = temp.get('critical')

                        # 根据温度设置颜色
                        if critical and current >= critical:
                            bg_color = "#FFCDD2"
                            text_color = "#B71C1C"
                        elif high and current >= high:
                            bg_color = "#FFE0B2"
                            text_color = "#E65100"
                        else:
                            bg_color = "#FFF3E0"
                            text_color = "#BF360C"

                        info_lines.append(f"<tr><td style='width: 40%; background-color: {bg_color}; color: {text_color}; font-weight: bold; padding: 8px;'>{label}</td><td style='padding: 8px; background-color: #FFF8E1;'>{current:.1f}°C")

                        if high:
                            info_lines.append(f" <span style='color: #FF9800;'>(警告: {high:.1f}°C)</span>")
                        if critical:
                            info_lines.append(f" <span style='color: #F44336;'>(严重: {critical:.1f}°C)</span>")

                        info_lines.append("</td></tr>")

                    info_lines.append("</table>")

            self.info_text.setHtml("".join(info_lines))

        except Exception as e:
            self.info_text.setHtml(f"<p style='color: red;'>显示温度信息时出错: {e}</p>")


class BatteryMonitorCard(StyledGroupBox):
    """电池监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("电池监控", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 电池信息显示
        self.info_label = QLabel("正在获取电池信息...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # 进度条
        self.battery_bar = QProgressBar()
        self.battery_bar.setMinimum(0)
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        layout.addWidget(self.battery_bar)

    def update_battery(self, battery_info: dict):
        """更新电池信息"""
        try:
            if 'error' in battery_info:
                self.info_label.setText(f"<p style='color: red;'>{battery_info['error']}</p>")
                self.battery_bar.setValue(0)
                return

            percent = battery_info.get('percent', 0)
            status = battery_info.get('status', '未知')
            time_left = battery_info.get('time_left_formatted', '')

            # 更新进度条
            self.battery_bar.setValue(int(percent))

            # 根据电量设置颜色
            if percent <= 20:
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
            elif percent <= 50:
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }")
            else:
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")

            # 更新文本
            info_text = f"<h2 style='text-align: center; color: #1976D2;'>{percent:.0f}%</h2>"
            info_text += f"<p style='text-align: center; font-size: 14px;'>"
            info_text += f"状态: <b>{status}</b><br>"
            if time_left:
                info_text += f"剩余时间: <b>{time_left}</b>"
            info_text += "</p>"

            self.info_label.setText(info_text)

        except Exception as e:
            self.info_label.setText(f"<p style='color: red;'>显示电池信息时出错: {e}</p>")


class ServicesMonitorCard(StyledGroupBox):
    """系统服务监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("系统服务", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 服务表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["服务名称", "显示名称", "状态"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def update_services(self, services: list):
        """更新服务列表"""
        try:
            if services and 'error' in services[0]:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem(services[0]['error']))
                self.table.setSpan(0, 0, 1, 3)
                return

            self.table.setRowCount(len(services))

            for row, service in enumerate(services):
                self.table.setItem(row, 0, QTableWidgetItem(service.get('name', 'N/A')))
                self.table.setItem(row, 1, QTableWidgetItem(service.get('display_name', 'N/A')))

                status_item = QTableWidgetItem(service.get('status', 'N/A'))

                # 根据状态设置颜色
                status = service.get('status', '')
                if '运行' in status:
                    status_item.setForeground(QBrush(Qt.GlobalColor.darkGreen))
                elif '停止' in status:
                    status_item.setForeground(QBrush(Qt.GlobalColor.red))

                self.table.setItem(row, 2, status_item)

            self.table.resizeColumnsToContents()

        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"显示服务信息时出错: {e}"))
            self.table.setSpan(0, 0, 1, 3)

