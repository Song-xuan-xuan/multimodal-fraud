import { describe, expect, it } from 'vitest'
import {
  normalizeForRender,
  buildModuleVisibility,
  buildAnchors,
} from '../../../utils/news/detailNormalizer'

const fullSample = {
  news_id: 'n-1',
  title: '新闻A',
  content: '正文',
  url: 'https://example.com/n-1',
  pic_url: 'https://example.com/n-1.png',
  label: '谣言',
  platform: '微博',
  hashtag: '#A',
  summary: '摘要A',
  location: '北京',
  conclusion: '结论A',
  publish_time: '2026-01-01',
  check_time: '2026-01-02',
  iscredit: false,
  credibility: {
    score: 0.78,
    verification_progress: 85,
    verified: true,
    dimension_scores: {
      source: 0.7,
      content: 0.8,
      logic: 0.6,
      propagation: 0.9,
      AI: 0.88,
      content1: '说明1',
      content2: '说明2',
    },
  },
  propagation: {
    total_mentions: 123,
    peak_timestamp: '2026-01-01 11:00:00',
    trend: [{ timestamp: '2026-01-01 10:00:00', value: 20 }],
    platform_distribution: [{ platform: '微博', count: 60, ratio: 0.4878 }],
    region_distribution: [{ region: '北京', count: 30 }],
  },
  relations: {
    related_news: [
      {
        news_id: 'n-2',
        title: '相关新闻',
        similarity: 0.8,
        platform: '微博',
        publish_time: '2026-01-01',
        url: 'https://example.com/n-2',
      },
    ],
    nodes: [{ node_id: 'node-1', name: '节点1', category: 'knowledge', value: 1 }],
    edges: [{ source: 'n-1', target: 'n-2', relation_type: 'related_rumor', weight: 1 }],
  },
  ui_fallbacks: {
    summary: '暂无摘要',
    conclusion: '暂无结论',
    propagation_empty_reason: '暂无传播数据',
    relations_empty_reason: '暂无关联关系数据',
  },
  propagation_data: {
    audience_profile: {
      年龄层: '18-24',
    },
  },
  relations_data: {},
}

describe('detail normalizer + module visibility', () => {
  it('normalizes complete payload and exposes all anchors', () => {
    const vm = normalizeForRender(fullSample as any)
    const visibility = buildModuleVisibility(vm)
    const anchors = buildAnchors(visibility)

    expect(vm.baseInfo.title).toBe('新闻A')
    expect(vm.credibility.scorePercentText).toBe('78.0%')

    expect(visibility.propagationTrend).toBe(true)
    expect(visibility.propagationPlatforms).toBe(true)
    expect(visibility.propagationRegions).toBe(true)
    expect(visibility.relationsRelatedNews).toBe(true)
    expect(visibility.relationsKnowledgeNodes).toBe(true)
    expect(visibility.relationsEdges).toBe(true)

    expect(anchors.map((item) => item.target)).toEqual([
      'base-info',
      'credibility',
      'propagation-trend',
      'propagation-platforms',
      'propagation-regions',
      'related-news',
      'knowledge-nodes',
      'relation-edges',
    ])
  })

  it('applies fallbacks for empty/null samples', () => {
    const vm = normalizeForRender({
      ...fullSample,
      title: '',
      content: '',
      summary: '',
      conclusion: '',
      platform: '',
      location: '',
      publish_time: '',
      check_time: '',
      hashtag: '',
      url: '',
      pic_url: '',
      propagation: {
        total_mentions: 0,
        peak_timestamp: '',
        trend: [],
        platform_distribution: [],
        region_distribution: [],
      },
      relations: {
        related_news: [],
        nodes: [],
        edges: [],
      },
      ui_fallbacks: {
        summary: '后备摘要',
        conclusion: '后备结论',
        propagation_empty_reason: '传播为空',
        relations_empty_reason: '关系为空',
      },
    } as any)

    expect(vm.baseInfo.title).toBe('新闻详情')
    expect(vm.baseInfo.content).toBe('暂无内容')
    expect(vm.baseInfo.summary).toBe('后备摘要')
    expect(vm.baseInfo.conclusion).toBe('后备结论')
    expect(vm.baseInfo.platform).toBe('未知平台')
    expect(vm.propagation.emptyReason).toBe('传播为空')
    expect(vm.relations.emptyReason).toBe('关系为空')
  })

  it('hides optional modules and keeps base anchors for empty relations/propagation', () => {
    const vm = normalizeForRender({
      ...fullSample,
      propagation: {
        total_mentions: 0,
        peak_timestamp: '',
        trend: [],
        platform_distribution: [],
        region_distribution: [],
      },
      relations: {
        related_news: [],
        nodes: [],
        edges: [],
      },
    } as any)

    const visibility = buildModuleVisibility(vm)
    const anchors = buildAnchors(visibility)

    expect(visibility.baseInfo).toBe(true)
    expect(visibility.credibility).toBe(true)
    expect(visibility.propagationTrend).toBe(false)
    expect(visibility.propagationPlatforms).toBe(false)
    expect(visibility.propagationRegions).toBe(false)
    expect(visibility.relationsRelatedNews).toBe(false)
    expect(visibility.relationsKnowledgeNodes).toBe(false)
    expect(visibility.relationsEdges).toBe(false)

    expect(anchors.map((item) => item.target)).toEqual(['base-info', 'credibility'])
  })
})
