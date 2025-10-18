# 系统监控工具 v1.0（经典版本）

这是系统监控工具的第一版本，使用传统的PySide6界面设计。

## 文件说明

- `main.py` - v1版本主入口文件
- `styles.py` - 样式定义
- `system_monitor.py` - 系统监控核心模块
- `ui_components.py` - UI组件模块

## 运行方式

```bash
# 从项目根目录运行
python v1/main.py

# 或者从v1目录运行
cd v1
python main.py
```

## 与v2版本的区别

- **v1（当前版本）**: 使用传统PySide6界面，较为简洁
- **v2（Fluent版本）**: 使用PySide6-Fluent-Widgets，现代化设计，启动更快

## 注意事项

v1版本已停止更新，建议使用项目根目录的Fluent版本（`main_fluent.py`）。

如果需要运行v1版本，请确保：
1. 已安装所有依赖（见项目根目录的requirements.txt）
2. 从正确的目录运行（注意导入路径）

