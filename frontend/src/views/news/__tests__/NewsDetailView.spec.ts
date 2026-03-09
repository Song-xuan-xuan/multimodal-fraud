import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const detailViewPath = path.resolve(__dirname, '../NewsDetailView.vue')
const listViewPath = path.resolve(__dirname, '../NewsListView.vue')

const detailViewSource = fs.readFileSync(detailViewPath, 'utf-8')
const listViewSource = fs.readFileSync(listViewPath, 'utf-8')

describe('NewsDetailView anchor + module wiring regression', () => {
  it('keeps anchor navigation event wired to scroll handler', () => {
    expect(detailViewSource).toContain('@navigate="scrollToSection"')
    expect(detailViewSource).toContain('function scrollToSection(target: string)')
    expect(detailViewSource).toContain('document.getElementById(target)')
    expect(detailViewSource).toContain('activeTarget.value = target')
    expect(detailViewSource).toContain("element.scrollIntoView({ behavior: 'smooth', block: 'start' })")
  })

  it('keeps intersection observer to sync active anchor target', () => {
    expect(detailViewSource).toContain('new IntersectionObserver(')
    expect(detailViewSource).toContain('entry.isIntersecting')
    expect(detailViewSource).toContain('activeTarget.value = visibleEntry.target.id')
  })

  it('keeps detail cover, audience and relation anchor injection logic', () => {
    expect(detailViewSource).toContain("item.target === 'related-news'")
    expect(detailViewSource).toContain("items.push({ target: 'audience-profile', label: '用户画像' })")
    expect(detailViewSource).toContain("items.splice(1, 0, { target: 'detail-cover', label: '相关图片' })")
    expect(detailViewSource).toContain('DetailAnchorNav :anchors="enhancedAnchors" :active-target="activeTarget"')
  })

  it('keeps module visibility controls for optional sections', () => {
    expect(detailViewSource).toContain('v-if="moduleVisibility.propagationTrend"')
    expect(detailViewSource).toContain('v-if="moduleVisibility.propagationPlatforms"')
    expect(detailViewSource).toContain('v-if="moduleVisibility.propagationRegions"')
    expect(detailViewSource).toContain('v-if="moduleVisibility.relationsRelatedNews"')
    expect(detailViewSource).toContain('v-if="moduleVisibility.relationsKnowledgeNodes"')
    expect(detailViewSource).toContain('v-if="moduleVisibility.relationsEdges"')
  })

  it('keeps page header color bindings on shared semantic tokens', () => {
    expect(detailViewSource).toContain('border: 1px solid var(--tech-border-color);')
    expect(detailViewSource).toContain('box-shadow: var(--tech-shadow-sm);')
    expect(detailViewSource).toContain('color: var(--tech-text-primary);')
    expect(detailViewSource).toContain('color: var(--tech-color-primary-strong);')
    expect(detailViewSource).toContain('color: var(--tech-text-secondary);')
  })
})

describe('list -> detail route regression', () => {
  it('keeps detail jump action in list view', () => {
    expect(listViewSource).toContain('<NewsCardList :items="displayItems" :mode="viewMode" @select="goToDetail" />')
    expect(listViewSource).toContain('function goToDetail(item: NewsItem)')
    expect(listViewSource).toContain('void router.push(appRoute.newsDetail(item.news_id))')
  })
})
