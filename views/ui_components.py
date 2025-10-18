#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent UI组件
使用PySide6-Fluent-Widgets创建现代化界面组件
"""

from typing import List, Optional, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSplitter, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

from qfluentwidgets import (
    FluentIcon as FIF, 
    CardWidget, 
    HeaderCardWidget,
    ElevatedCardWidget,
    SimpleCardWidget,
    PushButton,
    PrimaryPushButton,
    ToolButton,
    SearchLineEdit,
    ComboBox,
    ProgressBar,
    InfoBar,
    InfoBarPosition,
    TableWidget,
    TextEdit,
    BodyLabel,
    StrongBodyLabel,
    CaptionLabel,
    TitleLabel,
    SubtitleLabel,
    LargeTitleLabel,
    DisplayLabel,
    ScrollArea,
    FlowLayout,
    ProgressRing,
    IndeterminateProgressRing,
    Pivot,
    PivotItem,
    SplitPushButton,
    RoundMenu,
    Action,
    MenuAnimationType,
    Theme,
    setTheme,
    isDarkTheme,
    qconfig
)

from models import SystemInfo, ProcessInfo, NetworkConnection, format_bytes, format_frequency


class SystemOverviewCard(ElevatedCardWidget):
    """系统概览卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(200)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = SubtitleLabel("系统概览")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 资源使用情况网格
        grid_layout = QGridLayout()
        
        # CPU卡片
        self.cpu_card = self._create_resource_card("CPU", "0%", FIF.HOME)
        self.cpu_progress = ProgressBar()
        self.cpu_progress.setFixedHeight(8)
        
        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(self.cpu_card)
        cpu_layout.addWidget(self.cpu_progress)
        
        # 内存卡片
        self.memory_card = self._create_resource_card("内存", "0%", FIF.HOME)
        self.memory_progress = ProgressBar()
        self.memory_progress.setFixedHeight(8)
        
        memory_layout = QVBoxLayout()
        memory_layout.addWidget(self.memory_card)
        memory_layout.addWidget(self.memory_progress)
        
        # 磁盘卡片
        self.disk_card = self._create_resource_card("磁盘", "0%", FIF.HOME)
        self.disk_progress = ProgressBar()
        self.disk_progress.setFixedHeight(8)
        
        disk_layout = QVBoxLayout()
        disk_layout.addWidget(self.disk_card)
        disk_layout.addWidget(self.disk_progress)
        
        # 添加到网格
        grid_layout.addLayout(cpu_layout, 0, 0)
        grid_layout.addLayout(memory_layout, 0, 1)
        grid_layout.addLayout(disk_layout, 0, 2)
        
        layout.addLayout(grid_layout)
    
    def _create_resource_card(self, title: str, value: str, icon) -> QWidget:
        """创建资源使用卡片"""
        card = SimpleCardWidget()
        card.setFixedHeight(60)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 图标
        icon_label = QLabel()
        icon_pixmap = icon.icon(color=QColor(0, 120, 215)).pixmap(24, 24)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(24, 24)
        
        # 文本信息
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = CaptionLabel(title)
        title_label.setStyleSheet("color: #666666;")
        
        self.value_label = StrongBodyLabel(value)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
    
    def update_system_info(self, info: SystemInfo):
        """更新系统信息"""
        # 更新CPU
        cpu_percent = int(info.cpu_percent)
        self.cpu_progress.setValue(cpu_percent)
        self.cpu_card.findChild(StrongBodyLabel).setText(f"{cpu_percent}%")
        
        # 更新内存
        memory_percent = int(info.memory_percent)
        self.memory_progress.setValue(memory_percent)
        memory_gb = info.memory_used / (1024**3)
        total_gb = info.memory_total / (1024**3)
        self.memory_card.findChild(StrongBodyLabel).setText(f"{memory_percent}% ({memory_gb:.1f}GB)")
        
        # 更新磁盘
        disk_percent = int(info.disk_percent)
        self.disk_progress.setValue(disk_percent)
        disk_gb = info.disk_used / (1024**3)
        total_disk_gb = info.disk_total / (1024**3)
        self.disk_card.findChild(StrongBodyLabel).setText(f"{disk_percent}% ({disk_gb:.1f}GB)")


