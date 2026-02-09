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
import os
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
                'architecture': platform.machine() if hasattr(platform, 'machine') else 'Unknown',
                'hostname': platform.node(),
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

            # 每个核心的使用率（百分比）
            try:
                cpu_info['per_cpu_percent'] = psutil.cpu_percent(interval=0.1, percpu=True)
            except:
                cpu_info['per_cpu_percent'] = []

            # 总体CPU使用率
            try:
                cpu_info['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            except:
                cpu_info['cpu_percent'] = 0

            # CPU统计信息（上下文切换、中断、系统调用等）
            try:
                cpu_stats = psutil.cpu_stats()
                cpu_info['stats'] = {
                    'ctx_switches': cpu_stats.ctx_switches,
                    'interrupts': cpu_stats.interrupts,
                    'soft_interrupts': cpu_stats.soft_interrupts,
                    'syscalls': cpu_stats.syscalls
                }
            except:
                pass

            # CPU时间信息（用户、系统、空闲等）
            try:
                cpu_times = psutil.cpu_times()
                cpu_info['times'] = {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle
                }
                if hasattr(cpu_times, 'nice'):
                    cpu_info['times']['nice'] = cpu_times.nice
                if hasattr(cpu_times, 'iowait'):
                    cpu_info['times']['iowait'] = cpu_times.iowait
                if hasattr(cpu_times, 'irq'):
                    cpu_info['times']['irq'] = cpu_times.irq
                if hasattr(cpu_times, 'softirq'):
                    cpu_info['times']['softirq'] = cpu_times.softirq
                if hasattr(cpu_times, 'steal'):
                    cpu_info['times']['steal'] = cpu_times.steal
                if hasattr(cpu_times, 'guest'):
                    cpu_info['times']['guest'] = cpu_times.guest
            except:
                pass

            # 每个核心的时间信息
            try:
                cpu_times_percpu = psutil.cpu_times(percpu=True)
                cpu_info['per_cpu_times'] = []
                for times in cpu_times_percpu:
                    core_time = {
                        'user': times.user,
                        'system': times.system,
                        'idle': times.idle
                    }
                    if hasattr(times, 'nice'):
                        core_time['nice'] = times.nice
                    if hasattr(times, 'iowait'):
                        core_time['iowait'] = times.iowait
                    if hasattr(times, 'irq'):
                        core_time['irq'] = times.irq
                    if hasattr(times, 'softirq'):
                        core_time['softirq'] = times.softirq
                    cpu_info['per_cpu_times'].append(core_time)
            except:
                pass

            # 获取CPU缓存信息（仅Linux）
            try:
                if platform.system() == 'Linux':
                    import os
                    cache_info = {}
                    # L1缓存
                    for cache_type in ['dcache', 'icache']:
                        cache_path = f'/sys/devices/system/cpu/cpu0/cache/index0/{cache_type}'
                        if os.path.exists(cache_path):
                            try:
                                with open(cache_path, 'r') as f:
                                    cache_info[cache_type] = f.read().strip()
                            except:
                                pass

                    # 尝试读取缓存大小
                    for level in [0, 1, 2, 3]:
                        size_path = f'/sys/devices/system/cpu/cpu0/cache/index{level}/size'
                        if os.path.exists(size_path):
                            try:
                                with open(size_path, 'r') as f:
                                    cache_info[f'L{level}_cache'] = f.read().strip()
                            except:
                                pass

                    if cache_info:
                        cpu_info['cache_info'] = cache_info
            except:
                pass

            # 获取CPU型号和特性
            try:
                if platform.system() == 'Linux':
                    # 读取 /proc/cpuinfo
                    try:
                        with open('/proc/cpuinfo', 'r') as f:
                            cpuinfo_content = f.read()

                        # 提取CPU型号
                        for line in cpuinfo_content.split('\n'):
                            if line.startswith('model name'):
                                cpu_info['model_name'] = line.split(':', 1)[1].strip()
                                break
                            elif line.startswith('Hardware'):
                                cpu_info['hardware'] = line.split(':', 1)[1].strip()

                        # 提取CPU特性
                        for line in cpuinfo_content.split('\n'):
                            if line.startswith('flags') or line.startswith('Features'):
                                flags = line.split(':', 1)[1].strip()
                                cpu_info['flags'] = flags.split()
                                break
                    except:
                        pass
                elif platform.system() == 'Windows':
                    # 使用 WMI 获取更详细的CPU信息
                    try:
                        import wmi
                        c = wmi.WMI()
                        for cpu in c.Win32_Processor():
                            cpu_info['model_name'] = cpu.Name
                            cpu_info['manufacturer'] = cpu.Manufacturer
                            cpu_info['max_clock_speed'] = cpu.MaxClockSpeed
                            cpu_info['current_clock_speed'] = cpu.CurrentClockSpeed
                            cpu_info['number_of_cores'] = cpu.NumberOfCores
                            cpu_info['number_of_logical_processors'] = cpu.NumberOfLogicalProcessors
                            cpu_info['l2_cache_size'] = getattr(cpu, 'L2CacheSize', None)
                            cpu_info['l3_cache_size'] = getattr(cpu, 'L3CacheSize', None)
                            cpu_info['virtualization'] = getattr(cpu, 'VirtualizationFirmwareEnabled', False)
                            break
                    except:
                        pass
            except:
                pass

            # 获取CPU负载（1分钟、5分钟、15分钟）
            try:
                if hasattr(os, 'getloadavg'):
                    load1, load5, load15 = os.getloadavg()
                    cpu_info['load_average'] = {
                        '1min': load1,
                        '5min': load5,
                        '15min': load15
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

            # 音频设备信息
            hardware_info['audio'] = self._get_audio_devices()

            # 蓝牙设备信息
            hardware_info['bluetooth'] = self._get_bluetooth_devices()

            # USB设备信息
            hardware_info['usb_devices'] = self._get_usb_devices()

            # 键盘鼠标信息
            hardware_info['input_devices'] = self._get_keyboard_mouse_info()

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

    def _get_audio_devices(self) -> Dict:
        """获取音频设备信息"""
        audio_info = {'input_devices': [], 'output_devices': []}

        try:
            if platform.system() == 'Windows':
                try:
                    import pyaudio
                    p = pyaudio.PyAudio()

                    for i in range(p.get_device_count()):
                        info = p.get_device_info_by_index(i)
                        device = {
                            'name': info.get('name', 'Unknown'),
                            'channels': info.get('maxInputChannels', 0) if info.get('maxInputChannels', 0) > 0 else info.get('maxOutputChannels', 0),
                            'sample_rate': int(info.get('defaultSampleRate', 0)),
                        }

                        if info.get('maxInputChannels', 0) > 0:
                            audio_info['input_devices'].append(device)
                        if info.get('maxOutputChannels', 0) > 0:
                            audio_info['output_devices'].append(device)

                    p.terminate()
                except ImportError:
                    audio_info['message'] = '需要安装 pyaudio 库'
                except Exception as e:
                    audio_info['error'] = f"获取音频设备失败: {str(e)}"
            else:
                audio_info['message'] = f"{platform.system()} 系统音频设备获取待实现"

        except Exception as e:
            audio_info['error'] = str(e)

        return audio_info

    def _get_bluetooth_devices(self) -> List[Dict]:
        """获取蓝牙设备信息"""
        bluetooth_devices = []

        try:
            if platform.system() == 'Windows':
                try:
                    import wmi
                    c = wmi.WMI()

                    # 获取蓝牙无线电设备
                    for radio in c.Win32_PnPEntity(DeviceID="*BTH*"):
                        device = {
                            'name': radio.Name,
                            'device_id': radio.DeviceID,
                            'status': '已连接' if radio.Status else '未连接',
                            'type': '蓝牙适配器'
                        }
                        bluetooth_devices.append(device)

                    # 获取配对的蓝牙设备
                    try:
                        import win32com.client
                        shell = win32com.client.Dispatch("WScript.Shell")
                        # 尝试获取蓝牙设备信息
                        for device in c.Win32_PnPEntity():
                            if 'Bluetooth' in device.Name or 'bluetooth' in device.Name:
                                bluetooth_devices.append({
                                    'name': device.Name,
                                    'device_id': device.DeviceID,
                                    'type': '蓝牙设备'
                                })
                    except:
                        pass

                    if not bluetooth_devices:
                        bluetooth_devices.append({'message': '未检测到蓝牙设备'})

                except ImportError:
                    bluetooth_devices.append({'message': '需要安装 wmi 和 pywin32 库'})
                except Exception as e:
                    bluetooth_devices.append({'error': f"获取蓝牙设备失败: {str(e)}"})
            else:
                # Linux 下尝试获取蓝牙设备
                try:
                    result = subprocess.run(['bluetoothctl', 'list'], capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        bluetooth_devices.append({'message': 'Linux 蓝牙设备检测功能开发中'})
                    else:
                        bluetooth_devices.append({'message': '未检测到蓝牙适配器'})
                except:
                    bluetooth_devices.append({'message': f'{platform.system()} 系统蓝牙设备检测待实现'})

        except Exception as e:
            bluetooth_devices.append({'error': str(e)})

        return bluetooth_devices if bluetooth_devices else [{'message': '未检测到蓝牙设备'}]

    def _get_usb_devices(self) -> List[Dict]:
        """获取USB设备信息（包括鼠标、键盘等）"""
        usb_devices = []

        try:
            if platform.system() == 'Windows':
                try:
                    import wmi
                    c = wmi.WMI()

                    # 获取USB设备
                    for device in c.Win32_USBController():
                        usb_devices.append({
                            'name': device.Name,
                            'device_id': device.DeviceID,
                            'type': 'USB控制器',
                            'status': '正常'
                        })

                    # 获取连接的USB设备（人机接口设备）
                    hid_devices = []
                    for device in c.Win32_PnPEntity():
                        device_name = device.Name or ''
                        # 过滤出鼠标、键盘等HID设备
                        if any(keyword in device_name.lower() for keyword in ['mouse', 'keyboard', 'hid', 'usb', 'input']):
                            device_type = '其他'
                            if 'mouse' in device_name.lower():
                                device_type = '鼠标'
                            elif 'keyboard' in device_name.lower() or 'kbd' in device_name.lower():
                                device_type = '键盘'
                            elif 'hid' in device_name.lower():
                                device_type = '人机接口设备'
                            elif 'usb' in device_name.lower():
                                device_type = 'USB设备'

                            hid_devices.append({
                                'name': device_name,
                                'device_id': device.DeviceID,
                                'type': device_type,
                                'status': '已连接' if device.Status else '未连接',
                                'manufacturer': getattr(device, 'Manufacturer', 'Unknown')
                            })

                    # 去重并添加
                    seen_ids = set()
                    for device in hid_devices:
                        if device['device_id'] not in seen_ids:
                            usb_devices.append(device)
                            seen_ids.add(device['device_id'])

                    if not usb_devices:
                        usb_devices.append({'message': '未检测到USB设备'})

                except ImportError:
                    usb_devices.append({'message': '需要安装 wmi 和 pywin32 库'})
                except Exception as e:
                    usb_devices.append({'error': f"获取USB设备失败: {str(e)}"})
            else:
                # Linux 下读取USB设备信息
                try:
                    usb_info = []
                    # 读取/sys/bus/usb/devices/
                    import os
                    usb_path = '/sys/bus/usb/devices/'
                    if os.path.exists(usb_path):
                        for device_dir in os.listdir(usb_path):
                            if device_dir.startswith('usb') or ':' in device_dir:
                                continue
                            try:
                                with open(os.path.join(usb_path, device_dir, 'product'), 'r') as f:
                                    name = f.read().strip()
                                with open(os.path.join(usb_path, device_dir, 'idVendor'), 'r') as f:
                                    vendor = f.read().strip()
                                usb_devices.append({
                                    'name': name,
                                    'vendor_id': vendor,
                                    'type': 'USB设备'
                                })
                            except:
                                pass

                    if not usb_devices:
                        usb_devices.append({'message': '未检测到USB设备信息'})

                except Exception as e:
                    usb_devices.append({'error': f"获取USB设备失败: {str(e)}"})

        except Exception as e:
            usb_devices.append({'error': str(e)})

        return usb_devices if usb_devices else [{'message': '未检测到USB设备'}]

    def _get_keyboard_mouse_info(self) -> Dict:
        """获取键盘鼠标信息"""
        input_devices = {'keyboards': [], 'mice': []}

        try:
            if platform.system() == 'Windows':
                try:
                    import wmi
                    c = wmi.WMI()

                    # 获取键盘
                    for keyboard in c.Win32_Keyboard():
                        input_devices['keyboards'].append({
                            'name': getattr(keyboard, 'Name', 'Unknown'),
                            'description': getattr(keyboard, 'Description', 'Unknown'),
                            'status': '正常'
                        })

                    # 获取鼠标/指针设备
                    for mouse in c.Win32_PointingDevice():
                        input_devices['mice'].append({
                            'name': getattr(mouse, 'Name', 'Unknown'),
                            'description': getattr(mouse, 'Description', 'Unknown'),
                            'device_type': getattr(mouse, 'DeviceType', 'Unknown'),
                            'status': '正常'
                        })

                    if not input_devices['keyboards']:
                        input_devices['keyboards'].append({'message': '未检测到键盘'})
                    if not input_devices['mice']:
                        input_devices['mice'].append({'message': '未检测到鼠标'})

                except ImportError:
                    input_devices['message'] = '需要安装 wmi 和 pywin32 库'
                except Exception as e:
                    input_devices['error'] = f"获取输入设备失败: {str(e)}"
            else:
                input_devices['message'] = f"{platform.system()} 系统输入设备检测待实现"

        except Exception as e:
            input_devices['error'] = str(e)

        return input_devices

    def get_hardware_info_sync(self) -> Dict:
        """同步获取硬件信息（用于对话框，仍会阻塞）"""
        return self._fetch_hardware_info()

