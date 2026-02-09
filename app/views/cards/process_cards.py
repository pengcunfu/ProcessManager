#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程管理相关卡片组件
"""

from typing import List
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Signal

from app.models import ProcessInfo
from app.views.ui_utils import StyledTableWidget, StyledButton, StyledGroupBox


class ProcessTableCard(StyledGroupBox):
    """进程表格卡片"""

    # 信号定义
    refresh_requested = Signal()
    kill_requested = Signal(int, bool)  # pid, force

    def __init__(self, parent=None):
        super().__init__("进程管理", parent)
        self.current_processes = []
        self.filtered_processes = []
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 控制栏
        control_layout = QHBoxLayout()

        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索进程...")
        self.search_box.setFixedWidth(200)
        self.search_box.textChanged.connect(self._on_search_changed)
        control_layout.addWidget(self.search_box)

        # 排序选择
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["CPU使用率", "内存使用率", "进程名", "PID"])
        self.sort_combo.setFixedWidth(120)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        control_layout.addWidget(self.sort_combo)

        control_layout.addStretch()

        # 刷新按钮
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        control_layout.addWidget(refresh_btn)

        layout.addLayout(control_layout)

        # 进程表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "PID", "进程名", "CPU%", "内存%", "内存(MB)", "状态"
        ])

        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)

        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # 选择变化
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

        # 操作按钮栏
        button_layout = QHBoxLayout()

        self.kill_btn = StyledButton("结束进程", StyledButton.PRIMARY)
        self.kill_btn.clicked.connect(self._on_kill_clicked)
        self.kill_btn.setEnabled(False)

        self.force_kill_btn = StyledButton("强制结束", StyledButton.DANGER)
        self.force_kill_btn.clicked.connect(self._on_force_kill_clicked)
        self.force_kill_btn.setEnabled(False)

        self.details_btn = StyledButton("详细信息", StyledButton.PRIMARY)
        self.details_btn.clicked.connect(self._on_details_clicked)
        self.details_btn.setEnabled(False)

        button_layout.addWidget(self.kill_btn)
        button_layout.addWidget(self.force_kill_btn)
        button_layout.addWidget(self.details_btn)
        button_layout.addStretch()

        # 进程统计标签
        self.stats_label = QLabel("进程数: 0")
        button_layout.addWidget(self.stats_label)

        layout.addLayout(button_layout)

    def update_processes(self, processes: List[ProcessInfo]):
        """更新进程列表"""
        self.current_processes = processes
        self._apply_filter_and_sort()
        self.stats_label.setText(f"进程数: {len(processes)}")

    def _apply_filter_and_sort(self):
        """应用过滤和排序"""
        # 过滤
        search_text = self.search_box.text().lower()
        if search_text:
            self.filtered_processes = [
                p for p in self.current_processes
                if search_text in p.name.lower()
            ]
        else:
            self.filtered_processes = self.current_processes.copy()

        # 排序
        sort_key_map = {
            "CPU使用率": lambda x: x.cpu_percent,
            "内存使用率": lambda x: x.memory_percent,
            "进程名": lambda x: x.name.lower(),
            "PID": lambda x: x.pid
        }

        sort_key = sort_key_map.get(self.sort_combo.currentText(), lambda x: x.cpu_percent)
        reverse = self.sort_combo.currentText() in ["CPU使用率", "内存使用率"]
        self.filtered_processes.sort(key=sort_key, reverse=reverse)

        # 更新表格
        self.table.setRowCount(len(self.filtered_processes))

        for row, proc in enumerate(self.filtered_processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(proc.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(proc.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{proc.cpu_percent:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{proc.memory_percent:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{proc.memory_mb:.1f}"))
            self.table.setItem(row, 5, QTableWidgetItem(proc.status))

    def _on_search_changed(self):
        """搜索文本改变"""
        self._apply_filter_and_sort()

    def _on_sort_changed(self):
        """排序方式改变"""
        self._apply_filter_and_sort()

    def _on_selection_changed(self):
        """选择改变"""
        has_selection = len(self.table.selectedItems()) > 0
        self.kill_btn.setEnabled(has_selection)
        self.force_kill_btn.setEnabled(has_selection)
        self.details_btn.setEnabled(has_selection)

    def _on_kill_clicked(self):
        """结束进程"""
        self._kill_process(force=False)

    def _on_force_kill_clicked(self):
        """强制结束进程"""
        self._kill_process(force=True)

    def _kill_process(self, force: bool):
        """结束进程"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            pid_item = self.table.item(current_row, 0)
            name_item = self.table.item(current_row, 1)

            if pid_item and name_item:
                pid = int(pid_item.text())
                name = name_item.text()

                action_text = "强制结束" if force else "结束"
                reply = QMessageBox.question(
                    self, "确认操作",
                    f"确定要{action_text}进程 {name} (PID: {pid}) 吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.kill_requested.emit(pid, force)

    def _on_details_clicked(self):
        """显示进程详情"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_processes):
            process = self.filtered_processes[current_row]
            self._show_process_details(process)

    def _show_process_details(self, process: ProcessInfo):
        """显示进程详细信息"""
        details = f"""进程详细信息:

PID: {process.pid}
进程名称: {process.name}
状态: {process.status}
创建时间: {process.create_time}
CPU使用率: {process.cpu_percent:.1f}%
内存使用率: {process.memory_percent:.2f}%
内存使用量: {process.memory_mb:.2f} MB
"""

        QMessageBox.information(self, "进程详情", details)
