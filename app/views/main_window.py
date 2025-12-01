#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
使用原生PySide6创建现代化主窗口
"""

import sys
import platform
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from app.controllers import (
    SystemMonitorController,
    ProcessController,
    NetworkController,
    HardwareController,
    TrafficMonitorController
)
from app.views.ui_components import (
    SystemOverviewCard,
    ProcessTableCard,
    NetworkTableCard,
    HardwareInfoCard,
    SystemStatsCard,
    TrafficMonitorCard,
    ProcessTrafficCard
)
from app.views.ui_utils import (
    show_success_message,
    show_error_message
)
from app.views.styles import get_app_stylesheet


class SystemInfoInterface(QWidget):
    """系统信息界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 系统概览卡片
        self.overview_card = SystemOverviewCard()
        layout.addWidget(self.overview_card)
        
        # 系统统计卡片
        self.stats_card = SystemStatsCard()
        layout.addWidget(self.stats_card)
        
        # 硬件信息卡片
        self.hardware_card = HardwareInfoCard()
        layout.addWidget(self.hardware_card)
        
        layout.addStretch()
    
    def update_system_info(self, system_info):
        """更新系统信息"""
        self.overview_card.update_system_info(system_info)
        self.stats_card.update_system_info(system_info)
    
    def update_hardware_info(self, hardware_info):
        """更新硬件信息"""
        self.hardware_card.update_hardware_info(hardware_info)


class ProcessInterface(QWidget):
    """进程管理界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 进程表格卡片
        self.process_card = ProcessTableCard()
        layout.addWidget(self.process_card)
    
    def update_processes(self, processes):
        """更新进程列表"""
        self.process_card.update_processes(processes)


class NetworkInterface(QWidget):
    """网络监控界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 网络连接表格卡片
        self.network_card = NetworkTableCard()
        layout.addWidget(self.network_card)
    
    def update_connections(self, connections):
        """更新网络连接"""
        self.network_card.update_connections(connections)


