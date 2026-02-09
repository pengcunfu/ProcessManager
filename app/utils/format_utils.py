#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化工具模块
提供数据格式化等辅助功能
"""


def format_bytes(bytes_value: int) -> str:
    """
    格式化字节数为人类可读格式

    Args:
        bytes_value: 字节数

    Returns:
        格式化后的字符串，如 "1.5 GB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_frequency(freq_mhz: float) -> str:
    """
    格式化频率为人类可读格式

    Args:
        freq_mhz: 频率（MHz）

    Returns:
        格式化后的字符串，如 "2.4 GHz" 或 "800 MHz"
    """
    if freq_mhz >= 1000:
        return f"{freq_mhz / 1000:.2f} GHz"
    else:
        return f"{freq_mhz:.0f} MHz"
