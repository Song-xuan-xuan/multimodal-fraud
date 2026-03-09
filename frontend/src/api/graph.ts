import api from './index'
import type { KnowledgeGraphResponse } from '@/types/insight'

export interface SeedNewsOption {
  news_id: string
  title: string
  platform: string
  label: string
  publish_time: string
}

interface SeedNewsListResponse {
  items: SeedNewsOption[]
  total: number
}

interface NewsDetailRelationNode {
  node_id: string
  name: string
  category: string
  value: number
}

interface NewsDetailRelationEdge {
  source: string
  target: string
  relation_type: string
  weight: number
}

interface NewsDetailResponse {
  news_id: string
  title: string
  relations: {
    nodes: NewsDetailRelationNode[]
    edges: NewsDetailRelationEdge[]
  }
}

export const graphApi = {
  async listSeedNews(keyword = '', page = 1, perPage = 20): Promise<SeedNewsListResponse> {
    const { data } = await api.get('/news/', {
      params: {
        page,
        per_page: perPage,
        ...(keyword.trim() ? { keyword: keyword.trim() } : {}),
      },
    })

    return {
      items: (data.items || []) as SeedNewsOption[],
      total: Number(data.total || 0),
    }
  },

  async getKnowledgeGraph(seedNewsId: string): Promise<KnowledgeGraphResponse> {
    const { data } = await api.get<NewsDetailResponse>(`/news/${encodeURIComponent(seedNewsId)}/detail`)

    const relationNodes = data.relations?.nodes || []
    const relationEdges = data.relations?.edges || []

    const seedId = String(seedNewsId)
    const hasSeedNode = relationNodes.some((node) => node.node_id === seedId)

    const nodes = relationNodes.map((node) => ({
      id: String(node.node_id),
      name: String(node.name || ''),
      category: String(node.category || '实体'),
      value: Number(node.value || 1),
    }))

    if (!hasSeedNode) {
      nodes.unshift({
        id: seedId,
        name: String(data.title || '种子新闻'),
        category: '种子新闻',
        value: 20,
      })
    }

    const edges = relationEdges.map((edge) => ({
      source: String(edge.source),
      target: String(edge.target),
      relation_type: String(edge.relation_type || 'related'),
      weight: Number(edge.weight || 1),
    }))

    return {
      seed_news_id: seedId,
      seed_title: String(data.title || ''),
      nodes,
      edges,
    }
  },
}
