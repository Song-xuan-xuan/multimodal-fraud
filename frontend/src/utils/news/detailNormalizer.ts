import type { NewsDetailResponse } from '@/api/news'
import type {
  NewsDetailAnchorItem,
  NewsDetailModuleVisibility,
  NewsDetailNormalizerInput,
  NewsDetailVM,
} from '@/types/newsDetail'

const DEFAULT_TEXT = {
  title: '新闻详情',
  content: '暂无内容',
  summary: '暂无摘要',
  conclusion: '暂无结论',
  label: '未知',
  platform: '未知平台',
  location: '未知地点',
  publishTime: '未知时间',
  checkTime: '未知时间',
  hashtag: '暂无话题',
  url: '#',
  picUrl: '',
  propagationEmptyReason: '暂无传播数据',
  relationsEmptyReason: '暂无关联关系数据',
}

function safeText(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value : fallback
}

function safeNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function safeBoolean(value: unknown): boolean {
  return value === true
}

function safeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : []
}

function safeRecord(value: unknown): Record<string, any> {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, any>) : {}
}

export function normalizeForRender(detail: NewsDetailResponse): NewsDetailVM {
  const input = (detail ?? {}) as Partial<NewsDetailNormalizerInput>

  const fallbackSummary = safeText(input.ui_fallbacks?.summary, DEFAULT_TEXT.summary)
  const fallbackConclusion = safeText(input.ui_fallbacks?.conclusion, DEFAULT_TEXT.conclusion)
  const propagationEmptyReason = safeText(
    input.ui_fallbacks?.propagation_empty_reason,
    DEFAULT_TEXT.propagationEmptyReason,
  )
  const relationsEmptyReason = safeText(
    input.ui_fallbacks?.relations_empty_reason,
    DEFAULT_TEXT.relationsEmptyReason,
  )

  const score = safeNumber(input.credibility?.score, 0)
  const verificationProgress = Math.min(100, Math.max(0, safeNumber(input.credibility?.verification_progress, 0)))

  const dimensionScoresRaw = safeRecord(input.credibility?.dimension_scores)

  const vm: NewsDetailVM = {
    baseInfo: {
      newsId: safeText(input.news_id, ''),
      title: safeText(input.title, DEFAULT_TEXT.title),
      content: safeText(input.content, DEFAULT_TEXT.content),
      summary: safeText(input.summary, fallbackSummary),
      conclusion: safeText(input.conclusion, fallbackConclusion),
      label: safeText(input.label, DEFAULT_TEXT.label),
      platform: safeText(input.platform, DEFAULT_TEXT.platform),
      location: safeText(input.location, DEFAULT_TEXT.location),
      publishTime: safeText(input.publish_time, DEFAULT_TEXT.publishTime),
      checkTime: safeText(input.check_time, DEFAULT_TEXT.checkTime),
      hashtag: safeText(input.hashtag, DEFAULT_TEXT.hashtag),
      url: safeText(input.url, DEFAULT_TEXT.url),
      picUrl: safeText(input.pic_url, DEFAULT_TEXT.picUrl),
      isCredit: safeBoolean(input.iscredit),
    },
    credibility: {
      score,
      scorePercentText: `${(Math.min(1, Math.max(0, score)) * 100).toFixed(1)}%`,
      verificationProgress,
      verified: safeBoolean(input.credibility?.verified),
      dimensions: {
        source: safeNumber(dimensionScoresRaw.source, 0),
        content: safeNumber(dimensionScoresRaw.content, 0),
        logic: safeNumber(dimensionScoresRaw.logic, 0),
        propagation: safeNumber(dimensionScoresRaw.propagation, 0),
        AI: safeNumber(dimensionScoresRaw.AI, 0),
        content1: safeText(dimensionScoresRaw.content1, ''),
        content2: safeText(dimensionScoresRaw.content2, ''),
      },
    },
    propagation: {
      totalMentions: safeNumber(input.propagation?.total_mentions, 0),
      peakTimestamp: safeText(input.propagation?.peak_timestamp, ''),
      trend: safeArray(input.propagation?.trend),
      platformDistribution: safeArray(input.propagation?.platform_distribution),
      regionDistribution: safeArray(input.propagation?.region_distribution),
      emptyReason: propagationEmptyReason,
    },
    relations: {
      relatedNews: safeArray(input.relations?.related_news),
      knowledgeNodes: safeArray(input.relations?.nodes),
      edges: safeArray(input.relations?.edges),
      emptyReason: relationsEmptyReason,
    },
    raw: {
      news_id: safeText(input.news_id, ''),
      title: safeText(input.title, DEFAULT_TEXT.title),
      content: safeText(input.content, DEFAULT_TEXT.content),
      url: safeText(input.url, DEFAULT_TEXT.url),
      pic_url: safeText(input.pic_url, DEFAULT_TEXT.picUrl),
      label: safeText(input.label, DEFAULT_TEXT.label),
      platform: safeText(input.platform, DEFAULT_TEXT.platform),
      hashtag: safeText(input.hashtag, DEFAULT_TEXT.hashtag),
      summary: safeText(input.summary, fallbackSummary),
      location: safeText(input.location, DEFAULT_TEXT.location),
      conclusion: safeText(input.conclusion, fallbackConclusion),
      publish_time: safeText(input.publish_time, DEFAULT_TEXT.publishTime),
      check_time: safeText(input.check_time, DEFAULT_TEXT.checkTime),
      iscredit: safeBoolean(input.iscredit),
      credibility: {
        score,
        dimension_scores: {
          source: safeNumber(dimensionScoresRaw.source, 0),
          content: safeNumber(dimensionScoresRaw.content, 0),
          logic: safeNumber(dimensionScoresRaw.logic, 0),
          propagation: safeNumber(dimensionScoresRaw.propagation, 0),
          AI: safeNumber(dimensionScoresRaw.AI, 0),
          content1: safeText(dimensionScoresRaw.content1, ''),
          content2: safeText(dimensionScoresRaw.content2, ''),
        },
        verification_progress: verificationProgress,
        verified: safeBoolean(input.credibility?.verified),
      },
      propagation: {
        total_mentions: safeNumber(input.propagation?.total_mentions, 0),
        peak_timestamp: safeText(input.propagation?.peak_timestamp, ''),
        trend: safeArray(input.propagation?.trend),
        platform_distribution: safeArray(input.propagation?.platform_distribution),
        region_distribution: safeArray(input.propagation?.region_distribution),
      },
      relations: {
        related_news: safeArray(input.relations?.related_news),
        nodes: safeArray(input.relations?.nodes),
        edges: safeArray(input.relations?.edges),
      },
      ui_fallbacks: {
        summary: fallbackSummary,
        conclusion: fallbackConclusion,
        propagation_empty_reason: propagationEmptyReason,
        relations_empty_reason: relationsEmptyReason,
      },
      propagation_data: safeRecord(input.propagation_data),
      relations_data: safeRecord(input.relations_data),
    },
  }

  return vm
}

