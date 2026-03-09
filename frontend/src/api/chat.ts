import api from './index'

export const chatApi = {
  async list() {
    const { data } = await api.get('/chat/')
    return data
  },
  async create(title = '新对话') {
    const { data } = await api.post('/chat/', { title })
    return data
  },
  async get(chatId: string) {
    const { data } = await api.get(`/chat/${chatId}`)
    return data
  },
  async sendMessage(chatId: string, content: string) {
    const { data } = await api.post(`/chat/${chatId}/messages`, { content })
    return data
  },
  async delete(chatId: string) {
    await api.delete(`/chat/${chatId}`)
  },
}
