#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cards包 - UI卡片组件模块
"""

# 系统监控相关卡片
from .system_cards import (
    SystemOverviewCard,
    SystemStatsCard,
    SystemInfoCard
)

# 进程管理相关卡片
from .process_cards import ProcessTableCard

# 网络监控相关卡片
from .network_cards import NetworkTableCard

# 硬件信息相关卡片
from .hardware_cards import (
    HardwareInfoCard,
    HardwareInfoDialog
)

# 流量监控相关卡片
from .traffic_cards import (
    TrafficMonitorCard,
    ProcessTrafficCard
)

# 高级监控相关卡片
from .advanced_cards import (
    TemperatureMonitorCard,
    BatteryMonitorCard,
    ServicesMonitorCard
)

__all__ = [
    # 系统监控
    'SystemOverviewCard',
    'SystemStatsCard',
    'SystemInfoCard',
    # 进程管理
    'ProcessTableCard',
    # 网络监控
    'NetworkTableCard',
    # 硬件信息
    'HardwareInfoCard',
    'HardwareInfoDialog',
    # 流量监控
    'TrafficMonitorCard',
    'ProcessTrafficCard',
    # 高级监控
    'TemperatureMonitorCard',
    'BatteryMonitorCard',
    'ServicesMonitorCard',
]
