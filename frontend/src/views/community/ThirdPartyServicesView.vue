<template>
  <div class="third-party-services-view page-shell">
    <header class="third-party-services-view__hero tech-panel">
      <div>
        <p class="third-party-services-view__eyebrow">第三方服务聚合</p>
        <h2>外部平台与工具快速跳转</h2>
      </div>
      <el-alert
        class="third-party-services-view__alert"
        type="info"
        show-icon
        :closable="false"
        title="以下链接均为外部平台，将在新标签页打开。"
      />
    </header>

    <section class="third-party-services-view__grid">
      <article v-for="service in services" :key="service.name" class="third-party-services-view__card tech-panel">
        <div class="third-party-services-view__card-head">
          <img :src="service.logo" :alt="service.name" class="third-party-services-view__logo" loading="lazy" />
          <div>
            <h3>{{ service.name }}</h3>
            <p>{{ service.description }}</p>
          </div>
        </div>
        <div class="third-party-services-view__tags">
          <el-tag v-for="tag in service.tags" :key="tag" effect="dark" size="small">{{ tag }}</el-tag>
        </div>
        <div class="third-party-services-view__actions">
          <el-link :href="service.url" target="_blank" rel="noopener noreferrer" type="primary">
            访问平台
          </el-link>
          <span class="third-party-services-view__domain">{{ service.domain }}</span>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
type ThirdPartyService = {
  name: string
  description: string
  url: string
  domain: string
  logo: string
  tags: string[]
}

const services: ThirdPartyService[] = [
  {
    name: '中国互联网联合辟谣平台',
    description: '国家级辟谣平台，适合演示权威辟谣信息检索和官方内容对照核验。',
    url: 'https://www.piyao.org.cn/',
    domain: 'www.piyao.org.cn',
    logo: 'https://www.google.com/s2/favicons?domain=www.piyao.org.cn&sz=128',
    tags: ['官方平台', '辟谣', '权威来源'],
  },
  {
    name: '腾讯较真',
    description: '腾讯事实核查平台，适合与项目内风险核验能力做外部对照展示。',
    url: 'https://vp.fact.qq.com/',
    domain: 'vp.fact.qq.com',
    logo: 'https://www.google.com/s2/favicons?domain=vp.fact.qq.com&sz=128',
    tags: ['事实核查', '腾讯', '内容核验'],
  },
  {
    name: '公安部网络违法犯罪信息举报网站',
    description: '用于展示举报闭环和外部联动处置渠道，适合放在线索治理链路中讲解。',
    url: 'https://cyberpolice.mps.gov.cn/',
    domain: 'cyberpolice.mps.gov.cn',
    logo: 'https://www.google.com/s2/favicons?domain=cyberpolice.mps.gov.cn&sz=128',
    tags: ['官方举报', '公安部', '处置联动'],
  },
  {
    name: 'Reality Defender',
    description: '专业 Deepfake 检测平台，可作为多模态和深伪识别能力的外部参考样例。',
    url: 'https://www.realitydefender.com/',
    domain: 'www.realitydefender.com',
    logo: 'https://www.google.com/s2/favicons?domain=www.realitydefender.com&sz=128',
    tags: ['Deepfake', '国际平台', '多模态检测'],
  },
  {
    name: 'VirusTotal',
    description: '适合做诈骗链接、域名和 IP 风险核验的外部工具补充。',
    url: 'https://www.virustotal.com/',
    domain: 'www.virustotal.com',
    logo: 'https://www.google.com/s2/favicons?domain=www.virustotal.com&sz=128',
    tags: ['链接核验', '域名/IP', '安全情报'],
  },
  {
    name: '腾讯混元内容鉴别',
    description: '腾讯推出的图像与文本鉴别工具，适合做内容溯源和真假辅助判断。',
    url: 'https://matrix.tencent.com/ai-detect/ai_gen_txt?utm_source=ai-bot.cn',
    domain: 'matrix.tencent.com',
    logo: 'https://ai-bot.cn/wp-content/uploads/2025/02/matrix-tencent-logo.png',
    tags: ['内容鉴别', '腾讯', '文本/图像'],
  },
  {
    name: 'GPTZero',
    description: '覆盖面较广的 AI 文本检测平台，可用于演示外部工具协同能力。',
    url: 'https://gptzero.me/',
    domain: 'gptzero.me',
    logo: 'https://ai-bot.cn/wp-content/uploads/2023/11/gptzero-icon-new.png',
    tags: ['文本检测', '外部平台'],
  },
  {
    name: 'Copyleaks',
    description: '面向内容检测与风险判别的第三方服务，适合补充外部验证链路。',
    url: 'https://copyleaks.com/',
    domain: 'copyleaks.com',
    logo: 'https://ai-bot.cn/wp-content/uploads/2023/03/copyleaks-icon.png',
    tags: ['内容检测', '国际工具'],
  },
  {
    name: 'Sapling AI Detector',
    description: '免费在线 AI 内容检测工具，可作为课堂演示时的对照样例。',
    url: 'https://sapling.ai/ai-content-detector',
    domain: 'sapling.ai',
    logo: 'https://ai-bot.cn/wp-content/uploads/2023/03/sapling-ai-icon.png',
    tags: ['免费工具', '内容检测'],
  },
  {
    name: 'Originality.ai',
    description: '侧重原创度与 AI 内容检测，可作为第三方辅助审查平台展示。',
    url: 'https://originality.ai/',
    domain: 'originality.ai',
    logo: 'https://ai-bot.cn/wp-content/uploads/2023/03/originality-ai-icon.png',
    tags: ['原创度', 'AI检测'],
  },
  {
    name: 'Writefull GPT Detector',
    description: '在线检查文本是否由 GPT 或 ChatGPT 生成，适合做外部对照验证。',
    url: 'https://x.writefull.com/gpt-detector',
    domain: 'x.writefull.com',
    logo: 'https://ai-bot.cn/wp-content/uploads/2023/03/writefull-icon.png',
    tags: ['GPT检测', '文本核验'],
  },
]
</script>

