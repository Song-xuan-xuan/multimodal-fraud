import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const routerPath = path.resolve(__dirname, '../index.ts')
const source = fs.readFileSync(routerPath, 'utf-8')

describe('routes layout regression', () => {
  it('keeps auth, frontend and backend layout bindings for the new information architecture', () => {
    expect(source).toContain("layout: 'auth' | 'frontend' | 'backend'")
    expect(source).toContain("name: appRouteName.home")
    expect(source).toContain("layout: 'frontend'")
    expect(source).toContain("pageGroup: '前台首页'")

    expect(source).toContain("name: appRouteName.dashboard")
    expect(source).toContain("layout: 'backend'")
    expect(source).toContain("pageTitle: '数据看板'")

    expect(source).toContain("name: appRouteName.login")
    expect(source).toContain("pageTitle: '登录'")
  })

  it('keeps frontend bindings for detection tools and AI assistant routes', () => {
    expect(source).toContain("name: appRouteName.aiDetect")
    expect(source).toContain("pageGroup: '检测工具'")
    expect(source).toContain("name: appRouteName.aiAssistant")
    expect(source).toContain("pageGroup: '智能助手'")
    expect(source).toContain("name: appRouteName.agent")
  })

  it('keeps backend bindings for governance, education and insight routes', () => {
    expect(source).toContain("name: appRouteName.newsList")
    expect(source).toContain("pageGroup: '内容治理'")
    expect(source).toContain("name: appRouteName.forum")
    expect(source).toContain("pageGroup: '社区治理'")
    expect(source).toContain("name: appRouteName.edu")
    expect(source).toContain("pageGroup: '教育管理'")
    expect(source).toContain("name: appRouteName.insightKnowledgeGraph")
    expect(source).toContain("pageGroup: '运营分析'")
  })

  it('keeps path normalization for legacy page jumps', () => {
    expect(source).toContain("'/detection/ai': appRoute.aiDetect")
    expect(source).toContain("'/evidence/crowd-board': appRoute.crowdBoard")
    expect(source).toContain("'/insight/knowledge-graph': appRoute.insightKnowledgeGraph")
    expect(source).toContain('return appRoute.newsDetail(newsDetailMatch[1])')
  })
})
