import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const headerPath = path.resolve(__dirname, '../WorkbenchHeader.vue')
const source = fs.readFileSync(headerPath, 'utf-8')

describe('WorkbenchHeader regression', () => {
  it('keeps grouped backend navigation and frontend return button with admin-aware workbench entry', () => {
    expect(source).toContain('buildBackendNavGroups')
    expect(source).toContain('风险洞察')
    expect(source).toContain('反诈治理')
    expect(source).toContain('社区治理')
    expect(source).toContain('反诈训练')
    expect(source).toContain('返回前台')
  })
})
