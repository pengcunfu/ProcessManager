#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件信息控制器
负责硬件信息的获取
"""

import psutil
import platform
import subprocess
import re
from typing import Dict, List
from PySide6.QtCore import QObject, Signal

from app.utils.async_worker import AsyncWorkerManager


class HardwareController(QObject):
    """硬件信息控制器"""

    # 信号定义
    hardware_info_updated = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_manager = AsyncWorkerManager(self)

    def get_hardware_info(self) -> Dict:
        """获取硬件信息（异步执行）"""
        self.worker_manager.execute(
            name='get_hardware_info',
            target_func=self._fetch_hardware_info,
            callback=self.hardware_info_updated.emit,
            error_callback=lambda e: self.error_occurred.emit(f"获取硬件信息失败: {e}")
        )

    def _fetch_hardware_info(self) -> Dict:
        """
        实际获取硬件信息的函数（在后台线程执行）

        Returns:
            硬件信息字典
        """
        try:
            hardware_info = {}

            # CPU信息
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'processor': platform.processor(),
            }

            # CPU频率信息
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_info['frequency'] = {
                        'current': cpu_freq.current,
                        'min': cpu_freq.min,
                        'max': cpu_freq.max
                    }
            except:
                pass

            hardware_info['cpu'] = cpu_info

            # 内存信息
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }

            hardware_info['memory'] = memory_info

            # 磁盘信息
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': disk_usage.total,
                        'used': disk_usage.used,
                        'free': disk_usage.free,
                        'percent': (disk_usage.used / disk_usage.total) * 100
                    }
                    disks.append(disk_info)
                except Exception as e:
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'error': f"无法访问: {str(e)}"
                    })

            hardware_info['disks'] = disks

            # 网络接口信息
            network_interfaces = {}
            for interface_name, addresses in psutil.net_if_addrs().items():
                interface_info = []
                for addr in addresses:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    interface_info.append(addr_info)
                network_interfaces[interface_name] = interface_info

            hardware_info['network_interfaces'] = network_interfaces

            # 显卡信息
            hardware_info['gpus'] = self._get_gpu_info()

            # 主板信息
            hardware_info['motherboard'] = self._get_motherboard_info()

            # 温度传感器信息
            hardware_info['temperatures'] = self._get_temperature_info()

            # 风扇信息
            hardware_info['fans'] = self._get_fan_info()

            # 电池信息（如果有）
            hardware_info['battery'] = self._get_battery_info()

            return hardware_info

        except Exception as e:
            raise Exception(f"获取硬件信息失败: {str(e)}")

    def _get_gpu_info(self) -> List[Dict]:
        """获取显卡信息"""
        gpus = []

        try:
            # 尝试使用 pynvml 获取 NVIDIA GPU 信息
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()

                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle)
                    power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle)

                    # 获取驱动版本
                    try:
                        driver_version = pynvml.nvmlSystemGetDriverVersion()
                    except:
                        driver_version = "Unknown"

                    gpu_info = {
                        'name': name.decode('utf-8') if isinstance(name, bytes) else name,
                        'type': 'NVIDIA',
                        'memory_total': memory_info.total,
                        'memory_used': memory_info.used,
                        'memory_free': memory_info.free,
                        'temperature': temp,
                        'fan_speed': fan_speed,
                        'power_usage': power_usage / 1000,  # 转换为瓦特
                        'power_limit': power_limit / 1000,   # 转换为瓦特
                        'driver_version': driver_version,
                        'index': i
                    }
                    gpus.append(gpu_info)

                pynvml.nvmlShutdown()
            except ImportError:
                pass  # pynvml 未安装，尝试其他方法
            except Exception as e:
                pass  # NVIDIA GPU 不可用

            # 尝试使用 GPUtil 获取所有 GPU 信息
            if not gpus:
                try:
                    import GPUtil
                    gpu_list = GPUtil.getGPUs()
                    for gpu in gpu_list:
                        gpu_info = {
                            'name': gpu.name,
                            'type': 'GPU',
                            'memory_total': gpu.memoryTotal * 1024 * 1024,  # 转换为字节
                            'memory_used': gpu.memoryUsed * 1024 * 1024,
                            'memory_free': gpu.memoryFree * 1024 * 1024,
                            'temperature': gpu.temperature,
                            'fan_speed': getattr(gpu, 'fan', None),  # 可能不可用
                            'load': gpu.load * 100,
                            'driver_version': 'Unknown'
                        }
                        gpus.append(gpu_info)
                except ImportError:
                    pass
                except Exception as e:
                    pass

            # Windows 下使用 WMI 获取 GPU 信息
            if not gpus and platform.system() == 'Windows':
                try:
                    import wmi
                    c = wmi.WMI()
                    for gpu in c.Win32_VideoController():
                        gpu_info = {
                            'name': gpu.Name,
                            'type': 'Display Adapter',
                            'memory_total': getattr(gpu, 'AdapterRAM', 0) or 0,
                            'driver_version': getattr(gpu, 'DriverVersion', 'Unknown'),
                            'driver_date': getattr(gpu, 'DriverDate', 'Unknown'),
                        }
                        gpus.append(gpu_info)
                except ImportError:
                    pass
                except Exception as e:
                    pass

        except Exception as e:
            gpus.append({'error': str(e)})

        return gpus if gpus else [{'message': '未检测到显卡信息'}]

    def _get_motherboard_info(self) -> Dict:
        """获取主板信息"""
        motherboard_info = {}

        try:
            if platform.system() == 'Linux':
                # Linux 下读取 DMI 信息
                try:
                    # 获取主板制造商
                    with open('/sys/class/dmi/id/board_vendor', 'r') as f:
                        motherboard_info['manufacturer'] = f.read().strip()

                    # 获取主板型号
                    with open('/sys/class/dmi/id/board_name', 'r') as f:
                        motherboard_info['model'] = f.read().strip()

                    # 获取主板版本
                    with open('/sys/class/dmi/id/board_version', 'r') as f:
                        motherboard_info['version'] = f.read().strip()

                    # 获取 BIOS 信息
                    with open('/sys/class/dmi/id/bios_vendor', 'r') as f:
                        motherboard_info['bios_vendor'] = f.read().strip()

                    with open('/sys/class/dmi/id/bios_version', 'r') as f:
                        motherboard_info['bios_version'] = f.read().strip()

                    with open('/sys/class/dmi/id/bios_date', 'r') as f:
                        motherboard_info['bios_date'] = f.read().strip()
                except Exception as e:
                    motherboard_info['error'] = f"读取主板信息失败: {str(e)}"

            elif platform.system() == 'Windows':
                # Windows 下使用 WMI 获取主板信息
                try:
                    import wmi
                    c = wmi.WMI()

                    # 主板信息
                    for board in c.Win32_BaseBoard():
                        motherboard_info['manufacturer'] = board.Manufacturer
                        motherboard_info['model'] = board.Product
                        motherboard_info['version'] = board.Version
                        break

                    # BIOS 信息
                    for bios in c.Win32_BIOS():
                        motherboard_info['bios_vendor'] = bios.Manufacturer
                        motherboard_info['bios_version'] = bios.SMBIOSBIOSVersion
                        motherboard_info['bios_date'] = str(bios.ReleaseDate)[:8] if bios.ReleaseDate else 'Unknown'
                        break
                except ImportError:
                    motherboard_info['error'] = '需要安装 wmi 和 pywin32 库'
                except Exception as e:
                    motherboard_info['error'] = f"获取主板信息失败: {str(e)}"
            else:
                motherboard_info['message'] = f"{platform.system()} 系统暂不支持主板信息获取"

        except Exception as e:
            motherboard_info['error'] = str(e)

        return motherboard_info if motherboard_info else {'message': '未检测到主板信息'}

    def _get_temperature_info(self) -> Dict:
        """获取温度传感器信息"""
        temp_info = {}

        try:
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
                    temp_info['message'] = '未检测到温度传感器'
            else:
                temp_info['message'] = '当前系统不支持温度监控'

        except Exception as e:
            temp_info['error'] = str(e)

        return temp_info if temp_info else {'message': '未检测到温度信息'}

    def _get_fan_info(self) -> Dict:
        """获取风扇信息"""
        fan_info = {}

        try:
            if hasattr(psutil, 'sensors_fans'):
                fans = psutil.sensors_fans()
                if fans:
                    for name, entries in fans.items():
                        fan_list = []
                        for entry in entries:
                            fan_data = {
                                'label': entry.label or name,
                                'current_rpm': entry.current
                            }
                            fan_list.append(fan_data)
                        fan_info[name] = fan_list
                else:
                    fan_info['message'] = '未检测到风扇传感器'
            else:
                fan_info['message'] = '当前系统不支持风扇监控'

        except Exception as e:
            fan_info['error'] = str(e)

        return fan_info if fan_info else {'message': '未检测到风扇信息'}

    def _get_battery_info(self) -> Dict:
        """获取电池信息"""
        battery_info = {}

        try:
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
                    battery_info['message'] = "未检测到电池"
            else:
                battery_info['message'] = "当前系统不支持电池监控"

        except Exception as e:
            battery_info['error'] = str(e)

        return battery_info if battery_info else {'message': '未检测到电池信息'}

    def get_hardware_info_sync(self) -> Dict:
        """同步获取硬件信息（用于对话框，仍会阻塞）"""
        return self._fetch_hardware_info()

