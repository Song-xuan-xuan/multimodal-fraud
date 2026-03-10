import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const panelPath = path.resolve(__dirname, '../CrawlerFloatingPanel.vue')
const source = fs.readFileSync(panelPath, 'utf-8')

describe('CrawlerFloatingPanel regression', () => {
  it('keeps crawler news cached locally and avoids forced refresh on every mount', () => {
    expect(source).toContain('CRAWLER_CACHE_KEY')
    expect(source).toContain('localStorage.getItem(CRAWLER_CACHE_KEY)')
    expect(source).toContain('localStorage.setItem(CRAWLER_CACHE_KEY')
    expect(source).toContain('if (newsList.value.length === 0)')
    expect(source).toContain('fetchNews()')
  })
})
