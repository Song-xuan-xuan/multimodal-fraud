import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationRaw, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export const appRouteName = {
  login: 'login',
  register: 'register',
  home: 'home',
  dashboard: 'dashboard',
  newsList: 'news-list',
  newsDetail: 'news-detail',
  forum: 'forum',
  crowdsource: 'crowdsource',
  thirdPartyServices: 'third-party-services',
  edu: 'edu',
  sandbox: 'sandbox',
  question: 'question',
  stages: 'stages',
  educationCoach: 'education-coach',
  map: 'map',
  aiDetect: 'ai-detect',
  newsDetect: 'news-detect',
  classify: 'classify',
  factCheck: 'fact-check',
  aiChat: 'ai-chat',
  aiAssistant: 'ai-assistant',
  agent: 'agent',
  insightHotspot: 'insight-hotspot',
  insightKnowledgeGraph: 'insight-knowledge-graph',
  report: 'report',
  adminReviewWorkbench: 'admin-review-workbench',
  profile: 'profile',
} as const

export const appRoute = {
  login: { name: appRouteName.login },
  register: { name: appRouteName.register },
  home: { name: appRouteName.home },
  dashboard: { name: appRouteName.dashboard },
  newsList: (keyword?: string) => ({
    name: appRouteName.newsList,
    ...(keyword ? { query: { keyword } } : {}),
  }),
  newsDetail: (id: string | number) => ({
    name: appRouteName.newsDetail,
    params: { id: String(id) },
  }),
  forum: { name: appRouteName.forum },
  crowdsource: { name: appRouteName.crowdsource },
  thirdPartyServices: { name: appRouteName.thirdPartyServices },
  edu: { name: appRouteName.edu },
  sandbox: { name: appRouteName.sandbox },
  question: { name: appRouteName.question },
  stages: { name: appRouteName.stages },
  educationCoach: { name: appRouteName.educationCoach },
  map: { name: appRouteName.map },
  aiDetect: { name: appRouteName.aiDetect },
  newsDetect: { name: appRouteName.newsDetect },
  classify: { name: appRouteName.classify },
  factCheck: { name: appRouteName.factCheck },
  aiChat: { name: appRouteName.aiChat },
  aiAssistant: { name: appRouteName.aiAssistant },
  agent: { name: appRouteName.agent },
  insightHotspot: { name: appRouteName.insightHotspot },
  insightKnowledgeGraph: { name: appRouteName.insightKnowledgeGraph },
  report: { name: appRouteName.report },
  adminReviewWorkbench: { name: appRouteName.adminReviewWorkbench },
  profile: { name: appRouteName.profile },
} as const

const pathRouteMap: Record<string, RouteLocationRaw> = {
  '/': appRoute.home,
  '/login': appRoute.login,
  '/register': appRoute.register,
  '/dashboard': appRoute.dashboard,
  '/news': appRoute.newsList(),
  '/community/forum': appRoute.forum,
  '/community/crowdsource': appRoute.crowdsource,
  '/community/third-party-services': appRoute.thirdPartyServices,
  '/education': appRoute.edu,
  '/education/sandbox': appRoute.sandbox,
  '/education/question': appRoute.question,
  '/education/stages': appRoute.stages,
  '/education/coach': appRoute.educationCoach,
  '/map': appRoute.map,
  '/detection/ai': appRoute.aiDetect,
  '/detection/news': appRoute.newsDetect,
  '/detection/classify': appRoute.classify,
  '/fact-check': appRoute.factCheck,
  '/ai/chat': appRoute.aiChat,
  '/ai/assistant': appRoute.aiAssistant,
  '/ai/agent': appRoute.agent,
  '/insight/hotspot': appRoute.insightHotspot,
  '/insight/knowledge-graph': appRoute.insightKnowledgeGraph,
  '/report': appRoute.report,
  '/admin/review-workbench': appRoute.adminReviewWorkbench,
  '/profile': appRoute.profile,
}

