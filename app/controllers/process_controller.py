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
    
    def get_processes(self, force_refresh: bool = False) -> List[ProcessInfo]:
        """获取进程列表"""
        current_time = time.time()
        
        # 如果缓存有效且不强制刷新，返回缓存
        if not force_refresh and (current_time - self._last_update) < self._cache_duration:
            return self._processes_cache
        
        try:
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
                    info = proc.info
                    
                    # 获取内存使用量（MB）
                    memory_mb = 0
                    if info.get('memory_info'):
                        memory_mb = info['memory_info'].rss / 1024 / 1024
                    
                    # 获取创建时间
                    create_time = "未知"
                    if info.get('create_time'):
                        try:
                            create_time = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    # 创建进程信息对象
                    process_info = ProcessInfo(
                        pid=info.get('pid', 0),
                        name=info.get('name', 'Unknown'),
                        cpu_percent=info.get('cpu_percent', 0) or 0,
                        memory_percent=info.get('memory_percent', 0) or 0,
                        memory_mb=memory_mb,
                        status=info.get('status', 'Unknown'),
                        create_time=create_time,
                        exe_path="",  # 延迟加载
                        num_threads=0,  # 延迟加载
                        parent_pid=None  # 延迟加载
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

