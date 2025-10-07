# 系统监控与进程管理工具 - Fluent版本

## 项目概述

这是一个基于PySide6和PySide6-Fluent-Widgets开发的现代化系统监控工具，采用了清晰的架构分层设计，将界面和业务逻辑完全分离。

## 新架构特点

### 1. 业务逻辑层 (`business_logic.py`)
- **SystemMonitorService**: 系统资源监控服务
- **ProcessManagerService**: 进程管理服务  
- **NetworkMonitorService**: 网络连接监控服务
- **HardwareInfoService**: 硬件信息服务
- 使用数据类(dataclass)定义数据结构
- 基于Qt信号槽机制的异步通信

### 2. 界面组件层 (`fluent_ui_components.py`)
- **SystemOverviewCard**: 系统概览卡片
- **ProcessTableCard**: 进程管理表格卡片
- **NetworkTableCard**: 网络连接表格卡片
- **HardwareInfoCard**: 硬件信息卡片
- **SystemStatsCard**: 系统统计卡片
- 使用Fluent-Widgets现代化组件

### 3. 主窗口层 (`fluent_main_window.py`)
- **FluentMainWindow**: 主窗口类
- **SystemOverviewInterface**: 系统概览界面
- **ProcessInterface**: 进程管理界面
- **NetworkInterface**: 网络监控界面
- **HardwareInterface**: 硬件信息界面
- 采用导航式界面设计

## 功能特性

### 🎨 现代化界面
- 基于Microsoft Fluent Design设计语言
- 支持明暗主题自动切换
- 流畅的动画效果和交互体验
- 响应式布局设计

### 📊 系统监控
- 实时CPU、内存、磁盘使用率监控
- 系统启动时间和运行时间显示
- 进程数量统计
- 网络IO统计

### 🔧 进程管理
- 实时进程列表显示
- 进程搜索和过滤功能
- 多种排序方式（CPU、内存、进程名、PID）
- 进程结束和强制结束功能
- 进程详细信息查看
- 右键菜单快捷操作

### 🌐 网络监控
- 网络连接实时监控
- 协议类型过滤（TCP/UDP）
- 连接状态过滤
- 本地和远程地址显示

### 💻 硬件信息
- CPU详细信息（核心数、频率等）
- 内存信息（总量、使用量、交换内存）
- 磁盘信息（各分区使用情况）
- 网络接口信息

## 技术栈

- **PySide6**: Qt6的Python绑定
- **PySide6-Fluent-Widgets**: 现代化UI组件库
- **psutil**: 系统和进程信息获取
- **Python 3.9+**: 编程语言

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

### Fluent版本（推荐）
```bash
python main_fluent.py
```

### 传统版本
```bash
python main.py
```

## 项目结构

```
ProcessManager/
├── main_fluent.py              # Fluent版本主入口
├── fluent_main_window.py       # Fluent主窗口
├── fluent_ui_components.py     # Fluent界面组件
├── business_logic.py           # 业务逻辑层
├── main.py                     # 传统版本主入口
├── ui_components.py            # 传统界面组件
├── system_monitor.py           # 传统系统监控
├── styles.py                   # 传统样式
├── requirements.txt            # 依赖列表
└── README_FLUENT.md           # 本文档
```

## 架构优势

### 1. 清晰的分层架构
- **业务逻辑层**: 专注于数据处理和业务规则
- **界面组件层**: 专注于UI展示和用户交互
- **主窗口层**: 负责界面组织和事件协调

### 2. 松耦合设计
- 业务逻辑与界面完全分离
- 基于信号槽的异步通信
- 易于测试和维护

### 3. 可扩展性
- 新功能可以独立开发和集成
- 界面和业务逻辑可以独立演进
- 支持插件化扩展

### 4. 现代化体验
- 流畅的动画效果
- 响应式设计
- 符合现代UI设计规范

## 开发说明

### 添加新功能
1. 在`business_logic.py`中添加业务服务类
2. 在`fluent_ui_components.py`中创建对应的UI组件
3. 在`fluent_main_window.py`中集成新的界面
4. 连接信号槽实现数据流转

### 自定义主题
可以通过修改`fluent_main_window.py`中的主题设置来自定义界面外观：

```python
setTheme(Theme.DARK)  # 深色主题
setThemeColor('#ff6b6b')  # 自定义主题色
```

## 性能优化

- 使用缓存机制减少系统调用频率
- 异步数据获取避免界面卡顿
- 限制显示的进程数量避免性能问题
- 智能刷新策略减少资源消耗

## 兼容性

- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+)
- Python 3.9+

## 许可证

MIT License

## 更新日志

### v3.0 (Fluent版本)
- 全新的Fluent Design界面
- 重构架构，业务逻辑与界面分离
- 新增现代化UI组件
- 优化性能和用户体验
- 支持主题切换

### v2.0 (传统版本)
- 基础功能实现
- 传统Qt界面设计
- 系统监控和进程管理功能
