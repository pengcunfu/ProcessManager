#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络流量监控控制器
负责网络流量的监控和统计
"""

import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QTimer


@dataclass
class TrafficInfo:
    """流量信息数据类"""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


@dataclass
class ProcessTrafficInfo:
    """进程流量信息数据类"""
    pid: int
    name: str
    bytes_sent: int
    bytes_recv: int
    connections_count: int


class TrafficMonitorController(QObject):
    """网络流量监控控制器"""
    
    # 信号定义
    traffic_updated = Signal(dict)  # 总流量和速率信息
    process_traffic_updated = Signal(list)  # 进程流量信息列表
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_traffic)
        
        # 记录上一次的数值，用于计算速率
        self._last_bytes_sent = 0
        self._last_bytes_recv = 0
        self._last_update_time = time.time()
        
        # 初始化基准值
        net_io = psutil.net_io_counters()
        self._last_bytes_sent = net_io.bytes_sent
        self._last_bytes_recv = net_io.bytes_recv
    
    def start_monitoring(self, interval: int = 1000):
        """
        开始监控流量
        
        Args:
            interval: 更新间隔（毫秒），默认1秒
        """
        if not self.is_monitoring:
            self.is_monitoring = True
            self._timer.start(interval)
    
    def stop_monitoring(self):
        """停止监控流量"""
        if self.is_monitoring:
            self.is_monitoring = False
            self._timer.stop()
    
    def _update_traffic(self):
        """更新流量信息"""
        try:
            # 获取总流量
            net_io = psutil.net_io_counters()
            current_time = time.time()
            
            # 计算时间差
            time_delta = current_time - self._last_update_time
            
            # 计算流量差值
            sent_delta = net_io.bytes_sent - self._last_bytes_sent
            recv_delta = net_io.bytes_recv - self._last_bytes_recv
            
            # 计算速率（字节/秒）
            upload_speed = sent_delta / time_delta if time_delta > 0 else 0
            download_speed = recv_delta / time_delta if time_delta > 0 else 0
            
            # 更新记录
            self._last_bytes_sent = net_io.bytes_sent
            self._last_bytes_recv = net_io.bytes_recv
            self._last_update_time = current_time
            
            # 构建流量信息
            traffic_data = {
                'total_sent': net_io.bytes_sent,
                'total_recv': net_io.bytes_recv,
                'upload_speed': upload_speed,
                'download_speed': download_speed,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            self.traffic_updated.emit(traffic_data)
            
        except Exception as e:
            self.error_occurred.emit(f"更新流量信息失败: {str(e)}")
    
    def get_process_traffic(self) -> List[ProcessTrafficInfo]:
        """
        获取每个进程的流量信息
        注意：需要管理员权限才能获取进程的网络连接信息
        """
        try:
            process_traffic = {}
            
            # 获取所有网络连接
            try:
                connections = psutil.net_connections(kind='inet')
            except psutil.AccessDenied:
                self.error_occurred.emit("需要管理员权限才能获取进程流量信息")
                return []
            
            # 统计每个进程的连接数
            for conn in connections:
                if conn.pid:
                    if conn.pid not in process_traffic:
                        try:
                            proc = psutil.Process(conn.pid)
                            process_traffic[conn.pid] = {
                                'name': proc.name(),
                                'connections': 0,
                                'sent': 0,
                                'recv': 0
                            }
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    
                    process_traffic[conn.pid]['connections'] += 1
            
            # 尝试获取每个进程的IO信息
            # 注意：Windows上可能无法获取准确的网络IO
            for pid, data in process_traffic.items():
                try:
                    proc = psutil.Process(pid)
                    io_counters = proc.io_counters()
                    # 注意：这是所有IO，不仅仅是网络IO
                    data['sent'] = io_counters.write_bytes
                    data['recv'] = io_counters.read_bytes
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    pass
            
            # 转换为列表
            result = []
            for pid, data in process_traffic.items():
                result.append(ProcessTrafficInfo(
                    pid=pid,
                    name=data['name'],
                    bytes_sent=data['sent'],
                    bytes_recv=data['recv'],
                    connections_count=data['connections']
                ))
            
            # 按连接数排序
            result.sort(key=lambda x: x.connections_count, reverse=True)
            
            self.process_traffic_updated.emit(result)
            return result
            
        except Exception as e:
            self.error_occurred.emit(f"获取进程流量失败: {str(e)}")
            return []