<style scoped lang="scss">
.third-party-services-view {
  display: grid;
  gap: 20px;
}

.third-party-services-view__hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 360px);
  gap: 18px;
  padding: 24px;
}

.third-party-services-view__eyebrow {
  margin: 0 0 8px;
  color: var(--tech-color-primary-strong);
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.third-party-services-view__hero h2 {
  margin: 0;
  color: var(--tech-text-primary);
}

.third-party-services-view__summary {
  margin: 10px 0 0;
  max-width: 64ch;
  color: var(--tech-text-secondary);
  line-height: 1.72;
}

.third-party-services-view__alert {
  align-self: stretch;
}

.third-party-services-view__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.third-party-services-view__card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 240px;
  padding: 22px;
  transition:
    transform var(--tech-duration-fast) var(--tech-ease-out),
    box-shadow var(--tech-duration-fast) var(--tech-ease-out),
    border-color var(--tech-duration-fast) var(--tech-ease-out);
}

.third-party-services-view__card:hover {
  transform: translateY(-4px);
  border-color: color-mix(in srgb, var(--tech-color-primary) 36%, transparent);
  box-shadow: var(--tech-shadow-md);
}

.third-party-services-view__card-head {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.third-party-services-view__logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  object-fit: contain;
  padding: 8px;
  background: rgba(255, 255, 255, 0.08);
}

.third-party-services-view__card-head h3 {
  margin: 0;
  color: var(--tech-text-primary);
  font-size: 18px;
}

.third-party-services-view__card-head p {
  margin: 8px 0 0;
  color: var(--tech-text-secondary);
  line-height: 1.66;
}

.third-party-services-view__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.third-party-services-view__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  gap: 12px;
}

.third-party-services-view__domain {
  color: var(--tech-theme-text-tertiary);
  font-size: 12px;
}

@media (max-width: 980px) {
  .third-party-services-view__hero {
    grid-template-columns: 1fr;
  }
}
</style>
