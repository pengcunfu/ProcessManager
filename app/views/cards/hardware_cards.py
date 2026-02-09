#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件信息相关卡片组件
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QDialog, QTabWidget, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal

from app.models import format_bytes, format_frequency
from app.views.ui_utils import StyledButton, StyledGroupBox


class HardwareInfoCard(StyledGroupBox):
    """硬件信息卡片"""

    refresh_requested = Signal()
    detail_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("硬件信息", parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 刷新按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        detail_btn = StyledButton("查看详情", StyledButton.PRIMARY)
        detail_btn.clicked.connect(self.detail_requested.emit)
        button_layout.addWidget(detail_btn)
        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        # 硬件信息文本区域
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        layout.addWidget(self.info_text)

    def update_hardware_info(self, hardware_info: dict):
        """更新硬件信息显示"""
        info_lines = []

        try:
            # CPU信息
            if 'cpu' in hardware_info:
                cpu_info = hardware_info['cpu']
                info_lines.append("=== CPU信息 ===")
                info_lines.append(f"物理核心数: {cpu_info.get('physical_cores', 'N/A')}")
                info_lines.append(f"逻辑核心数: {cpu_info.get('logical_cores', 'N/A')}")

                if cpu_info.get('frequency'):
                    freq = cpu_info['frequency']
                    info_lines.append(f"当前频率: {format_frequency(freq.get('current', 0))}")
                    info_lines.append(f"最大频率: {format_frequency(freq.get('max', 0))}")
                    info_lines.append(f"最小频率: {format_frequency(freq.get('min', 0))}")

                info_lines.append(f"处理器: {cpu_info.get('processor', 'N/A')}")
                info_lines.append("")

            # 内存信息
            if 'memory' in hardware_info:
                mem_info = hardware_info['memory']
                info_lines.append("=== 内存信息 ===")
                info_lines.append(f"总内存: {format_bytes(mem_info.get('total', 0))}")
                info_lines.append(f"可用内存: {format_bytes(mem_info.get('available', 0))}")
                info_lines.append(f"已使用内存: {format_bytes(mem_info.get('used', 0))}")
                info_lines.append(f"内存使用率: {mem_info.get('percent', 0):.1f}%")
                info_lines.append(f"交换内存总量: {format_bytes(mem_info.get('swap_total', 0))}")
                info_lines.append(f"交换内存使用: {format_bytes(mem_info.get('swap_used', 0))}")
                info_lines.append("")

            # 磁盘信息
            if 'disks' in hardware_info:
                info_lines.append("=== 磁盘信息 ===")
                for disk in hardware_info['disks']:
                    info_lines.append(f"设备: {disk.get('device', 'N/A')}")
                    info_lines.append(f"挂载点: {disk.get('mountpoint', 'N/A')}")
                    info_lines.append(f"文件系统: {disk.get('fstype', 'N/A')}")

                    if 'error' in disk:
                        info_lines.append(f"  {disk['error']}")
                    else:
                        info_lines.append(f"  总空间: {format_bytes(disk.get('total', 0))}")
                        info_lines.append(f"  已使用: {format_bytes(disk.get('used', 0))}")
                        info_lines.append(f"  可用空间: {format_bytes(disk.get('free', 0))}")
                        info_lines.append(f"  使用率: {disk.get('percent', 0):.1f}%")
                    info_lines.append("")

            # 网络接口信息
            if 'network_interfaces' in hardware_info:
                info_lines.append("=== 网络接口 ===")
                for interface_name, addresses in hardware_info['network_interfaces'].items():
                    info_lines.append(f"接口: {interface_name}")
                    for addr in addresses:
                        if 'AF_INET' in addr['family']:
                            info_lines.append(f"  IP地址: {addr['address']}")
                            if addr['netmask']:
                                info_lines.append(f"  子网掩码: {addr['netmask']}")
                        elif 'AF_PACKET' in addr['family'] or 'AF_LINK' in addr['family']:
                            info_lines.append(f"  MAC地址: {addr['address']}")
                    info_lines.append("")

        except Exception as e:
            info_lines.append(f"显示硬件信息时出错: {e}")

        self.info_text.setPlainText("\n".join(info_lines))


class HardwareInfoDialog(QDialog):
    """硬件信息对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("硬件信息")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # CPU信息标签页
        self.cpu_text = self.create_tab("CPU信息", "cpu")
        # 内存信息标签页
        self.memory_text = self.create_tab("内存信息", "memory")
        # 磁盘信息标签页
        self.disk_text = self.create_tab("磁盘信息", "disk")
        # 网络接口标签页
        self.network_text = self.create_tab("网络接口", "network")

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = StyledButton("刷新", StyledButton.PRIMARY)
        refresh_btn.clicked.connect(self.refresh_info)
        button_layout.addWidget(refresh_btn)

        close_btn = StyledButton("关闭", StyledButton.PRIMARY)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def create_tab(self, title, key):
        """创建标签页"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        scroll_area.setWidget(text_edit)
        self.tab_widget.addTab(scroll_area, title)

        return text_edit

    def update_hardware_info(self, hardware_info: dict):
        """更新硬件信息显示"""

        # 更新CPU信息
        self.update_cpu_info(hardware_info.get('cpu', {}))

        # 更新内存信息
        self.update_memory_info(hardware_info.get('memory', {}))

        # 更新磁盘信息
        self.update_disk_info(hardware_info.get('disks', []))

        # 更新网络接口信息
        self.update_network_info(hardware_info.get('network_interfaces', {}))

    def update_cpu_info(self, cpu_info: dict):
        """更新CPU信息"""
        info_lines = []

        try:
            info_lines.append("<h2>CPU 处理器信息</h2>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

            if cpu_info.get('processor'):
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>处理器型号</b></td><td>{cpu_info['processor']}</td></tr>")

            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>物理核心数</b></td><td>{cpu_info.get('physical_cores', 'N/A')}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>逻辑核心数</b></td><td>{cpu_info.get('logical_cores', 'N/A')}</td></tr>")

            if cpu_info.get('frequency'):
                freq = cpu_info['frequency']
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>当前频率</b></td><td>{format_frequency(freq.get('current', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最大频率</b></td><td>{format_frequency(freq.get('max', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最小频率</b></td><td>{format_frequency(freq.get('min', 0))}</td></tr>")

            info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示CPU信息时出错: {e}</p>")

        self.cpu_text.setHtml("".join(info_lines))

    def update_memory_info(self, mem_info: dict):
        """更新内存信息"""
        info_lines = []

        try:
            info_lines.append("<h2>内存信息</h2>")

            # 物理内存
            info_lines.append("<h3>物理内存</h3>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>总内存</b></td><td>{format_bytes(mem_info.get('total', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>可用内存</b></td><td>{format_bytes(mem_info.get('available', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用内存</b></td><td>{format_bytes(mem_info.get('used', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>内存使用率</b></td><td>{mem_info.get('percent', 0):.1f}%</td></tr>")
            info_lines.append("</table>")

            # 交换内存
            info_lines.append("<h3>交换内存</h3>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>交换内存总量</b></td><td>{format_bytes(mem_info.get('swap_total', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用交换内存</b></td><td>{format_bytes(mem_info.get('swap_used', 0))}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>空闲交换内存</b></td><td>{format_bytes(mem_info.get('swap_free', 0))}</td></tr>")
            info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示内存信息时出错: {e}</p>")

        self.memory_text.setHtml("".join(info_lines))

    def update_disk_info(self, disks: list):
        """更新磁盘信息"""
        info_lines = []

        try:
            info_lines.append("<h2>磁盘信息</h2>")

            for idx, disk in enumerate(disks, 1):
                info_lines.append(f"<h3>磁盘 {idx}</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>设备</b></td><td>{disk.get('device', 'N/A')}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>挂载点</b></td><td>{disk.get('mountpoint', 'N/A')}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>文件系统类型</b></td><td>{disk.get('fstype', 'N/A')}</td></tr>")

                if 'error' in disk:
                    info_lines.append(f"<tr><td colspan='2' style='color: red;'>{disk['error']}</td></tr>")
                else:
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>总空间</b></td><td>{format_bytes(disk.get('total', 0))}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用</b></td><td>{format_bytes(disk.get('used', 0))}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>可用空间</b></td><td>{format_bytes(disk.get('free', 0))}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>使用率</b></td><td>{disk.get('percent', 0):.1f}%</td></tr>")

                info_lines.append("</table><br>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示磁盘信息时出错: {e}</p>")

        self.disk_text.setHtml("".join(info_lines))

    def update_network_info(self, interfaces: dict):
        """更新网络接口信息"""
        info_lines = []

        try:
            info_lines.append("<h2>网络接口信息</h2>")

            for idx, (interface_name, addresses) in enumerate(interfaces.items(), 1):
                info_lines.append(f"<h3>{interface_name}</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                for addr in addresses:
                    if 'AF_INET' in addr['family']:
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>IP地址</b></td><td>{addr['address']}</td></tr>")
                        if addr.get('netmask'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>子网掩码</b></td><td>{addr['netmask']}</td></tr>")
                        if addr.get('broadcast'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>广播地址</b></td><td>{addr['broadcast']}</td></tr>")
                    elif 'AF_INET6' in addr['family']:
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>IPv6地址</b></td><td>{addr['address']}</td></tr>")
                    elif 'AF_PACKET' in addr['family'] or 'AF_LINK' in addr['family']:
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>MAC地址</b></td><td>{addr['address']}</td></tr>")

                info_lines.append("</table><br>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示网络信息时出错: {e}</p>")

        self.network_text.setHtml("".join(info_lines))

    def refresh_info(self):
        """刷新硬件信息（由主窗口调用）"""
        # 这个方法会被主窗口重写或者通过信号连接
        pass
