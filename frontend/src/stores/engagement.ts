import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { engagementApi } from '@/api/engagement'
import type { EngagementLoadingState, NewsFeedbackStats, VoteOption } from '@/types/engagement'

const FAVORITE_STORAGE_KEY = 'news_detail_favorites'

function createLoadingState(): EngagementLoadingState {
  return {
    stats: false,
    vote: false,
    rebuttal: false,
  }
}

function createEmptyStats(newsId: string): NewsFeedbackStats {
  return {
    news_id: newsId,
    total: 0,
    vote_total: 0,
    vote_agree: 0,
    vote_disagree: 0,
    feedback_total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
  }
}

export const useEngagementStore = defineStore('engagement', () => {
  const favoriteIds = ref<string[]>([])
  const hydrated = ref(false)

  const statsByNews = ref<Record<string, NewsFeedbackStats>>({})
  const myVoteByNews = ref<Record<string, VoteOption | null>>({})
  const loadingByNews = ref<Record<string, EngagementLoadingState>>({})

  function ensureHydrated() {
    if (hydrated.value || typeof window === 'undefined') {
      return
    }

    try {
      const raw = localStorage.getItem(FAVORITE_STORAGE_KEY)
      if (!raw) {
        hydrated.value = true
        return
      }
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        favoriteIds.value = parsed.filter((id) => typeof id === 'string' && id.trim())
      }
    } catch {
      favoriteIds.value = []
    } finally {
      hydrated.value = true
    }
  }

  function persistFavorites() {
    if (typeof window === 'undefined') {
      return
    }
    localStorage.setItem(FAVORITE_STORAGE_KEY, JSON.stringify(favoriteIds.value))
  }

  function ensureLoadingState(newsId: string) {
    if (!loadingByNews.value[newsId]) {
      loadingByNews.value[newsId] = createLoadingState()
    }
    return loadingByNews.value[newsId]
  }

  function isFavorited(newsId: string) {
    ensureHydrated()
    return favoriteIds.value.includes(newsId)
  }

  function toggleFavorite(newsId: string) {
    ensureHydrated()
    const index = favoriteIds.value.indexOf(newsId)
    if (index >= 0) {
      favoriteIds.value.splice(index, 1)
      persistFavorites()
      return false
    }

    favoriteIds.value.unshift(newsId)
    persistFavorites()
    return true
  }

  function getStats(newsId: string) {
    return statsByNews.value[newsId] || createEmptyStats(newsId)
  }

  function getMyVote(newsId: string) {
    return myVoteByNews.value[newsId] || null
  }

  function getLoading(newsId: string) {
    return ensureLoadingState(newsId)
  }

  async function fetchStats(newsId: string) {
    const loading = ensureLoadingState(newsId)
    loading.stats = true
    try {
      const [stats, mine] = await Promise.all([
        engagementApi.getStats(newsId),
        engagementApi.getMyFeedback(newsId),
      ])
      statsByNews.value[newsId] = stats

      const latestVote = mine.items
        .filter((item) => item.type === 'vote')
        .sort((a, b) => +new Date(b.updated_at) - +new Date(a.updated_at))[0]

      if (latestVote && (latestVote.content === 'agree' || latestVote.content === 'disagree')) {
        myVoteByNews.value[newsId] = latestVote.content
      } else if (!(newsId in myVoteByNews.value)) {
        myVoteByNews.value[newsId] = null
      }

      return stats
    } finally {
      loading.stats = false
    }
  }

  async function submitVote(newsId: string, vote: VoteOption) {
    const loading = ensureLoadingState(newsId)
    loading.vote = true
    try {
      await engagementApi.submitVote(newsId, vote)
      myVoteByNews.value[newsId] = vote
      await fetchStats(newsId)
    } finally {
      loading.vote = false
    }
  }

  async function submitRebuttal(newsId: string, feedback: string) {
    const loading = ensureLoadingState(newsId)
    loading.rebuttal = true
    try {
      const response = await engagementApi.submitRebuttal(newsId, feedback)
      await fetchStats(newsId)
      return response
    } finally {
      loading.rebuttal = false
    }
  }

  const favoriteCount = computed(() => favoriteIds.value.length)

  return {
    favoriteCount,
    ensureHydrated,
    isFavorited,
    toggleFavorite,
    getStats,
    getMyVote,
    getLoading,
    fetchStats,
    submitVote,
    submitRebuttal,
  }
})
