#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控控制器
负责系统信息的获取和更新
"""

import psutil
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer

from app.models import SystemInfo


class SystemMonitorController(QObject):
    """系统监控控制器"""
    
    # 信号定义
    system_info_updated = Signal(SystemInfo)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.update_interval = 2.0  # 更新间隔（秒）
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_system_info)
        self._cpu_initialized = False  # CPU监控是否已初始化
    
    def start_monitoring(self):
        """开始监控"""
        if not self.is_running:
            self.is_running = True
            # 异步初始化CPU监控
            if not self._cpu_initialized:
                QTimer.singleShot(0, self._init_cpu_monitoring)
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
    
    def _init_cpu_monitoring(self):
        """初始化CPU监控（在后台异步执行）"""
        try:
            psutil.cpu_percent()  # 初始化CPU监控
            self._cpu_initialized = True
        except Exception as e:
            print(f"初始化CPU监控失败: {e}")
    
    def _update_system_info(self):
        """更新系统信息"""
        try:
            # CPU信息（不阻塞，使用缓存值）
            cpu_percent = psutil.cpu_percent(interval=0)
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

