import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../NewsDetectView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('NewsDetectView multi-mode workbench regression', () => {
  it('defines the four workbench tabs and active mode state', () => {
    expect(source).toContain("name=\"aggregate\"")
    expect(source).toContain("name=\"url\"")
    expect(source).toContain("name=\"file\"")
    expect(source).toContain("name=\"segments\"")
    expect(source).toContain('const activeMode = ref')
  })

  it('keeps file, result component, and normalized display result wiring', () => {
    expect(source).toContain('const selectedFile = ref<File | null>(null)')
    expect(source).toContain('const displayResult = ref')
    expect(source).toContain('NewsDetectionResult')
    expect(source).toContain(':result="displayResult"')
    expect(source).toContain('normalizeAggregateNewsDetectionResult')
    expect(source).toContain('normalizeConsistencyDetectionResult')
    expect(source).toContain('normalizeSegmentDetectionResult')
  })

  it('keeps mode-specific forms and handlers', () => {
    expect(source).toContain('const aggregateForm = reactive')
    expect(source).toContain('const urlForm = reactive')
    expect(source).toContain('const segmentForm = reactive')
    expect(source).toContain('function handleFileSelect(file: File)')
    expect(source).toContain('async function detectAggregate()')
    expect(source).toContain('async function detectUrl()')
    expect(source).toContain('async function detectFile()')
    expect(source).toContain('async function detectSegments()')
  })
})
