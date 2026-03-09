import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../CrowdBoardView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('CrowdBoardView regression', () => {
  it('keeps workbench sections for filters, board list and progress', () => {
    expect(source).toContain('title="众筹看板"')
    expect(source).toContain('title="看板筛选"')
    expect(source).toContain('title="我的证据提交"')
    expect(source).toContain('title="新闻核验进度"')
  })

  it('keeps board and progress API wiring', () => {
    expect(source).toContain('evidenceApi.getBoardStats')
    expect(source).toContain('evidenceApi.listBoard')
    expect(source).toContain('evidenceApi.listVerificationProgress')
    expect(source).toContain('refreshAll')
  })

  it('keeps filters and progress range interactions', () => {
    expect(source).toContain('@keyup.enter="loadBoard(1)"')
    expect(source).toContain('@clear="loadBoard(1)"')
    expect(source).toContain('@change="loadProgress"')
    expect(source).toContain('progressRange')
  })

  it('keeps workbench color bindings for table and status visuals', () => {
    expect(source).toContain('tone="workbench"')
    expect(source).toContain("if (status === 'pending') return 'warning'")
    expect(source).toContain("if (status === 'approved') return 'success'")
    expect(source).toContain("if (status === 'rejected') return 'danger'")
    expect(source).toContain('--el-table-text-color: var(--tech-text-primary);')
    expect(source).toContain('--el-table-header-bg-color: rgba(76, 201, 255, 0.08);')
    expect(source).toContain('background: rgba(255, 255, 255, 0.06);')
  })
})
