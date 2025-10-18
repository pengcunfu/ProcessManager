# 系统监控与进程管理工具 v3.0 (MVC架构)

一个使用 PySide6 和 Fluent-Widgets 开发的现代化系统监控和进程管理工具，采用标准MVC架构设计。

## ✨ 主要特性

### 🔧 系统信息
- 实时CPU、内存、磁盘使用率监控
- 系统启动时间和运行时间
- 进程数量统计
- CPU信息（核心数、频率）
- 内存信息（总量、使用情况、交换内存）
- 磁盘信息（所有分区的使用情况）
- 网络接口信息（IP、MAC地址）
- 美观的进度条和卡片式展示

### 📊 进程管理
- 显示所有运行中的进程（PID、名称、CPU%、内存%等）
- 搜索和过滤进程
- 结束/强制结束进程
- 查看进程详细信息
- 多种排序方式

### 🌐 网络监控
- 显示所有网络连接（TCP/UDP）
- 按协议和状态过滤
- 显示本地/远程地址和端口
- 关联进程PID

### 🎨 现代化界面
- 基于Fluent Design设计风格
- 响应式布局
- 自动/手动主题切换
- 流畅的动画效果

## 📁 项目结构（MVC架构）

```
ProcessManager/
├── app.py                      # 🚀 主入口文件（推荐使用）
│
├── models/                     # 📦 模型层（数据模型）
│   ├── __init__.py
│   ├── system_models.py        # SystemInfo, ProcessInfo, NetworkConnection
│   └── utils.py                # 工具函数：format_bytes, format_frequency
│
├── views/                      # 🎨 视图层（UI界面）
│   ├── __init__.py
│   ├── main_window.py          # 主窗口和应用程序类
│   ├── ui_components.py        # UI组件：卡片、表格等
│   └── ui_utils.py             # UI工具：消息提示函数
│
├── controllers/                # 🎮 控制器层（业务逻辑）
│   ├── __init__.py
│   ├── system_controller.py    # 系统监控控制器
│   ├── process_controller.py   # 进程管理控制器
│   ├── network_controller.py   # 网络监控控制器
│   └── hardware_controller.py  # 硬件信息控制器
│
├── v1/                         # 📦 v1版本（经典版本，已归档）
│   ├── main.py
│   ├── styles.py
│   ├── system_monitor.py
│   └── ui_components.py
│
├── requirements.txt            # 依赖包列表
├── README.md                   # 本文件
├── MVC_ARCHITECTURE.md         # 📖 MVC架构详细说明
└── OPTIMIZATION_SUMMARY.md     # 性能优化总结
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

#### ✨ 推荐方式：使用MVC架构版本
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

## 📖 架构说明

本项目采用**标准MVC（Model-View-Controller）架构**：

- **Model（模型层）**: 定义数据结构（`SystemInfo`, `ProcessInfo`, `NetworkConnection`）
- **View（视图层）**: 负责UI展示和用户交互
- **Controller（控制器层）**: 处理业务逻辑，协调Model和View

**详细架构说明请查看**: [MVC_ARCHITECTURE.md](MVC_ARCHITECTURE.md)

### 数据流向

```
用户操作 → View → Controller → psutil → Model → Controller → View → 显示
```

## 🎯 使用说明

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

### 网络监控
1. 切换到"网络监控"标签页
2. 使用协议和状态过滤器筛选连接
3. 查看每个连接的详细信息

## ⚡ 性能优化

- **启动速度**: < 1秒（优化后提升70-80%）
- **延迟加载**: UI组件按需创建
- **智能缓存**: 减少重复系统调用
- **异步初始化**: 避免阻塞主线程

详细优化说明请查看: [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)

## 📋 技术栈

- **GUI框架**: PySide6 (Qt6)
- **UI库**: PySide6-Fluent-Widgets
- **系统监控**: psutil
- **架构**: MVC
- **Python版本**: 3.8+

## ⚠️ 注意事项

1. 某些功能可能需要管理员权限
2. 进程详细信息（exe路径、线程数等）需要点击"详细信息"查看
3. 最多显示200个进程和500个网络连接（性能优化）
4. CPU使用率在前几次更新时可能不够精确

## 🔧 故障排除

**Q: 程序无法启动**  
A: 确保已安装所有依赖：`pip install -r requirements.txt`

**Q: 某些进程信息显示为N/A**  
A: 权限不足，请以管理员身份运行

**Q: 网络信息不完整**  
A: 需要更高权限访问，请以管理员身份运行

## 📝 开发信息

- **版本**: v3.0 (MVC架构)
- **开发语言**: Python 3.8+
- **架构模式**: MVC
- **最后更新**: 2025-10-18

## 📜 许可证

本项目仅供学习和个人使用。

---

**Enjoy monitoring your system!** 🚀

**查看更多**:
- [MVC架构详细说明](MVC_ARCHITECTURE.md)
- [性能优化总结](OPTIMIZATION_SUMMARY.md)
- [v1版本说明](v1/README_V1.md)
