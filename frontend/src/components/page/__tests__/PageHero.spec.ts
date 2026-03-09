import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const filePath = path.resolve(__dirname, '../PageHero.vue')
const source = fs.readFileSync(filePath, 'utf-8')

describe('PageHero color regression', () => {
  it('keeps tone variants and shared panel tokens for page headers', () => {
    expect(source).toContain("SectionHeader :eyebrow=\"eyebrow\" :title=\"title\" :description=\"description\"")
    expect(source).toContain("tone?: 'insight' | 'workbench'")
    expect(source).toContain("tone: 'insight'")
    expect(source).toContain('border: 1px solid var(--tech-border-color);')
    expect(source).toContain('background: var(--tech-bg-panel);')
    expect(source).toContain('box-shadow: var(--tech-shadow-sm);')
    expect(source).toContain('.page-hero--insight {')
    expect(source).toContain('.page-hero--workbench {')
    expect(source).toContain('--page-hero-accent: rgba(86, 194, 255, 0.18);')
    expect(source).toContain('--page-hero-accent: rgba(120, 227, 189, 0.14);')
  })
})
