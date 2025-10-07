#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息监控工具 - 重构版本
使用模块化设计的系统监控工具，具有清晰的架构分层
"""

import sys
import signal
import psutil
import platform
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
    QMessageBox, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QTextEdit, QProgressBar, QHeaderView, QMenuBar, QMenu, QStatusBar, QToolBar, 
    QSplitter, QGroupBox, QGridLayout, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QAction, QIcon, QFont

# 导入自定义模块（如果存在的话）
try:
    from styles import AppStyles, Themes
    from system_monitor import SystemMonitor, SystemInfoWorker, ProcessManager, NetworkMonitor
    from ui_components import (
        SystemOverviewWidget, ProcessTableWidget, NetworkTableWidget,
        HardwareInfoWidget, SystemDetailsWidget, StatusBar,
        show_error_message, show_info_message
    )
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("自定义模块不可用，使用内置实现")


class SystemInfoWorker(QThread):
    """系统信息更新工作线程"""
    info_updated = Signal(dict)
    
    def __init__(self, update_interval=2000):
        super().__init__()
        self.update_interval = update_interval
        self.running = True
        self.setTerminationEnabled(True)  # 允许线程被终止
    
    def run(self):
        # 初始化CPU百分比计算
        psutil.cpu_percent()  # 第一次调用，初始化内部状态
        
        while self.running:
            try:
                # 检查是否应该停止
                if not self.running:
                    break
                
                # 获取系统信息 - 使用非阻塞方式获取CPU使用率
                cpu_percent = psutil.cpu_percent(interval=None)  # 非阻塞获取
                
                # 再次检查是否应该停止
                if not self.running:
                    break
                    
                memory = psutil.virtual_memory()
                try:
                    disk = psutil.disk_usage('/')
                except:
                    disk = psutil.disk_usage('C:\\')
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                
                info = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'disk_percent': disk.percent,
                    'disk_used': disk.used,
                    'disk_total': disk.total,
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if self.running:  # 只有在运行状态下才发送信号
                    self.info_updated.emit(info)
                
                # 分段休眠，以便更快响应停止信号
                sleep_count = self.update_interval // 100
                for i in range(sleep_count):
                    if not self.running:
                        break
                    self.msleep(100)
                    
            except Exception as e:
                print(f"系统信息更新错误: {e}")
                if self.running:
                    # 出错时也要分段休眠
                    for i in range(50):  # 5秒分成50段
                        if not self.running:
                            break
                        self.msleep(100)
    
    def stop(self):
        self.running = False
        self.requestInterruption()  # 请求中断
        self.quit()
        if not self.wait(3000):  # 等待3秒
            self.terminate()  # 强制终止
            self.wait()


class ProcessWorker(QThread):
    """进程信息获取工作线程"""
    processes_updated = Signal(list)
    loading_started = Signal()
    loading_finished = Signal()
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.should_update = False
    
    def run(self):
        while self.running:
            if self.should_update:
                try:
                    self.loading_started.emit()
                    processes = self.get_processes()
                    self.processes_updated.emit(processes)
                    self.loading_finished.emit()
                    self.should_update = False
                except Exception as e:
                    self.error_occurred.emit(f"获取进程信息失败: {str(e)}")
                    self.loading_finished.emit()
                    self.should_update = False
            
            self.msleep(100)  # 短暂休眠，避免CPU占用过高
    
    def get_processes(self):
        """获取进程列表"""
        processes = []
        try:
            # 使用进程迭代器获取所有进程信息，限制获取的进程数量以避免长时间阻塞
            process_count = 0
            max_processes = 500  # 限制最大进程数，避免系统卡顿
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                # 检查是否应该停止
                if not self.running:
                    break
                    
                try:
                    # 跳过获取磁盘IO信息，因为这个操作很耗时且容易导致权限错误
                    process_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'] or 'Unknown',
                        'cpu_percent': proc.info['cpu_percent'] or 0,
                        'memory_percent': proc.info['memory_percent'] or 0,
                        'disk_read': 0,  # 暂时设为0，避免耗时操作
                        'status': proc.info['status'] or 'Unknown'
                    }
                    processes.append(process_info)
                    
                    process_count += 1
                    if process_count >= max_processes:
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # 进程可能在获取信息过程中消失，跳过
                    continue
                except Exception:
                    # 其他异常也跳过，避免整个获取过程中断
                    continue
                    
        except Exception as e:
            print(f"获取进程列表时出错: {e}")
        
        return processes
    
    def request_update(self):
        """请求更新进程信息"""
        self.should_update = True
    
    def stop(self):
        """停止工作线程"""
        self.running = False
        self.quit()
        self.wait()


class SystemInfoMainWindow(QMainWindow):
    """系统信息监控工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统监控与进程管理工具 v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化核心组件
        if MODULES_AVAILABLE:
            self.system_monitor = SystemMonitor()
            self.process_manager = ProcessManager()
            self.network_monitor = NetworkMonitor()
        
        # 初始化界面
        self.init_ui()
        self.init_worker_threads()
        self.connect_signals()
        
        # 初始化定时器 - 增加刷新间隔，减少系统负担
        self.timer = QTimer()
        self.timer.timeout.connect(self.request_process_update)
        self.timer.start(5000)  # 每5秒更新一次进程列表，减少频率避免卡顿
        
        # 应用样式
        self.apply_theme()
        
        # 初始加载数据
        self.request_process_update()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页组件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_tabs()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        refresh_action = QAction('刷新', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.update_process_list)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        auto_refresh_action = QAction('自动刷新', self)
        auto_refresh_action.setCheckable(True)
        auto_refresh_action.setChecked(True)
        auto_refresh_action.triggered.connect(self.toggle_auto_refresh)
        view_menu.addAction(auto_refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 刷新按钮
        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.update_process_list)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # 结束进程按钮
        kill_action = QAction('结束进程', self)
        kill_action.triggered.connect(self.kill_selected_process)
        toolbar.addAction(kill_action)

    def create_tabs(self):
        """创建所有标签页"""
        # 进程管理标签页
        self.create_process_tab()
        
        # 系统信息标签页
        self.create_system_info_tab()
        
        # 如果模块可用，创建其他标签页
        if MODULES_AVAILABLE:
            # 网络端口标签页
            self.network_widget = NetworkTableWidget()
            self.tab_widget.addTab(self.network_widget, "网络端口")
            
            # 硬件信息标签页
            self.hardware_widget = HardwareInfoWidget()
            self.tab_widget.addTab(self.hardware_widget, "硬件信息")
            
            # 系统详情标签页
            self.details_widget = SystemDetailsWidget()
            self.tab_widget.addTab(self.details_widget, "系统详情")
    
    def create_process_tab(self):
        """创建进程管理选项卡"""
        process_widget = QWidget()
        layout = QVBoxLayout(process_widget)
        
        # 搜索栏
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索进程:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入进程名称进行搜索...")
        self.search_input.textChanged.connect(self.filter_processes)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        
        # 进程表格
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels([
            'PID', '进程名称', 'CPU使用率(%)', '内存使用率(%)', '磁盘读取(MB)', '状态'
        ])
        
        # 设置表格属性
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setSortingEnabled(True)
        
        # 启用右键菜单
        self.process_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.process_table.customContextMenuRequested.connect(self.show_process_context_menu)
        
        # 设置列宽
        header = self.process_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # PID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 进程名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CPU
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 内存
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 磁盘
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 状态
        
        layout.addWidget(self.process_table)
        
        # 操作按钮（简化版本，主要功能在右键菜单中）
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 刷新进程列表")
        self.refresh_btn.clicked.connect(self.update_process_list)
        
        # 添加提示标签
        tip_label = QLabel("💡 提示：右键点击进程可查看更多操作")
        tip_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(tip_label)
        
        layout.addLayout(button_layout)
        
        # 添加加载指示器
        self.loading_label = QLabel("正在加载进程信息...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
        
        self.tab_widget.addTab(process_widget, "进程管理")
        
    def create_system_info_tab(self):
        """创建系统信息选项卡"""
        system_widget = QWidget()
        layout = QVBoxLayout(system_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：系统概览
        overview_group = QGroupBox("系统概览")
        overview_layout = QGridLayout(overview_group)
        
        # 系统信息标签
        self.system_labels = {}
        labels = [
            ('操作系统:', platform.system() + ' ' + platform.release()),
            ('处理器:', platform.processor() or platform.machine()),
            ('Python版本:', platform.python_version()),
            ('启动时间:', ''),
            ('运行时间:', '')
        ]
        
        for i, (label, value) in enumerate(labels):
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Arial", 9, QFont.Bold))
            value_widget = QLabel(value)
            overview_layout.addWidget(label_widget, i, 0)
            overview_layout.addWidget(value_widget, i, 1)
            self.system_labels[label] = value_widget
        
        splitter.addWidget(overview_group)
        
        # 右侧：资源使用情况
        resources_group = QGroupBox("资源使用情况")
        resources_layout = QVBoxLayout(resources_group)
        
        # CPU使用率
        cpu_frame = QFrame()
        cpu_layout = QHBoxLayout(cpu_frame)
        cpu_layout.addWidget(QLabel("CPU使用率:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_progress)
        cpu_layout.addWidget(self.cpu_label)
        resources_layout.addWidget(cpu_frame)
        
        # 内存使用率
        memory_frame = QFrame()
        memory_layout = QHBoxLayout(memory_frame)
        memory_layout.addWidget(QLabel("内存使用率:"))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_label = QLabel("0%")
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addWidget(self.memory_label)
        resources_layout.addWidget(memory_frame)
        
        # 磁盘使用率
        disk_frame = QFrame()
        disk_layout = QHBoxLayout(disk_frame)
        disk_layout.addWidget(QLabel("磁盘使用率:"))
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        self.disk_label = QLabel("0%")
        disk_layout.addWidget(self.disk_progress)
        disk_layout.addWidget(self.disk_label)
        resources_layout.addWidget(disk_frame)
        
        # 详细信息文本区域
        self.system_details = QTextEdit()
        self.system_details.setReadOnly(True)
        self.system_details.setMaximumHeight(200)
        resources_layout.addWidget(QLabel("详细信息:"))
        resources_layout.addWidget(self.system_details)
        
        splitter.addWidget(resources_group)
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(system_widget, "系统信息")

    def init_worker_threads(self):
        """初始化后台工作线程"""
        # 系统信息工作线程 - 增加更新间隔，减少系统负担
        self.system_worker = SystemInfoWorker(update_interval=3000)  # 从2秒改为3秒
        self.system_worker.info_updated.connect(self.on_system_info_updated)
        self.system_worker.start()
        
        # 进程信息工作线程
        self.process_worker = ProcessWorker()
        self.process_worker.processes_updated.connect(self.on_processes_updated)
        self.process_worker.loading_started.connect(self.on_process_loading_started)
        self.process_worker.loading_finished.connect(self.on_process_loading_finished)
        self.process_worker.error_occurred.connect(self.on_process_error)
        self.process_worker.start()
    
    def connect_signals(self):
        """连接信号和槽"""
        # 如果模块可用，连接模块化组件的信号
        if MODULES_AVAILABLE:
            # 网络监控信号
            if hasattr(self, 'network_widget'):
                self.network_widget.refresh_btn.clicked.connect(self.refresh_network_info)
            
            # 硬件信息信号
            if hasattr(self, 'hardware_widget'):
                self.hardware_widget.refresh_btn.clicked.connect(self.refresh_hardware_info)
            
            # 系统详情信号
            if hasattr(self, 'details_widget'):
                self.details_widget.refresh_btn.clicked.connect(self.refresh_system_details)
            
            # 初始加载数据
            self.refresh_all_data()
    
    def apply_theme(self, theme_name: str = "light"):
        """应用主题"""
        if MODULES_AVAILABLE:
            if theme_name.lower() == "dark":
                self.setStyleSheet(Themes.get_dark_stylesheet())
            else:
                self.setStyleSheet(AppStyles.get_complete_stylesheet())
    
    def on_system_info_updated(self, info):
        """系统信息更新回调"""
        try:
            # 更新系统信息标签页
            self.update_system_info_display(info)
            
            # 如果模块可用，更新概览页面
            if MODULES_AVAILABLE and hasattr(self, 'overview_widget'):
                self.overview_widget.update_system_info(info)
            
            # 更新状态栏
            if MODULES_AVAILABLE and hasattr(self, 'status_bar') and hasattr(self.status_bar, 'update_system_status'):
                self.status_bar.update_system_status(info)
                self.status_bar.update_status("系统信息已更新")
            
        except Exception as e:
            print(f"更新系统信息显示时出错: {e}")
    
    def update_system_info_display(self, info):
        """更新系统信息显示"""
        # 更新启动时间
        if '启动时间:' in self.system_labels:
            self.system_labels['启动时间:'].setText(info['boot_time'])
        
        # 计算运行时间
        try:
            boot_time = datetime.strptime(info['boot_time'], '%Y-%m-%d %H:%M:%S')
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            uptime_str = f"{days}天 {hours}小时 {minutes}分钟"
            if '运行时间:' in self.system_labels:
                self.system_labels['运行时间:'].setText(uptime_str)
        except Exception as e:
            print(f"计算运行时间出错: {e}")
        
        # 更新进度条
        if hasattr(self, 'cpu_progress'):
            self.cpu_progress.setValue(int(info['cpu_percent']))
            self.cpu_label.setText(f"{info['cpu_percent']:.1f}%")
        
        if hasattr(self, 'memory_progress'):
            self.memory_progress.setValue(int(info['memory_percent']))
            self.memory_label.setText(f"{info['memory_percent']:.1f}%")
        
        if hasattr(self, 'disk_progress'):
            self.disk_progress.setValue(int(info['disk_percent']))
            self.disk_label.setText(f"{info['disk_percent']:.1f}%")
        
        # 更新详细信息
        if hasattr(self, 'system_details'):
            details = f"""CPU核心数: {psutil.cpu_count(logical=False)} 物理核心, {psutil.cpu_count(logical=True)} 逻辑核心
内存: {info['memory_used'] / 1024**3:.2f} GB / {info['memory_total'] / 1024**3:.2f} GB
磁盘: {info['disk_used'] / 1024**3:.2f} GB / {info['disk_total'] / 1024**3:.2f} GB
进程数: {len(psutil.pids())}
"""
            self.system_details.setText(details)
    
    def request_process_update(self):
        """请求更新进程列表（多线程方式）"""
        if hasattr(self, 'process_worker'):
            self.process_worker.request_update()
    
    def on_processes_updated(self, processes):
        """进程信息更新完成的回调"""
        try:
            self.populate_process_table(processes)
            self.status_bar.showMessage(f"已加载 {len(processes)} 个进程")
        except Exception as e:
            self.status_bar.showMessage(f"更新进程表格失败: {str(e)}")
    
    def on_process_loading_started(self):
        """进程加载开始的回调"""
        if hasattr(self, 'loading_label'):
            self.loading_label.show()
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setEnabled(False)
            self.refresh_btn.setText("加载中...")
        self.status_bar.showMessage("正在获取进程信息...")
    
    def on_process_loading_finished(self):
        """进程加载完成的回调"""
        if hasattr(self, 'loading_label'):
            self.loading_label.hide()
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setEnabled(True)
            self.refresh_btn.setText("刷新")
    
    def on_process_error(self, error_message):
        """进程获取错误的回调"""
        self.status_bar.showMessage(error_message)
        QMessageBox.warning(self, "错误", error_message)
    
    def update_process_list(self):
        """更新进程列表（兼容性方法）"""
        self.request_process_update()
            
    def get_processes(self):
        """获取进程列表（已移至ProcessWorker类中）"""
        # 这个方法现在由ProcessWorker处理，保留用于兼容性
        return []
        
    def populate_process_table(self, processes):
        """填充进程表格"""
        try:
            # 获取搜索关键词
            search_text = self.search_input.text().lower() if hasattr(self, 'search_input') else ""
            
            # 过滤进程
            if search_text:
                processes = [p for p in processes if search_text in p['name'].lower()]
            
            # 限制显示的进程数量，避免界面卡顿
            max_display_processes = 200
            if len(processes) > max_display_processes:
                processes = processes[:max_display_processes]
            
            # 暂时禁用排序，避免在更新过程中触发排序导致的性能问题
            self.process_table.setSortingEnabled(False)
            
            self.process_table.setRowCount(len(processes))
            
            # 批量更新，减少界面重绘次数
            for row, proc in enumerate(processes):
                # 创建表格项时避免不必要的格式化
                pid_item = QTableWidgetItem(str(proc['pid']))
                name_item = QTableWidgetItem(proc['name'])
                cpu_item = QTableWidgetItem(f"{proc['cpu_percent']:.1f}")
                memory_item = QTableWidgetItem(f"{proc['memory_percent']:.1f}")
                disk_item = QTableWidgetItem(f"{proc['disk_read']:.2f}")
                status_item = QTableWidgetItem(proc['status'])
                
                # 设置数值类型的项目用于正确排序
                pid_item.setData(Qt.UserRole, proc['pid'])
                cpu_item.setData(Qt.UserRole, proc['cpu_percent'])
                memory_item.setData(Qt.UserRole, proc['memory_percent'])
                disk_item.setData(Qt.UserRole, proc['disk_read'])
                
                self.process_table.setItem(row, 0, pid_item)
                self.process_table.setItem(row, 1, name_item)
                self.process_table.setItem(row, 2, cpu_item)
                self.process_table.setItem(row, 3, memory_item)
                self.process_table.setItem(row, 4, disk_item)
                self.process_table.setItem(row, 5, status_item)
            
            # 重新启用排序
            self.process_table.setSortingEnabled(True)
            
        except Exception as e:
            print(f"更新进程表格时出错: {e}")
            self.status_bar.showMessage(f"更新进程表格失败: {str(e)}")
            
    def filter_processes(self):
        """过滤进程列表"""
        # 过滤是在populate_process_table中处理的，所以请求新的进程数据
        self.request_process_update()
        
    def kill_selected_process(self):
        """结束选中的进程"""
        current_row = self.process_table.currentRow()
        if current_row >= 0:
            pid_item = self.process_table.item(current_row, 0)
            name_item = self.process_table.item(current_row, 1)
            
            if pid_item and name_item:
                pid = int(pid_item.text())
                name = name_item.text()
                
                reply = QMessageBox.question(
                    self, '确认操作', 
                    f'确定要结束进程 "{name}" (PID: {pid}) 吗？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        QMessageBox.information(self, '成功', f'进程 "{name}" 已被结束')
                        self.request_process_update()  # 使用多线程更新
                    except psutil.NoSuchProcess:
                        QMessageBox.warning(self, '错误', '进程不存在')
                    except psutil.AccessDenied:
                        QMessageBox.warning(self, '错误', '权限不足，无法结束此进程')
                    except Exception as e:
                        QMessageBox.critical(self, '错误', f'结束进程失败: {str(e)}')
        else:
            QMessageBox.information(self, '提示', '请先选择一个进程')
            
    def show_process_details(self):
        """显示进程详情"""
        current_row = self.process_table.currentRow()
        if current_row >= 0:
            pid_item = self.process_table.item(current_row, 0)
            if pid_item:
                pid = int(pid_item.text())
                try:
                    proc = psutil.Process(pid)
                    details = f"""进程详细信息:
                    
PID: {proc.pid}
进程名称: {proc.name()}
状态: {proc.status()}
创建时间: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}
CPU使用率: {proc.cpu_percent()}%
内存使用率: {proc.memory_percent():.2f}%
内存使用量: {proc.memory_info().rss / 1024 / 1024:.2f} MB
线程数: {proc.num_threads()}
"""
                    try:
                        if proc.parent():
                            details += f"父进程: {proc.parent().name()} (PID: {proc.parent().pid})\n"
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    
                    QMessageBox.information(self, '进程详情', details)
                except psutil.NoSuchProcess:
                    QMessageBox.warning(self, '错误', '进程不存在')
                except Exception as e:
                    QMessageBox.critical(self, '错误', f'获取进程详情失败: {str(e)}')
        else:
            QMessageBox.information(self, '提示', '请先选择一个进程')
    
    def show_process_context_menu(self, position):
        """显示进程右键菜单"""
        # 检查是否点击在有效行上
        item = self.process_table.itemAt(position)
        if item is None:
            return
        
        # 获取选中的进程信息
        current_row = self.process_table.currentRow()
        if current_row < 0:
            return
            
        pid_item = self.process_table.item(current_row, 0)
        name_item = self.process_table.item(current_row, 1)
        
        if not pid_item or not name_item:
            return
            
        pid = int(pid_item.text())
        name = name_item.text()
        
        # 创建右键菜单
        context_menu = QMenu(self)
        
        # 刷新进程列表
        refresh_action = QAction("🔄 刷新进程列表", self)
        refresh_action.triggered.connect(self.update_process_list)
        context_menu.addAction(refresh_action)
        
        context_menu.addSeparator()
        
        # 查看进程详情
        details_action = QAction("📋 查看进程详情", self)
        details_action.triggered.connect(self.show_process_details)
        context_menu.addAction(details_action)
        
        # 打开进程文件位置（如果可能）
        location_action = QAction("📁 打开文件位置", self)
        location_action.triggered.connect(lambda: self.open_process_location(pid))
        context_menu.addAction(location_action)
        
        context_menu.addSeparator()
        
        # 结束进程
        kill_action = QAction(f"❌ 结束进程 {name}", self)
        kill_action.triggered.connect(self.kill_selected_process)
        kill_action.setStyleSheet("QAction { color: red; font-weight: bold; }")
        context_menu.addAction(kill_action)
        
        # 强制结束进程
        force_kill_action = QAction(f"⚠️ 强制结束进程 {name}", self)
        force_kill_action.triggered.connect(lambda: self.force_kill_selected_process(pid, name))
        force_kill_action.setStyleSheet("QAction { color: darkred; font-weight: bold; }")
        context_menu.addAction(force_kill_action)
        
        # 显示菜单
        context_menu.exec(self.process_table.mapToGlobal(position))
    
    def open_process_location(self, pid):
        """打开进程文件位置"""
        try:
            import os
            import subprocess
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            
            if os.path.exists(exe_path):
                # Windows系统
                if platform.system() == "Windows":
                    subprocess.run(['explorer', '/select,', exe_path])
                # macOS系统
                elif platform.system() == "Darwin":
                    subprocess.run(['open', '-R', exe_path])
                # Linux系统
                else:
                    directory = os.path.dirname(exe_path)
                    subprocess.run(['xdg-open', directory])
                    
                self.status_bar.showMessage(f"已打开进程文件位置: {exe_path}")
            else:
                QMessageBox.warning(self, '警告', '无法找到进程文件位置')
                
        except psutil.NoSuchProcess:
            QMessageBox.warning(self, '错误', '进程不存在')
        except psutil.AccessDenied:
            QMessageBox.warning(self, '错误', '权限不足，无法访问进程信息')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开文件位置失败: {str(e)}')
    
    def force_kill_selected_process(self, pid, name):
        """强制结束选中的进程"""
        reply = QMessageBox.question(
            self, '确认强制结束', 
            f'确定要强制结束进程 "{name}" (PID: {pid}) 吗？\n\n'
            f'⚠️ 警告：强制结束可能导致数据丢失！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                proc = psutil.Process(pid)
                proc.kill()  # 使用kill()而不是terminate()来强制结束
                QMessageBox.information(self, '成功', f'进程 "{name}" 已被强制结束')
                self.request_process_update()
            except psutil.NoSuchProcess:
                QMessageBox.warning(self, '错误', '进程不存在')
            except psutil.AccessDenied:
                QMessageBox.warning(self, '错误', '权限不足，无法结束此进程')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'强制结束进程失败: {str(e)}')
    
    def toggle_auto_refresh(self, checked):
        """切换自动刷新"""
        if checked:
            self.timer.start(5000)  # 使用与初始化相同的间隔
            self.status_bar.showMessage("自动刷新已启用 (每5秒)")
        else:
            self.timer.stop()
            self.status_bar.showMessage("自动刷新已禁用")
            
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, '关于', 
            '系统监控与进程管理工具 v2.0\n\n'
            '基于PySide6开发的系统监控和进程管理工具\n\n'
            '功能特性:\n'
            '• 实时系统监控\n'
            '• 进程管理和监控\n'
            '• 进程搜索和过滤\n'
            '• 进程终止操作\n'
            '• 系统资源监控\n'
            '• 现代化用户界面'
        )

    def refresh_processes(self):
        """刷新进程列表（兼容性方法）"""
        self.request_process_update()
    
    def kill_process(self, pid: int):
        """结束进程（兼容性方法）"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            self.request_process_update()  # 使用多线程更新
            return True, f"进程 {pid} 已结束"
        except Exception as e:
            return False, f"结束进程失败: {str(e)}"
    
    def refresh_network_info(self):
        """刷新网络信息"""
        if MODULES_AVAILABLE and hasattr(self, 'network_monitor'):
            try:
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("正在刷新网络信息...")
                else:
                    self.status_bar.showMessage("正在刷新网络信息...")
                connections = self.network_monitor.get_connections()
                self.network_widget.update_connections(connections)
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status(f"已加载 {len(connections)} 个网络连接")
                else:
                    self.status_bar.showMessage(f"已加载 {len(connections)} 个网络连接")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"刷新网络信息时出错: {e}")
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("刷新网络信息失败")
                else:
                    self.status_bar.showMessage("刷新网络信息失败")
    
    def refresh_hardware_info(self):
        """刷新硬件信息"""
        if MODULES_AVAILABLE and hasattr(self, 'system_monitor'):
            try:
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("正在获取硬件信息...")
                else:
                    self.status_bar.showMessage("正在获取硬件信息...")
                hardware_info = self.system_monitor.get_hardware_info()
                self.hardware_widget.update_hardware_info(hardware_info)
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("硬件信息已更新")
                else:
                    self.status_bar.showMessage("硬件信息已更新")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"获取硬件信息时出错: {e}")
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("获取硬件信息失败")
                else:
                    self.status_bar.showMessage("获取硬件信息失败")
    
    def refresh_system_details(self):
        """刷新系统详情"""
        if MODULES_AVAILABLE and hasattr(self, 'system_monitor'):
            try:
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("正在获取系统详情...")
                else:
                    self.status_bar.showMessage("正在获取系统详情...")
                details = self.system_monitor.get_system_details()
                self.details_widget.update_system_details(details)
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("系统详情已更新")
                else:
                    self.status_bar.showMessage("系统详情已更新")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"获取系统详情时出错: {e}")
                if hasattr(self.status_bar, 'update_status'):
                    self.status_bar.update_status("获取系统详情失败")
                else:
                    self.status_bar.showMessage("获取系统详情失败")
    
    def refresh_all_data(self):
        """刷新所有数据"""
        try:
            if hasattr(self.status_bar, 'update_status'):
                self.status_bar.update_status("正在初始化数据...")
            else:
                self.status_bar.showMessage("正在初始化数据...")
            
            # 刷新进程列表
            self.refresh_processes()
            
            # 如果模块可用，刷新其他信息
            if MODULES_AVAILABLE:
                # 刷新网络信息
                self.refresh_network_info()
                
                # 刷新硬件信息
                self.refresh_hardware_info()
                
                # 刷新系统详情
                self.refresh_system_details()
            
            if hasattr(self.status_bar, 'update_status'):
                self.status_bar.update_status("初始化完成")
            else:
                self.status_bar.showMessage("初始化完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化数据时出错: {e}")
    
    def switch_theme(self, theme_name: str):
        """切换主题"""
        try:
            self.apply_theme(theme_name)
            if hasattr(self.status_bar, 'update_status'):
                self.status_bar.update_status(f"已切换到 {theme_name} 主题")
            else:
                self.status_bar.showMessage(f"已切换到 {theme_name} 主题")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换主题时出错: {e}")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        try:
            # 停止所有后台线程
            if hasattr(self, 'system_worker'):
                self.system_worker.stop()
            
            if hasattr(self, 'process_worker'):
                self.process_worker.stop()
            
            # 兼容旧版本
            if hasattr(self, 'worker'):
                self.worker.stop()
            
            # 停止定时器
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            # 保存设置等清理工作
            if hasattr(self.status_bar, 'update_status'):
                self.status_bar.update_status("正在关闭应用程序...")
            else:
                self.status_bar.showMessage("正在关闭应用程序...")
            
            event.accept()
        except Exception as e:
            print(f"关闭应用程序时出错: {e}")
            event.accept()


class SystemInfoApplication(QApplication):
    """系统信息应用程序类"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setup_application()
    
    def setup_application(self):
        """设置应用程序属性"""
        self.setApplicationName("系统信息监控工具")
        self.setApplicationVersion("2.0")
        self.setOrganizationName("System Monitor")
        self.setOrganizationDomain("systemmonitor.local")
        
        # 设置应用程序图标（如果有的话）
        # self.setWindowIcon(QIcon("icon.png"))
    
    def create_main_window(self) -> SystemInfoMainWindow:
        """创建主窗口"""
        return SystemInfoMainWindow()


def signal_handler(signum, frame):
    """信号处理函数，用于处理Ctrl+C等中断信号"""
    print("\n接收到中断信号，正在安全退出...")
    QApplication.quit()

def main():
    """主函数"""
    try:
        # 设置信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 创建应用程序
        app = SystemInfoApplication(sys.argv)
        
        # 设置定时器来处理信号（Qt在Windows上需要这样处理信号）
        timer = QTimer()
        timer.start(500)  # 每500ms检查一次信号
        timer.timeout.connect(lambda: None)  # 空操作，只是为了让事件循环运行
        
        # 创建并显示主窗口
        main_window = app.create_main_window()
        main_window.show()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"启动应用程序时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
