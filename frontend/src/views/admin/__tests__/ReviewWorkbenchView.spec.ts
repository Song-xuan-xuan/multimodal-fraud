import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../ReviewWorkbenchView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('ReviewWorkbenchView regression', () => {
  it('keeps workbench hero metrics and refresh action', () => {
    expect(source).toContain('title="管理审核工作台"')
    expect(source).toContain('待审核')
    expect(source).toContain('已审核')
    expect(source).toContain('已选择')
    expect(source).toContain('工作模式')
    expect(source).toContain('@click="loadQueue"')
  })

  it('keeps single and batch review actions wired', () => {
    expect(source).toContain("@review=\"reviewSingle\"")
    expect(source).toContain("@click=\"batchReview('approved')\"")
    expect(source).toContain("@click=\"batchReview('rejected')\"")
    expect(source).toContain('adminReviewApi.reviewSubmission')
    expect(source).toContain('adminReviewApi.batchReview')
  })

  it('keeps admin-only access guard', () => {
    expect(source).toContain('ADMIN_USERNAMES')
    expect(source).toContain('hasAccess')
    expect(source).toContain('v-if="!hasAccess"')
    expect(source).toContain('仅管理员可见该页面')
  })
})
