import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../HomeView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('HomeView regression', () => {
  it('keeps homepage focused on the static hero scene', () => {
    expect(source).toContain('<HeroSection @primary="goTo(\'/detection/ai\')" @secondary="goTo(\'/dashboard\')" />')
    expect(source).not.toContain('<CoreFeaturesSection @navigate="goTo" />')
    expect(source).not.toContain('<AnalysisCapabilitiesSection @navigate="goTo" />')
    expect(source).not.toContain('<ProToolsSection @navigate="goTo" />')
    expect(source).not.toContain('<StatsSection />')
  })

  it('keeps route jump interactions for primary homepage actions', () => {
    expect(source).toContain('function goTo(route: string)')
    expect(source).toContain('void router.push(route)')
  })

  it('keeps the home hero as a fixed-width-free full page surface', () => {
    expect(source).toContain('width: 100%')
    expect(source).toContain('height: 100%')
    expect(source).toContain('overflow: hidden')
  })
})
