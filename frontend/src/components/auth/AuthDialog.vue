<template>
  <el-dialog
    :model-value="modelValue"
    width="min(92vw, 460px)"
    :show-close="true"
    align-center
    class="auth-dialog"
    @close="emit('update:modelValue', false)"
  >
    <div class="auth-dialog__ambient auth-dialog__ambient--left" aria-hidden="true" />
    <div class="auth-dialog__ambient auth-dialog__ambient--right" aria-hidden="true" />

    <template #header>
      <div class="auth-dialog__header">
        <span class="auth-dialog__badge">FRAUDSHIELD · ACCESS</span>
        <span class="auth-dialog__title">欢迎使用 FraudShield</span>
        <span class="auth-dialog__subtitle">请先登录或注册后继续访问</span>
      </div>
    </template>

    <el-tabs v-model="activeTab" stretch class="auth-dialog__tabs">
      <el-tab-pane label="登录" name="login">
        <el-form :model="loginForm" label-position="top" class="auth-dialog__form" @submit.prevent="handleLogin">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="loginLoading" style="width: 100%">登录</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="注册" name="register">
        <el-form :model="registerForm" label-position="top" class="auth-dialog__form" @submit.prevent="handleRegister">
          <el-form-item label="用户名">
            <el-input v-model="registerForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="registerLoading" style="width: 100%">注册</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    initialTab?: 'login' | 'register'
  }>(),
  {
    initialTab: 'login',
  },
)

const emit = defineEmits<{
  'update:modelValue': [boolean]
  success: []
}>()

const authStore = useAuthStore()
const activeTab = ref<'login' | 'register'>(props.initialTab)
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', password: '', confirmPassword: '' })

watch(
  () => props.initialTab,
  (value) => {
    activeTab.value = value
  },
)

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      activeTab.value = props.initialTab
    }
  },
)

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }

  loginLoading.value = true
  try {
    await authStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    emit('update:modelValue', false)
    emit('success')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loginLoading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.username || !registerForm.password || !registerForm.confirmPassword) {
    ElMessage.warning('请填写所有字段')
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  registerLoading.value = true
  try {
    await authApi.register(registerForm.username, registerForm.password, registerForm.confirmPassword)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    loginForm.password = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '注册失败')
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-dialog :deep(.el-dialog) {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(124, 231, 255, 0.18);
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(8, 18, 32, 0.96), rgba(3, 10, 18, 0.98));
  box-shadow: 0 30px 100px rgba(0, 0, 0, 0.52), 0 0 0 1px rgba(124, 231, 255, 0.06);
  backdrop-filter: blur(22px);
}

.auth-dialog :deep(.el-dialog__body) {
  position: relative;
  padding-top: 8px;
}

.auth-dialog :deep(.el-dialog__headerbtn) {
  top: 20px;
  right: 20px;
}

.auth-dialog__ambient {
  position: absolute;
  top: -10%;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  filter: blur(36px);
  opacity: 0.42;
  pointer-events: none;
}

.auth-dialog__ambient--left {
  left: -8%;
  background: radial-gradient(circle, rgba(92, 255, 225, 0.22) 0%, rgba(0, 0, 0, 0) 70%);
}

.auth-dialog__ambient--right {
  right: -8%;
  background: radial-gradient(circle, rgba(36, 170, 255, 0.2) 0%, rgba(0, 0, 0, 0) 70%);
}

.auth-dialog__header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-dialog__badge {
  display: inline-flex;
  width: fit-content;
  padding: 6px 10px;
  border: 1px solid rgba(124, 231, 255, 0.18);
  border-radius: 999px;
  background: rgba(7, 19, 30, 0.6);
  color: rgba(212, 245, 255, 0.78);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.22em;
}

.auth-dialog__title {
  color: #f3fbff;
  font-size: 24px;
  font-weight: 700;
}

.auth-dialog__subtitle {
  color: rgba(205, 232, 255, 0.72);
  font-size: 13px;
}

.auth-dialog__tabs {
  position: relative;
  z-index: 1;
}

.auth-dialog__form {
  margin-top: 8px;
}

.auth-dialog__tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(124, 231, 255, 0.08);
}

.auth-dialog__tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #7ce7ff, #59ffd7);
}

.auth-dialog__tabs :deep(.el-tabs__item) {
  color: rgba(214, 238, 255, 0.76);
}

.auth-dialog__tabs :deep(.el-tabs__item.is-active) {
  color: #8cf7ff;
}

.auth-dialog__tabs :deep(.el-form-item__label) {
  color: rgba(226, 242, 255, 0.86);
}

.auth-dialog__tabs :deep(.el-input__wrapper) {
  border: 1px solid rgba(124, 231, 255, 0.1);
  border-radius: 14px;
  background: rgba(8, 20, 32, 0.68);
  box-shadow: none;
  transition: border-color var(--tech-duration-fast) var(--tech-ease-out), box-shadow var(--tech-duration-fast) var(--tech-ease-out);
}

.auth-dialog__tabs :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(124, 231, 255, 0.32);
  box-shadow: 0 0 0 1px rgba(124, 231, 255, 0.16), 0 0 18px rgba(92, 255, 225, 0.12);
}

.auth-dialog__tabs :deep(.el-input__inner) {
  color: #eef9ff;
}

.auth-dialog__tabs :deep(.el-button--primary) {
  border-color: rgba(124, 231, 255, 0.24);
  background: linear-gradient(135deg, rgba(38, 195, 172, 0.92), rgba(46, 132, 255, 0.92));
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.28);
}
</style>
