import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const headerPath = path.resolve(__dirname, '../PortalHeader.vue')
const source = fs.readFileSync(headerPath, 'utf-8')

describe('PortalHeader regression', () => {
  it('keeps primary frontend navigation buttons and grouped fallback menus for unauthenticated users', () => {
    expect(source).toContain('{{ frontendDirectNav.label }}')
    expect(source).toContain('frontendPrimaryNav')
    expect(source).toContain('多模态分析')
    expect(source).toContain('反诈助手')
    expect(source).toContain('frontendNavGroups')
    expect(source).toContain('登录')
    expect(source).toContain('注册')
    expect(source).toContain('width: min(1680px, calc(100vw - 64px))')
    expect(source).toContain('margin: 0 auto')
  })
})
