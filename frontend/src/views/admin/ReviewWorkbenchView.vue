<template>
  <div class="workbench-page review-workbench">
    <PageHero
      tone="workbench"
      eyebrow="运营工作台"
      title="管理审核工作台"
      description="统一后台运营页的页头、指令区与表格容器，支持线索审核与反诈知识库更新。"
    >
      <article class="hero-metric tech-panel">
        <span>待审核</span>
        <strong>{{ pendingQueue.length }}</strong>
        <small>当前待处理队列</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>已审核</span>
        <strong>{{ reviewedQueue.length }}</strong>
        <small>已完成处置</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>知识条目</span>
        <strong>{{ knowledgeItems.length }}</strong>
        <small>知识库候选条目</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>工作模式</span>
        <strong>{{ hasAccess ? '管理员' : '受限' }}</strong>
        <small>账号权限状态</small>
      </article>
      <template #actions>
        <el-button @click="loadQueue" :loading="loading" :disabled="!hasAccess">刷新队列</el-button>
        <el-button @click="loadKnowledge" :loading="knowledgeLoading" :disabled="!hasAccess">刷新知识库</el-button>
      </template>
    </PageHero>

    <el-result
      v-if="!hasAccess"
      icon="warning"
      title="无权限访问"
      sub-title="仅管理员可见该页面，请使用管理员账号登录。"
      class="access-result tech-panel"
    />

    <template v-else>
      <!-- <section class="content-section tech-panel">
        <SectionHeader eyebrow="批量处置" title="批量审核操作" description="统一运营页指令区视觉，聚焦批量通过、驳回与说明输入。" />
        <el-alert
          v-if="queueErrorMessage"
          type="warning"
          :closable="false"
          show-icon
          class="workbench-inline-alert"
          :title="queueErrorMessage"
        />
        <div class="action-row">
          <el-input v-model="batchReason" placeholder="批量审核说明（可选）" clearable class="reason-input" />
          <el-button
            type="success"
            :disabled="selectedPendingRows.length === 0"
            :loading="batchLoading"
            @click="batchReview('approved')"
          >
            批量通过 ({{ selectedPendingRows.length }})
          </el-button>
          <el-button
            type="danger"
            :disabled="selectedPendingRows.length === 0"
            :loading="batchLoading"
            @click="batchReview('rejected')"
          >
            批量驳回 ({{ selectedPendingRows.length }})
          </el-button>
        </div>
      </section> -->

      <section class="content-section tech-panel">
        <SectionHeader eyebrow="知识更新" title="反诈知识库管理" description="录入案例、审核知识条目，并在需要时重建向量索引。" />
        <el-alert
          v-if="knowledgeErrorMessage"
          type="warning"
          :closable="false"
          show-icon
          class="workbench-inline-alert"
          :title="knowledgeErrorMessage"
        />
        <div class="knowledge-form-grid">
          <el-input v-model="knowledgeForm.item_id" placeholder="* 条目标识（必选），如 case_001" />
          <el-select v-model="knowledgeForm.item_type" placeholder="* 知识类型（必选）">
            <el-option label="案例" value="case" />
            <el-option label="法规" value="law" />
            <el-option label="指南" value="guideline" />
            <el-option label="公告" value="notice" />
          </el-select>
          <el-input v-model="knowledgeForm.fraud_type" placeholder="可选：诈骗类型" />
          <el-input v-model="knowledgeForm.risk_level" placeholder="可选：风险等级" />
          <el-input v-model="knowledgeForm.source" placeholder="可选：来源" />
          <el-input v-model="knowledgeForm.tagsInput" placeholder="可选：标签，使用逗号分隔" />
          <el-input v-model="knowledgeForm.targetGroupsInput" placeholder="可选：适用人群，使用逗号分隔" />
          <el-input v-model="knowledgeForm.signalsInput" placeholder="可选：风险信号，使用逗号分隔" />
          <el-input v-model="knowledgeForm.adviceInput" placeholder="可选：处置建议，使用逗号分隔" />
          <el-input v-model="knowledgeForm.title" class="knowledge-form-grid__full" placeholder="* 标题（必选）" />
          <el-input v-model="knowledgeForm.content" type="textarea" :rows="4" class="knowledge-form-grid__full" placeholder="* 正文内容（必选）" />
          <el-input v-model="knowledgeForm.conclusion" type="textarea" :rows="2" class="knowledge-form-grid__full" placeholder="可选：结论摘要" />
        </div>
        <div class="action-row">
          <el-button type="primary" :loading="createKnowledgeLoading" @click="submitKnowledge">新增知识条目</el-button>
          <el-button type="success" :loading="rebuildLoading" @click="rebuildKnowledgeIndex">新增知识库索引</el-button>
        </div>

        <el-table :data="knowledgeItems" v-loading="knowledgeLoading" class="knowledge-table">
          <el-table-column prop="item_id" label="标识" width="140" />
          <el-table-column prop="item_type" label="类型" width="100" />
          <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
          <el-table-column prop="content" label="描述" min-width="320" show-overflow-tooltip />
          <el-table-column prop="fraud_type" label="诈骗类型" width="140" />
          <el-table-column prop="status" label="状态" width="110" />
          <el-table-column prop="source" label="来源" width="140" show-overflow-tooltip />
          <el-table-column label="操作" width="210">
            <template #default="{ row }">
              <el-button text type="success" @click="reviewKnowledge(row.id, 'approved')">通过</el-button>
              <el-button text type="danger" @click="deleteKnowledge(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <section class="content-section tech-panel tabs-section">
        <SectionHeader eyebrow="审核队列" title="审核列表" description="待审核与已审核队列统一落入后台工作台容器，保持边界和节奏一致。" />
        <el-tabs v-model="activeTab" class="queue-tabs">
          <el-tab-pane :label="`待审核 (${pendingQueue.length})`" name="pending">
            <ReviewQueueTable
              :items="pendingQueue"
              :loading="loading"
              selectable
              show-actions
              @selection-change="onPendingSelectionChange"
              @review="reviewSingle"
              @promote="promoteSubmissionToKnowledge"
            />
          </el-tab-pane>

          <el-tab-pane :label="`已审 (${reviewedQueue.length})`" name="reviewed">
            <ReviewQueueTable
              :items="reviewedQueue"
              :loading="loading"
              show-actions
              @promote="promoteSubmissionToKnowledge"
            />
          </el-tab-pane>
        </el-tabs>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ReviewQueueTable from '@/components/admin/ReviewQueueTable.vue'
