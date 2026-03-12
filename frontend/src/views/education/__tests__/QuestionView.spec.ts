import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../QuestionView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('QuestionView regression', () => {
  it('loads questions from the education api and supports llm refresh', () => {
    expect(source).toContain('educationApi.getQuestions')
    expect(source).toContain('educationApi.submitTest')
    expect(source).toContain('DeepSeek 换一批')
    expect(source).toContain('统一训练模式')
    expect(source).toContain('question_ids')
    expect(source).toContain('学习诊断')
    expect(source).toContain('result.weaknesses')
    expect(source).toContain('result.next_actions')
    expect(source).toContain('近3次训练趋势')
    expect(source).toContain('result.recent_trend')
    expect(source).toContain('result.trend_delta')
    expect(source).toContain('微课卡片')
    expect(source).toContain('高频误区')
    expect(source).not.toContain('LLM 反诈教练')
    expect(source).not.toContain('educationApi.askCoach')
  })
})
