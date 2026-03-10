import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const headerPath = path.resolve(__dirname, '../WorkbenchHeader.vue')
const source = fs.readFileSync(headerPath, 'utf-8')

describe('WorkbenchHeader regression', () => {
  it('keeps grouped backend navigation and exposes admin review workbench as a standalone account-side button', () => {
    expect(source).toContain('buildBackendNavGroups')
    expect(source).toContain('风险洞察')
    expect(source).toContain('反诈治理')
    expect(source).toContain('社区治理')
    expect(source).toContain('反诈训练')
    expect(source).toContain('showAdminWorkbenchButton')
    expect(source).toContain('isAdminUsername')
    expect(source).toContain('appRoute.adminReviewWorkbench')
    expect(source).toContain('workbench-header__review-button')
    expect(source).toContain('审核工作台')
    expect(source).toContain('返回前台')
  })
})
