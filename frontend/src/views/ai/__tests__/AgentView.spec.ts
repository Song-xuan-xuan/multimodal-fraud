import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../AgentView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('AgentView high-risk acknowledgment regression', () => {
  it('blocks full result rendering behind a high-risk acknowledgment gate', () => {
    expect(source).toContain('const hasRiskAcknowledged = ref')
    expect(source).toContain('const isResultBlocked = computed')
    expect(source).toContain('result.value?.user_ack_required')
    expect(source).toContain('guardian_notification')
    expect(source).toContain('我已暂停进一步操作')
    expect(source).toContain('handleRiskAcknowledged')
  })
})