import { adminReviewApi } from '@/api/adminReview'
import { knowledgeApi } from '@/api/knowledge'
import { useAuthStore } from '@/stores/auth'
import type { AdminReviewActionStatus, AdminReviewItem } from '@/types/admin'
import type { KnowledgeItem, KnowledgeItemCreatePayload } from '@/types/knowledge'
import SectionHeader from '@/components/dashboard/SectionHeader.vue'
import PageHero from '@/components/page/PageHero.vue'

const authStore = useAuthStore()
const ADMIN_USERNAMES = ['admin']

const activeTab = ref<'pending' | 'reviewed'>('pending')
const loading = ref(false)
const batchLoading = ref(false)
const batchReason = ref('')
const queue = ref<AdminReviewItem[]>([])
const reviewedByActions = ref<AdminReviewItem[]>([])
const selectedPendingRows = ref<AdminReviewItem[]>([])
const queueErrorMessage = ref('')

const knowledgeItems = ref<KnowledgeItem[]>([])
const knowledgeLoading = ref(false)
const createKnowledgeLoading = ref(false)
const rebuildLoading = ref(false)
const knowledgeErrorMessage = ref('')
let queueRequestId = 0
let knowledgeRequestId = 0
const knowledgeForm = reactive({
  item_id: '',
  item_type: 'case',
  title: '',
  content: '',
  conclusion: '',
  fraud_type: '',
  risk_level: '',
  source: '',
  tagsInput: '',
  targetGroupsInput: '',
  signalsInput: '',
  adviceInput: '',
})

const hasAccess = computed(() => ADMIN_USERNAMES.includes((authStore.username || '').trim().toLowerCase()))

const pendingQueue = computed(() => queue.value.filter((item) => item.status === 'pending'))
const reviewedQueue = computed(() => {
  const fromServer = queue.value.filter((item) => item.status !== 'pending')
  const merged = [...reviewedByActions.value, ...fromServer]
  const seen = new Set<number>()
  return merged.filter((item) => {
    if (seen.has(item.id)) return false
    seen.add(item.id)
    return true
  })
})

