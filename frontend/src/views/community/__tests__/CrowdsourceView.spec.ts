import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../CrowdsourceView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('CrowdsourceView regression', () => {
  it('uses NewsItem.news_id when opening evidence submission', () => {
    expect(source).toContain('function openSubmit(row: NewsItem)')
    expect(source).toContain('currentNewsId.value = String(row.news_id)')
  })
})
