import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../NewsDetailView.vue')
const actionBarPath = path.resolve(__dirname, '../../../components/engagement/NewsActionBar.vue')

const viewSource = fs.readFileSync(viewPath, 'utf-8')
const actionBarSource = fs.readFileSync(actionBarPath, 'utf-8')

describe('NewsDetail engagement regression', () => {
  it('keeps action bar integration for favorite, vote, rebuttal', () => {
    expect(viewSource).toContain('@toggle-favorite="handleToggleFavorite"')
    expect(viewSource).toContain('@vote="handleVote"')
    expect(viewSource).toContain('@submit-rebuttal="handleSubmitRebuttal"')
    expect(viewSource).toContain('engagementStore.toggleFavorite')
    expect(viewSource).toContain('engagementStore.submitVote')
    expect(viewSource).toContain('engagementStore.submitRebuttal')
  })

  it('keeps rebuttal dialog validation and submit event', () => {
    expect(actionBarSource).toContain('title="提交驳斥"')
    expect(actionBarSource).toContain('ElMessage.warning(\'请先填写驳斥内容\')')
    expect(actionBarSource).toContain("emit('submit-rebuttal', content)")
  })
})
