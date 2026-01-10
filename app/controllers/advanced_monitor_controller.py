#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级监控控制器
负责温度、电池、服务等高级监控功能
"""

import psutil
import platform
from typing import Dict, List
from PySide6.QtCore import QObject, Signal


class AdvancedMonitorController(QObject):
    """高级监控控制器"""

    # 信号定义
    temperature_updated = Signal(dict)
    battery_updated = Signal(dict)
    services_updated = Signal(list)
    error_occurred = Signal(str)

    def get_temperature_info(self) -> Dict:
        """获取温度信息"""
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

            self.temperature_updated.emit(temp_info)
            return temp_info

        except Exception as e:
            error_msg = f"获取温度信息失败: {str(e)}"
            self.error_occurred.emit(error_msg)
            return {'error': error_msg}

    def get_battery_info(self) -> Dict:
        """获取电池信息"""
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

                    # 计算剩余时间（小时:分钟格式）
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

            self.battery_updated.emit(battery_info)
            return battery_info

        except Exception as e:
            error_msg = f"获取电池信息失败: {str(e)}"
            self.error_occurred.emit(error_msg)
            return {'error': error_msg}

    def get_services_info(self) -> List[Dict]:
        """获取Windows服务信息"""
        try:
            services = []

            if platform.system() == 'Windows':
                try:
                    import win32service
                    import win32con

                    # 打开服务管理器
                    hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)

                    # 获取所有服务
                    service_list = win32service.EnumServicesStatus(
                        hscm,
                        win32service.SERVICE_WIN32,
                        win32service.SERVICE_STATE_ALL
                    )

                    # 关闭服务管理器句柄
                    win32service.CloseServiceHandle(hscm)

                    for service in service_list[:100]:  # 限制显示前100个服务
                        service_name = service[0]
                        display_name = service[1]
                        status_code = service[2][1]

                        # 转换状态码
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

            self.services_updated.emit(services)
            return services

        except Exception as e:
            error_msg = f"获取服务信息失败: {str(e)}"
            self.error_occurred.emit(error_msg)
            return [{'error': error_msg}]
