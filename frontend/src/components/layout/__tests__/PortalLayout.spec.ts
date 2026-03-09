import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const layoutPath = path.resolve(__dirname, '../PortalLayout.vue')
const source = fs.readFileSync(layoutPath, 'utf-8')

describe('PortalLayout regression', () => {
  it('keeps dedicated home canvas handling and hides footer on home route', () => {
    expect(source).toContain("'portal-layout__canvas--home': isHomeRoute")
    expect(source).toContain("'portal-layout__canvas--footerless': hideFooter")
    expect(source).toContain("const isHomeRoute = computed(() => route.name === appRouteName.home)")
    expect(source).toContain('const hideFooter = computed(() => isHomeRoute.value)')
    expect(source).toContain('const contentClass = computed(() => (isHomeRoute.value ?')
    expect(source).toContain('<template v-if="!hideFooter" #footer>')
    expect(source).toContain('height: calc(100vh - 72px)')
    expect(source).toContain('overflow: hidden')
  })
})
