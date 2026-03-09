import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDetectionStore = defineStore('detection', () => {
  const lastResult = ref<any>(null)
  const loading = ref(false)

  function setResult(result: any) { lastResult.value = result }
  function setLoading(val: boolean) { loading.value = val }

  return { lastResult, loading, setResult, setLoading }
})
