#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件信息控制器
负责硬件信息的获取
"""

import psutil
import platform
from typing import Dict
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

            return hardware_info

        except Exception as e:
            raise Exception(f"获取硬件信息失败: {str(e)}")

    def get_hardware_info_sync(self) -> Dict:
        """同步获取硬件信息（用于对话框，仍会阻塞）"""
        return self._fetch_hardware_info()

