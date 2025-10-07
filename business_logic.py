#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务逻辑层
负责处理系统监控、进程管理等核心业务功能
"""

import psutil
import platform
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QTimer, QThread


@dataclass
class SystemInfo:
    """系统信息数据类"""
    cpu_percent: float
    cpu_count: int
    memory_percent: float
    memory_used: int
    memory_total: int
    memory_available: int
    disk_percent: float
    disk_used: int
    disk_total: int
    disk_free: int
    boot_time: str
    uptime: str
    process_count: int
    bytes_sent: int = 0
    bytes_recv: int = 0


@dataclass
class ProcessInfo:
    """进程信息数据类"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: str
    exe_path: str = ""
    cmdline: List[str] = None
    num_threads: int = 0
    parent_pid: Optional[int] = None


@dataclass
class NetworkConnection:
    """网络连接信息数据类"""
    protocol: str
    local_addr: str
    remote_addr: str
    status: str
    pid: Optional[int]


class SystemMonitorService(QObject):
    """系统监控服务"""
    
    # 信号定义
    system_info_updated = Signal(SystemInfo)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.update_interval = 2.0  # 更新间隔（秒）
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_system_info)
        
        # 初始化CPU百分比计算
        psutil.cpu_percent()
    
    def start_monitoring(self):
        """开始监控"""
        if not self.is_running:
            self.is_running = True
            self._timer.start(int(self.update_interval * 1000))
    
    def stop_monitoring(self):
        """停止监控"""
        if self.is_running:
            self.is_running = False
            self._timer.stop()
    
    def set_update_interval(self, interval: float):
        """设置更新间隔"""
        self.update_interval = interval
        if self.is_running:
            self._timer.setInterval(int(interval * 1000))
    
    def _update_system_info(self):
        """更新系统信息"""
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息
            try:
                disk = psutil.disk_usage('/')
            except:
                disk = psutil.disk_usage('C:\\')
            
            # 启动时间和运行时间
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            boot_time_str = boot_time.strftime('%Y-%m-%d %H:%M:%S')
            
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            uptime_str = f"{days}天 {hours}小时 {minutes}分钟"
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 网络IO统计
            net_io = psutil.net_io_counters()
            
            # 创建系统信息对象
            system_info = SystemInfo(
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                memory_available=memory.available,
                disk_percent=disk.percent,
                disk_used=disk.used,
                disk_total=disk.total,
                disk_free=disk.free,
                boot_time=boot_time_str,
                uptime=uptime_str,
                process_count=process_count,
                bytes_sent=net_io.bytes_sent,
                bytes_recv=net_io.bytes_recv
            )
            
            self.system_info_updated.emit(system_info)
            
        except Exception as e:
            self.error_occurred.emit(f"获取系统信息失败: {str(e)}")


