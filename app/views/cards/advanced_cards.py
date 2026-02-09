#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级监控相关卡片组件
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QTableWidget, QTableWidgetItem, QProgressBar, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush

from app.views.ui_utils import StyledTableWidget, StyledButton, StyledGroupBox


class TemperatureMonitorCard(StyledGroupBox):
    """温度监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("温度监控", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 温度信息显示
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(300)
        layout.addWidget(self.info_text)

    def update_temperature(self, temp_info: dict):
        """更新温度信息"""
        info_lines = []

        try:
            if 'error' in temp_info:
                info_lines.append(f"<p style='color: red;'>{temp_info['error']}</p>")
            else:
                for sensor_name, temps in temp_info.items():
                    info_lines.append(f"<h3 style='color: #E65100;'>{sensor_name}</h3>")
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%; border: 1px solid #FFB74D;'>")

                    for temp in temps:
                        label = temp.get('label', 'N/A')
                        current = temp.get('current', 0)
                        high = temp.get('high')
                        critical = temp.get('critical')

                        # 根据温度设置颜色
                        if critical and current >= critical:
                            bg_color = "#FFCDD2"
                            text_color = "#B71C1C"
                        elif high and current >= high:
                            bg_color = "#FFE0B2"
                            text_color = "#E65100"
                        else:
                            bg_color = "#FFF3E0"
                            text_color = "#BF360C"

                        info_lines.append(f"<tr><td style='width: 40%; background-color: {bg_color}; color: {text_color}; font-weight: bold; padding: 8px;'>{label}</td><td style='padding: 8px; background-color: #FFF8E1;'>{current:.1f}°C")

                        if high:
                            info_lines.append(f" <span style='color: #FF9800;'>(警告: {high:.1f}°C)</span>")
                        if critical:
                            info_lines.append(f" <span style='color: #F44336;'>(严重: {critical:.1f}°C)</span>")

                        info_lines.append("</td></tr>")

                    info_lines.append("</table>")

            self.info_text.setHtml("".join(info_lines))

        except Exception as e:
            self.info_text.setHtml(f"<p style='color: red;'>显示温度信息时出错: {e}</p>")


class BatteryMonitorCard(StyledGroupBox):
    """电池监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("电池监控", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 电池信息显示
        self.info_label = QLabel("正在获取电池信息...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # 进度条
        self.battery_bar = QProgressBar()
        self.battery_bar.setMinimum(0)
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        layout.addWidget(self.battery_bar)

    def update_battery(self, battery_info: dict):
        """更新电池信息"""
        try:
            if 'error' in battery_info:
                self.info_label.setText(f"<p style='color: red;'>{battery_info['error']}</p>")
                self.battery_bar.setValue(0)
                return

            percent = battery_info.get('percent', 0)
            status = battery_info.get('status', '未知')
            time_left = battery_info.get('time_left_formatted', '')

            # 更新进度条
            self.battery_bar.setValue(int(percent))

            # 根据电量设置颜色
            if percent <= 20:
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
            elif percent <= 50:
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }")
            else:
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")

            # 更新文本
            info_text = f"<h2 style='text-align: center; color: #1976D2;'>{percent:.0f}%</h2>"
            info_text += f"<p style='text-align: center; font-size: 14px;'>"
            info_text += f"状态: <b>{status}</b><br>"
            if time_left:
                info_text += f"剩余时间: <b>{time_left}</b>"
            info_text += "</p>"

            self.info_label.setText(info_text)

        except Exception as e:
            self.info_label.setText(f"<p style='color: red;'>显示电池信息时出错: {e}</p>")


class ServicesMonitorCard(StyledGroupBox):
    """系统服务监控卡片"""

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("系统服务", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 服务表格
        self.table = StyledTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["服务名称", "显示名称", "状态"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def update_services(self, services: list):
        """更新服务列表"""
        try:
            if services and 'error' in services[0]:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem(services[0]['error']))
                self.table.setSpan(0, 0, 1, 3)
                return

            self.table.setRowCount(len(services))

            for row, service in enumerate(services):
                self.table.setItem(row, 0, QTableWidgetItem(service.get('name', 'N/A')))
                self.table.setItem(row, 1, QTableWidgetItem(service.get('display_name', 'N/A')))

                status_item = QTableWidgetItem(service.get('status', 'N/A'))

                # 根据状态设置颜色
                status = service.get('status', '')
                if '运行' in status:
                    status_item.setForeground(QBrush(Qt.GlobalColor.darkGreen))
                elif '停止' in status:
                    status_item.setForeground(QBrush(Qt.GlobalColor.red))

                self.table.setItem(row, 2, status_item)

            self.table.resizeColumnsToContents()

        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"显示服务信息时出错: {e}"))
            self.table.setSpan(0, 0, 1, 3)
