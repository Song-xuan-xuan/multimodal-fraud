import { defineStore } from 'pinia'
import { ref } from 'vue'
import { newsApi, type NewsItem, type NewsListResult } from '@/api/news'

export const useNewsStore = defineStore('news', () => {
  const newsList = ref<NewsItem[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const loading = ref(false)

  async function fetchNews(page = 1, keyword?: string) {
    loading.value = true
    try {
      const result = await newsApi.list(page, 10, keyword)
      newsList.value = result.items
      total.value = result.total
      currentPage.value = page
    } finally {
      loading.value = false
    }
  }

  return { newsList, total, currentPage, loading, fetchNews }
})