export function normalizeAppRouteTarget(target: RouteLocationRaw): RouteLocationRaw {
  if (typeof target !== 'string') {
    return target.path ? normalizeAppRouteTarget(target.path) : target
  }

  const newsDetailMatch = target.match(/^\/news\/([^/?#]+)/)
  if (newsDetailMatch) {
    return appRoute.newsDetail(newsDetailMatch[1])
  }

  return pathRouteMap[target] || { path: target }
}

type AppRouteMeta = {
  requiresAuth?: boolean
  adminOnly?: boolean
  layout: 'auth' | 'frontend' | 'backend'
  pageGroup: string
  pageTitle: string
  motionPreset: 'fade' | 'slide-up' | 'slide-left'
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: appRouteName.login,
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      requiresAuth: false,
      layout: 'auth',
      pageGroup: '账户',
      pageTitle: '登录',
      motionPreset: 'fade',
    } satisfies AppRouteMeta,
  },
  {
    path: '/register',
    name: appRouteName.register,
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: {
      requiresAuth: false,
      layout: 'auth',
      pageGroup: '账户',
      pageTitle: '注册',
      motionPreset: 'fade',
    } satisfies AppRouteMeta,
  },
  {
    path: '/',
    name: appRouteName.home,
    component: () => import('@/views/portal/HomeView.vue'),
    meta: {
      requiresAuth: false,
      layout: 'frontend',
      pageGroup: '前台首页',
      pageTitle: '首页',
      motionPreset: 'fade',
    } satisfies AppRouteMeta,
  },
  {
    path: '/dashboard',
    name: appRouteName.dashboard,
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '风险洞察',
      pageTitle: '风险看板',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/news',
    name: appRouteName.newsList,
    component: () => import('@/views/news/NewsListView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈治理',
      pageTitle: '案例库',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/news/:id',
    name: appRouteName.newsDetail,
    component: () => import('@/views/news/NewsDetailView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈治理',
      pageTitle: '新闻详情',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/community/forum',
    name: appRouteName.forum,
    component: () => import('@/views/community/ForumView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '社区治理',
      pageTitle: '论坛',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/community/crowdsource',
    name: appRouteName.crowdsource,
    component: () => import('@/views/community/CrowdsourceView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '社区治理',
      pageTitle: '众包社区',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/community/third-party-services',
    name: appRouteName.thirdPartyServices,
    component: () => import('@/views/community/ThirdPartyServicesView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '社区治理',
      pageTitle: '第三方服务',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/education',
    name: appRouteName.edu,
    component: () => import('@/views/education/EduView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈训练',
      pageTitle: '教育研学',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/education/sandbox',
    name: appRouteName.sandbox,
    component: () => import('@/views/education/SandboxView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈训练',
      pageTitle: '沙盒',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/education/question',
    name: appRouteName.question,
    component: () => import('@/views/education/QuestionView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈训练',
      pageTitle: '测试',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/education/stages',
    name: appRouteName.stages,
    component: () => import('@/views/education/StagesView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈训练',
      pageTitle: '学习阶段',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/education/coach',
    name: appRouteName.educationCoach,
    component: () => import('@/views/education/CoachView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈训练',
      pageTitle: '反诈教练',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/map',
    name: appRouteName.map,
    component: () => import('@/views/map/MapView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '风险洞察',
      pageTitle: '传播地图',
      motionPreset: 'slide-up',
    } satisfies AppRouteMeta,
  },
  {
    path: '/detection/ai',
    name: appRouteName.aiDetect,
    component: () => import('@/views/detection/AIDetectView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '专项分析',
      pageTitle: '专项分析',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/detection/news',
    name: appRouteName.newsDetect,
    component: () => import('@/views/detection/NewsDetectView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '专项分析',
      pageTitle: '内容风险检测',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/detection/classify',
    name: appRouteName.classify,
    component: () => import('@/views/detection/FakeNewsClassifyView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '专项分析',
      pageTitle: '话术分类识别',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/fact-check',
    name: appRouteName.factCheck,
    component: () => import('@/views/fact-check/FactCheckView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '专项分析',
      pageTitle: '风险核验',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/ai/chat',
    name: appRouteName.aiChat,
    component: () => import('@/views/ai/AIChatView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '反诈顾问',
      pageTitle: '反诈咨询',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/ai/assistant',
    name: appRouteName.aiAssistant,
    component: () => import('@/views/ai/AIAssistantView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '反诈顾问',
      pageTitle: '反诈助手',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/ai/agent',
    name: appRouteName.agent,
    component: () => import('@/views/ai/AgentView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'frontend',
      pageGroup: '反诈顾问',
      pageTitle: '多模态分析',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/insight/hotspot',
    name: appRouteName.insightHotspot,
    component: () => import('@/views/insight/HotspotView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '风险洞察',
      pageTitle: '风险热点',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/insight/knowledge-graph',
    name: appRouteName.insightKnowledgeGraph,
    component: () => import('@/views/insight/KnowledgeGraphView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '风险洞察',
      pageTitle: '风险图谱',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/report',
    name: appRouteName.report,
    component: () => import('@/views/report/ReportView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '反诈治理',
      pageTitle: '线索上报',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
  {
    path: '/admin/review-workbench',
    name: appRouteName.adminReviewWorkbench,
    component: () => import('@/views/admin/ReviewWorkbenchView.vue'),
    meta: { adminOnly: true },
  },
  {
    path: '/profile',
    name: appRouteName.profile,
    component: () => import('@/views/profile/ProfileView.vue'),
    meta: {
      requiresAuth: true,
      layout: 'backend',
      pageGroup: '个人账户',
      pageTitle: '个人账户',
      motionPreset: 'slide-left',
    } satisfies AppRouteMeta,
  },
]

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
  routes: routes.map((route) => {
    if (route.name === appRouteName.adminReviewWorkbench) {
      return {
        ...route,
        meta: {
          requiresAuth: true,
          layout: 'backend',
          pageGroup: '反诈治理',
          pageTitle: '治理工作台',
          motionPreset: 'slide-left',
          ...(route.meta || {}),
        } satisfies AppRouteMeta,
      }
    }

    return route
  }),
})

const CHUNK_RELOAD_GUARD_KEY = 'app_chunk_reload_guard'

router.onError((error, to) => {
  const message = error instanceof Error ? error.message : String(error || '')
  const isChunkLoadError =
    /Failed to fetch dynamically imported module/i.test(message) ||
    /Importing a module script failed/i.test(message) ||
    /Loading chunk [\d\w-]+ failed/i.test(message)

  if (!isChunkLoadError || typeof window === 'undefined') {
    console.error('[router] navigation error:', error)
    return
  }

  const currentGuard = window.sessionStorage.getItem(CHUNK_RELOAD_GUARD_KEY)
  const targetPath = typeof to?.fullPath === 'string' && to.fullPath ? to.fullPath : window.location.pathname

  if (currentGuard === targetPath) {
    window.sessionStorage.removeItem(CHUNK_RELOAD_GUARD_KEY)
    console.error('[router] chunk reload failed after retry:', error)
    return
  }

  window.sessionStorage.setItem(CHUNK_RELOAD_GUARD_KEY, targetPath)
  window.location.assign(targetPath)
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth !== false && !authStore.isLoggedIn) {
    return {
      name: appRouteName.home,
      query: {
        auth: 'login',
        redirect: typeof to.fullPath === 'string' ? to.fullPath : '/',
      },
    }
  }

  if (to.meta.adminOnly) {
    const username = (authStore.username || '').trim().toLowerCase()
    const adminAllowlist = ['admin', 'administrator', 'superadmin']
    if (!adminAllowlist.includes(username)) {
      return { name: appRouteName.dashboard }
    }
  }

  if ((to.name === appRouteName.login || to.name === appRouteName.register) && !authStore.isLoggedIn) {
    return {
      name: appRouteName.home,
      query: {
        auth: to.name === appRouteName.register ? 'register' : 'login',
      },
    }
  }
})

export default router