export function buildModuleVisibility(detail: NewsDetailVM | null): NewsDetailModuleVisibility {
  if (!detail) {
    return {
      baseInfo: false,
      credibility: false,
      propagationTrend: false,
      propagationPlatforms: false,
      propagationRegions: false,
      relationsRelatedNews: false,
      relationsKnowledgeNodes: false,
      relationsEdges: false,
    }
  }

  return {
    baseInfo: true,
    credibility: true,
    propagationTrend: detail.propagation.trend.length > 0,
    propagationPlatforms: detail.propagation.platformDistribution.length > 0,
    propagationRegions: detail.propagation.regionDistribution.length > 0,
    relationsRelatedNews: detail.relations.relatedNews.length > 0,
    relationsKnowledgeNodes: detail.relations.knowledgeNodes.length > 0,
    relationsEdges: detail.relations.edges.length > 0,
  }
}

const ANCHOR_MAP: Record<keyof NewsDetailModuleVisibility, { target: string; label: string }> = {
  baseInfo: { target: 'base-info', label: '基础信息' },
  credibility: { target: 'credibility', label: '可信度分析' },
  propagationTrend: { target: 'propagation-trend', label: '传播趋势' },
  propagationPlatforms: { target: 'propagation-platforms', label: '平台分布' },
  propagationRegions: { target: 'propagation-regions', label: '地域分布' },
  relationsRelatedNews: { target: 'related-news', label: '相关新闻' },
  relationsKnowledgeNodes: { target: 'knowledge-nodes', label: '知识节点' },
  relationsEdges: { target: 'relation-edges', label: '关系连线' },
}

export function buildAnchors(visibility: NewsDetailModuleVisibility): NewsDetailAnchorItem[] {
  return (Object.keys(visibility) as Array<keyof NewsDetailModuleVisibility>)
    .filter((key) => visibility[key])
    .map((key) => ({
      key,
      target: ANCHOR_MAP[key].target,
      label: ANCHOR_MAP[key].label,
    }))
}
