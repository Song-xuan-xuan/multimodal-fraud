import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const routerPath = path.resolve(__dirname, '../index.ts')
const source = fs.readFileSync(routerPath, 'utf-8')

describe('route regression for backend governance pages', () => {
  it('keeps routes for review workbench, crowd board and knowledge graph', () => {
    expect(source).toContain("path: '/admin/review-workbench'")
    expect(source).toContain("name: appRouteName.adminReviewWorkbench")

    expect(source).toContain("path: '/evidence/crowd-board'")
    expect(source).toContain("name: appRouteName.crowdBoard")

    expect(source).toContain("path: '/insight/knowledge-graph'")
    expect(source).toContain("name: appRouteName.insightKnowledgeGraph")
  })

  it('keeps admin-only guard for review workbench route', () => {
    expect(source).toContain('meta: { adminOnly: true }')
    expect(source).toContain('if (to.meta.adminOnly)')
    expect(source).toContain("const adminAllowlist = ['admin', 'administrator', 'superadmin']")
    expect(source).toContain("layout: 'backend'")
  })
})
