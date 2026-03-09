import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const tokensPath = path.resolve(__dirname, '../tokens.scss')
const themePath = path.resolve(__dirname, '../theme-dark-tech.scss')

const tokensSource = fs.readFileSync(tokensPath, 'utf-8')
const themeSource = fs.readFileSync(themePath, 'utf-8')

describe('theme token regression', () => {
  it('keeps base semantic color tokens stable', () => {
    expect(tokensSource).toContain('--tech-color-primary: var(--tech-color-brand-500);')
    expect(tokensSource).toContain('--tech-color-success: #37d67a;')
    expect(tokensSource).toContain('--tech-color-warning: #ffb347;')
    expect(tokensSource).toContain('--tech-color-danger: #ff6b8b;')
    expect(tokensSource).toContain('--tech-color-info: #5cb8ff;')
    expect(tokensSource).toContain('--tech-text-primary: #eef7ff;')
    expect(tokensSource).toContain('--tech-text-secondary: rgba(203, 223, 245, 0.72);')
    expect(tokensSource).toContain('--tech-border-color: rgba(0, 138, 188, 0.2);')
    expect(tokensSource).toContain('--tech-button-primary-bg: var(--tech-color-brand-gradient);')
    expect(tokensSource).toContain('--tech-button-secondary-text: var(--tech-text-primary);')
  })

  it('keeps chart and component color tokens stable', () => {
    expect(tokensSource).toContain('--tech-chart-1: #00c6fb;')
    expect(tokensSource).toContain('--tech-chart-2: #37d67a;')
    expect(tokensSource).toContain('--tech-chart-3: #ffb347;')
    expect(tokensSource).toContain('--tech-chart-4: #ff6b8b;')
    expect(tokensSource).toContain('--tech-chart-5: #9b8cff;')
    expect(tokensSource).toContain('--el-color-primary: var(--tech-color-primary);')
    expect(tokensSource).toContain('--el-text-color-primary: var(--tech-text-primary);')
    expect(tokensSource).toContain('--el-border-color: var(--tech-border-color);')
  })

  it('keeps semantic theme aliases and status surfaces stable', () => {
    expect(themeSource).toContain('--tech-theme-surface-panel: var(--tech-bg-panel);')
    expect(themeSource).toContain('--tech-theme-surface-card: var(--tech-bg-card);')
    expect(themeSource).toContain('--tech-theme-text-primary: var(--tech-text-primary);')
    expect(themeSource).toContain('--tech-theme-text-brand: var(--tech-text-brand);')
    expect(themeSource).toContain('--tech-theme-border: var(--tech-border-color);')
    expect(themeSource).toContain('--tech-theme-focus-ring: 0 0 0 1px var(--tech-border-focus)')
    expect(themeSource).toContain('.tech-status-surface.is-success {')
    expect(themeSource).toContain('background: var(--tech-theme-surface-success);')
    expect(themeSource).toContain('.tech-status-surface.is-warning {')
    expect(themeSource).toContain('background: var(--tech-theme-surface-warning);')
    expect(themeSource).toContain('.tech-status-surface.is-danger {')
    expect(themeSource).toContain('background: var(--tech-theme-surface-danger);')
    expect(themeSource).toContain('.tech-status-surface.is-info {')
    expect(themeSource).toContain('background: var(--tech-theme-surface-info);')
  })
})
