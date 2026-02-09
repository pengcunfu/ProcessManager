#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步工作线程工具
提供QThread包装器，用于在后台线程执行耗时操作
"""

from PySide6.QtCore import QThread, Signal, QObject


class AsyncWorker(QThread):
    """异步工作线程"""

    # 定义信号
    finished = Signal(object)  # 完成信号，携带结果
    error = Signal(str)  # 错误信号

    def __init__(self, target_func, *args, **kwargs):
        """
        初始化异步工作线程

        Args:
            target_func: 要执行的目标函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__()
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs
        self._result = None

    def run(self):
        """执行目标函数"""
        try:
            self._result = self.target_func(*self.args, **self.kwargs)
            self.finished.emit(self._result)
        except Exception as e:
            self.error.emit(str(e))

    def get_result(self):
        """获取执行结果"""
        return self._result


class AsyncWorkerManager(QObject):
    """异步工作线程管理器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers = {}

    def execute(self, name, target_func, callback=None, error_callback=None, *args, **kwargs):
        """
        执行异步任务

        Args:
            name: 任务名称（用于管理）
            target_func: 要执行的函数
            callback: 完成回调函数
            error_callback: 错误回调函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        # 如果已有同名任务在运行，先停止
        if name in self._workers and self._workers[name].isRunning():
            self._workers[name].terminate()
            self._workers[name].wait()

        # 创建新的工作线程
        worker = AsyncWorker(target_func, *args, **kwargs)

        # 连接信号
        if callback:
            worker.finished.connect(callback)
        if error_callback:
            worker.error.connect(error_callback)

        # 保存引用
        self._workers[name] = worker

        # 启动线程
        worker.start()

        return worker

    def stop(self, name):
        """停止指定任务"""
        if name in self._workers:
            worker = self._workers[name]
            if worker.isRunning():
                worker.terminate()
                worker.wait()
            del self._workers[name]

    def stop_all(self):
        """停止所有任务"""
        for name in list(self._workers.keys()):
            self.stop(name)
