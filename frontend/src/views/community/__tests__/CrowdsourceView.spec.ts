  import fs from 'node:fs'
  import path from 'node:path'
  import { describe, expect, it } from 'vitest'
  import type { EvidenceBoardItem } from '@/types/insight'

  const viewPath = path.resolve(__dirname, '../CrowdsourceView.vue')
  const source = fs.readFileSync(viewPath, 'utf-8')

  describe('CrowdsourceView regression', () => {
    it('uses NewsItem.news_id when opening evidence submission', () => {
      expect(source).toContain('function openSubmit(row: NewsItem)')
      expect(source).toContain('currentNewsId.value = String(row.news_id)')
    })

    it('submits evidence to the community endpoint with backend-compatible fields', () => {
      expect(source).toContain("await api.post('/community/evidence', {")
      expect(source).toContain('news_id: currentNewsId.value')
      expect(source).toContain('content:')
      expect(source).toContain('source: evidence.url.trim() || undefined')
    })

    it('loads and refreshes my latest submissions after submit', () => {
      expect(source).toContain('const mySubmissions = ref<EvidenceBoardItem[]>([])')
      expect(source).toContain('async function loadMySubmissions()')
      expect(source).toContain('await loadMySubmissions()')
      expect(source).toContain('我的最新提交')
    })
  })