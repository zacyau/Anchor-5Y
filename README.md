# Anchor-5Y | 国证A股指数五年之锚

基于 Vue 3 + FastAPI 的 A 股指数技术分析可视化平台，集成 baostock 金融数据源，提供国证A股指数的五年之锚（SMA1210 包络线）、RSI 指标和滚动最大回撤三个核心图表。

## 功能特性

- **五年之锚图表**：国证A股指数走势 + SMA1210 ±15% 包络线 + 实时乖离率
- **RSI 指标**：周线 Wilder RSI14，含超买超卖参考线（80/60/50/40/20）
- **滚动最大回撤**：滚动 5 年（1260 交易日）最大回撤曲线
- **时间范围选择**：全部 / 5年 / 3年 / 1年 / 自定义日期
- **数据缓存**：SQLite 本地缓存，24 小时 TTL，减少 baostock 调用
- **定时刷新**：APScheduler 每日 20:00 自动更新数据
- **响应式布局**：适配桌面端、平板、移动端
- **交互功能**：ECharts 缩放/平移/Tooltip 悬停详情

## 技术栈

### 前端

| 技术 | 用途 |
|------|------|
| Vue 3 + TypeScript | 组合式 API 框架 |
| Vite | 构建工具 |
| ECharts 5 + Vue-ECharts | 图表渲染 |
| Pinia | 状态管理 |
| Tailwind CSS | 样式框架 |

### 后端

| 技术 | 用途 |
|------|------|
| FastAPI | Web API 框架 |
| baostock | A 股金融数据源 |
| pandas + numpy | 数据处理与指标计算 |
| APScheduler | 定时任务调度 |
| SQLite | 本地数据缓存 |
| Pydantic | 数据校验 |

## 项目结构

```
etf_01/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── config.py                # Pydantic 配置管理
│   │   ├── routers/
│   │   │   └── chart.py             # 图表 API /api/v1/chart/
│   │   ├── services/
│   │   │   ├── baostock_service.py  # baostock 数据获取
│   │   │   ├── indicator_service.py # 指标计算（SMA/RSI/回撤）
│   │   │   └── cache_service.py     # SQLite 缓存服务
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic 响应模型
│   │   └── tasks/
│   │       └── scheduler.py         # APScheduler 定时任务
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MainChart.vue        # 五年之锚主图
│   │   │   ├── RsiChart.vue         # RSI 周线图
│   │   │   ├── DrawdownChart.vue    # 滚动最大回撤图
│   │   │   ├── TimeRangeSelector.vue
│   │   │   └── LoadingOverlay.vue
│   │   ├── views/
│   │   │   └── Dashboard.vue        # 主页面
│   │   ├── stores/
│   │   │   └── chartStore.ts        # Pinia 状态管理
│   │   ├── api/
│   │   │   └── chart.ts             # Axios API 封装
│   │   ├── types/
│   │   │   └── chart.ts             # TypeScript 类型定义
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 9+

### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（开发模式，自动重载）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端运行在 `http://localhost:8000`，API 文档见 `http://localhost:8000/docs`。

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`，默认代理后端 API 到 `http://localhost:8000`。

### 3. 访问

浏览器打开 `http://localhost:5173`，首次加载会从 baostock 获取完整历史数据（约 5000+ 交易日），后续使用本地缓存。

## API 接口

### GET `/api/v1/chart/data`

获取图表全部数据。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `index_code` | string | `sz.399317` | 指数代码 |
| `start_date` | string | null | 起始日期 YYYY-MM-DD |
| `end_date` | string | null | 结束日期 YYYY-MM-DD |

返回：
```json
{
  "dates": ["2003-01-02", ...],
  "index_values": [1000.0, ...],
  "sma1210": [null, ...],
  "upper_band": [null, ...],
  "lower_band": [null, ...],
  "deviation_rate": 12.34,
  "rsi_daily": [null, ...],
  "current_rsi": 55.5,
  "drawdown_5y": [0.0, ...],
  "min_drawdown": -55.59,
  "last_update": "2026-05-03 20:00:00"
}
```

### GET `/api/v1/chart/health`

健康检查。

### POST `/api/v1/chart/refresh`

手动刷新数据，强制从 baostock 获取最新数据。

## 指标计算说明

| 指标 | 算法 | 参数 |
|------|------|------|
| SMA1210 | `close.rolling(1210).mean()` | 窗口 1210 日 ≈ 5 年 |
| 包络上轨 | `SMA1210 × (1 + 15%)` | 固定百分比通道 |
| 包络下轨 | `SMA1210 × (1 - 15%)` | 固定百分比通道 |
| RSI14(周) | Wilder EMA 平滑 | 日→周 resample → RSI(14) |
| 滚动 5 年最大回撤 | `(close - rolling_max_1260) / rolling_max_1260 × 100` | 1260 交易日 |

## 配置

后端配置通过环境变量或 `.env` 文件管理（[config.py](backend/app/config.py)）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `true` | 调试模式 |
| `HOST` | `0.0.0.0` | 监听地址 |
| `PORT` | `8000` | 监听端口 |
| `CACHE_TTL_HOURS` | `24` | 缓存有效期（小时） |
| `DATA_UPDATE_HOUR` | `20` | 定时更新时间（小时） |
| `DATA_UPDATE_MINUTE` | `0` | 定时更新时间（分钟） |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | 允许的跨域来源 |

## 数据来源

- 指数数据：[baostock](http://baostock.com/) — `sz.399317` 国证A股指数
- 数据范围：2003-01-02 ~ 至今（5000+ 交易日）
- 缓存策略：SQLite 本地存储，24 小时自动刷新