class TrafficInterface(QWidget):
    """流量监控界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 实时流量监控卡片
        self.traffic_card = TrafficMonitorCard()
        layout.addWidget(self.traffic_card)
        
        # 进程流量统计卡片
        self.process_traffic_card = ProcessTrafficCard()
        layout.addWidget(self.process_traffic_card)
    
    def update_traffic(self, traffic_data):
        """更新流量信息"""
        self.traffic_card.update_traffic(traffic_data)
    
    def update_process_traffic(self, traffic_list):
        """更新进程流量列表"""
        self.process_traffic_card.update_process_traffic(traffic_list)


class MainWindow(QMainWindow):
    """系统监控主窗口（MVC架构）"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("系统监控与进程管理工具")
        self.resize(1200, 800)
        
        # 初始化控制器
        self.init_controllers()
        
        # 延迟初始化UI（减少启动阻塞）
        QTimer.singleShot(0, self._delayed_init)
        
        # 居中显示
        self.center_window()
    
    def _delayed_init(self):
        """延迟初始化UI和信号连接"""
        self.init_ui()
        self.init_menu()
        self.connect_signals()
        
        # 再延迟启动监控
        QTimer.singleShot(100, self.start_monitoring)
    
    def init_controllers(self):
        """初始化控制器"""
        self.system_controller = SystemMonitorController()
        self.process_controller = ProcessController()
        self.network_controller = NetworkController()
        self.hardware_controller = HardwareController()
        self.traffic_controller = TrafficMonitorController()
    
    def init_ui(self):
        """初始化界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 创建各个界面
        self.system_interface = SystemInfoInterface()
        self.process_interface = ProcessInterface()
        self.network_interface = NetworkInterface()
        self.traffic_interface = TrafficInterface()
        
        # 添加标签页
        self.tab_widget.addTab(self.system_interface, "系统信息")
        self.tab_widget.addTab(self.process_interface, "进程管理")
        self.tab_widget.addTab(self.network_interface, "网络监控")
        self.tab_widget.addTab(self.traffic_interface, "流量监控")
        
        layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        refresh_action = QAction("刷新当前页面", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current_tab)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 系统监控信号
        self.system_controller.system_info_updated.connect(self.on_system_info_updated)
        self.system_controller.error_occurred.connect(self.on_error)
        
        # 进程管理信号
        self.process_controller.processes_updated.connect(self.on_processes_updated)
        self.process_controller.process_killed.connect(self.on_process_killed)
        self.process_controller.error_occurred.connect(self.on_error)
        
        # 网络监控信号
        self.network_controller.connections_updated.connect(self.on_connections_updated)
        self.network_controller.error_occurred.connect(self.on_error)
        
        # 硬件信息信号
        self.hardware_controller.hardware_info_updated.connect(self.on_hardware_info_updated)
        self.hardware_controller.error_occurred.connect(self.on_error)
        
        # 流量监控信号
        self.traffic_controller.traffic_updated.connect(self.on_traffic_updated)
        self.traffic_controller.process_traffic_updated.connect(self.on_process_traffic_updated)
        self.traffic_controller.error_occurred.connect(self.on_error)
        
        # 界面组件信号
        self.process_interface.process_card.refresh_requested.connect(self.refresh_processes)
        self.process_interface.process_card.kill_requested.connect(self.kill_process)
        
        self.network_interface.network_card.refresh_requested.connect(self.refresh_network)
        
        self.system_interface.hardware_card.refresh_requested.connect(self.refresh_hardware)
        
        self.traffic_interface.process_traffic_card.refresh_requested.connect(self.refresh_process_traffic)
    
    def start_monitoring(self):
        """开始监控"""
        # 启动系统监控（自动刷新）
        self.system_controller.start_monitoring()
        
        # 启动流量监控（自动刷新）
        self.traffic_controller.start_monitoring(interval=1000)  # 每1秒更新一次流量
        
        # 定时刷新硬件信息（仅硬件信息自动刷新）
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_hardware)
        self.refresh_timer.start(10000)  # 每10秒刷新一次硬件信息
        
        # 初始加载数据（仅加载一次）
        QTimer.singleShot(200, self.refresh_hardware)
        QTimer.singleShot(500, self.refresh_processes_once)
        QTimer.singleShot(1000, self.refresh_network_once)
    
    def refresh_processes_once(self):
        """初始加载进程列表（仅一次）"""
        self.process_controller.get_processes(force_refresh=True)
    
    def refresh_network_once(self):
        """初始加载网络连接（仅一次）"""
        self.network_controller.get_connections(force_refresh=True)
    
    def refresh_current_tab(self):
        """刷新当前标签页"""
        current_index = self.tab_widget.currentIndex()
        
        if current_index == 0:  # 系统信息
            self.refresh_hardware()
        elif current_index == 1:  # 进程管理
            self.refresh_processes()
        elif current_index == 2:  # 网络监控
            self.refresh_network()
    
    def refresh_processes(self):
        """刷新进程列表"""
        self.process_controller.get_processes(force_refresh=True)
        self.status_bar.showMessage("进程列表已刷新", 2000)
    
    def refresh_network(self):
        """刷新网络连接"""
        self.network_controller.get_connections(force_refresh=True)
        self.status_bar.showMessage("网络连接已刷新", 2000)
    
    def refresh_hardware(self):
        """刷新硬件信息"""
        self.hardware_controller.get_hardware_info()
        self.status_bar.showMessage("硬件信息已刷新", 2000)
    
    def kill_process(self, pid: int, force: bool):
        """结束进程"""
        self.process_controller.kill_process(pid, force)
    
    def on_system_info_updated(self, system_info):
        """系统信息更新"""
        self.system_interface.update_system_info(system_info)
    
    def on_processes_updated(self, processes):
        """进程列表更新"""
        self.process_interface.update_processes(processes)
    
    def on_connections_updated(self, connections):
        """网络连接更新"""
        self.network_interface.update_connections(connections)
    
    def on_hardware_info_updated(self, hardware_info):
        """硬件信息更新"""
        self.system_interface.update_hardware_info(hardware_info)
    
    def on_traffic_updated(self, traffic_data):
        """流量信息更新"""
        self.traffic_interface.update_traffic(traffic_data)
    
    def on_process_traffic_updated(self, traffic_list):
        """进程流量更新"""
        self.traffic_interface.update_process_traffic(traffic_list)
    
    def refresh_process_traffic(self):
        """刷新进程流量"""
        self.traffic_controller.get_process_traffic()
    
    def on_process_killed(self, pid: int, message: str):
        """进程结束成功"""
        show_success_message(self, message)
        # 刷新进程列表
        QTimer.singleShot(1000, self.refresh_processes)
    
    def on_error(self, error_message: str):
        """错误处理"""
        show_error_message(self, error_message)
    
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""系统监控与进程管理工具 v3.1

基于PySide6开发的现代化系统监控工具

功能特性:
• 实时系统资源监控
• 进程管理和监控
• 网络连接监控
• 网络流量监控（实时速度+进程流量）
• 硬件信息查看
• MVC架构设计

系统信息:
• 操作系统: {platform.system()} {platform.release()}
• Python版本: {platform.python_version()}
• 架构: {platform.architecture()[0]}

开发框架:
• PySide6
• psutil"""
        
        QMessageBox.about(self, "关于", about_text)
    
    def center_window(self):
        """将窗口移动到屏幕中央"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            # 停止监控服务
            self.system_controller.stop_monitoring()
            self.traffic_controller.stop_monitoring()
            
            # 停止定时器
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()
            
            event.accept()
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
            event.accept()


def main():
    """主函数"""
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("系统监控工具")
        app.setApplicationVersion("3.0")
        app.setOrganizationName("System Monitor")
        
        # 应用样式表
        app.setStyleSheet(get_app_stylesheet())
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用程序
        return app.exec()
        
    except Exception as e:
        print(f"启动应用程序时出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
