import api from './index'
import type { RawAIAudioDetectionResponse, RawAIImageDetectionResponse, RawAITextDetectionResponse } from '@/types/detection'
import type {
  RawAggregateNewsDetectionResponse,
  RawConsistencyDetectionResponse,
  RawNewsDetectionResponse,
  RawSegmentsDetectionResponse,
} from '@/types/newsDetection'

export const detectionApi = {
  async detectAIText(text: string) {
    const { data } = await api.post<RawAITextDetectionResponse>('/detection/ai-text', { text })
    return data
  },
  async detectAIImage(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post<RawAIImageDetectionResponse>('/detection/ai-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async detectAudioRisk(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post<RawAIAudioDetectionResponse>('/detection/audio-risk', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async detectNews(title: string, content: string) {
    const { data } = await api.post<RawNewsDetectionResponse>('/detection/news', { title, content })
    return data
  },
  async detectByUrl(url: string) {
    const { data } = await api.post<RawConsistencyDetectionResponse>('/detection/url', { url })
    return data
  },
  async detectByFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post<RawConsistencyDetectionResponse>('/detection/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async detectSegments(title: string, content: string, segmentSize = 500) {
    const { data } = await api.post<RawSegmentsDetectionResponse>('/detection/segments', {
      title,
      content,
      segment_size: segmentSize,
    })
    return data
  },
  async detectAggregate(title: string, content: string, url?: string) {
    const { data } = await api.post<RawAggregateNewsDetectionResponse>('/detection/aggregate', {
      title,
      content,
      ...(url ? { url } : {}),
    })
    return data
  },
}
