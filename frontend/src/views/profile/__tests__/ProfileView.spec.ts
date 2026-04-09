import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../ProfileView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('ProfileView guardian contact regression', () => {
  it('keeps guardian info fields in the edit dialog and save payload', () => {
    expect(source).toContain('guardian_name')
    expect(source).toContain('guardian_relation')
    expect(source).toContain('guardian_email')
    expect(source).toContain('guardian_notify_enabled')
    expect(source).toContain("label=\"监护人姓名\"")
    expect(source).toContain("label=\"关系\"")
    expect(source).toContain("label=\"监护人邮箱\"")
    expect(source).toContain("label=\"预警通知\"")
  })
})
