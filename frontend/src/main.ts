import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { ElMessage } from 'element-plus'

import App from './App.vue'
import router from './router'
import './styles/global.scss'

const app = createApp(App)

app.config.errorHandler = (error, instance, info) => {
  console.error('[vue] runtime error:', error, info, instance)
  ElMessage.error('页面出现异常，已尝试保护当前界面。')
}

if (typeof window !== 'undefined') {
  window.addEventListener('unhandledrejection', (event) => {
    console.error('[window] unhandled rejection:', event.reason)
    ElMessage.error('页面请求出现异常，请稍后重试。')
  })
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
