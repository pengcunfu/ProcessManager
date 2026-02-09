#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流量监控相关卡片组件
"""

from typing import List
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal

from app.models import format_bytes
from app.controllers.traffic_controller import ProcessTrafficInfo
from app.views.ui_utils import StyledTableWidget, StyledButton, StyledGroupBox


class TrafficMonitorCard(StyledGroupBox):
    """网络流量监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("实时流量监控", parent)
        self.setFixedHeight(220)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 实时速率显示
        speed_layout = QHBoxLayout()

        # 上传速度
        upload_box = QVBoxLayout()
        upload_label = QLabel("上传速度")
        upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upload_speed = QLabel("0 B/s")
        self.upload_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_box.addWidget(upload_label)
        upload_box.addWidget(self.upload_speed)

        # 下载速度
        download_box = QVBoxLayout()
        download_label = QLabel("下载速度")
        download_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_speed = QLabel("0 B/s")
        self.download_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        download_box.addWidget(download_label)
        download_box.addWidget(self.download_speed)

        speed_layout.addLayout(upload_box)
        speed_layout.addLayout(download_box)
        layout.addLayout(speed_layout)

        # 分隔线
        line = QLabel()
        line.setFrameStyle(QLabel.Shape.HLine | QLabel.Shadow.Sunken)
        layout.addWidget(line)

        # 总流量统计
        stats_layout = QGridLayout()

        stats_layout.addWidget(QLabel("总上传:"), 0, 0)
        self.total_sent = QLabel("0 B")
        stats_layout.addWidget(self.total_sent, 0, 1)

        stats_layout.addWidget(QLabel("总下载:"), 0, 2)
        self.total_recv = QLabel("0 B")
        stats_layout.addWidget(self.total_recv, 0, 3)

        stats_layout.addWidget(QLabel("发送包:"), 1, 0)
        self.packets_sent = QLabel("0")
        stats_layout.addWidget(self.packets_sent, 1, 1)

        stats_layout.addWidget(QLabel("接收包:"), 1, 2)
        self.packets_recv = QLabel("0")
        stats_layout.addWidget(self.packets_recv, 1, 3)

        layout.addLayout(stats_layout)

    def update_traffic(self, traffic_data: dict):
        """更新流量信息"""
        # 更新实时速度
        upload_speed = traffic_data.get('upload_speed', 0)
        download_speed = traffic_data.get('download_speed', 0)

        self.upload_speed.setText(f"{format_bytes(int(upload_speed))}/s")
        self.download_speed.setText(f"{format_bytes(int(download_speed))}/s")

        # 更新总流量
        total_sent = traffic_data.get('total_sent', 0)
        total_recv = traffic_data.get('total_recv', 0)

        self.total_sent.setText(format_bytes(total_sent))
        self.total_recv.setText(format_bytes(total_recv))

        # 更新包统计
        packets_sent = traffic_data.get('packets_sent', 0)
        packets_recv = traffic_data.get('packets_recv', 0)

        self.packets_sent.setText(f"{packets_sent:,}")
        self.packets_recv.setText(f"{packets_recv:,}")


class ProcessTrafficCard(StyledGroupBox):
    """进程流量统计卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("进程流量统计", parent)
        self.current_traffic = []
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 控制栏
        control_layout = QHBoxLayout()

        info_label = QLabel("💡 提示: 需要管理员权限才能查看详细的进程流量")
        control_layout.addWidget(info_label)

        control_layout.addStretch()

        # 刷新按钮
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        control_layout.addWidget(refresh_btn)

        layout.addLayout(control_layout)

        # 进程流量表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "PID", "进程名", "连接数", "读取", "写入"
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

        layout.addWidget(self.table)

        # 统计信息
        self.stats_label = QLabel("进程数: 0")
        layout.addWidget(self.stats_label)

    def update_process_traffic(self, traffic_list: List[ProcessTrafficInfo]):
        """更新进程流量列表"""
        self.current_traffic = traffic_list

        # 只显示前50个（性能考虑）
        display_list = traffic_list[:50]

        self.table.setRowCount(len(display_list))

        for row, traffic in enumerate(display_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(traffic.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(traffic.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(traffic.connections_count)))
            self.table.setItem(row, 3, QTableWidgetItem(format_bytes(traffic.bytes_recv)))
            self.table.setItem(row, 4, QTableWidgetItem(format_bytes(traffic.bytes_sent)))

        self.stats_label.setText(f"显示进程: {len(display_list)} / 总计: {len(traffic_list)}")
