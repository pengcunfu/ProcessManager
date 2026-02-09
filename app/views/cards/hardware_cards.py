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

                info_lines.append(f"处理器: {cpu_info.get('processor', 'N/A')}")
                info_lines.append("")

            # 显卡信息
            if 'gpus' in hardware_info:
                info_lines.append("=== 显卡信息 ===")
                gpus = hardware_info['gpus']
                if gpus and 'message' not in gpus[0]:
                    for gpu in gpus:
                        if 'error' in gpu:
                            info_lines.append(f"错误: {gpu['error']}")
                        else:
                            info_lines.append(f"显卡: {gpu.get('name', 'N/A')}")
                            info_lines.append(f"类型: {gpu.get('type', 'N/A')}")
                            if gpu.get('memory_total'):
                                info_lines.append(f"显存: {format_bytes(gpu.get('memory_total', 0))}")
                            if gpu.get('temperature'):
                                info_lines.append(f"温度: {gpu.get('temperature', 0)}°C")
                            if gpu.get('fan_speed'):
                                info_lines.append(f"风扇转速: {gpu.get('fan_speed', 0)}%")
                            if gpu.get('power_usage'):
                                info_lines.append(f"功耗: {gpu.get('power_usage', 0):.1f}W / {gpu.get('power_limit', 0):.1f}W")
                else:
                    info_lines.append(gpus[0].get('message', '未检测到显卡'))
                info_lines.append("")

            # 主板信息
            if 'motherboard' in hardware_info:
                info_lines.append("=== 主板信息 ===")
                mb = hardware_info['motherboard']
                if 'error' in mb:
                    info_lines.append(f"错误: {mb['error']}")
                else:
                    if mb.get('manufacturer'):
                        info_lines.append(f"制造商: {mb.get('manufacturer', 'N/A')}")
                    if mb.get('model'):
                        info_lines.append(f"型号: {mb.get('model', 'N/A')}")
                    if mb.get('bios_vendor'):
                        info_lines.append(f"BIOS: {mb.get('bios_vendor', 'N/A')} {mb.get('bios_version', 'N/A')}")
                info_lines.append("")

            # 温度信息
            if 'temperatures' in hardware_info:
                info_lines.append("=== 温度传感器 ===")
                temps = hardware_info['temperatures']
                if temps and 'message' not in temps:
                    for sensor_name, sensor_list in temps.items():
                        for sensor in sensor_list:
                            label = sensor.get('label', sensor_name)
                            current = sensor.get('current', 0)
                            info_lines.append(f"{label}: {current:.1f}°C")
                else:
                    info_lines.append(temps.get('message', '未检测到温度传感器'))
                info_lines.append("")

            # 风扇信息
            if 'fans' in hardware_info:
                info_lines.append("=== 风扇信息 ===")
                fans = hardware_info['fans']
                if fans and 'message' not in fans:
                    for fan_name, fan_list in fans.items():
                        for fan in fan_list:
                            label = fan.get('label', fan_name)
                            rpm = fan.get('current_rpm', 0)
                            info_lines.append(f"{label}: {rpm} RPM")
                else:
                    info_lines.append(fans.get('message', '未检测到风扇'))
                info_lines.append("")

            # 内存信息
            if 'memory' in hardware_info:
                mem_info = hardware_info['memory']
                info_lines.append("=== 内存信息 ===")
                info_lines.append(f"总内存: {format_bytes(mem_info.get('total', 0))}")
                info_lines.append(f"可用内存: {format_bytes(mem_info.get('available', 0))}")
                info_lines.append(f"已使用: {format_bytes(mem_info.get('used', 0))}")
                info_lines.append(f"使用率: {mem_info.get('percent', 0):.1f}%")
                info_lines.append("")

            # 电池信息
            if 'battery' in hardware_info:
                battery = hardware_info['battery']
                if battery and 'message' not in battery:
                    info_lines.append("=== 电池信息 ===")
                    info_lines.append(f"电量: {battery.get('percent', 0)}%")
                    info_lines.append(f"状态: {battery.get('status', 'N/A')}")
                    if battery.get('time_left_formatted'):
                        info_lines.append(f"剩余时间: {battery.get('time_left_formatted', 'N/A')}")
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
        # 显卡信息标签页
        self.gpu_text = self.create_tab("显卡信息", "gpu")
        # 主板信息标签页
        self.motherboard_text = self.create_tab("主板信息", "motherboard")
        # 温度信息标签页
        self.temperature_text = self.create_tab("温度监控", "temperature")
        # 风扇信息标签页
        self.fan_text = self.create_tab("风扇信息", "fan")
        # 内存信息标签页
        self.memory_text = self.create_tab("内存信息", "memory")
        # 磁盘信息标签页
        self.disk_text = self.create_tab("磁盘信息", "disk")
        # 网络接口标签页
        self.network_text = self.create_tab("网络接口", "network")
        # 电池信息标签页
        self.battery_text = self.create_tab("电池信息", "battery")

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

        # 更新显卡信息
        self.update_gpu_info(hardware_info.get('gpus', []))

        # 更新主板信息
        self.update_motherboard_info(hardware_info.get('motherboard', {}))

        # 更新温度信息
        self.update_temperature_info(hardware_info.get('temperatures', {}))

        # 更新风扇信息
        self.update_fan_info(hardware_info.get('fans', {}))

        # 更新内存信息
        self.update_memory_info(hardware_info.get('memory', {}))

        # 更新磁盘信息
        self.update_disk_info(hardware_info.get('disks', []))

        # 更新网络接口信息
        self.update_network_info(hardware_info.get('network_interfaces', {}))

        # 更新电池信息
        self.update_battery_info(hardware_info.get('battery', {}))

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

    def update_gpu_info(self, gpus: list):
        """更新显卡信息"""
        info_lines = []

        try:
            info_lines.append("<h2>显卡信息</h2>")

            if not gpus or ('message' in gpus[0] and '未检测到' in gpus[0]['message']):
                info_lines.append("<p>未检测到显卡信息</p>")
                info_lines.append("<p style='color: #666; font-size: 12px;'>提示: 安装 nvidia-ml-py3 或 GPUtil 可获取更详细的显卡信息</p>")
            else:
                for idx, gpu in enumerate(gpus, 1):
                    if 'error' in gpu:
                        info_lines.append(f"<p style='color: red;'>显卡 {idx} 错误: {gpu['error']}</p>")
                        continue

                    info_lines.append(f"<h3>显卡 {idx}</h3>")
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                    info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>显卡名称</b></td><td>{gpu.get('name', 'N/A')}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>类型</b></td><td>{gpu.get('type', 'N/A')}</td></tr>")

                    if gpu.get('memory_total'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>显存总量</b></td><td>{format_bytes(gpu.get('memory_total', 0))}</td></tr>")
                    if gpu.get('memory_used'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用显存</b></td><td>{format_bytes(gpu.get('memory_used', 0))}</td></tr>")
                    if gpu.get('memory_free'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>可用显存</b></td><td>{format_bytes(gpu.get('memory_free', 0))}</td></tr>")
                    if gpu.get('temperature'):
                        temp = gpu.get('temperature', 0)
                        temp_color = "red" if temp > 80 else "orange" if temp > 70 else "green"
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>温度</b></td><td style='color: {temp_color}; font-weight: bold;'>{temp}°C</td></tr>")
                    if gpu.get('fan_speed'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>风扇转速</b></td><td>{gpu.get('fan_speed', 0)}%</td></tr>")
                    if gpu.get('power_usage'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>当前功耗</b></td><td>{gpu.get('power_usage', 0):.1f}W / {gpu.get('power_limit', 0):.1f}W</td></tr>")
                    if gpu.get('load'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>负载</b></td><td>{gpu.get('load', 0):.1f}%</td></tr>")
                    if gpu.get('driver_version'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>驱动版本</b></td><td>{gpu.get('driver_version', 'N/A')}</td></tr>")

                    info_lines.append("</table><br>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示显卡信息时出错: {e}</p>")

        self.gpu_text.setHtml("".join(info_lines))

    def update_motherboard_info(self, motherboard: dict):
        """更新主板信息"""
        info_lines = []

        try:
            info_lines.append("<h2>主板信息</h2>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

            if 'error' in motherboard:
                info_lines.append(f"<tr><td colspan='2' style='color: red;'>{motherboard['error']}</td></tr>")
            elif 'message' in motherboard:
                info_lines.append(f"<tr><td colspan='2'>{motherboard['message']}</td></tr>")
            else:
                if motherboard.get('manufacturer'):
                    info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>制造商</b></td><td>{motherboard.get('manufacturer', 'N/A')}</td></tr>")
                if motherboard.get('model'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>型号</b></td><td>{motherboard.get('model', 'N/A')}</td></tr>")
                if motherboard.get('version'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>版本</b></td><td>{motherboard.get('version', 'N/A')}</td></tr>")
                if motherboard.get('bios_vendor'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>BIOS厂商</b></td><td>{motherboard.get('bios_vendor', 'N/A')}</td></tr>")
                if motherboard.get('bios_version'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>BIOS版本</b></td><td>{motherboard.get('bios_version', 'N/A')}</td></tr>")
                if motherboard.get('bios_date'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>BIOS日期</b></td><td>{motherboard.get('bios_date', 'N/A')}</td></tr>")

            info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示主板信息时出错: {e}</p>")

        self.motherboard_text.setHtml("".join(info_lines))

    def update_temperature_info(self, temperatures: dict):
        """更新温度信息"""
        info_lines = []

        try:
            info_lines.append("<h2>温度传感器</h2>")

            if not temperatures or ('message' in temperatures):
                info_lines.append("<p>未检测到温度传感器</p>")
            else:
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                for sensor_name, sensor_list in temperatures.items():
                    for sensor in sensor_list:
                        label = sensor.get('label', sensor_name)
                        current = sensor.get('current', 0)
                        high = sensor.get('high')
                        critical = sensor.get('critical')

                        # 根据温度设置颜色
                        if critical and current >= critical:
                            bg_color = "#FFCDD2"
                            text_color = "#B71C1C"
                        elif high and current >= high:
                            bg_color = "#FFE0B2"
                            text_color = "#E65100"
                        else:
                            bg_color = "#E8F5E9"
                            text_color = "#2E7D32"

                        info_lines.append(f"<tr><td style='width: 40%; background-color: {bg_color}; color: {text_color}; font-weight: bold;'>{label}</td><td style='padding: 5px;'>{current:.1f}°C")

                        if high:
                            info_lines.append(f" <span style='color: orange;'>(警告: {high:.1f}°C)</span>")
                        if critical:
                            info_lines.append(f" <span style='color: red;'>(严重: {critical:.1f}°C)</span>")

                        info_lines.append("</td></tr>")

                info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示温度信息时出错: {e}</p>")

        self.temperature_text.setHtml("".join(info_lines))

    def update_fan_info(self, fans: dict):
        """更新风扇信息"""
        info_lines = []

        try:
            info_lines.append("<h2>风扇信息</h2>")

            if not fans or ('message' in fans):
                info_lines.append("<p>未检测到风扇传感器</p>")
            else:
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                for fan_name, fan_list in fans.items():
                    for fan in fan_list:
                        label = fan.get('label', fan_name)
                        rpm = fan.get('current_rpm', 0)

                        info_lines.append(f"<tr><td style='width: 40%; background-color: #E3F2FD;'><b>{label}</b></td><td>{rpm} RPM</td></tr>")

                info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示风扇信息时出错: {e}</p>")

        self.fan_text.setHtml("".join(info_lines))

    def update_battery_info(self, battery: dict):
        """更新电池信息"""
        info_lines = []

        try:
            info_lines.append("<h2>电池信息</h2>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

            if not battery or 'message' in battery:
                info_lines.append(f"<tr><td colspan='2'>{battery.get('message', '未检测到电池') if battery else '未检测到电池'}</td></tr>")
            elif 'error' in battery:
                info_lines.append(f"<tr><td colspan='2' style='color: red;'>{battery['error']}</td></tr>")
            else:
                percent = battery.get('percent', 0)
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>电量</b></td><td>{percent:.0f}%</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>状态</b></td><td>{battery.get('status', 'N/A')}</td></tr>")

                if battery.get('time_left_formatted'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>剩余时间</b></td><td>{battery.get('time_left_formatted', 'N/A')}</td></tr>")

            info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示电池信息时出错: {e}</p>")

        self.battery_text.setHtml("".join(info_lines))

    def refresh_info(self):
        """刷新硬件信息（由主窗口调用）"""
        # 这个方法会被主窗口重写或者通过信号连接
        pass
