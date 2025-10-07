#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控核心功能模块
提供系统信息获取、进程管理、网络监控等核心功能
"""

import os
import platform
import socket
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import psutil
from PySide6.QtCore import QThread, Signal


@dataclass
class SystemInfo:
    """系统信息数据类"""
    cpu_percent: float
    cpu_count: int
    cpu_count_logical: int
    cpu_freq: Optional[psutil._common.scpufreq]
    memory_total: int
    memory_available: int
    memory_percent: float
    memory_used: int
    disk_total: int
    disk_used: int
    disk_free: int
    disk_percent: float
    bytes_sent: int
    bytes_recv: int


@dataclass
class ProcessInfo:
    """进程信息数据类"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str


@dataclass
class NetworkConnection:
    """网络连接信息数据类"""
    protocol: str
    local_addr: str
    remote_addr: str
    status: str
    pid: Optional[int]


class SystemMonitor:
    """系统监控核心类"""
    
    def __init__(self):
        self._last_cpu_times = None
    
    def get_system_info(self) -> SystemInfo:
        """获取系统基本信息"""
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=False) or 0
            cpu_count_logical = psutil.cpu_count(logical=True) or 0
            cpu_freq = psutil.cpu_freq()
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息 - 使用主分区
            disk_path = self._get_main_disk_path()
            disk = psutil.disk_usage(disk_path)
            
            # 网络信息
            net_io = psutil.net_io_counters()
            
            return SystemInfo(
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                cpu_count_logical=cpu_count_logical,
                cpu_freq=cpu_freq,
                memory_total=memory.total,
                memory_available=memory.available,
                memory_percent=memory.percent,
                memory_used=memory.used,
                disk_total=disk.total,
                disk_used=disk.used,
                disk_free=disk.free,
                disk_percent=(disk.used / disk.total) * 100,
                bytes_sent=net_io.bytes_sent,
                bytes_recv=net_io.bytes_recv
            )
        except Exception as e:
            print(f"获取系统信息时出错: {e}")
            # 返回默认值
            return SystemInfo(0, 0, 0, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def _get_main_disk_path(self) -> str:
        """获取主磁盘路径"""
        if platform.system() == "Windows":
            return "C:\\"
        else:
            return "/"
    
    def get_processes(self, sort_by: str = 'cpu_percent') -> List[ProcessInfo]:
        """获取进程列表"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
                try:
                    info = proc.info
                    memory_mb = (info['memory_info'].rss / (1024*1024)) if info['memory_info'] else 0
                    
                    process_info = ProcessInfo(
                        pid=info['pid'],
                        name=info['name'] or 'N/A',
                        cpu_percent=info['cpu_percent'] or 0,
                        memory_percent=info['memory_percent'] or 0,
                        memory_mb=memory_mb,
                        status=info['status'] or 'N/A'
                    )
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 排序
            if sort_by == 'cpu_percent':
                processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            elif sort_by == 'memory_percent':
                processes.sort(key=lambda x: x.memory_percent, reverse=True)
            elif sort_by == 'name':
                processes.sort(key=lambda x: x.name.lower())
            elif sort_by == 'pid':
                processes.sort(key=lambda x: x.pid)
                
        except Exception as e:
            print(f"获取进程列表时出错: {e}")
        
        return processes
    
    def kill_process(self, pid: int) -> tuple[bool, str]:
        """结束进程"""
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()
            return True, f"进程 {proc_name} (PID: {pid}) 已被结束"
        except psutil.NoSuchProcess:
            return False, f"进程 PID {pid} 不存在"
        except psutil.AccessDenied:
            return False, f"没有权限结束进程 PID {pid}"
        except Exception as e:
            return False, f"结束进程时出错: {e}"
    
    def get_network_connections(self) -> List[NetworkConnection]:
        """获取网络连接信息"""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                status = conn.status if conn.status else "N/A"
                
                connection = NetworkConnection(
                    protocol=protocol,
                    local_addr=local_addr,
                    remote_addr=remote_addr,
                    status=status,
                    pid=conn.pid
                )
                connections.append(connection)
                
        except Exception as e:
            print(f"获取网络连接时出错: {e}")
        
        return connections
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        info = {}
        
        try:
            # CPU信息
            info['cpu'] = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'architecture': platform.architecture(),
                'processor': platform.processor()
            }
            
            # 内存信息
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
            
            # 磁盘信息
            partitions = psutil.disk_partitions()
            disk_info = []
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    })
                except PermissionError:
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'error': '无法访问'
                    })
            info['disks'] = disk_info
            
            # 网络接口信息
            net_interfaces = {}
            net_if_addrs = psutil.net_if_addrs()
            for interface_name, interface_addresses in net_if_addrs.items():
                addresses = []
                for address in interface_addresses:
                    addr_info = {
                        'family': str(address.family),
                        'address': address.address,
                        'netmask': address.netmask,
                        'broadcast': address.broadcast
                    }
                    addresses.append(addr_info)
                net_interfaces[interface_name] = addresses
            info['network_interfaces'] = net_interfaces
            
        except Exception as e:
            print(f"获取硬件信息时出错: {e}")
            info['error'] = str(e)
        
        return info
    
    def get_system_details(self) -> Dict[str, Any]:
        """获取系统详细信息"""
        info = {}
        
        try:
            # 基本系统信息
            info['system'] = {
                'computer_name': platform.node(),
                'os_name': platform.system(),
                'os_release': platform.release(),
                'os_version': platform.version(),
                'architecture': platform.architecture(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 用户信息
            users = []
            for user in psutil.users():
                user_info = {
                    'name': user.name,
                    'terminal': user.terminal,
                    'host': user.host,
                    'started': datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
                }
                users.append(user_info)
            info['users'] = users
            
            # 重要环境变量
            important_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER', 'COMPUTERNAME', 'PROCESSOR_IDENTIFIER']
            env_vars = {}
            for var in important_vars:
                value = os.environ.get(var, 'N/A')
                if len(value) > 100:
                    value = value[:100] + "..."
                env_vars[var] = value
            info['environment'] = env_vars
            
        except Exception as e:
            print(f"获取系统详情时出错: {e}")
            info['error'] = str(e)
        
        return info


class SystemInfoWorker(QThread):
    """后台线程用于获取系统信息，避免UI阻塞"""
    info_updated = Signal(SystemInfo)
    
    def __init__(self, update_interval: int = 2000):
        super().__init__()
        self.running = True
        self.update_interval = update_interval
        self.monitor = SystemMonitor()
    
    def run(self):
        """线程运行方法"""
        while self.running:
            try:
                info = self.monitor.get_system_info()
                self.info_updated.emit(info)
                self.msleep(self.update_interval)
            except Exception as e:
                print(f"后台获取系统信息时出错: {e}")
                self.msleep(5000)  # 出错时等待更长时间
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.quit()
        self.wait()
    
    def set_update_interval(self, interval: int):
        """设置更新间隔（毫秒）"""
        self.update_interval = max(1000, interval)  # 最小1秒


class ProcessManager:
    """进程管理器"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
    
    def get_process_list(self, sort_by: str = 'cpu_percent', filter_name: str = '') -> List[ProcessInfo]:
        """获取进程列表，支持过滤和排序"""
        processes = self.monitor.get_processes(sort_by)
        
        if filter_name:
            processes = [p for p in processes if filter_name.lower() in p.name.lower()]
        
        return processes
    
    def terminate_process(self, pid: int) -> tuple[bool, str]:
        """结束进程"""
        return self.monitor.kill_process(pid)
    
    def get_process_details(self, pid: int) -> Optional[Dict[str, Any]]:
        """获取进程详细信息"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'exe': proc.exe(),
                'cwd': proc.cwd(),
                'cmdline': proc.cmdline(),
                'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_percent': proc.cpu_percent(),
                'memory_info': proc.memory_info()._asdict(),
                'memory_percent': proc.memory_percent(),
                'status': proc.status(),
                'num_threads': proc.num_threads(),
                'connections': len(proc.connections())
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return None


class NetworkMonitor:
    """网络监控器"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
    
    def get_connections(self, protocol_filter: str = 'all') -> List[NetworkConnection]:
        """获取网络连接，支持协议过滤"""
        connections = self.monitor.get_network_connections()
        
        if protocol_filter.upper() in ['TCP', 'UDP']:
            connections = [c for c in connections if c.protocol == protocol_filter.upper()]
        
        return connections
    
    def get_listening_ports(self) -> List[NetworkConnection]:
        """获取监听端口"""
        connections = self.get_connections()
        return [c for c in connections if c.status == 'LISTEN']
    
    def get_network_stats(self) -> Dict[str, Any]:
        """获取网络统计信息"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }
        except Exception as e:
            print(f"获取网络统计信息时出错: {e}")
            return {}


# 工具函数
def format_bytes(bytes_value: int) -> str:
    """格式化字节数为可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_frequency(freq_mhz: float) -> str:
    """格式化频率为可读格式"""
    if freq_mhz >= 1000:
        return f"{freq_mhz / 1000:.2f} GHz"
    else:
        return f"{freq_mhz:.0f} MHz"


def get_system_uptime() -> str:
    """获取系统运行时间"""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"
    except Exception:
        return "未知"
