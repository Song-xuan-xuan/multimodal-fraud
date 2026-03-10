import api from './index'
import type { RagSource } from '@/types/rag'

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
  sources: RagSource[]
  retrieval_mode?: string | null
}

export interface ChatListItem {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatListResponse {
  items: ChatListItem[]
  total: number
}

export interface ChatDetail {
  id: string
  title: string
  created_at: string
  updated_at: string
  is_shared: boolean
  messages: ChatMessage[]
}

export interface ChatSendResponse {
  user_message: ChatMessage
  assistant_message: ChatMessage
}

export const chatApi = {
  async list() {
    const { data } = await api.get('/chat/')
    return data as ChatListResponse
  },
  async create(title = '新对话') {
    const { data } = await api.post('/chat/', { title })
    return data as ChatDetail
  },
  async get(chatId: string) {
    const { data } = await api.get(`/chat/${chatId}`)
    return data as ChatDetail
  },
  async sendMessage(chatId: string, content: string) {
    const { data } = await api.post(`/chat/${chatId}/messages`, { content })
    return data as ChatSendResponse
  },
  async delete(chatId: string) {
    await api.delete(`/chat/${chatId}`)
  },
  async rename(chatId: string, title: string) {
    const { data } = await api.patch(`/chat/${chatId}`, { title })
    return data as ChatDetail
  },
}
