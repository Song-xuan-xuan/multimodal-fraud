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

interface GraphApiResponse {
  seed_news_id: string
  seed_title: string
  nodes: Array<{ node_id: string; name: string; category: string; value: number }>
  edges: Array<{ source: string; target: string; relation_type: string; weight: number }>
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

  async getKnowledgeGraph(seedNewsId: string, depth = 2, maxNodes = 60): Promise<KnowledgeGraphResponse> {
    const { data } = await api.get<GraphApiResponse>(
      `/news/${encodeURIComponent(seedNewsId)}/graph`,
      { params: { depth, max_nodes: maxNodes } },
    )

    const nodes = (data.nodes || []).map((node) => ({
      id: String(node.node_id),
      name: String(node.name || ''),
      category: String(node.category || 'news'),
      value: Number(node.value || 1),
    }))

    const edges = (data.edges || []).map((edge) => ({
      source: String(edge.source),
      target: String(edge.target),
      relation_type: String(edge.relation_type || 'related'),
      weight: Number(edge.weight || 1),
    }))

    return {
      seed_news_id: String(data.seed_news_id),
      seed_title: String(data.seed_title || ''),
      nodes,
      edges,
    }
  },
}