function onPendingSelectionChange(rows: AdminReviewItem[]) {
  selectedPendingRows.value = rows
}

function moveToReviewed(item: AdminReviewItem) {
  reviewedByActions.value = [item, ...reviewedByActions.value.filter((it) => it.id !== item.id)]
  queue.value = queue.value.filter((it) => it.id !== item.id)
  selectedPendingRows.value = selectedPendingRows.value.filter((it) => it.id !== item.id)
}

function splitInput(value: string) {
  return value
    .split(/[，,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function resetKnowledgeForm() {
  knowledgeForm.item_id = ''
  knowledgeForm.item_type = 'case'
  knowledgeForm.title = ''
  knowledgeForm.content = ''
  knowledgeForm.conclusion = ''
  knowledgeForm.fraud_type = ''
  knowledgeForm.risk_level = ''
  knowledgeForm.source = ''
  knowledgeForm.tagsInput = ''
  knowledgeForm.targetGroupsInput = ''
  knowledgeForm.signalsInput = ''
  knowledgeForm.adviceInput = ''
}

function nowIso() {
  return new Date().toISOString()
}

function updateDemoKnowledge(itemId: number, status: 'approved' | 'rejected') {
  knowledgeItems.value = knowledgeItems.value.map((entry) =>
    entry.id === itemId
      ? {
          ...entry,
          status,
          reviewed_by: authStore.username || 'admin',
          reviewed_reason: '本地审核结果',
          updated_at: nowIso(),
        }
      : entry,
  )
}

async function loadQueue() {
  if (!hasAccess.value) return
  const requestId = ++queueRequestId
  loading.value = true
  queueErrorMessage.value = ''
  try {
    const response = await adminReviewApi.listSubmissions()
    if (requestId !== queueRequestId) {
      return
    }
    queue.value = response.items
  } catch (error: any) {
    if (requestId !== queueRequestId) {
      return
    }
    queueErrorMessage.value = error?.response?.data?.detail || '加载审核队列失败，已保留当前列表。'
  } finally {
    if (requestId === queueRequestId) {
      loading.value = false
    }
  }
}

async function loadKnowledge() {
  if (!hasAccess.value) return
  const requestId = ++knowledgeRequestId
  knowledgeLoading.value = true
  knowledgeErrorMessage.value = ''
  try {
    const response = await knowledgeApi.list()
    if (requestId !== knowledgeRequestId) {
      return
    }
    knowledgeItems.value = response.items
  } catch (error: any) {
    if (requestId !== knowledgeRequestId) {
      return
    }
    knowledgeErrorMessage.value = error?.response?.data?.detail || '加载知识条目失败，已保留当前列表。'
  } finally {
    if (requestId === knowledgeRequestId) {
      knowledgeLoading.value = false
    }
  }
}

async function submitKnowledge() {
  if (!knowledgeForm.item_id || !knowledgeForm.title || !knowledgeForm.content) {
    ElMessage.warning('请填写知识标识、标题和正文')
    return
  }

  const payload: KnowledgeItemCreatePayload = {
    item_id: knowledgeForm.item_id,
    item_type: knowledgeForm.item_type as KnowledgeItemCreatePayload['item_type'],
    title: knowledgeForm.title,
    content: knowledgeForm.content,
    conclusion: knowledgeForm.conclusion,
    fraud_type: knowledgeForm.fraud_type,
    risk_level: knowledgeForm.risk_level,
    source: knowledgeForm.source,
    tags: splitInput(knowledgeForm.tagsInput),
    target_groups: splitInput(knowledgeForm.targetGroupsInput),
    signals: splitInput(knowledgeForm.signalsInput),
    advice: splitInput(knowledgeForm.adviceInput),
  }

  createKnowledgeLoading.value = true
  try {
    const item = await knowledgeApi.create(payload)
    knowledgeItems.value = [item, ...knowledgeItems.value]
    resetKnowledgeForm()
    ElMessage.success('知识条目提交成功')
    await loadKnowledge()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '新增知识条目失败')
  } finally {
    createKnowledgeLoading.value = false
  }
}

async function reviewKnowledge(itemId: number, status: 'approved' | 'rejected') {
  try {
    if (itemId < 0) {
      updateDemoKnowledge(itemId, status)
      ElMessage.success(`知识条目已${status === 'approved' ? '通过' : '驳回'}`)
      return
    }

    const item = await knowledgeApi.review(itemId, { status })
    knowledgeItems.value = knowledgeItems.value.map((entry) => (entry.id === item.id ? item : entry))
    ElMessage.success(`知识条目已${status === 'approved' ? '通过' : '驳回'}`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '知识审核失败')
  }
}

async function deleteKnowledge(itemId: number) {
  try {
    await ElMessageBox.confirm('确定删除这条知识条目吗？删除后将无法恢复。', '提示', { type: 'warning' })

    if (itemId < 0) {
      knowledgeItems.value = knowledgeItems.value.filter((entry) => entry.id !== itemId)
      ElMessage.success('知识条目已删除')
      return
    }

    const result = await knowledgeApi.delete(itemId)
    knowledgeItems.value = knowledgeItems.value.filter((entry) => entry.id !== result.id)
    ElMessage.success(result.message)
  } catch (error: any) {
    if (error === 'cancel' || error === 'close' || error?.message === 'cancel') return
    ElMessage.error(error?.response?.data?.detail || '删除知识条目失败')
  }
}

async function rebuildKnowledgeIndex() {
  rebuildLoading.value = true
  try {
    const result = await knowledgeApi.rebuildIndex()
    ElMessage.success(`${result.message}（共 ${result.item_count} 条）`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '知识索引重建失败')
  } finally {
    rebuildLoading.value = false
  }
}

async function promoteSubmissionToKnowledge(row: AdminReviewItem) {
  try {
    const response = await adminReviewApi.promoteToKnowledge(row.id)
    knowledgeItems.value = [response.item, ...knowledgeItems.value.filter((entry) => entry.id !== response.item.id)]
    ElMessage.success(response.message)
    await loadKnowledge()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '加入知识库失败')
  }
}

async function reviewSingle(row: AdminReviewItem, status: AdminReviewActionStatus) {
  try {
    const response = await adminReviewApi.reviewSubmission(row.id, {
      status,
      reason: row.review_reason || undefined,
    })
    moveToReviewed(response.item)
    ElMessage.success(`审核成功：${status === 'approved' ? '已通过' : '已驳回'}`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '审核失败')
  }
}

async function batchReview(status: AdminReviewActionStatus) {
  if (selectedPendingRows.value.length === 0) {
    ElMessage.warning('请先选择待审核项')
    return
  }

  batchLoading.value = true
  try {
    const result = await adminReviewApi.batchReview(
      selectedPendingRows.value.map((item) => item.id),
      status,
      batchReason.value.trim() || undefined,
    )

    result.succeeded.forEach((item) => moveToReviewed(item))

    if (result.succeeded.length > 0) {
      ElMessage.success(`批量审核成功 ${result.succeeded.length} 条`)
    }
    if (result.failed.length > 0) {
      ElMessage.error(`批量审核失败 ${result.failed.length} 条`)
    }
  } finally {
    batchLoading.value = false
  }
}

onMounted(() => {
  void loadQueue()
  void loadKnowledge()
})
</script>

<style scoped lang="scss">
.workbench-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-workbench__demo-alert {
  border-radius: 20px;
}

.hero-metric {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
}

.hero-metric span,
.hero-metric small {
  color: var(--tech-text-secondary);
}

.hero-metric strong {
  font-size: clamp(24px, 3vw, 34px);
  color: var(--tech-text-primary);
}

.access-result,
.content-section {
  padding: 24px;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.workbench-inline-alert {
  margin-bottom: 4px;
}

.reason-input {
  max-width: 360px;
}

.knowledge-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.knowledge-form-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: -2px;
  color: var(--tech-text-secondary);
  font-size: 13px;
}

.knowledge-form-hint__required {
  color: var(--tech-text-danger);
  font-weight: 600;
}

.knowledge-form-hint__optional {
  color: var(--tech-text-info);
  font-weight: 600;
}

.knowledge-form-grid__full {
  grid-column: 1 / -1;
}

.knowledge-table {
  width: 100%;
}

.tabs-section {
  padding-bottom: 18px;
}

.queue-tabs {
  width: 100%;
}

.queue-tabs :deep(.el-tabs__content) {
  padding-top: 10px;
}

@media (max-width: 900px) {
  .knowledge-form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .access-result,
  .content-section {
    padding: 20px;
  }

  .reason-input {
    max-width: 100%;
    width: 100%;
  }
}
</style>
