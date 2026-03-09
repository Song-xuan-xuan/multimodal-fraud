import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../NewsListView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('NewsListView regression', () => {
  it('keeps hero, filter, summary and result layout sections', () => {
    expect(source).toContain('<section class="hero-section">')
    expect(source).toContain('<NewsFilterPanel')
    expect(source).toContain('<NewsResultSummary :summary="summary" :filters="appliedFilters" />')
    expect(source).toContain('<NewsListToolbar v-model:mode="viewMode" :loading="loading" @refresh="fetchList" />')
    expect(source).toContain('<NewsCardList :items="displayItems" :mode="viewMode" @select="goToDetail" />')
    expect(source).toContain('<NewsListPagination')
  })

  it('keeps list empty state and detail navigation wiring', () => {
    expect(source).toContain("v-else-if=\"!displayItems.length\"")
    expect(source).toContain(":action-text=\"errorMessage ? '重新加载' : '重置筛选'\"")
    expect(source).toContain('function goToDetail(item: NewsItem)')
    expect(source).toContain('void router.push(appRoute.newsDetail(item.news_id))')
  })

  it('keeps query driven refresh and page change behavior', () => {
    expect(source).toContain('watch(')
    expect(source).toContain('await fetchList()')
    expect(source).toContain('async function handlePageChange(page: number)')
    expect(source).toContain("window.scrollTo({ top: 0, behavior: 'smooth' })")
  })

  it('keeps hero and content card color bindings on shared tokens', () => {
    expect(source).toContain('border: 1px solid var(--tech-border-color);')
    expect(source).toContain('color: var(--tech-color-primary-strong);')
    expect(source).toContain('color: var(--tech-text-primary);')
    expect(source).toContain('color: var(--tech-text-secondary);')
    expect(source).toContain('box-shadow: var(--tech-shadow-sm);')
    expect(source).toContain('border-bottom-color: var(--tech-divider-color);')
    expect(source).toContain('color: var(--tech-text-regular);')
    expect(source).toContain('color: var(--tech-text-secondary);')
  })
})
