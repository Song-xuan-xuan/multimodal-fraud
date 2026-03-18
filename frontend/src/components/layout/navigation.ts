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

export const ADMIN_USERNAMES = ['admin'] as const

export function isAdminUsername(username: string | null | undefined) {
  return ADMIN_USERNAMES.includes(String(username || '').trim().toLowerCase() as (typeof ADMIN_USERNAMES)[number])
}

export const frontendDirectNav = {
  label: '首页',
  routeName: appRouteName.home,
  route: appRoute.home,
}

export const frontendPrimaryNav: NavigationItem[] = [
  { label: '多模态分析', routeName: appRouteName.agent, route: appRoute.agent },
  { label: '专项分析', routeName: appRouteName.aiDetect, route: appRoute.aiDetect },
  { label: '反诈助手', routeName: appRouteName.aiAssistant, route: appRoute.aiAssistant },
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
        { label: '众包社区', routeName: appRouteName.crowdsource, route: appRoute.crowdsource },
        { label: '第三方服务', routeName: appRouteName.thirdPartyServices, route: appRoute.thirdPartyServices },
      ],
    },
    {
      index: 'backend-education',
      label: '反诈训练',
      items: [
        { label: '答题训练', routeName: appRouteName.question, route: appRoute.question },
        { label: '反诈教练', routeName: appRouteName.educationCoach, route: appRoute.educationCoach },
      ],
    },
    {
      index: 'backend-account',
      label: '个人账户',
      items: [{ label: '个人账户', routeName: appRouteName.profile, route: appRoute.profile }],
    },
  ]
}

export function findActiveGroupIndex(routeName: string | symbol | undefined, groups: NavigationGroup[]) {
  const normalizedName = String(routeName || '')
  return groups.find((group) => group.items.some((item) => item.routeName === normalizedName))?.index
}
