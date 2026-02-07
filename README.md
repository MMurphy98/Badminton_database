# 🏸 羽毛球数字化开销分析系统

这是一个基于 Python Streamlit 构建的数据可视化看板，旨在帮助羽毛球爱好者记录运动频次、分析开销构成，并追踪装备损耗（如球拍与球线的适配情况）。

## ✨ 功能特性

*   **🏆 竞技座舱 (Dashboard)**: 仿 iOS 风格的 UI 设计，直观展示年度打球时长、资金投入及综合时薪成本。
*   **📊 多维可视化**:
    *   通过饼图分析单打、双打、练球的资金与时间占比。
    *   通过堆叠柱状图展示每周的运动强度与开销趋势。
*   **📝 快捷录入**: 侧边栏集成了双模录入功能，支持快速记录「打球活动」或「新购装备」，数据直接存入 CSV 文件。
*   **🧬 装备透视**: 专门的球线/球拍适配分析面板，帮助分析哪款球线在使用中最易断线，以及球拍的换线频率。

## 📂 文件结构说明

本项目采用模块化架构设计，核心代码按照功能拆分如下：

| 文件/目录 | 说明 |
| :--- | :--- |
| `badminton_app.py` | **主程序入口**。负责组装各模块并启动 Streamlit 应用。 |
| `modules/` | **核心主要模块**。包含应用的具体逻辑实现：<br>• `data_loader.py`: 数据加载、缓存与 CSV 写入逻辑<br>• `sidebar.py`: 侧边栏控制中心与数据录入表单<br>• `tabs.py`: 核心功能标签页（统计、趋势、装备等）的渲染逻辑<br>• `kpi.py`: 顶部 KPI 核心指标卡片<br>• `heatmap.py`: 年度运动热力图组件<br>• `styles.py`: 全局 CSS 注入与样式工具 |
| `themes.py` | **主题配置文件**。定义了应用的多套配色方案（如 Nerd, GitHub, Dracula 等）。 |
| `sessions_cleaned.csv` | **活动数据库**。存储所有的打球记录（日期、类型、费用、时长等）。 |
| `equipment_cleaned.csv` | **装备数据库**。存储所有的装备购买记录（球拍、球线、球鞋等）。 |
| `export_raw_data.ipynb` | **数据转换工具**。用于将原始 Excel 记录 (`羽毛球开销记录.xlsx`) 批量导出为 CSV 的 Jupyter Notebook。 |

## 🚀 快速开始

### 1. 环境准备

确保你的 Python 环境中安装了以下依赖库：

```bash
pip install streamlit pandas plotly openpyxl
```

### 2. 启动应用

在终端中运行以下命令启动看板：

```bash
streamlit run badminton_app.py
```

启动后，浏览器会自动打开 `http://localhost:8501`。

## 💾 数据管理

本项目支持两种数据管理方式：

1.  **APP 直接录入 (推荐)**
    *   在网页左侧侧边栏选择年份。
    *   选择「📝 快速录入」模式（记录打球 / 录入装备）。
    *   填写表单并点击保存，数据会自动追加到 [`sessions_cleaned.csv`](sessions_cleaned.csv ) 或 [`equipment_cleaned.csv`](equipment_cleaned.csv )。

2.  **Excel 批量导入**
    *   如果你习惯在 Excel 中维护数据，可以使用 [`export_raw_data.ipynb`](export_raw_data.ipynb )。
    *   该脚本会读取 [`羽毛球开销记录.xlsx`](羽毛球开销记录.xlsx ) 中的指定 Sheet，并转换为 CSV 文件（注意：脚本默认输出名为 [`sessions.csv`](sessions.csv )，需要根据需要重命名为 `_cleaned.csv` 版本以供 APP 读取）。

## 📝 数据格式示例

**活动记录 (sessions_cleaned.csv)**
```csv
年份,日期,周数,起始时间,结束时间,类型,金额,持续时间,时间段,备注
2026,2026-02-06,6,21:00:00,22:00:00,单打,15.5,1.0,晚上,3人轮单，黑金隼 单线区断线
```

**装备记录 (equipment_cleaned.csv)**
```csv
日期,类型,型号,金额,说明
2026-01-18,球线,Exbolt68,70,ZSP
```

## 🎨 UI 风格

系统采用了自定义 CSS 注入，实现了类 iOS/macOS 的设计语言：
*   **字体**: 优先调用系统原生字体 (SF Pro / PingFang SC)。
*   **卡片**: 带有柔和阴影的圆角卡片设计。
*   **交互**: 优化了按钮与 Tab 的悬停和选中状态。