class ProcessTableCard(ElevatedCardWidget):
    """进程表格卡片"""
    
    # 信号定义
    process_selected = Signal(int)
    kill_requested = Signal(int, bool)  # pid, force
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_processes = []
        self.filtered_processes = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和控制栏
        header_layout = QHBoxLayout()
        
        title = SubtitleLabel("进程管理")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 搜索框
        self.search_box = SearchLineEdit()
        self.search_box.setPlaceholderText("搜索进程...")
        self.search_box.setFixedWidth(200)
        self.search_box.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_box)
        
        # 排序选择
        self.sort_combo = ComboBox()
        self.sort_combo.addItems(["CPU使用率", "内存使用率", "进程名", "PID"])
        self.sort_combo.setFixedWidth(120)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        header_layout.addWidget(self.sort_combo)
        
        # 刷新按钮
        self.refresh_btn = PrimaryPushButton(FIF.HOME, "刷新")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 进程表格
        self.table = TableWidget()
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
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # PID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 进程名
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CPU
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 内存%
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 内存MB
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 状态
        
        # 右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        # 选择变化
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table)
        
        # 操作按钮栏
        button_layout = QHBoxLayout()
        
        self.kill_btn = PushButton(FIF.HOME, "结束进程")
        self.kill_btn.clicked.connect(self._on_kill_clicked)
        self.kill_btn.setEnabled(False)
        
        self.force_kill_btn = PushButton(FIF.HOME, "强制结束")
        self.force_kill_btn.clicked.connect(self._on_force_kill_clicked)
        self.force_kill_btn.setEnabled(False)
        
        self.details_btn = PushButton(FIF.HOME, "详细信息")
        self.details_btn.clicked.connect(self._on_details_clicked)
        self.details_btn.setEnabled(False)
        
        button_layout.addWidget(self.kill_btn)
        button_layout.addWidget(self.force_kill_btn)
        button_layout.addWidget(self.details_btn)
        button_layout.addStretch()
        
        # 进程统计标签
        self.stats_label = CaptionLabel("进程数: 0")
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
        
        if has_selection:
            current_row = self.table.currentRow()
            if current_row >= 0:
                pid_item = self.table.item(current_row, 0)
                if pid_item:
                    pid = int(pid_item.text())
                    self.process_selected.emit(pid)
    
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
线程数: {process.num_threads}
可执行文件: {process.exe_path or '未知'}
"""
        
        if process.parent_pid:
            details += f"父进程PID: {process.parent_pid}\n"
        
        QMessageBox.information(self, "进程详情", details)
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.table.itemAt(position)
        if item is None:
            return
        
        menu = RoundMenu(parent=self)
        
        # 刷新
        refresh_action = Action(FIF.HOME, "刷新进程列表")
        refresh_action.triggered.connect(self.refresh_requested.emit)
        menu.addAction(refresh_action)
        
        menu.addSeparator()
        
        # 进程操作
        details_action = Action(FIF.HOME, "查看详情")
        details_action.triggered.connect(self._on_details_clicked)
        menu.addAction(details_action)
        
        kill_action = Action(FIF.HOME, "结束进程")
        kill_action.triggered.connect(self._on_kill_clicked)
        menu.addAction(kill_action)
        
        force_kill_action = Action(FIF.HOME, "强制结束")
        force_kill_action.triggered.connect(self._on_force_kill_clicked)
        menu.addAction(force_kill_action)
        
        menu.exec(self.table.mapToGlobal(position), aniType=MenuAnimationType.DROP_DOWN)


class NetworkTableCard(ElevatedCardWidget):
    """网络连接表格卡片"""
    
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_connections = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和控制栏
        header_layout = QHBoxLayout()
        
        title = SubtitleLabel("网络连接")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 协议过滤
        self.protocol_combo = ComboBox()
        self.protocol_combo.addItems(["全部", "TCP", "UDP"])
        self.protocol_combo.setFixedWidth(100)
        self.protocol_combo.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(QLabel("协议:"))
        header_layout.addWidget(self.protocol_combo)
        
        # 状态过滤
        self.status_combo = ComboBox()
        self.status_combo.addItems(["全部", "LISTEN", "ESTABLISHED", "TIME_WAIT"])
        self.status_combo.setFixedWidth(120)
        self.status_combo.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(QLabel("状态:"))
        header_layout.addWidget(self.status_combo)
        
        # 刷新按钮
        self.refresh_btn = PrimaryPushButton(FIF.HOME, "刷新")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 网络连接表格
        self.table = TableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "协议", "本地地址", "远程地址", "状态", "PID"
        ])
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 协议
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 本地地址
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 远程地址
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 状态
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # PID
        
        layout.addWidget(self.table)
        
        # 统计信息
        self.stats_label = CaptionLabel("连接数: 0")
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


class HardwareInfoCard(ElevatedCardWidget):
    """硬件信息卡片"""
    
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和刷新按钮
        header_layout = QHBoxLayout()
        
        title = SubtitleLabel("硬件信息")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_btn = PrimaryPushButton(FIF.HOME, "刷新")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # 硬件信息文本区域
        self.info_text = TextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.info_text)
    
    def update_hardware_info(self, hardware_info: Dict):
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


class SystemStatsCard(SimpleCardWidget):
    """系统统计卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题
        title = StrongBodyLabel("系统统计")
        layout.addWidget(title)
        
        # 统计信息网格
        stats_layout = QGridLayout()
        
        # 启动时间
        self.boot_time_label = CaptionLabel("启动时间: --")
        stats_layout.addWidget(self.boot_time_label, 0, 0)
        
        # 运行时间
        self.uptime_label = CaptionLabel("运行时间: --")
        stats_layout.addWidget(self.uptime_label, 0, 1)
        
        # 进程数
        self.process_count_label = CaptionLabel("进程数: --")
        stats_layout.addWidget(self.process_count_label, 1, 0)
        
        # CPU核心数
        self.cpu_count_label = CaptionLabel("CPU核心: --")
        stats_layout.addWidget(self.cpu_count_label, 1, 1)
        
        layout.addLayout(stats_layout)
    
    def update_system_info(self, info: SystemInfo):
        """更新系统统计信息"""
        self.boot_time_label.setText(f"启动时间: {info.boot_time}")
        self.uptime_label.setText(f"运行时间: {info.uptime}")
        self.process_count_label.setText(f"进程数: {info.process_count}")
        self.cpu_count_label.setText(f"CPU核心: {info.cpu_count}")


# 消息提示函数已移至 ui_utils.py
