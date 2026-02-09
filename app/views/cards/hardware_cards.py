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


def format_seconds(seconds: float) -> str:
    """格式化时间（秒）为可读格式"""
    if seconds >= 86400:
        days = seconds / 86400
        return f"{days:.1f} 天"
    elif seconds >= 3600:
        hours = seconds / 3600
        return f"{hours:.1f} 小时"
    elif seconds >= 60:
        minutes = seconds / 60
        return f"{minutes:.1f} 分钟"
    else:
        return f"{seconds:.1f} 秒"


def format_number(num: int) -> str:
    """格式化数字，添加千位分隔符"""
    return f"{num:,}"


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

            # 音频设备
            if 'audio' in hardware_info:
                audio = hardware_info['audio']
                if audio.get('output_devices'):
                    info_lines.append("=== 音频设备 ===")
                    info_lines.append(f"输出设备: {len(audio.get('output_devices', []))} 个")
                    for device in audio.get('output_devices', [])[:2]:
                        info_lines.append(f"  - {device.get('name', 'N/A')}")
                    info_lines.append("")

            # 蓝牙设备
            if 'bluetooth' in hardware_info:
                bt = hardware_info['bluetooth']
                if bt and 'message' not in bt[0]:
                    info_lines.append("=== 蓝牙设备 ===")
                    for device in bt[:3]:
                        if 'error' not in device:
                            info_lines.append(f"  - {device.get('name', 'N/A')}")
                    info_lines.append("")

            # 输入设备
            if 'input_devices' in hardware_info:
                input_dev = hardware_info['input_devices']
                keyboards = input_dev.get('keyboards', [])
                mice = input_dev.get('mice', [])
                if keyboards and 'message' not in keyboards[0]:
                    info_lines.append("=== 输入设备 ===")
                    info_lines.append(f"键盘: {len(keyboards)} 个")
                    info_lines.append(f"鼠标: {len(mice)} 个")
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
        # 音频设备标签页
        self.audio_text = self.create_tab("音频设备", "audio")
        # 蓝牙设备标签页
        self.bluetooth_text = self.create_tab("蓝牙设备", "bluetooth")
        # USB设备标签页
        self.usb_text = self.create_tab("USB设备", "usb")
        # 输入设备标签页
        self.input_text = self.create_tab("键盘鼠标", "input")

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

        # 更新音频设备信息
        self.update_audio_info(hardware_info.get('audio', {}))

        # 更新蓝牙设备信息
        self.update_bluetooth_info(hardware_info.get('bluetooth', []))

        # 更新USB设备信息
        self.update_usb_info(hardware_info.get('usb_devices', []))

        # 更新输入设备信息
        self.update_input_info(hardware_info.get('input_devices', {}))

    def update_cpu_info(self, cpu_info: dict):
        """更新CPU信息"""
        info_lines = []

        try:
            info_lines.append("<h2>CPU 处理器信息</h2>")

            # 基本信息
            info_lines.append("<h3>基本信息</h3>")
            info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

            if cpu_info.get('model_name'):
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>处理器型号</b></td><td>{cpu_info['model_name']}</td></tr>")
            elif cpu_info.get('processor'):
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>处理器</b></td><td>{cpu_info['processor']}</td></tr>")

            if cpu_info.get('manufacturer'):
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>制造商</b></td><td>{cpu_info['manufacturer']}</td></tr>")

            if cpu_info.get('hardware'):
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>硬件</b></td><td>{cpu_info['hardware']}</td></tr>")

            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>架构</b></td><td>{cpu_info.get('architecture', 'N/A')}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>物理核心数</b></td><td>{cpu_info.get('physical_cores', 'N/A')}</td></tr>")
            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>逻辑核心数</b></td><td>{cpu_info.get('logical_cores', 'N/A')}</td></tr>")

            # Windows 特有信息
            if cpu_info.get('number_of_cores'):
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>物理核心 (WMI)</b></td><td>{cpu_info['number_of_cores']}</td></tr>")
            if cpu_info.get('number_of_logical_processors'):
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>逻辑处理器 (WMI)</b></td><td>{cpu_info['number_of_logical_processors']}</td></tr>")

            info_lines.append("</table>")

            # 频率信息
            if cpu_info.get('frequency'):
                info_lines.append("<h3>频率信息</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                freq = cpu_info['frequency']
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>当前频率</b></td><td>{format_frequency(freq.get('current', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最大频率</b></td><td>{format_frequency(freq.get('max', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最小频率</b></td><td>{format_frequency(freq.get('min', 0))}</td></tr>")
                info_lines.append("</table>")

            # Windows 频率信息
            if cpu_info.get('max_clock_speed'):
                info_lines.append("<h3>时钟频率 (WMI)</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>最大时钟频率</b></td><td>{cpu_info['max_clock_speed']} MHz</td></tr>")
                if cpu_info.get('current_clock_speed'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>当前时钟频率</b></td><td>{cpu_info['current_clock_speed']} MHz</td></tr>")
                info_lines.append("</table>")

            # CPU 使用率
            if cpu_info.get('cpu_percent') is not None:
                info_lines.append("<h3>CPU 使用率</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                percent = cpu_info['cpu_percent']
                color = "red" if percent > 80 else "orange" if percent > 60 else "green"
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>总体使用率</b></td><td style='color: {color}; font-weight: bold;'>{percent:.1f}%</td></tr>")
                info_lines.append("</table>")

            # 每个核心的使用率
            if cpu_info.get('per_cpu_percent'):
                info_lines.append("<h3>各核心使用率</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append("<tr><th style='background-color: #f0f0f0;'>核心</th><th style='background-color: #f0f0f0;'>使用率</th><th style='background-color: #f0f0f0;'>状态</th></tr>")

                for idx, core_percent in enumerate(cpu_info['per_cpu_percent']):
                    color = "red" if core_percent > 80 else "orange" if core_percent > 60 else "green"
                    status = "高负载" if core_percent > 80 else "中等" if core_percent > 50 else "正常"
                    info_lines.append(f"<tr><td>核心 {idx}</td><td style='color: {color}; font-weight: bold;'>{core_percent:.1f}%</td><td>{status}</td></tr>")

                info_lines.append("</table>")

            # CPU 时间信息
            if cpu_info.get('times'):
                info_lines.append("<h3>CPU 时间分布</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                times = cpu_info['times']
                total_time = sum(times.values())

                for key, value in times.items():
                    percentage = (value / total_time * 100) if total_time > 0 else 0
                    label_map = {
                        'user': '用户空间',
                        'system': '内核空间',
                        'idle': '空闲',
                        'nice': '优先级调整',
                        'iowait': 'IO等待',
                        'irq': '硬中断',
                        'softirq': '软中断',
                        'steal': '被窃取',
                        'guest': '虚拟机'
                    }
                    label = label_map.get(key, key)
                    info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>{label}</b></td><td>{format_seconds(value)}</td><td>{percentage:.1f}%</td></tr>")

                info_lines.append("</table>")

            # 每个核心的时间信息
            if cpu_info.get('per_cpu_times'):
                info_lines.append("<h3>各核心时间分布</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append("<tr><th style='background-color: #f0f0f0;'>核心</th><th style='background-color: #f0f0f0;'>用户</th><th style='background-color: #f0f0f0;'>系统</th><th style='background-color: #f0f0f0;'>空闲</th></tr>")

                for idx, times in enumerate(cpu_info['per_cpu_times']):
                    user_pct = (times['user'] / sum(times.values()) * 100) if times else 0
                    sys_pct = (times['system'] / sum(times.values()) * 100) if times else 0
                    idle_pct = (times['idle'] / sum(times.values()) * 100) if times else 0

                    info_lines.append(f"<tr><td>核心 {idx}</td><td>{user_pct:.1f}%</td><td>{sys_pct:.1f}%</td><td>{idle_pct:.1f}%</td></tr>")

                info_lines.append("</table>")

            # CPU 统计信息
            if cpu_info.get('stats'):
                info_lines.append("<h3>CPU 统计</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                stats = cpu_info['stats']
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>上下文切换</b></td><td>{format_number(stats.get('ctx_switches', 0))}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>中断</b></td><td>{format_number(stats.get('interrupts', 0))}</td></tr>")
                if stats.get('soft_interrupts'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>软中断</b></td><td>{format_number(stats['soft_interrupts'])}</td></tr>")
                if stats.get('syscalls'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>系统调用</b></td><td>{format_number(stats['syscalls'])}</td></tr>")
                info_lines.append("</table>")

            # 缓存信息
            if cpu_info.get('cache_info'):
                info_lines.append("<h3>缓存信息</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                cache = cpu_info['cache_info']
                for key, value in cache.items():
                    info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>{key}</b></td><td>{value}</td></tr>")
                info_lines.append("</table>")

            # Windows 缓存信息
            if cpu_info.get('l2_cache_size') or cpu_info.get('l3_cache_size'):
                info_lines.append("<h3>缓存信息 (WMI)</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                if cpu_info.get('l2_cache_size'):
                    info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>L2 缓存</b></td><td>{cpu_info['l2_cache_size']}</td></tr>")
                if cpu_info.get('l3_cache_size'):
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>L3 缓存</b></td><td>{cpu_info['l3_cache_size']}</td></tr>")
                info_lines.append("</table>")

            # CPU 特性
            if cpu_info.get('flags'):
                info_lines.append("<h3>CPU 特性</h3>")
                flags = cpu_info['flags']
                # 显示前 30 个特性
                info_lines.append(f"<p>{', '.join(flags[:30])}")
                if len(flags) > 30:
                    info_lines.append(f"<p style='color: #666;'>... 还有 {len(flags) - 30} 个特性</p>")

            # 虚拟化支持
            if cpu_info.get('virtualization') is not None:
                info_lines.append("<h3>虚拟化</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                virt_status = "支持" if cpu_info['virtualization'] else "不支持"
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>硬件虚拟化</b></td><td>{virt_status}</td></tr>")
                info_lines.append("</table>")

            # 系统负载
            if cpu_info.get('load_average'):
                info_lines.append("<h3>系统负载均衡</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                load = cpu_info['load_average']
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>1分钟平均负载</b></td><td>{load['1min']:.2f}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>5分钟平均负载</b></td><td>{load['5min']:.2f}</td></tr>")
                info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>15分钟平均负载</b></td><td>{load['15min']:.2f}</td></tr>")
                info_lines.append("</table>")

            # 主机名
            if cpu_info.get('hostname'):
                info_lines.append("<h3>系统信息</h3>")
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>主机名</b></td><td>{cpu_info['hostname']}</td></tr>")
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

                    # 基本信息
                    info_lines.append("<h4>基本信息</h4>")
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                    info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>显卡名称</b></td><td>{gpu.get('name', 'N/A')}</td></tr>")
                    info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>类型</b></td><td>{gpu.get('type', 'N/A')}</td></tr>")

                    if gpu.get('index') is not None:
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>GPU 索引</b></td><td>{gpu['index']}</td></tr>")

                    if gpu.get('uuid'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>UUID</b></td><td style='font-family: monospace; font-size: 11px;'>{gpu['uuid']}</td></tr>")

                    if gpu.get('serial_number'):
                        info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>序列号</b></td><td style='font-family: monospace;'>{gpu['serial_number']}</td></tr>")

                    info_lines.append("</table>")

                    # 显存信息
                    if gpu.get('memory_total'):
                        info_lines.append("<h4>显存信息</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>显存总量</b></td><td>{format_bytes(gpu.get('memory_total', 0))}</td></tr>")

                        if gpu.get('memory_used'):
                            mem_used = gpu['memory_used']
                            mem_total = gpu['memory_total']
                            mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>已使用显存</b></td><td>{format_bytes(mem_used)} ({mem_percent:.1f}%)</td></tr>")

                        if gpu.get('memory_free'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>可用显存</b></td><td>{format_bytes(gpu['memory_free'])}</td></tr>")

                        if gpu.get('memory_utilization'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>显存利用率</b></td><td>{gpu['memory_utilization']}%</td></tr>")

                        info_lines.append("</table>")

                    # 温度和风扇
                    if gpu.get('temperature') or gpu.get('fan_speed'):
                        info_lines.append("<h4>温度与散热</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('temperature'):
                            temp = gpu['temperature']
                            temp_color = "red" if temp > 80 else "orange" if temp > 70 else "green"
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>当前温度</b></td><td style='color: {temp_color}; font-weight: bold;'>{temp}°C</td></tr>")

                        if gpu.get('temperature_threshold'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>温度阈值</b></td><td>{gpu['temperature_threshold']}°C</td></tr>")

                        if gpu.get('temp_slowdown'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>降频温度</b></td><td style='color: orange;'>{gpu['temp_slowdown']}°C</td></tr>")

                        if gpu.get('temp_shutdown'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>关机温度</b></td><td style='color: red;'>{gpu['temp_shutdown']}°C</td></tr>")

                        if gpu.get('fan_speed'):
                            fan = gpu['fan_speed']
                            fan_color = "red" if fan > 90 else "orange" if fan > 70 else "green"
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>风扇转速</b></td><td style='color: {fan_color}; font-weight: bold;'>{fan}%</td></tr>")

                        info_lines.append("</table>")

                    # 功耗信息
                    if gpu.get('power_usage'):
                        info_lines.append("<h4>功耗信息</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                        power = gpu['power_usage']
                        power_limit = gpu.get('power_limit', 0)
                        power_percent = gpu.get('power_percent', 0)

                        power_color = "red" if power_percent > 90 else "orange" if power_percent > 75 else "green"
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>当前功耗</b></td><td style='color: {power_color}; font-weight: bold;'>{power:.1f}W ({power_percent:.1f}%)</td></tr>")

                        if power_limit:
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>功耗上限</b></td><td>{power_limit:.1f}W</td></tr>")

                        if gpu.get('power_min_limit') and gpu.get('power_max_limit'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>功耗范围</b></td><td>{gpu['power_min_limit']:.0f}W - {gpu['power_max_limit']:.0f}W</td></tr>")

                        info_lines.append("</table>")

                    # GPU 利用率
                    if gpu.get('gpu_utilization') or gpu.get('load'):
                        info_lines.append("<h4>GPU 利用率</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('gpu_utilization'):
                            util = gpu['gpu_utilization']
                            util_color = "red" if util > 90 else "orange" if util > 75 else "green"
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>GPU 利用率</b></td><td style='color: {util_color}; font-weight: bold;'>{util}%</td></tr>")
                        elif gpu.get('load'):
                            load = gpu['load']
                            load_color = "red" if load > 90 else "orange" if load > 75 else "green"
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>负载</b></td><td style='color: {load_color}; font-weight: bold;'>{load:.1f}%</td></tr>")

                        if gpu.get('running_processes'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>运行进程数</b></td><td>{gpu['running_processes']}</td></tr>")

                        if gpu.get('performance_state'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>性能状态</b></td><td>{gpu['performance_state']}</td></tr>")

                        info_lines.append("</table>")

                    # 时钟频率
                    if gpu.get('graphics_clock') or gpu.get('memory_clock'):
                        info_lines.append("<h4>时钟频率</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('graphics_clock'):
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>图形时钟</b></td><td>{gpu['graphics_clock']} MHz</td></tr>")

                        if gpu.get('max_graphics_clock'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最大图形时钟</b></td><td>{gpu['max_graphics_clock']} MHz</td></tr>")

                        if gpu.get('sm_clock'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>SM 时钟</b></td><td>{gpu['sm_clock']} MHz</td></tr>")

                        if gpu.get('memory_clock'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>显存时钟</b></td><td>{gpu['memory_clock']} MHz</td></tr>")

                        if gpu.get('max_memory_clock'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最大显存时钟</b></td><td>{gpu['max_memory_clock']} MHz</td></tr>")

                        info_lines.append("</table>")

                    # PCIe 信息
                    if gpu.get('pcie_gen') or gpu.get('pcie_width'):
                        info_lines.append("<h4>PCIe 总线</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('bus_type'):
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>总线类型</b></td><td>{gpu['bus_type']}</td></tr>")

                        if gpu.get('pcie_gen'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>当前 PCIe 代数</b></td><td>Gen {gpu['pcie_gen']}</td></tr>")

                        if gpu.get('pcie_width'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>当前 PCIe 带宽</b></td><td>x{gpu['pcie_width']}</td></tr>")

                        if gpu.get('max_pcie_gen') or gpu.get('max_pcie_width'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>最大 PCIe 规格</b></td><td>Gen {gpu.get('max_pcie_gen', 'N/A')} x{gpu.get('max_pcie_width', 'N/A')}</td></tr>")

                        if gpu.get('pcie_throughput_rx') and gpu.get('pcie_throughput_tx'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>PCIe 吞吐量</b></td><td>↓{format_bytes(gpu['pcie_throughput_rx'])}/s ↑{format_bytes(gpu['pcie_throughput_tx'])}/s</td></tr>")

                        info_lines.append("</table>")

                    # 驱动和固件信息
                    if gpu.get('driver_version') or gpu.get('vbios_version') or gpu.get('cuda_version'):
                        info_lines.append("<h4>驱动与固件</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('driver_version'):
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>驱动版本</b></td><td>{gpu['driver_version']}</td></tr>")

                        if gpu.get('cuda_version'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>CUDA 版本</b></td><td>{gpu['cuda_version']}</td></tr>")

                        if gpu.get('vbios_version'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>VBIOS 版本</b></td><td>{gpu['vbios_version']}</td></tr>")

                        if gpu.get('driver_date'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>驱动日期</b></td><td>{gpu['driver_date']}</td></tr>")

                        if gpu.get('install_date'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>安装日期</b></td><td>{gpu['install_date']}</td></tr>")

                        info_lines.append("</table>")

                    # 计算能力
                    if gpu.get('compute_capability'):
                        info_lines.append("<h4>计算能力</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                        info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>计算能力</b></td><td>{gpu['compute_capability']}</td></tr>")
                        info_lines.append("</table>")

                    # 显示模式
                    if gpu.get('display_mode') or gpu.get('persistence_mode') or gpu.get('ecc_enabled'):
                        info_lines.append("<h4>模式与特性</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('display_mode'):
                            display_color = "green" if gpu['display_mode'] == "Enabled" else "#666"
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>显示模式</b></td><td style='color: {display_color};'>{gpu['display_mode']}</td></tr>")

                        if gpu.get('persistence_mode'):
                            persistence_color = "green" if gpu['persistence_mode'] == "Enabled" else "#666"
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>持久化模式</b></td><td style='color: {persistence_color};'>{gpu['persistence_mode']}</td></tr>")

                        if gpu.get('ecc_enabled') is not None:
                            ecc_status = "启用" if gpu['ecc_enabled'] else "禁用"
                            ecc_color = "green" if gpu['ecc_enabled'] else "#666"
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>ECC 内存</b></td><td style='color: {ecc_color};'>{ecc_status}</td></tr>")

                        if gpu.get('mig_mode'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>MIG 模式</b></td><td>{gpu['mig_mode']}</td></tr>")

                        info_lines.append("</table>")

                    # Windows 额外信息
                    if gpu.get('video_processor') or gpu.get('video_architecture') or gpu.get('memory_type'):
                        info_lines.append("<h4>其他信息</h4>")
                        info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                        if gpu.get('video_processor'):
                            info_lines.append(f"<tr><td style='width: 30%; background-color: #f0f0f0;'><b>视频处理器</b></td><td>{gpu['video_processor']}</td></tr>")

                        if gpu.get('video_architecture'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>架构</b></td><td>{gpu['video_architecture']}</td></tr>")

                        if gpu.get('memory_type'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>内存类型</b></td><td>{gpu['memory_type']}</td></tr>")

                        if gpu.get('adapter_type'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>适配器类型</b></td><td>{gpu['adapter_type']}</td></tr>")

                        if gpu.get('resolution'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>分辨率</b></td><td>{gpu['resolution']}</td></tr>")

                        if gpu.get('refresh_rate'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>刷新率</b></td><td>{gpu['refresh_rate']} Hz</td></tr>")

                        if gpu.get('color_depth'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>色深</b></td><td>{gpu['color_depth']}</td></tr>")

                        if gpu.get('caption'):
                            info_lines.append(f"<tr><td style='background-color: #f0f0f0;'><b>描述</b></td><td>{gpu['caption']}</td></tr>")

                        info_lines.append("</table>")

                    info_lines.append("<br>")

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

    def update_audio_info(self, audio: dict):
        """更新音频设备信息"""
        info_lines = []

        try:
            info_lines.append("<h2>音频设备</h2>")

            if 'error' in audio:
                info_lines.append(f"<p style='color: red;'>{audio['error']}</p>")
            elif 'message' in audio:
                info_lines.append(f"<p>{audio['message']}</p>")
            else:
                info_lines.append("<h3>输出设备</h3>")
                output_devices = audio.get('output_devices', [])
                if output_devices:
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                    for idx, device in enumerate(output_devices, 1):
                        info_lines.append(f"<tr><td style='width: 10%; background-color: #f0f0f0;'><b>{idx}</b></td>")
                        info_lines.append(f"<td style='width: 40%;'>{device.get('name', 'N/A')}</td>")
                        info_lines.append(f"<td>声道: {device.get('channels', 'N/A')}</td>")
                        info_lines.append(f"<td>采样率: {device.get('sample_rate', 0)} Hz</td></tr>")
                    info_lines.append("</table>")
                else:
                    info_lines.append("<p>未检测到输出设备</p>")

                info_lines.append("<h3>输入设备</h3>")
                input_devices = audio.get('input_devices', [])
                if input_devices:
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                    for idx, device in enumerate(input_devices, 1):
                        info_lines.append(f"<tr><td style='width: 10%; background-color: #f0f0f0;'><b>{idx}</b></td>")
                        info_lines.append(f"<td style='width: 40%;'>{device.get('name', 'N/A')}</td>")
                        info_lines.append(f"<td>声道: {device.get('channels', 'N/A')}</td>")
                        info_lines.append(f"<td>采样率: {device.get('sample_rate', 0)} Hz</td></tr>")
                    info_lines.append("</table>")
                else:
                    info_lines.append("<p>未检测到输入设备</p>")

                if not output_devices and not input_devices:
                    info_lines.append("<p style='color: #666; font-size: 12px;'>提示: 安装 pyaudio 可获取详细音频设备信息</p>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示音频设备信息时出错: {e}</p>")

        self.audio_text.setHtml("".join(info_lines))

    def update_bluetooth_info(self, bluetooth: list):
        """更新蓝牙设备信息"""
        info_lines = []

        try:
            info_lines.append("<h2>蓝牙设备</h2>")

            if not bluetooth or ('message' in bluetooth[0]):
                info_lines.append("<p>未检测到蓝牙设备</p>")
            else:
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")

                for idx, device in enumerate(bluetooth, 1):
                    if 'error' in device:
                        info_lines.append(f"<tr><td colspan='3' style='color: red;'>{device['error']}</td></tr>")
                        continue

                    info_lines.append(f"<tr><td style='width: 5%; background-color: #f0f0f0;'><b>{idx}</b></td>")
                    info_lines.append(f"<td style='width: 40%;'><b>{device.get('name', 'N/A')}</b></td>")
                    info_lines.append(f"<td>{device.get('type', 'N/A')}</td></tr>")

                    if device.get('status'):
                        status_color = "green" if device['status'] == '已连接' else "#666"
                        info_lines.append(f"<tr><td></td><td colspan='2' style='color: {status_color};'>状态: {device.get('status', 'N/A')}</td></tr>")

                    if device.get('device_id'):
                        info_lines.append(f"<tr><td></td><td colspan='2' style='font-size: 11px; color: #999;'>ID: {device.get('device_id', 'N/A')[:50]}</td></tr>")
                    info_lines.append(f"<tr><td colspan='3' style='padding: 5px;'></td></tr>")

                info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示蓝牙设备信息时出错: {e}</p>")

        self.bluetooth_text.setHtml("".join(info_lines))

    def update_usb_info(self, usb_devices: list):
        """更新USB设备信息"""
        info_lines = []

        try:
            info_lines.append("<h2>USB设备</h2>")

            if not usb_devices or ('message' in usb_devices[0]):
                info_lines.append("<p>未检测到USB设备</p>")
            else:
                info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                info_lines.append("<tr><th style='background-color: #f0f0f0;'>设备名称</th><th style='background-color: #f0f0f0;'>类型</th><th style='background-color: #f0f0f0;'>状态</th></tr>")

                for idx, device in enumerate(usb_devices[:50], 1):  # 限制显示前50个
                    if 'error' in device:
                        continue
                    if 'message' in device:
                        info_lines.append(f"<tr><td colspan='3'>{device['message']}</td></tr>")
                        continue

                    device_type = device.get('type', 'USB设备')
                    bg_color = "#E8F5E9" if '鼠标' in device_type or '键盘' in device_type else "#fff"

                    info_lines.append(f"<tr style='background-color: {bg_color};'>")
                    info_lines.append(f"<td>{device.get('name', 'N/A')}</td>")
                    info_lines.append(f"<td>{device_type}</td>")
                    info_lines.append(f"<td>{device.get('status', 'N/A')}</td></tr>")

                if len(usb_devices) > 50:
                    info_lines.append(f"<tr><td colspan='3' style='text-align: center; color: #666;'>... 还有 {len(usb_devices) - 50} 个设备未显示</td></tr>")

                info_lines.append("</table>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示USB设备信息时出错: {e}</p>")

        self.usb_text.setHtml("".join(info_lines))

    def update_input_info(self, input_devices: dict):
        """更新输入设备信息"""
        info_lines = []

        try:
            info_lines.append("<h2>键盘与鼠标</h2>")

            if 'error' in input_devices:
                info_lines.append(f"<p style='color: red;'>{input_devices['error']}</p>")
            elif 'message' in input_devices:
                info_lines.append(f"<p>{input_devices['message']}</p>")
            else:
                # 键盘信息
                keyboards = input_devices.get('keyboards', [])
                info_lines.append("<h3>键盘</h3>")
                if keyboards and 'message' not in keyboards[0]:
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                    for idx, keyboard in enumerate(keyboards, 1):
                        info_lines.append("<tr><td style='width: 5%; background-color: #f0f0f0;'><b>⌨</b></td>")
                        info_lines.append(f"<td style='width: 45%;'><b>{keyboard.get('name', 'N/A')}</b></td>")
                        info_lines.append(f"<td>{keyboard.get('status', 'N/A')}</td></tr>")
                        if keyboard.get('description'):
                            info_lines.append(f"<tr><td></td><td colspan='2' style='font-size: 11px; color: #666;'>{keyboard.get('description', 'N/A')}</td></tr>")
                    info_lines.append("</table>")
                else:
                    info_lines.append("<p>未检测到键盘</p>")

                # 鼠标信息
                mice = input_devices.get('mice', [])
                info_lines.append("<h3>鼠标</h3>")
                if mice and 'message' not in mice[0]:
                    info_lines.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>")
                    for idx, mouse in enumerate(mice, 1):
                        info_lines.append("<tr><td style='width: 5%; background-color: #f0f0f0;'><b>🖱</b></td>")
                        info_lines.append(f"<td style='width: 45%;'><b>{mouse.get('name', 'N/A')}</b></td>")
                        info_lines.append(f"<td>{mouse.get('status', 'N/A')}</td></tr>")
                        if mouse.get('description'):
                            info_lines.append(f"<tr><td></td><td colspan='2' style='font-size: 11px; color: #666;'>{mouse.get('description', 'N/A')}</td></tr>")
                    info_lines.append("</table>")
                else:
                    info_lines.append("<p>未检测到鼠标</p>")

                if not keyboards and not mice:
                    info_lines.append("<p style='color: #666; font-size: 12px;'>提示: 安装 wmi 和 pywin32 可获取详细输入设备信息</p>")

        except Exception as e:
            info_lines.append(f"<p style='color: red;'>显示输入设备信息时出错: {e}</p>")

        self.input_text.setHtml("".join(info_lines))

    def refresh_info(self):
        """刷新硬件信息（由主窗口调用）"""
        # 这个方法会被主窗口重写或者通过信号连接
        pass
