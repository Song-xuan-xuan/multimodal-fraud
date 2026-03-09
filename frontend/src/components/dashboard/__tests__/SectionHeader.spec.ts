import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const filePath = path.resolve(__dirname, '../SectionHeader.vue')
const source = fs.readFileSync(filePath, 'utf-8')

describe('SectionHeader color regression', () => {
  it('keeps title, eyebrow and description bound to theme tokens', () => {
    expect(source).toContain('class="section-header__eyebrow"')
    expect(source).toContain('class="section-header__title"')
    expect(source).toContain('class="section-header__description"')
    expect(source).toContain('color: #56c2ff;')
    expect(source).toContain('color: var(--tech-text-primary);')
    expect(source).toContain('color: var(--tech-text-secondary);')
    expect(source).toContain('text-shadow: 0 0 18px rgba(86, 194, 255, 0.08);')
  })
})
