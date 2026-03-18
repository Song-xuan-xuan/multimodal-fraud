  <template>
    <div class="crowdsource-view page-shell">
      <div class="crowdsource-view__intro">
        <h2>众包验证</h2>
        <p>参与新闻真实性的验证，贡献你的判断</p>
      </div>

      <div class="crowdsource-view__recent">
        <div class="crowdsource-view__recent-head">
          <h3>我的最新提交</h3>
          <el-button text type="primary" @click="loadMySubmissions" :loading="recentLoading">刷新</el-button>
        </div>
        <el-skeleton v-if="recentLoading && !mySubmissions.length" :rows="3" animated />
        <el-empty v-else-if="!mySubmissions.length" description="你还没有提交过证据" />
        <div v-else class="crowdsource-view__recent-list">
          <article v-for="item in mySubmissions" :key="item.id" class="crowdsource-view__recent-item">
            <div>
              <p class="crowdsource-view__recent-title">{{ item.title }}</p>
              <p class="crowdsource-view__recent-meta">{{ item.platform }} · {{ item.submitted_at }}</p>
            </div>
            <el-tag :type="statusTagType(item.status)">{{ statusLabel(item.status) }}</el-tag>
          </article>
        </div>
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
  import { evidenceApi } from '@/api/evidence'
  import type { EvidenceBoardItem } from '@/types/insight'
  import { ElMessage } from 'element-plus'
  import api from '@/api/index'

  const loading = ref(false)
  const newsList = ref<NewsItem[]>([])
  const recentLoading = ref(false)
  const mySubmissions = ref<EvidenceBoardItem[]>([])
  const dialogVisible = ref(false)
  const submitting = ref(false)
  const currentNewsId = ref<string | null>(null)

  const evidence = reactive({
    verdict: 'uncertain',
    url: '',
    description: '',
  })

  function statusLabel(status: string) {
    if (status === 'pending') return '待审核'
    if (status === 'approved') return '已通过'
    if (status === 'rejected') return '已驳回'
    return status
  }

  function statusTagType(status: string): 'warning' | 'success' | 'danger' | 'info' {
    if (status === 'pending') return 'warning'
    if (status === 'approved') return 'success'
    if (status === 'rejected') return 'danger'
    return 'info'
  }

  async function loadMySubmissions() {
    recentLoading.value = true
    try {
      const res = await evidenceApi.listBoard({ page: 1, pageSize: 5 })
      mySubmissions.value = res.items
    } catch {
      ElMessage.error('加载我的证据提交失败')
    } finally {
      recentLoading.value = false
    }
  }

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

    await loadMySubmissions()
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
      const content = [`判断：${evidence.verdict}`, evidence.description.trim()].filter(Boolean).join('\n')
      await api.post('/community/evidence', {
        news_id: currentNewsId.value,
        content,
        source: evidence.url.trim() || undefined,
      })
      await loadMySubmissions()
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

  .crowdsource-view__recent {
    margin-top: 16px;
    padding: 20px;
    border: 1px solid rgba(76, 201, 255, 0.12);
    border-radius: 20px;
    background: rgba(10, 21, 39, 0.72);
  }

  .crowdsource-view__recent-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
  }

  .crowdsource-view__recent-head h3 {
    margin: 0;
    font-size: 18px;
  }

  .crowdsource-view__recent-list {
    display: grid;
    gap: 10px;
  }

  .crowdsource-view__recent-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 14px 16px;
    border-radius: 16px;
    background: rgba(76, 201, 255, 0.06);
  }

  .crowdsource-view__recent-title {
    margin: 0;
    font-weight: 600;
    color: var(--tech-text-primary, #f3f7ff);
  }

  .crowdsource-view__recent-meta {
    margin: 6px 0 0;
    color: var(--tech-theme-text-secondary);
    font-size: 13px;
  }

  .crowdsource-view__table :deep(.el-table) {
    --el-table-bg-color: transparent;
    --el-table-tr-bg-color: rgba(14, 28, 54, 0.6);
    --el-table-border-color: rgba(76, 201, 255, 0.08);
    --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
    --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.10);
    --el-table-text-color: var(--tech-text-regular, #ccc);
    --el-table-header-text-color: var(--tech-text-secondary, #a0aec0);
    --el-table-current-row-bg-color: rgba(76, 201, 255, 0.12);
  }

  .crowdsource-view__table :deep(.el-table__row--striped td.el-table__cell) {
    background: rgba(76, 201, 255, 0.04) !important;
  }
  </style>