class ProcessManagerService(QObject):
    """进程管理服务"""
    
    # 信号定义
    processes_updated = Signal(list)
    process_killed = Signal(int, str)  # pid, message
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._processes_cache = []
        self._last_update = 0
        self._cache_duration = 2.0  # 缓存持续时间（秒）
    
    def get_processes(self, force_refresh: bool = False) -> List[ProcessInfo]:
        """获取进程列表"""
        current_time = time.time()
        
        # 如果缓存有效且不强制刷新，返回缓存
        if not force_refresh and (current_time - self._last_update) < self._cache_duration:
            return self._processes_cache
        
        try:
            processes = []
            
            # 限制获取的进程数量，避免性能问题
            max_processes = 300
            process_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
                if process_count >= max_processes:
                    break
                
                try:
                    info = proc.info
                    
                    # 获取内存使用量（MB）
                    try:
                        memory_info = proc.memory_info()
                        memory_mb = memory_info.rss / 1024 / 1024
                    except:
                        memory_mb = 0
                    
                    # 获取创建时间
                    try:
                        create_time = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        create_time = "未知"
                    
                    # 获取可执行文件路径
                    try:
                        exe_path = proc.exe()
                    except:
                        exe_path = ""
                    
                    # 获取线程数
                    try:
                        num_threads = proc.num_threads()
                    except:
                        num_threads = 0
                    
                    # 获取父进程ID
                    try:
                        parent_pid = proc.ppid()
                    except:
                        parent_pid = None
                    
                    process_info = ProcessInfo(
                        pid=info['pid'],
                        name=info['name'] or 'Unknown',
                        cpu_percent=info['cpu_percent'] or 0,
                        memory_percent=info['memory_percent'] or 0,
                        memory_mb=memory_mb,
                        status=info['status'] or 'Unknown',
                        create_time=create_time,
                        exe_path=exe_path,
                        num_threads=num_threads,
                        parent_pid=parent_pid
                    )
                    
                    processes.append(process_info)
                    process_count += 1
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception:
                    continue
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            
            # 更新缓存
            self._processes_cache = processes
            self._last_update = current_time
            
            self.processes_updated.emit(processes)
            return processes
            
        except Exception as e:
            self.error_occurred.emit(f"获取进程列表失败: {str(e)}")
            return []
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """结束进程"""
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            if force:
                proc.kill()
                message = f"强制结束进程 {process_name} (PID: {pid}) 成功"
            else:
                proc.terminate()
                message = f"结束进程 {process_name} (PID: {pid}) 成功"
            
            self.process_killed.emit(pid, message)
            
            # 清除缓存，强制刷新
            self._last_update = 0
            
            return True
            
        except psutil.NoSuchProcess:
            self.error_occurred.emit(f"进程 {pid} 不存在")
            return False
        except psutil.AccessDenied:
            self.error_occurred.emit(f"权限不足，无法结束进程 {pid}")
            return False
        except Exception as e:
            self.error_occurred.emit(f"结束进程 {pid} 失败: {str(e)}")
            return False
    
    def get_process_details(self, pid: int) -> Optional[Dict]:
        """获取进程详细信息"""
        try:
            proc = psutil.Process(pid)
            
            details = {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'memory_info': proc.memory_info(),
                'num_threads': proc.num_threads(),
                'exe': proc.exe() if proc.exe() else "未知",
                'cwd': proc.cwd() if proc.cwd() else "未知",
                'cmdline': proc.cmdline(),
            }
            
            # 获取父进程信息
            try:
                parent = proc.parent()
                if parent:
                    details['parent'] = {
                        'pid': parent.pid,
                        'name': parent.name()
                    }
            except:
                details['parent'] = None
            
            # 获取子进程信息
            try:
                children = proc.children()
                details['children'] = [{'pid': child.pid, 'name': child.name()} for child in children]
            except:
                details['children'] = []
            
            return details
            
        except psutil.NoSuchProcess:
            return None
        except Exception as e:
            self.error_occurred.emit(f"获取进程 {pid} 详情失败: {str(e)}")
            return None


class NetworkMonitorService(QObject):
    """网络监控服务"""
    
    # 信号定义
    connections_updated = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._connections_cache = []
        self._last_update = 0
        self._cache_duration = 3.0  # 缓存持续时间（秒）
    
    def get_connections(self, force_refresh: bool = False) -> List[NetworkConnection]:
        """获取网络连接列表"""
        current_time = time.time()
        
        # 如果缓存有效且不强制刷新，返回缓存
        if not force_refresh and (current_time - self._last_update) < self._cache_duration:
            return self._connections_cache
        
        try:
            connections = []
            
            # 获取所有网络连接
            for conn in psutil.net_connections(kind='inet'):
                try:
                    # 格式化地址
                    local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    
                    # 协议类型
                    protocol = "TCP" if conn.type == 1 else "UDP"
                    
                    # 连接状态
                    status = conn.status if conn.status else "N/A"
                    
                    connection_info = NetworkConnection(
                        protocol=protocol,
                        local_addr=local_addr,
                        remote_addr=remote_addr,
                        status=status,
                        pid=conn.pid
                    )
                    
                    connections.append(connection_info)
                    
                except Exception:
                    continue
            
            # 更新缓存
            self._connections_cache = connections
            self._last_update = current_time
            
            self.connections_updated.emit(connections)
            return connections
            
        except Exception as e:
            self.error_occurred.emit(f"获取网络连接失败: {str(e)}")
            return []


class HardwareInfoService(QObject):
    """硬件信息服务"""
    
    # 信号定义
    hardware_info_updated = Signal(dict)
    error_occurred = Signal(str)
    
    def get_hardware_info(self) -> Dict:
        """获取硬件信息"""
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
            
            self.hardware_info_updated.emit(hardware_info)
            return hardware_info
            
        except Exception as e:
            self.error_occurred.emit(f"获取硬件信息失败: {str(e)}")
            return {}


# 工具函数
def format_bytes(bytes_value: int) -> str:
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_frequency(freq_mhz: float) -> str:
    """格式化频率"""
    if freq_mhz >= 1000:
        return f"{freq_mhz / 1000:.2f} GHz"
    else:
        return f"{freq_mhz:.0f} MHz"
