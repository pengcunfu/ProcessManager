#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程管理控制器
负责进程信息的获取和管理
"""

import psutil
import time
from datetime import datetime
from typing import List, Optional, Dict
from PySide6.QtCore import QObject, Signal

from app.models import ProcessInfo
from app.utils.async_worker import AsyncWorkerManager


class ProcessController(QObject):
    """进程管理控制器"""

    # 信号定义
    processes_updated = Signal(list)
    process_killed = Signal(int, str)  # pid, message
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._processes_cache = []
        self._last_update = 0
        self._cache_duration = 2.0  # 缓存持续时间（秒）
        self.worker_manager = AsyncWorkerManager(self)

    def get_processes(self, force_refresh: bool = False):
        """
        获取进程列表（异步执行）

        Args:
            force_refresh: 是否强制刷新，忽略缓存
        """
        # 检查缓存
        current_time = time.time()
        if not force_refresh and (current_time - self._last_update) < self._cache_duration:
            self.processes_updated.emit(self._processes_cache)
            return

        # 异步获取进程列表
        self.worker_manager.execute(
            name='get_processes',
            target_func=self._fetch_processes,
            callback=self._on_processes_fetched,
            error_callback=lambda e: self.error_occurred.emit(f"获取进程列表失败: {e}")
        )

    def _fetch_processes(self) -> List[ProcessInfo]:
        """
        实际获取进程列表的函数（在后台线程执行）

        Returns:
            进程信息列表
        """
        processes = []

        # 限制获取的进程数量，避免性能问题
        max_processes = 200
        process_count = 0

        # 一次性获取所有需要的属性，减少系统调用
        attrs = ['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time']

        for proc in psutil.process_iter(attrs):
            if process_count >= max_processes:
                break

            try:
                # 创建进程信息对象
                process_info = ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info['name'],
                    cpu_percent=proc.info['cpu_percent'] or 0,
                    memory_percent=proc.info['memory_percent'] or 0,
                    memory_mb=proc.info['memory_info'].rss / (1024 * 1024) if proc.info['memory_info'] else 0,
                    status=proc.info['status'],
                    create_time=datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S') if proc.info['create_time'] else 'N/A'
                )
                processes.append(process_info)
                process_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # 按CPU使用率排序
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)

        # 更新缓存
        self._processes_cache = processes
        self._last_update = time.time()

        return processes

    def _on_processes_fetched(self, processes: List[ProcessInfo]):
        """进程列表获取完成回调"""
        self.processes_updated.emit(processes)

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
