#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统数据模型
定义系统监控相关的数据结构
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SystemInfo:
    """系统信息数据模型"""
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
    """进程信息数据模型"""
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
    """网络连接信息数据模型"""
    protocol: str
    local_addr: str
    remote_addr: str
    status: str
    pid: Optional[int]

