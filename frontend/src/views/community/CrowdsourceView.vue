<template>
  <div class="crowdsource-view page-shell">
    <div class="crowdsource-view__intro">
      <h2>众包验证</h2>
      <p>参与新闻真实性的验证，贡献你的判断</p>
    </div>

    <div class="crowdsource-view__table">
      <el-table :data="newsList" stripe v-loading="loading" style="margin-top: 16px">
        <el-table-column prop="title" label="新闻标题" min-width="200" />
        <el-table-column prop="label" label="当前标签" width="100">
          <template #default="{ row }">
            <el-tag :type="row.iscredit ? 'success' : 'danger'">{{ row.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button text type="primary" @click="openSubmit(row)">提交证据</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="提交验证证据" width="500px">
      <el-form label-position="top">
        <el-form-item label="你的判断">
          <el-radio-group v-model="evidence.verdict">
            <el-radio value="real">真实</el-radio>
            <el-radio value="fake">虚假</el-radio>
            <el-radio value="uncertain">不确定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="证据来源URL">
          <el-input v-model="evidence.url" placeholder="提供支持你判断的来源链接" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="evidence.description" type="textarea" :rows="3" placeholder="简要说明你的判断依据" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEvidence" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { newsApi, type NewsItem } from '@/api/news'
import { ElMessage } from 'element-plus'
import api from '@/api/index'

const loading = ref(false)
const newsList = ref<NewsItem[]>([])
const dialogVisible = ref(false)
const submitting = ref(false)
const currentNewsId = ref<string | null>(null)
const evidence = reactive({
  verdict: 'uncertain',
  url: '',
  description: '',
})

onMounted(async () => {
  loading.value = true
  try {
    const res = await newsApi.list(1, 20)
    newsList.value = res.items
  } catch {
    ElMessage.error('加载众包验证列表失败')
  } finally {
    loading.value = false
  }
})

function openSubmit(row: NewsItem) {
  currentNewsId.value = String(row.news_id)
  evidence.verdict = 'uncertain'
  evidence.url = ''
  evidence.description = ''
  dialogVisible.value = true
}

async function submitEvidence() {
  if (!currentNewsId.value) return
  submitting.value = true
  try {
    await api.post(`/evidence/submit/${currentNewsId.value}`, evidence)
    ElMessage.success('提交成功')
    dialogVisible.value = false
  } catch {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.crowdsource-view__intro p {
  margin: 12px 0 0;
  color: var(--tech-theme-text-secondary);
}

.crowdsource-view__table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-border-color: var(--tech-theme-border);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.08);
  --el-table-text-color: var(--tech-theme-text-regular);
  --el-table-header-text-color: var(--tech-theme-text-secondary);
}
</style>
