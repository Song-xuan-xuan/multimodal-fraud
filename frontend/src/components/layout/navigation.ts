import type { RouteLocationRaw } from 'vue-router'
import { appRoute, appRouteName } from '@/router'

export type NavigationItem = {
  label: string
  routeName: string
  route: RouteLocationRaw
}

export type NavigationGroup = {
  index: string
  label: string
  items: NavigationItem[]
}

export const ADMIN_USERNAMES = ['admin', 'administrator', 'superadmin'] as const

export function isAdminUsername(username: string | null | undefined) {
  return ADMIN_USERNAMES.includes(String(username || '').trim().toLowerCase() as (typeof ADMIN_USERNAMES)[number])
}

export const frontendDirectNav = {
  label: '首页',
  routeName: appRouteName.home,
  route: appRoute.home,
}

export const frontendPrimaryNav: NavigationItem[] = [
  { label: '专项分析', routeName: appRouteName.aiDetect, route: appRoute.aiDetect },
  { label: '反诈助手', routeName: appRouteName.aiAssistant, route: appRoute.aiAssistant },
  { label: '多模态分析', routeName: appRouteName.agent, route: appRoute.agent },
]

export const frontendNavGroups: NavigationGroup[] = []

export const backendDirectNav = {
  label: '风险看板',
  routeName: appRouteName.dashboard,
  route: appRoute.dashboard,
}

export function buildBackendNavGroups(username: string | null | undefined): NavigationGroup[] {
  return [
    {
      index: 'backend-insight',
      label: '风险洞察',
      items: [
        { label: '热点追踪', routeName: appRouteName.insightHotspot, route: appRoute.insightHotspot },
        { label: '知识图谱', routeName: appRouteName.insightKnowledgeGraph, route: appRoute.insightKnowledgeGraph },
        { label: '传播地图', routeName: appRouteName.map, route: appRoute.map },
      ],
    },
    {
      index: 'backend-content',
      label: '反诈治理',
      items: [
        { label: '反诈案例', routeName: appRouteName.newsList, route: appRoute.newsList() },
        { label: '线索举报', routeName: appRouteName.report, route: appRoute.report },
      ],
    },
    {
      index: 'backend-community',
      label: '社区治理',
      items: [
        { label: '论坛', routeName: appRouteName.forum, route: appRoute.forum },
        { label: '排行榜', routeName: appRouteName.leaderboard, route: appRoute.leaderboard },
        { label: '众包社区', routeName: appRouteName.crowdsource, route: appRoute.crowdsource },
        { label: '众包看板', routeName: appRouteName.crowdBoard, route: appRoute.crowdBoard },
      ],
    },
    {
      index: 'backend-education',
      label: '反诈训练',
      items: [
        { label: '教育研学', routeName: appRouteName.edu, route: appRoute.edu },
        { label: '沙盒', routeName: appRouteName.sandbox, route: appRoute.sandbox },
        { label: '测试', routeName: appRouteName.question, route: appRoute.question },
        { label: '学习阶段', routeName: appRouteName.stages, route: appRoute.stages },
      ],
    },
    {
      index: 'backend-account',
      label: '账户',
      items: [{ label: '个人中心', routeName: appRouteName.profile, route: appRoute.profile }],
    },
  ]
}

export function findActiveGroupIndex(routeName: string | symbol | undefined, groups: NavigationGroup[]) {
  const normalizedName = String(routeName || '')
  return groups.find((group) => group.items.some((item) => item.routeName === normalizedName))?.index
}
