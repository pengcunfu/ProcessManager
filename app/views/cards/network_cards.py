#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络监控相关卡片组件
"""

from typing import List
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Signal

from app.models import NetworkConnection
from app.views.ui_utils import StyledTableWidget, StyledButton, StyledGroupBox


class NetworkTableCard(StyledGroupBox):
    """网络连接表格卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("网络连接", parent)
        self.current_connections = []
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 控制栏
        control_layout = QHBoxLayout()

        # 协议过滤
        control_layout.addWidget(QLabel("协议:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["全部", "TCP", "UDP"])
        self.protocol_combo.setFixedWidth(100)
        self.protocol_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.protocol_combo)

        # 状态过滤
        control_layout.addWidget(QLabel("状态:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "LISTEN", "ESTABLISHED", "TIME_WAIT"])
        self.status_combo.setFixedWidth(120)
        self.status_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.status_combo)

        control_layout.addStretch()

        # 刷新按钮
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        control_layout.addWidget(refresh_btn)

        layout.addLayout(control_layout)

        # 网络连接表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "协议", "本地地址", "远程地址", "状态", "PID"
        ])

        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # 统计信息
        self.stats_label = QLabel("连接数: 0")
        layout.addWidget(self.stats_label)

    def update_connections(self, connections: List[NetworkConnection]):
        """更新网络连接列表"""
        self.current_connections = connections
        self._apply_filters()
        self.stats_label.setText(f"连接数: {len(connections)}")

    def _apply_filters(self):
        """应用过滤器"""
        filtered_connections = self.current_connections

        # 协议过滤
        protocol_filter = self.protocol_combo.currentText()
        if protocol_filter != "全部":
            filtered_connections = [
                c for c in filtered_connections
                if c.protocol == protocol_filter
            ]

        # 状态过滤
        status_filter = self.status_combo.currentText()
        if status_filter != "全部":
            filtered_connections = [
                c for c in filtered_connections
                if c.status == status_filter
            ]

        # 更新表格
        self.table.setRowCount(len(filtered_connections))

        for row, conn in enumerate(filtered_connections):
            self.table.setItem(row, 0, QTableWidgetItem(conn.protocol))
            self.table.setItem(row, 1, QTableWidgetItem(conn.local_addr))
            self.table.setItem(row, 2, QTableWidgetItem(conn.remote_addr))
            self.table.setItem(row, 3, QTableWidgetItem(conn.status))
            self.table.setItem(row, 4, QTableWidgetItem(str(conn.pid) if conn.pid else "N/A"))

    def _on_filter_changed(self):
        """过滤器改变"""
        self._apply_filters()
