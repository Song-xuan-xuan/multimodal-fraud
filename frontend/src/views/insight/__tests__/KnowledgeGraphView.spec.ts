import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../KnowledgeGraphView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('KnowledgeGraphView regression', () => {
  it('keeps page hero and graph container sections', () => {
    expect(source).toContain('title="知识图谱洞察"')
    expect(source).toContain('title="图谱条件设置"')
    expect(source).toContain('title="图谱画布"')
    expect(source).toContain('<KnowledgeGraphCanvas :graph="graph" :loading="loadingGraph" />')
  })

  it('keeps seed search and graph loading interactions', () => {
    expect(source).toContain('@keyup.enter="searchSeeds"')
    expect(source).toContain('@change="loadGraph"')
    expect(source).toContain('graphApi.listSeedNews')
    expect(source).toContain('graphApi.getKnowledgeGraph')
    expect(source).toContain('KnowledgeGraphCanvas')
  })

  it('resets graph when seed is cleared', () => {
    expect(source).toContain("if (!selectedSeed.value)")
    expect(source).toContain("graph.nodes = []")
    expect(source).toContain("graph.edges = []")
  })

  it('keeps hero and section accents bound to shared palette tokens', () => {
    expect(source).toContain("const heroAccentColor = chartColors.semantic.fake")
    expect(source).toContain('color: v-bind(heroAccentColor);')
    expect(source).toContain('color: var(--tech-text-secondary);')
    expect(source).toContain('color: var(--tech-text-primary);')
    expect(source).toContain('background: linear-gradient(180deg, rgba(14, 28, 44, 0.72), rgba(7, 15, 28, 0.94));')
  })
})
