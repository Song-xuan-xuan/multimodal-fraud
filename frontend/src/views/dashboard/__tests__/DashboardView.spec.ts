import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../DashboardView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('DashboardView regression', () => {
  it('keeps primary navigation entry points in hero and quick actions', () => {
    expect(source).toContain('@click="navigate(appRoute.newsList())"')
    expect(source).toContain('@click="navigate(appRoute.adminReviewWorkbench)"')
    expect(source).toContain("{ label: 'AI 检测', path: '/detection/ai', icon: 'AI' }")
    expect(source).toContain("{ label: '众包看板', path: '/evidence/crowd-board', icon: 'CB' }")
  })

  it('keeps route normalization and detail jump wiring', () => {
    expect(source).toContain('function navigate(target: RouteLocationRaw)')
    expect(source).toContain('void router.push(normalizeAppRouteTarget(target))')
    expect(source).toContain('function openNewsDetail(newsId: string)')
    expect(source).toContain('void router.push(appRoute.newsDetail(newsId))')
  })

  it('keeps command and alert blocks for dashboard layout coverage', () => {
    expect(source).toContain('<DashboardGrid>')
    expect(source).toContain('<AlertBubble :alerts="alerts" @action="onAlertAction" />')
    expect(source).toContain('<FloatingQuickActions :items="quickActions" @navigate="navigate" />')
    expect(source).toContain("title: 'AI 协作入口可用'")
  })

  it('keeps hero and command color bindings on semantic tokens', () => {
    expect(source).toContain('color: var(--tech-color-primary-strong);')
    expect(source).toContain('color: var(--tech-text-primary);')
    expect(source).toContain('color: var(--tech-text-secondary);')
    expect(source).toContain('border: 1px solid color-mix(in srgb, var(--tech-color-primary) 16%, transparent);')
    expect(source).toContain('background: color-mix(in srgb, var(--tech-color-primary-soft) 24%, rgba(255, 255, 255, 0.02));')
    expect(source).toContain('border-color: color-mix(in srgb, var(--tech-color-warning) 18%, transparent);')
    expect(source).toContain('color: var(--tech-text-warning);')
  })
})
