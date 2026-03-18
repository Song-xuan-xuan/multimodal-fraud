# 页面分层与首批改版锚点

## 1. 目标

本清单用于落实 `AFSO-010`，把当前前端页面固定到统一的体验线分层中，并冻结第一批视觉改版锚点页。后续页面迁移、布局重构和样板页复用都必须引用本文件中的分层命名，不得绕开审议随意新增锚点页。

## 2. 三条体验线

### 2.1 前台门户

定义：承担品牌入口、公共引导、轻任务入口和工具前台承载，强调可信度、入口清晰度和转化节奏。

包含页面：

- `HomeView`：品牌首页与入口总览。
- `AIDetectView`、`NewsDetectView`、`FakeNewsClassifyView`、`FactCheckView`：专项分析前台的工具入口和任务页。
- `AIChatView`、`AIAssistantView`、`AgentView`：前台化的咨询、助手和多模态分析工作流。

布局依据：`router` 中这些页面使用 `layout: 'frontend'`，对应前台入口与工具工作流语义。

### 2.2 专项分析前台

定义：前台门户中的高密度工具流子集，强调输入、处理中间态、结果输出和证据展示。

包含页面：

- `AIDetectView`
- `NewsDetectView`
- `FakeNewsClassifyView`
- `FactCheckView`
- `AgentView`

说明：该层不是独立路由布局，而是从前台门户中单独抽出的“高信息密度工具工作流”类别，后续样式评审可用来区分门户型首页与工具型页面。

### 2.3 治理后台

定义：承担风险洞察、治理任务、案例库、线索处理、训练与个人后台能力，强调工作台稳定性、数据密度和操作效率。

包含页面：

- `DashboardView`、`HotspotView`、`KnowledgeGraphView`、`MapView`
- `NewsListView`、`NewsDetailView`、`NewsAggregateView`、`ReportView`
- `ForumView`、`CrowdsourceView`、`LeaderboardView`、`ThirdPartyServicesView`
- `EduView`、`SandboxView`、`QuestionView`、`StagesView`、`CoachView`
- `ReviewWorkbenchView`、`ProfileView`
- `CrowdBoardView`

布局依据：以上页面主要使用 `layout: 'backend'`，或服务于治理后台流程。

## 3. 首批改版锚点

首批只冻结以下三张样板页，作为后续所有视觉迁移的参照物：

1. `HomeView`
2. `DashboardView`
3. `AIDetectView`

冻结理由：

- `HomeView` 代表品牌首页与门户级信息编排。
- `DashboardView` 代表治理后台的驾驶舱与指标密度。
- `AIDetectView` 代表专项分析前台的工具工作流、输入输出和结果态。

这三页分别覆盖首页、后台、工具工作流三类内容密度，足以支撑后续页面复用和扩散。

## 4. 后续迁移映射规则

- 后续任务必须先声明自己属于“前台门户 / 专项分析前台 / 治理后台”哪一层，再进入具体视觉改版。
- 未在首批锚点中的页面，只能复用首批样板页建立的布局节奏、组件边界和语义 token，不得自行发明新视觉中心。
- 若出现无法映射到三条体验线的页面，必须先补本文件并在 issue `notes` 中写明依据，再继续改版。

## 5. 新增锚点准入规则

默认禁止新增首批锚点页。确需新增时，必须同时满足：

- 现有三张锚点页无法覆盖该页面的信息密度或任务流。
- 在对应 issue 的 `notes` 或 `refs` 中记录新增理由。
- 明确说明该新增锚点是补充哪一类体验线的空白，而不是重复已有样板页。

未满足上述条件前，不得把任何页面标记为新的首批锚点。

## 6. 直接引用入口

- `src/router/index.ts`：体验线与页面分组的当前路由来源。
- `src/views/portal/HomeView.vue`：门户首页锚点。
- `src/views/dashboard/DashboardView.vue`：治理后台锚点。
- `src/views/detection/AIDetectView.vue`：专项分析前台锚点。
- `docs/design-system/anti-fraud-visual-system.md`：视觉语言与禁用清单基线。
