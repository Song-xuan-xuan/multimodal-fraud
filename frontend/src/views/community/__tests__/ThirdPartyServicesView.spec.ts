import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const viewPath = path.resolve(__dirname, '../ThirdPartyServicesView.vue')
const source = fs.readFileSync(viewPath, 'utf-8')

describe('ThirdPartyServicesView regression', () => {
  it('keeps the restored third-party service aggregation cards', () => {
    expect(source).toContain('第三方服务聚合')
    expect(source).toContain('const services: ThirdPartyService[] = [')
    expect(source).toContain('中国互联网联合辟谣平台')
    expect(source).toContain('腾讯较真')
    expect(source).toContain('Reality Defender')
    expect(source).toContain('VirusTotal')
    expect(source).toContain('腾讯混元内容鉴别')
    expect(source).toContain('Copyleaks')
    expect(source).toContain('访问平台')
  })
})
