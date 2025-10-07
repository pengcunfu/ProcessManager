#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent主窗口
使用PySide6-Fluent-Widgets创建现代化主窗口
"""

import sys
import platform
from typing import Optional
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon

from qfluentwidgets import (
    FluentIcon as FIF,
    NavigationInterface,
    NavigationItemPosition,
    MessageBox,
    SplashScreen,
    Theme,
    setTheme,
    setThemeColor,
    qconfig,
    isDarkTheme,
    MSFluentWindow,
    SubtitleLabel,
    setFont
)

from business_logic import (
    SystemMonitorService, 
    ProcessManagerService, 
    NetworkMonitorService, 
    HardwareInfoService
)
from fluent_ui_components import (
    SystemOverviewCard,
    ProcessTableCard,
    NetworkTableCard,
    HardwareInfoCard,
    SystemStatsCard,
    show_success_message,
    show_error_message,
    show_warning_message,
    show_info_message
)


class SystemOverviewInterface(QWidget):
    """系统概览界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SystemOverview")
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 系统概览卡片
        self.overview_card = SystemOverviewCard()
        layout.addWidget(self.overview_card)
        
        # 系统统计卡片
        self.stats_card = SystemStatsCard()
        layout.addWidget(self.stats_card)
        
        layout.addStretch()
    
    def update_system_info(self, system_info):
        """更新系统信息"""
        self.overview_card.update_system_info(system_info)
        self.stats_card.update_system_info(system_info)


class ProcessInterface(QWidget):
    """进程管理界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProcessManager")
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
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
        self.setObjectName("NetworkMonitor")
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 网络连接表格卡片
        self.network_card = NetworkTableCard()
        layout.addWidget(self.network_card)
    
    def update_connections(self, connections):
        """更新网络连接"""
        self.network_card.update_connections(connections)


class HardwareInterface(QWidget):
    """硬件信息界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HardwareInfo")
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 硬件信息卡片
        self.hardware_card = HardwareInfoCard()
        layout.addWidget(self.hardware_card)
    
    def update_hardware_info(self, hardware_info):
        """更新硬件信息"""
        self.hardware_card.update_hardware_info(hardware_info)


