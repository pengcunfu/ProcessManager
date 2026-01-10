# 系统监控与进程管理工具 v3.1 (MVC架构)

一个使用原生 PySide6 开发的现代化系统监控和进程管理工具，采用标准MVC架构设计。

## 主要特性

### 系统信息
- 实时CPU、内存、磁盘使用率监控
- 系统启动时间和运行时间
- 进程数量统计
- CPU信息（核心数、频率）
- 内存信息（总量、使用情况、交换内存）
- 磁盘信息（所有分区的使用情况）
- 网络接口信息（IP、MAC地址）
- 美观的进度条和卡片式展示

### 进程管理
- 显示所有运行中的进程（PID、名称、CPU%、内存%等）
- 搜索和过滤进程
- 结束/强制结束进程
- 查看进程详细信息
- 多种排序方式

### 网络监控
- 显示所有网络连接（TCP/UDP）
- 按协议和状态过滤
- 显示本地/远程地址和端口
- 关联进程PID

### 流量监控
- 实时显示上传/下载速度（每秒更新）
- 总流量统计（总上传/下载量、收发包数）
- 进程流量分析（每个进程的网络连接数和IO统计）
- 大字体速度显示，清晰易读
- 注意：查看进程流量详情需要管理员权限

### 高级监控
- **温度监控**：CPU温度、硬盘温度等硬件温度监控，带有警告和严重阈值提示
- **电池监控**：电池电量、充电状态、剩余使用时间估算（笔记本专用）
- **系统服务监控**：Windows服务列表、服务状态查看
- **GPU监控**：GPU使用率、显存使用情况（开发中）
- **计划任务**：Windows计划任务列表（开发中）

### 现代化界面
- 原生PySide6界面设计
- 简洁清爽的UI风格
- 响应式布局
- 标签页导航

## 项目结构（MVC架构）

```
ProcessManager/
├── app.py                      # 主入口文件（推荐使用）
│
├── models/                     # 模型层（数据模型）
│   ├── __init__.py
│   ├── system_models.py        # SystemInfo, ProcessInfo, NetworkConnection
│   └── utils.py                # 工具函数：format_bytes, format_frequency
│
├── views/                      # 视图层（UI界面）
│   ├── __init__.py
│   ├── main_window.py          # 主窗口和应用程序类
│   ├── ui_components.py        # UI组件：卡片、表格等
│   └── ui_utils.py             # UI工具：消息提示函数
│
├── controllers/                # 控制器层（业务逻辑）
│   ├── __init__.py
│   ├── system_controller.py    # 系统监控控制器
│   ├── process_controller.py   # 进程管理控制器
│   ├── network_controller.py   # 网络监控控制器
│   ├── hardware_controller.py  # 硬件信息控制器
│   ├── traffic_controller.py   # 流量监控控制器
│   └── advanced_monitor_controller.py  # 高级监控控制器（温度、电池、服务）
│
├── v1/                         # v1版本（经典版本，已归档）
│   ├── main.py
│   ├── styles.py
│   ├── system_monitor.py
│   └── ui_components.py
│
├── requirements.txt            # 依赖包列表
├── README.md                   # 本文件
├── MVC_ARCHITECTURE.md         # MVC架构详细说明
└── OPTIMIZATION_SUMMARY.md     # 性能优化总结
```

## 快速开始

### 环境要求
- Python 3.8+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

#### 推荐方式：使用MVC架构版本
```bash
python app.py
```

#### 其他方式

**运行v1经典版本：**
```bash
python v1/main.py
```

**直接运行视图模块：**
```bash
python views/main_window.py
```

## 架构说明

本项目采用**标准MVC（Model-View-Controller）架构**：

- **Model（模型层）**: 定义数据结构（`SystemInfo`, `ProcessInfo`, `NetworkConnection`）
- **View（视图层）**: 负责UI展示和用户交互
- **Controller（控制器层）**: 处理业务逻辑，协调Model和View

**详细架构说明请查看**: [MVC_ARCHITECTURE.md](MVC_ARCHITECTURE.md)

### 数据流向

```
用户操作 → View → Controller → psutil → Model → Controller → View → 显示
```

## 使用说明

### 系统信息（默认界面）
1. 启动后自动显示"系统信息"标签页
2. 实时查看CPU、内存、磁盘使用率
3. 查看系统启动时间、运行时间、进程数
4. 查看详细的硬件信息：
   - CPU核心数和频率
   - 内存和交换内存情况
   - 所有磁盘分区使用情况
   - 网络接口和IP/MAC地址
5. 点击"刷新"按钮更新硬件信息

### 进程管理
1. 切换到"进程管理"标签页查看所有进程
2. 使用搜索框过滤特定进程
3. 选择进程后，可以：
   - 点击"结束进程"正常结束
   - 点击"强制结束"立即终止
   - 点击"详细信息"查看更多信息
4. 使用排序下拉框按CPU、内存等排序
5. 点击"刷新"按钮或按F5键手动刷新进程列表
   - 注意：进程列表不会自动刷新，需要手动刷新

### 网络监控
1. 切换到"网络监控"标签页
2. 使用协议和状态过滤器筛选连接
3. 查看每个连接的详细信息
4. 点击"刷新"按钮或按F5键手动刷新网络连接
   - 注意：网络连接不会自动刷新，需要手动刷新

### 流量监控
1. 切换到"流量监控"标签页
2. **实时流量监控**：
   - 查看当前上传和下载速度（每秒自动更新）
   - 上传速度显示为红色，下载速度显示为绿色
   - 查看总上传/下载流量和收发包统计
3. **进程流量统计**：
   - 点击"刷新"按钮查看各进程的流量消耗
   - 显示每个进程的PID、进程名、连接数、读取和写入数据量
   - 按连接数降序排列，方便查看网络活跃的进程
   - **注意**：需要以管理员权限运行程序才能查看详细的进程流量信息
   - 显示前50个进程（性能考虑）

## 性能优化

- **启动速度**: < 1秒（优化后提升70-80%）
- **延迟加载**: UI组件按需创建
- **智能缓存**: 减少重复系统调用
- **异步初始化**: 避免阻塞主线程

详细优化说明请查看: [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)

## 技术栈

- **GUI框架**: PySide6 (Qt6) - 原生界面
- **系统监控**: psutil
- **架构**: MVC
- **Python版本**: 3.8+

## 注意事项

1. 某些功能可能需要管理员权限
2. 进程详细信息（exe路径、线程数等）需要点击"详细信息"查看
3. 最多显示200个进程和500个网络连接（性能优化）
4. **进程列表和网络连接不会自动刷新**，需要手动点击"刷新"按钮或按F5键
5. 系统信息（CPU、内存、磁盘）会自动实时更新
6. CPU使用率在前几次更新时可能不够精确

## 故障排除

**Q: 程序无法启动**  
A: 确保已安装所有依赖：`pip install -r requirements.txt`

**Q: 某些进程信息显示为N/A**  
A: 权限不足，请以管理员身份运行

**Q: 网络信息不完整**  
A: 需要更高权限访问，请以管理员身份运行

## 开发信息

- **版本**: v3.0 (MVC架构)
- **开发语言**: Python 3.8+
- **架构模式**: MVC
- **最后更新**: 2025-10-18

## 许可证

本项目仅供学习和个人使用。

---

**Enjoy monitoring your system!**

**查看更多**:
- [MVC架构详细说明](MVC_ARCHITECTURE.md)
- [性能优化总结](OPTIMIZATION_SUMMARY.md)
- [v1版本说明](v1/README_V1.md)
