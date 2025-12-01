#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络监控控制器
负责网络连接信息的获取
"""

import psutil
import time
from typing import List
from PySide6.QtCore import QObject, Signal

from app.models import NetworkConnection


class NetworkController(QObject):
    """网络监控控制器"""
    
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
            max_connections = 500  # 限制最大连接数
            
            # 获取所有网络连接
            try:
                all_conns = psutil.net_connections(kind='inet')
            except psutil.AccessDenied:
                self.error_occurred.emit("权限不足，无法获取网络连接信息")
                return self._connections_cache if self._connections_cache else []
            
            for idx, conn in enumerate(all_conns):
                if idx >= max_connections:
                    break
                    
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
            return self._connections_cache if self._connections_cache else []

