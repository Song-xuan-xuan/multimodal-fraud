import { beforeEach, describe, expect, it, vi } from 'vitest'

const getStatsMock = vi.hoisted(() => vi.fn())
const getMyFeedbackMock = vi.hoisted(() => vi.fn())
const submitVoteMock = vi.hoisted(() => vi.fn())
const submitRebuttalMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/engagement', () => ({
  engagementApi: {
    getStats: getStatsMock,
    getMyFeedback: getMyFeedbackMock,
    submitVote: submitVoteMock,
    submitRebuttal: submitRebuttalMock,
  },
}))

import { createPinia, setActivePinia } from 'pinia'
import { useEngagementStore } from '../engagement'

const storageData: Record<string, string> = {}
const localStorageMock = {
  getItem: vi.fn((key: string) => (key in storageData ? storageData[key] : null)),
  setItem: vi.fn((key: string, value: string) => {
    storageData[key] = String(value)
  }),
  clear: vi.fn(() => {
    Object.keys(storageData).forEach((key) => delete storageData[key])
  }),
}

Object.defineProperty(globalThis, 'window', {
  value: {},
  writable: true,
})

Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

describe('engagement store regression', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('toggles favorites and persists to localStorage', () => {
    const store = useEngagementStore()

    expect(store.isFavorited('news-1')).toBe(false)

    const added = store.toggleFavorite('news-1')
    expect(added).toBe(true)
    expect(store.isFavorited('news-1')).toBe(true)

    const removed = store.toggleFavorite('news-1')
    expect(removed).toBe(false)
    expect(store.isFavorited('news-1')).toBe(false)

    const raw = localStorage.getItem('news_detail_favorites')
    expect(raw).toBe(JSON.stringify([]))
  })

  it('updates myVote and stats after submitVote', async () => {
    const store = useEngagementStore()
    getStatsMock.mockResolvedValue({
      news_id: 'news-1',
      total: 3,
      vote_total: 2,
      vote_agree: 1,
      vote_disagree: 1,
      feedback_total: 1,
      pending: 1,
      approved: 1,
      rejected: 1,
    })
    getMyFeedbackMock.mockResolvedValue({
      items: [
        {
          id: 1,
          news_id: 'news-1',
          type: 'vote',
          content: 'agree',
          submitted_by: 'tester',
          submitted_at: '2026-03-01T10:00:00+00:00',
          updated_at: '2026-03-01T10:00:00+00:00',
          status: 'pending',
          reason: '',
          reviewed_by: '',
          reviewed_at: '',
        },
      ],
      total: 1,
      page: 1,
      page_size: 50,
      total_pages: 1,
    })
    submitVoteMock.mockResolvedValue({})

    await store.submitVote('news-1', 'agree')

    expect(submitVoteMock).toHaveBeenCalledWith('news-1', 'agree')
    expect(store.getMyVote('news-1')).toBe('agree')
    expect(store.getStats('news-1').vote_total).toBe(2)
    expect(store.getLoading('news-1').vote).toBe(false)
  })

  it('hydrates favorites from localStorage only once', () => {
    storageData.news_detail_favorites = JSON.stringify(['news-3'])
    const store = useEngagementStore()

    store.ensureHydrated()
    expect(store.isFavorited('news-3')).toBe(true)

    storageData.news_detail_favorites = JSON.stringify([])
    store.ensureHydrated()
    expect(store.isFavorited('news-3')).toBe(true)
  })

  it('submits rebuttal and refreshes stats', async () => {
    const store = useEngagementStore()
    submitRebuttalMock.mockResolvedValue({ message: 'ok' })
    getStatsMock.mockResolvedValue({
      news_id: 'news-2',
      total: 1,
      vote_total: 0,
      vote_agree: 0,
      vote_disagree: 0,
      feedback_total: 1,
      pending: 1,
      approved: 0,
      rejected: 0,
    })
    getMyFeedbackMock.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 50,
      total_pages: 0,
    })

    await store.submitRebuttal('news-2', '证据补充')

    expect(submitRebuttalMock).toHaveBeenCalledWith('news-2', '证据补充')
    expect(store.getStats('news-2').feedback_total).toBe(1)
  })
})
