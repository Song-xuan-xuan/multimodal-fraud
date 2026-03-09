<template>
  <div class="auth-redirect">
    <el-card class="auth-redirect__card">
      <div class="auth-redirect__title">正在返回首页</div>
      <div class="auth-redirect__desc">登录入口已整合到首页悬浮框，请稍候…</div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appRouteName } from '@/router'

const router = useRouter()
const route = useRoute()

onMounted(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : undefined
  void router.replace({
    name: appRouteName.home,
    query: {
      auth: 'login',
      ...(redirect ? { redirect } : {}),
    },
  })
})
</script>

<style scoped lang="scss">
.auth-redirect {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(3, 8, 16, 0.98), rgba(1, 4, 10, 1));
}

.auth-redirect__card {
  width: min(90vw, 420px);
  border: 1px solid rgba(124, 231, 255, 0.18);
  background: rgba(6, 14, 26, 0.78);
}

.auth-redirect__title {
  color: #f4fbff;
  font-size: 22px;
  font-weight: 700;
}

.auth-redirect__desc {
  margin-top: 8px;
  color: rgba(210, 235, 255, 0.72);
}
</style>
