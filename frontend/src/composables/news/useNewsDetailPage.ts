import { computed, ref } from 'vue'
import { newsApi, type NewsDetailResponse } from '@/api/news'
import type {
  NewsDetailAnchorItem,
  NewsDetailModuleVisibility,
  NewsDetailVM,
} from '@/types/newsDetail'
import { buildAnchors, buildModuleVisibility, normalizeForRender } from '@/utils/news/detailNormalizer'

const EMPTY_VISIBILITY: NewsDetailModuleVisibility = {
  baseInfo: false,
  credibility: false,
  propagationTrend: false,
  propagationPlatforms: false,
  propagationRegions: false,
  relationsRelatedNews: false,
  relationsKnowledgeNodes: false,
  relationsEdges: false,
}

export function useNewsDetailPage() {
  const loading = ref(false)
  const errorMessage = ref('')
  const raw = ref<NewsDetailResponse | null>(null)
  const detail = ref<NewsDetailVM | null>(null)

  const moduleVisibility = computed<NewsDetailModuleVisibility>(() => {
    if (!detail.value) {
      return EMPTY_VISIBILITY
    }
    return buildModuleVisibility(detail.value)
  })

  const anchors = computed<NewsDetailAnchorItem[]>(() => buildAnchors(moduleVisibility.value))

  async function load(newsId: string) {
    loading.value = true
    errorMessage.value = ''
    try {
      const response = await newsApi.getDetail(newsId)
      raw.value = response
      detail.value = normalizeForRender(response)
      return detail.value
    } catch (error) {
      detail.value = null
      raw.value = null
      errorMessage.value = error instanceof Error ? error.message : '加载新闻详情失败'
      return null
    } finally {
      loading.value = false
    }
  }

  function reset() {
    loading.value = false
    errorMessage.value = ''
    raw.value = null
    detail.value = null
  }

  return {
    loading,
    errorMessage,
    raw,
    detail,
    moduleVisibility,
    anchors,
    load,
    reset,
  }
}
