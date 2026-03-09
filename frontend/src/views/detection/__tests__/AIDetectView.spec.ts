import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../AIDetectView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('AIDetectView AI result flow regression', () => {
  it('owns normalized display result state and object url lifecycle', () => {
    expect(source).toContain('const imagePreviewUrl = ref')
    expect(source).toContain('const displayResult = ref')
    expect(source).toContain('URL.createObjectURL(file)')
    expect(source).toContain('URL.revokeObjectURL')
    expect(source).toContain(':result="displayResult"')
    expect(source).toContain('normalizeDetectionResult')
  })
})
