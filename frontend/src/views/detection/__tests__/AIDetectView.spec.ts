import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../AIDetectView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('AIDetectView AI result flow regression', () => {
  it('owns normalized display result state and hosts the integrated analysis workspace', () => {
    expect(source).toContain('const imagePreviewUrl = ref')
    expect(source).toContain('const displayResult = ref')
    expect(source).toContain('const activeWorkspace = ref')
    expect(source).toContain('URL.createObjectURL(file)')
    expect(source).toContain('URL.revokeObjectURL')
    expect(source).toContain(':result="displayResult"')
    expect(source).toContain('normalizeDetectionResult')
    expect(source).toContain('<NewsDetectView')
    expect(source).toContain('<FakeNewsClassifyView')
    expect(source).toContain('<FactCheckView')
  })
})