class FluentMainWindow(MSFluentWindow):
    """Fluent设计风格的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_services()
        self.init_ui()
        self.init_navigation()
        self.connect_signals()
        self.start_monitoring()
        
        # 设置窗口属性
        self.setWindowTitle("系统监控与进程管理工具")
        self.setWindowIcon(QIcon(":/images/logo.png"))  # 如果有图标的话
        self.resize(1200, 800)
        
        # 居中显示
        self.move_to_center()
    
    def init_services(self):
        """初始化业务服务"""
        self.system_monitor = SystemMonitorService()
        self.process_manager = ProcessManagerService()
        self.network_monitor = NetworkMonitorService()
        self.hardware_service = HardwareInfoService()
    
    def init_ui(self):
        """初始化界面"""
        # 创建各个界面
        self.overview_interface = SystemOverviewInterface()
        self.process_interface = ProcessInterface()
        self.network_interface = NetworkInterface()
        self.hardware_interface = HardwareInterface()
        
        # 添加界面到堆栈
        self.addSubInterface(self.overview_interface, FIF.HOME, "系统概览")
        self.addSubInterface(self.process_interface, FIF.APPLICATION, "进程管理")
        self.addSubInterface(self.network_interface, FIF.GLOBE, "网络监控")
        self.addSubInterface(self.hardware_interface, FIF.INFO, "硬件信息")
        
        # 设置默认界面
        self.stackedWidget.setCurrentWidget(self.overview_interface)
        self.navigationInterface.setCurrentItem(self.overview_interface.objectName())
    
    def init_navigation(self):
        """初始化导航栏"""
        # 添加设置页面
        self.navigationInterface.addItem(
            routeKey="Settings",
            icon=FIF.HOME,
            text="设置",
            onClick=self.show_settings,
            position=NavigationItemPosition.BOTTOM
        )
        
        # 添加关于页面
        self.navigationInterface.addItem(
            routeKey="About",
            icon=FIF.HOME,
            text="关于",
            onClick=self.show_about,
            position=NavigationItemPosition.BOTTOM
        )
    
    def connect_signals(self):
        """连接信号和槽"""
        # 系统监控信号
        self.system_monitor.system_info_updated.connect(self.on_system_info_updated)
        self.system_monitor.error_occurred.connect(self.on_system_monitor_error)
        
        # 进程管理信号
        self.process_manager.processes_updated.connect(self.on_processes_updated)
        self.process_manager.process_killed.connect(self.on_process_killed)
        self.process_manager.error_occurred.connect(self.on_process_manager_error)
        
        # 网络监控信号
        self.network_monitor.connections_updated.connect(self.on_connections_updated)
        self.network_monitor.error_occurred.connect(self.on_network_monitor_error)
        
        # 硬件信息信号
        self.hardware_service.hardware_info_updated.connect(self.on_hardware_info_updated)
        self.hardware_service.error_occurred.connect(self.on_hardware_service_error)
        
        # 界面组件信号
        self.process_interface.process_card.refresh_requested.connect(self.refresh_processes)
        self.process_interface.process_card.kill_requested.connect(self.kill_process)
        
        self.network_interface.network_card.refresh_requested.connect(self.refresh_network)
        
        self.hardware_interface.hardware_card.refresh_requested.connect(self.refresh_hardware)
    
    def start_monitoring(self):
        """开始监控"""
        # 启动系统监控
        self.system_monitor.start_monitoring()
        
        # 定时刷新其他信息
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        self.refresh_timer.start(5000)  # 每5秒刷新一次
        
        # 初始加载数据
        self.refresh_all_data()
    
    def refresh_all_data(self):
        """刷新所有数据"""
        self.refresh_processes()
        self.refresh_network()
        self.refresh_hardware()
    
    def refresh_processes(self):
        """刷新进程列表"""
        self.process_manager.get_processes(force_refresh=True)
    
    def refresh_network(self):
        """刷新网络连接"""
        self.network_monitor.get_connections(force_refresh=True)
    
    def refresh_hardware(self):
        """刷新硬件信息"""
        self.hardware_service.get_hardware_info()
    
    def kill_process(self, pid: int, force: bool):
        """结束进程"""
        self.process_manager.kill_process(pid, force)
    
    def on_system_info_updated(self, system_info):
        """系统信息更新"""
        self.overview_interface.update_system_info(system_info)
    
    def on_processes_updated(self, processes):
        """进程列表更新"""
        self.process_interface.update_processes(processes)
    
    def on_connections_updated(self, connections):
        """网络连接更新"""
        self.network_interface.update_connections(connections)
    
    def on_hardware_info_updated(self, hardware_info):
        """硬件信息更新"""
        self.hardware_interface.update_hardware_info(hardware_info)
    
    def on_process_killed(self, pid: int, message: str):
        """进程结束成功"""
        show_success_message(self, message)
        # 刷新进程列表
        QTimer.singleShot(1000, self.refresh_processes)
    
    def on_system_monitor_error(self, error_message: str):
        """系统监控错误"""
        show_error_message(self, f"系统监控错误: {error_message}")
    
    def on_process_manager_error(self, error_message: str):
        """进程管理错误"""
        show_error_message(self, f"进程管理错误: {error_message}")
    
    def on_network_monitor_error(self, error_message: str):
        """网络监控错误"""
        show_error_message(self, f"网络监控错误: {error_message}")
    
    def on_hardware_service_error(self, error_message: str):
        """硬件信息错误"""
        show_error_message(self, f"硬件信息错误: {error_message}")
    
    def show_settings(self):
        """显示设置对话框"""
        w = MessageBox(
            "设置",
            "设置功能正在开发中...\n\n可配置项目:\n• 刷新间隔\n• 主题设置\n• 显示选项",
            self
        )
        w.exec()
    
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""系统监控与进程管理工具 v3.0

基于PySide6和Fluent-Widgets开发的现代化系统监控工具

功能特性:
• 实时系统资源监控
• 进程管理和监控
• 网络连接监控
• 硬件信息查看
• 现代化Fluent设计界面

系统信息:
• 操作系统: {platform.system()} {platform.release()}
• Python版本: {platform.python_version()}
• 架构: {platform.architecture()[0]}

开发框架:
• PySide6
• PySide6-Fluent-Widgets
• psutil"""
        
        w = MessageBox("关于", about_text, self)
        w.exec()
    
    def move_to_center(self):
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
            self.system_monitor.stop_monitoring()
            
            # 停止定时器
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()
            
            event.accept()
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
            event.accept()


class FluentApplication(QApplication):
    """Fluent应用程序"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setup_application()
    
    def setup_application(self):
        """设置应用程序"""
        # 设置应用程序信息
        self.setApplicationName("系统监控工具")
        self.setApplicationVersion("3.0")
        self.setOrganizationName("System Monitor")
        self.setOrganizationDomain("systemmonitor.local")
        
        # 设置主题
        setTheme(Theme.AUTO)  # 自动主题
        setThemeColor('#0078d4')  # 设置主题色
        
        # 设置字体
        # setFont(self.font())  # 暂时注释掉，可能有兼容性问题
        
        # 国际化支持
        # translator = FluentTranslator()  # 暂时注释掉，可能有兼容性问题
        # self.installTranslator(translator)


def create_splash_screen():
    """创建启动画面"""
    try:
        splash = SplashScreen("系统监控工具", parent=None)
        splash.raise_()
        return splash
    except:
        # 如果SplashScreen有问题，返回None
        return None


def main():
    """主函数"""
    try:
        # 创建应用程序
        app = FluentApplication(sys.argv)
        
        # 创建启动画面
        splash = create_splash_screen()
        if splash:
            splash.show()
            # 处理启动事件
            app.processEvents()
        
        # 创建主窗口
        window = FluentMainWindow()
        
        # 模拟加载过程
        import time
        time.sleep(0.5)
        
        # 显示主窗口并关闭启动画面
        window.show()
        if splash:
            splash.close()
        
        # 运行应用程序
        return app.exec()
        
    except Exception as e:
        print(f"启动应用程序时出错: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
