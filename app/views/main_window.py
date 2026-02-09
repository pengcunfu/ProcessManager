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
    HardwareInfoDialog,
    SystemStatsCard,
    SystemInfoCard,
    TrafficMonitorCard,
    ProcessTrafficCard,
    TemperatureMonitorCard,
    BatteryMonitorCard,
    ServicesMonitorCard
)
from app.views.ui_utils import (
    show_success_message,
    show_error_message
)


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

        # 系统信息卡片（详细的静态信息）
        self.system_info_card = SystemInfoCard()
        layout.addWidget(self.system_info_card)

        # 系统统计卡片
        self.stats_card = SystemStatsCard()
        layout.addWidget(self.stats_card)

        layout.addStretch()

    def update_system_info(self, system_info):
        """更新系统信息"""
        self.system_info_card.update_system_info(system_info)
        self.stats_card.update_system_info(system_info)


class SystemMonitorInterface(QWidget):
    """系统监控界面（实时监控）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 系统概览卡片（实时监控）
        self.overview_card = SystemOverviewCard()
        layout.addWidget(self.overview_card)

        # 温度监控卡片
        self.temperature_card = TemperatureMonitorCard()
        layout.addWidget(self.temperature_card)

        # 电池监控卡片
        self.battery_card = BatteryMonitorCard()
        layout.addWidget(self.battery_card)

        layout.addStretch()

    def update_system_info(self, system_info):
        """更新系统监控信息"""
        self.overview_card.update_system_info(system_info)

    def update_temperature(self, temp_info):
        """更新温度信息"""
        self.temperature_card.update_temperature(temp_info)

    def update_battery(self, battery_info):
        """更新电池信息"""
        self.battery_card.update_battery(battery_info)


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


class ServicesInterface(QWidget):
    """系统服务管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 系统服务监控卡片
        self.services_card = ServicesMonitorCard()
        layout.addWidget(self.services_card)

    def update_services(self, services):
        """更新服务列表"""
        self.services_card.update_services(services)


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
        self.system_info_interface = SystemInfoInterface()
        self.system_monitor_interface = SystemMonitorInterface()
        self.process_interface = ProcessInterface()
        self.network_interface = NetworkInterface()
        self.traffic_interface = TrafficInterface()
        self.services_interface = ServicesInterface()

        # 添加标签页
        self.tab_widget.addTab(self.system_info_interface, "系统信息")
        self.tab_widget.addTab(self.system_monitor_interface, "系统监控")
        self.tab_widget.addTab(self.process_interface, "进程管理")
        self.tab_widget.addTab(self.network_interface, "网络监控")
        self.tab_widget.addTab(self.traffic_interface, "流量监控")
        self.tab_widget.addTab(self.services_interface, "系统服务")
        
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

        # 工具菜单
        tools_menu = menubar.addMenu("工具")

        hardware_action = QAction("硬件信息", self)
        hardware_action.setShortcut("Ctrl+H")
        hardware_action.triggered.connect(self.show_hardware_detail)
        tools_menu.addAction(hardware_action)

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

        # 流量监控信号
        self.traffic_controller.traffic_updated.connect(self.on_traffic_updated)
        self.traffic_controller.process_traffic_updated.connect(self.on_process_traffic_updated)
        self.traffic_controller.error_occurred.connect(self.on_error)

        # 界面组件信号
        self.process_interface.process_card.refresh_requested.connect(self.refresh_processes)
        self.process_interface.process_card.kill_requested.connect(self.kill_process)

        self.network_interface.network_card.refresh_requested.connect(self.refresh_network)

        self.traffic_interface.process_traffic_card.refresh_requested.connect(self.refresh_process_traffic)

        self.system_monitor_interface.temperature_card.refresh_requested.connect(self.refresh_temperature)
        self.system_monitor_interface.battery_card.refresh_requested.connect(self.refresh_battery)
        self.services_interface.services_card.refresh_requested.connect(self.refresh_services)
    
    def start_monitoring(self):
        """开始监控"""
        # 启动系统监控（自动刷新）
        self.system_controller.start_monitoring()

        # 启动流量监控（自动刷新）
        self.traffic_controller.start_monitoring(interval=1000)  # 每1秒更新一次流量

        # 初始加载数据（仅加载一次）
        QTimer.singleShot(500, self.refresh_processes_once)
        QTimer.singleShot(1000, self.refresh_network_once)

        # 初始加载高级监控数据
        QTimer.singleShot(1500, self.refresh_temperature)
        QTimer.singleShot(1500, self.refresh_battery)
        QTimer.singleShot(2000, self.refresh_services)
    
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

    def show_hardware_detail(self):
        """显示硬件信息详情对话框"""
        # 创建对话框
        dialog = HardwareInfoDialog(self)

        # 连接刷新信号
        dialog.refresh_requested = lambda: self._refresh_hardware_dialog(dialog)

        # 获取并显示硬件信息
        hardware_info = self.hardware_controller.get_hardware_info_sync()
        dialog.update_hardware_info(hardware_info)

        # 显示对话框
        dialog.exec()

    def _refresh_hardware_dialog(self, dialog):
        """刷新硬件信息对话框"""
        hardware_info = self.hardware_controller.get_hardware_info_sync()
        dialog.update_hardware_info(hardware_info)
    
    def kill_process(self, pid: int, force: bool):
        """结束进程"""
        self.process_controller.kill_process(pid, force)
    
    def on_system_info_updated(self, system_info):
        """系统信息更新"""
        self.system_info_interface.update_system_info(system_info)
        self.system_monitor_interface.update_system_info(system_info)
    
    def on_processes_updated(self, processes):
        """进程列表更新"""
        self.process_interface.update_processes(processes)
    
    def on_connections_updated(self, connections):
        """网络连接更新"""
        self.network_interface.update_connections(connections)

    def on_traffic_updated(self, traffic_data):
        """流量信息更新"""
        self.traffic_interface.update_traffic(traffic_data)
    
    def on_process_traffic_updated(self, traffic_list):
        """进程流量更新"""
        self.traffic_interface.update_process_traffic(traffic_list)

    def refresh_process_traffic(self):
        """刷新进程流量"""
        self.traffic_controller.get_process_traffic()

    # 高级监控信号处理
    def on_temperature_updated(self, temp_info):
        """温度信息更新"""
        self.system_monitor_interface.update_temperature(temp_info)

    def on_battery_updated(self, battery_info):
        """电池信息更新"""
        self.system_monitor_interface.update_battery(battery_info)

    def on_services_updated(self, services):
        """服务列表更新"""
        self.services_interface.update_services(services)

    def refresh_temperature(self):
        """刷新温度信息"""
        import psutil
        try:
            temp_info = {}
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        temp_list = []
                        for entry in entries:
                            temp_data = {
                                'label': entry.label or name,
                                'current': entry.current,
                                'high': entry.high,
                                'critical': entry.critical
                            }
                            temp_list.append(temp_data)
                        temp_info[name] = temp_list
                else:
                    temp_info['error'] = "未检测到温度传感器"
            else:
                temp_info['error'] = "当前系统不支持温度监控"
            self.on_temperature_updated(temp_info)
            self.status_bar.showMessage("温度信息已刷新", 2000)
        except Exception as e:
            self.on_error(f"获取温度信息失败: {str(e)}")

    def refresh_battery(self):
        """刷新电池信息"""
        import psutil
        try:
            battery_info = {}
            if hasattr(psutil, 'sensors_battery'):
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = {
                        'percent': battery.percent,
                        'power_plugged': battery.power_plugged,
                        'seconds_left': battery.secsleft if not battery.power_plugged else None,
                    }
                    if battery_info['seconds_left'] and battery_info['seconds_left'] != -1:
                        hours = battery_info['seconds_left'] // 3600
                        minutes = (battery_info['seconds_left'] % 3600) // 60
                        battery_info['time_left_formatted'] = f"{hours}小时{minutes}分钟"
                    else:
                        battery_info['time_left_formatted'] = "正在充电或无法估算"
                    battery_info['status'] = "充电中" if battery.power_plugged else "使用电池"
                else:
                    battery_info['error'] = "未检测到电池"
            else:
                battery_info['error'] = "当前系统不支持电池监控"
            self.on_battery_updated(battery_info)
            self.status_bar.showMessage("电池信息已刷新", 2000)
        except Exception as e:
            self.on_error(f"获取电池信息失败: {str(e)}")

    def refresh_services(self):
        """刷新服务列表"""
        import platform
        try:
            services = []
            if platform.system() == 'Windows':
                try:
                    import win32service
                    import win32con

                    hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
                    service_list = win32service.EnumServicesStatus(
                        hscm,
                        win32service.SERVICE_WIN32,
                        win32service.SERVICE_STATE_ALL
                    )
                    win32service.CloseServiceHandle(hscm)

                    for service in service_list[:100]:
                        service_name = service[0]
                        display_name = service[1]
                        status_code = service[2][1]

                        status_map = {
                            win32service.SERVICE_STOPPED: "已停止",
                            win32service.SERVICE_START_PENDING: "启动中",
                            win32service.SERVICE_STOP_PENDING: "停止中",
                            win32service.SERVICE_RUNNING: "运行中",
                            win32service.SERVICE_CONTINUE_PENDING: "继续中",
                            win32service.SERVICE_PAUSE_PENDING: "暂停中",
                            win32service.SERVICE_PAUSED: "已暂停",
                        }

                        services.append({
                            'name': service_name,
                            'display_name': display_name,
                            'status': status_map.get(status_code, "未知"),
                            'status_code': status_code
                        })

                except ImportError:
                    services = [{'error': '需要安装 pywin32 库'}]
                except Exception as e:
                    services = [{'error': f'获取服务失败: {str(e)}'}]
            else:
                services = [{'error': '仅支持Windows系统'}]

            self.on_services_updated(services)
            self.status_bar.showMessage("服务列表已刷新", 2000)
        except Exception as e:
            self.on_error(f"获取服务信息失败: {str(e)}")

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
        about_text = f"""系统监控与进程管理工具 v3.2

基于PySide6开发的现代化系统监控工具

功能特性:
• 系统信息查看（详细系统配置）
• 系统监控（CPU、内存、磁盘、温度、电池）
• 进程管理和监控
• 网络连接监控
• 网络流量监控（实时速度+进程流量）
• 硬件信息查看
• 系统服务管理
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
        app.setStyle("windowsvista")
        # 设置应用程序信息
        app.setApplicationName("系统监控工具")
        app.setApplicationVersion("3.0")
        app.setOrganizationName("System Monitor")
        
        # 使用PySide6默认样式
        
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
