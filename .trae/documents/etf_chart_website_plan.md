# ETF 图表网站开发计划

## 1. 项目概述

基于附件图表设计，开发一个能够动态更新中证A股全收益指数数据的网站。网站需集成 baostock 作为数据源，实现定期数据获取、图表展示、实时更新、响应式布局和交互功能。

## 2. 需求分析

### 2.1 图表内容分析（基于附件图片）

网站需要展示以下三个核心图表：

1. **中证A股全收益指数五年之锚**
   - 主图：中证A股全收益指数走势（黑色线）
   - 辅助线：SMA1210（1210日简单移动平均线，蓝色线）
   - 带状区域：基于SMA的上下通道/置信区间（浅蓝色半透明带）
   - 指标：乖离率（当前值 +31.56%）
   - Y轴：指数点位（500-8000）
   - X轴：时间（2008-2024）

2. **中证A股全收益 RSI14 (周)**
   - RSI14周线指标
   - 参考线：80（超买）、60、50、40、20（超卖）
   - 当前值标注：61.96
   - Y轴：0-100

3. **滚动5年最大回撤**
   - 滚动计算5年期的最大回撤曲线
   - 最小值标注：-55.59%
   - Y轴：百分比（-60% ~ 0%）

### 2.2 功能需求

| 需求编号 | 需求描述 | 优先级 |
|---------|---------|--------|
| F1 | 集成 baostock 获取中证A股全收益指数历史数据 | 高 |
| F2 | 计算 SMA1210 及上下通道 | 高 |
| F3 | 计算 RSI14 (周线) | 高 |
| F4 | 计算滚动5年最大回撤 | 高 |
| F5 | 设计并实现与附件一致的前端界面 | 高 |
| F6 | 数据定时更新机制（每日/每周自动刷新） | 高 |
| F7 | 响应式布局，适配不同设备 | 高 |
| F8 | 时间范围选择交互 | 中 |
| F9 | 数据加载状态反馈 | 中 |
| F10 | 数据筛选功能 | 中 |

## 3. 技术架构

### 3.1 技术栈

**前端：**
- Vue 3 + TypeScript（组合式 API）
- Vite（构建工具）
- ECharts 5（图表库，支持响应式和丰富交互）
- Axios（HTTP 客户端）
- Pinia（状态管理）
- Tailwind CSS（样式框架）

**后端：**
- Python 3.11+
- FastAPI（Web 框架）
- baostock（金融数据接口）
- pandas（数据处理）
- numpy（数值计算）
- APScheduler（定时任务）
- SQLite（轻量级数据缓存）

### 3.2 项目结构

```
etf_01/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── chart.py       # 图表数据 API
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── baostock_service.py  # baostock 数据获取
│   │   │   ├── indicator_service.py # 指标计算
│   │   │   └── cache_service.py     # 数据缓存
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py     # Pydantic 模型
│   │   └── tasks/
│   │       ├── __init__.py
│   │       └── scheduler.py   # 定时任务
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartContainer.vue    # 图表容器
│   │   │   ├── MainChart.vue         # 主图（五年之锚）
│   │   │   ├── RsiChart.vue          # RSI 图
│   │   │   ├── DrawdownChart.vue     # 回撤图
│   │   │   ├── ChartLegend.vue       # 图例
│   │   │   ├── TimeRangeSelector.vue # 时间范围选择
│   │   │   └── LoadingOverlay.vue    # 加载状态
│   │   ├── views/
│   │   │   └── Dashboard.vue         # 主页面
│   │   ├── stores/
│   │   │   └── chartStore.ts         # Pinia 状态管理
│   │   ├── api/
│   │   │   └── chart.ts              # API 接口
│   │   ├── types/
│   │   │   └── chart.ts              # TypeScript 类型
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── .trae/documents/
│   └── etf_chart_website_plan.md     # 本计划文档
└── README.md
```

## 4. 后端设计

### 4.1 API 设计

```
GET /api/v1/chart/data
  Query Params:
    - index_code: str = "sh.000001" (指数代码)
    - start_date: str | null (开始日期)
    - end_date: str | null (结束日期)
  Response:
    {
      "dates": ["2024-01-01", ...],
      "index_values": [3000.5, ...],
      "sma1210": [2800.3, ...],
      "upper_band": [3200.1, ...],
      "lower_band": [2400.5, ...],
      "deviation_rate": 31.56,
      "rsi14": [55.2, ...],
      "drawdown_5y": [-15.3, ...],
      "min_drawdown": -55.59
    }

GET /api/v1/chart/health
  Response: {"status": "ok", "last_update": "2024-01-01T00:00:00"}
```

### 4.2 数据流

1. **初始化/定时任务**：
   - APScheduler 每日 17:00 执行数据更新任务
   - 调用 baostock 获取最新日线数据
   - 存入 SQLite 缓存

