import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'

export function useSocket(namespace = '/') {
  const socket = ref<Socket | null>(null)
  const connected = ref(false)

  onMounted(() => {
    socket.value = io(namespace, {
      path: '/ws/socket.io',
      transports: ['websocket', 'polling'],
    })
    socket.value.on('connect', () => { connected.value = true })
    socket.value.on('disconnect', () => { connected.value = false })
  })

  onUnmounted(() => {
    socket.value?.disconnect()
  })

  function emit(event: string, data: any) {
    socket.value?.emit(event, data)
  }

  function on(event: string, callback: (...args: any[]) => void) {
    socket.value?.on(event, callback)
  }

  return { socket, connected, emit, on }
}