2. **指标计算**：
   - SMA1210：1210 日简单移动平均
   - 通道：SMA ± N * 标准差（根据图表视觉调整 N）
   - RSI14：14 周期相对强弱指数（周线需先转周 K）
   - 滚动 5 年最大回撤：滚动 1260 交易日窗口计算

3. **API 响应**：
   - 优先从缓存读取
   - 缓存 miss 或过期时重新计算

## 5. 前端设计

### 5.1 视觉风格

- 整体风格：专业金融图表，简洁清晰
- 配色方案：
  - 主线条：#333333（深灰/黑色）
  - SMA线：#4472C4（蓝色）
  - 通道带：rgba(68, 114, 196, 0.15)（浅蓝半透明）
  - RSI参考线：#999999（灰色虚线）
  - 背景：#FFFFFF
  - 网格线：#E0E0E0
- 字体：系统默认无衬线字体

### 5.2 组件设计

**Dashboard.vue（主页面）**
- 顶部标题栏："中证A股全收益指数五年之锚"
- 中部：三个图表垂直排列
- 底部：数据来源说明、时间戳
- 右上角：时间范围选择器、刷新按钮

**MainChart.vue（主图）**
- 双 Y 轴（左侧指数点位）
- 线图：指数走势 + SMA1210
- 面积图：上下通道带
- 标注：当前乖离率

**RsiChart.vue（RSI）**
- 单线图：RSI14
- 水平参考线：80/60/50/40/20
- 标注：当前 RSI 值

**DrawdownChart.vue（回撤）**
- 单线图：滚动 5 年最大回撤
- 标注：历史最小值

### 5.3 响应式策略

- 桌面端（>1024px）：三图垂直排列，全宽展示
- 平板端（768-1024px）：保持布局，适当缩小字体
- 移动端（<768px）：图表高度自适应，简化部分标注

### 5.4 交互功能

- 时间范围选择：预设（全部/5年/3年/1年）或自定义
- 数据刷新：手动刷新按钮 + 自动刷新提示
- 图表交互：缩放、平移、tooltip 详情
- 加载状态：骨架屏 + 进度提示

## 6. 实施步骤

### 阶段一：后端基础（第 1-2 天）

1. 初始化 FastAPI 项目结构
2. 集成 baostock，实现数据获取服务
3. 实现 SQLite 缓存机制
4. 实现指标计算服务（SMA、RSI、回撤）
5. 实现 Chart API
6. 配置 APScheduler 定时任务

### 阶段二：前端基础（第 3-4 天）

1. 初始化 Vue 3 + Vite 项目
2. 配置 Tailwind CSS、ECharts
3. 实现 API 接口层
4. 实现 Pinia 状态管理
5. 实现三个核心图表组件
6. 实现 Dashboard 页面布局

### 阶段三：交互与优化（第 5-6 天）

1. 实现时间范围选择器
2. 实现数据加载状态反馈
3. 实现响应式布局适配
4. 图表交互优化（tooltip、缩放）
5. 性能优化（数据分页、懒加载）
6. 错误处理与重试机制

### 阶段四：联调与部署（第 7 天）

1. 前后端联调
2. 数据准确性验证
3. 编写 README 文档
4. 准备部署配置（Docker）

## 7. 关键技术细节

### 7.1 baostock 集成

```python
import baostock as bs

# 登录
lg = bs.login()

# 获取历史数据
rs = bs.query_history_k_data_plus(
    "sh.000001",
    "date,close",
    start_date='2005-01-01',
    frequency='d',
    adjustflag='3'  # 复权
)
```

### 7.2 指标计算

**SMA1210：**
```python
df['sma1210'] = df['close'].rolling(window=1210).mean()
```

**RSI14（周线）：**
```python
# 先合成周K，再计算RSI
weekly = df.resample('W').last()
delta = weekly['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
weekly['rsi14'] = 100 - (100 / (1 + rs))
```

**滚动5年最大回撤：**
```python
rolling_max = df['close'].rolling(window=1260).max()
drawdown = (df['close'] - rolling_max) / rolling_max * 100
```

### 7.3 性能考虑

- 后端：数据缓存 1 天，减少 baostock 调用
- 前端：ECharts dataZoom 处理大数据量，虚拟滚动
- 传输：API 响应启用 gzip 压缩

## 8. 风险与应对

| 风险 | 影响 | 应对措施 |
|-----|------|---------|
| baostock 服务不稳定 | 高 | 增加重试机制 + 本地缓存 |
| 历史数据量大 | 中 | 分页加载 + 增量更新 |
| 计算密集型操作慢 | 中 | 异步任务 + 缓存预计算 |
| 跨域问题 | 低 | FastAPI CORS 配置 |

## 9. 验收标准

- [ ] 后端能稳定获取 baostock 数据并正确计算指标
- [ ] 前端图表视觉风格与附件一致
- [ ] 支持时间范围选择和数据筛选
- [ ] 响应式适配桌面端、平板、手机
- [ ] 数据更新不影响用户体验
- [ ] 提供清晰的加载状态反馈
