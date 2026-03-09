<template>
  <div class="news-action-bar">
    <div class="action-bar-shell">
      <div class="action-bar-head">
        <div>
          <p class="action-bar-kicker">ENGAGEMENT</p>
          <h3 class="action-bar-title">参与这条新闻的研判</h3>
        </div>
        <div class="action-bar-summary">
          <span class="summary-pill">反馈 {{ stats.feedback_total }}</span>
          <span class="summary-pill">已通过 {{ stats.approved }}</span>
        </div>
      </div>

      <div class="action-row">
        <FavoriteButton :favorited="favorited" @toggle="emit('toggle-favorite')" />
        <VotePanel :stats="stats" :my-vote="myVote" :loading="voteLoading" @vote="(vote) => emit('vote', vote)" />
        <el-button class="rebuttal-trigger" type="primary" :loading="rebuttalLoading" @click="dialogVisible = true">
          提交驳斥
        </el-button>
      </div>

      <div class="feedback-stats">
        <span>待审核 {{ stats.pending }}</span>
        <span>已通过 {{ stats.approved }}</span>
        <span>已驳回 {{ stats.rejected }}</span>
      </div>
    </div>
  </div>

  <el-dialog v-model="dialogVisible" title="提交驳斥" width="520px" class="rebuttal-dialog" @closed="onDialogClosed">
    <ModalShell>
      <el-input
        v-model="rebuttalText"
        type="textarea"
        :rows="5"
        maxlength="500"
        show-word-limit
        placeholder="请输入驳斥理由或证据"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="rebuttalLoading" @click="submitRebuttal">提交</el-button>
      </template>
    </ModalShell>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import FavoriteButton from './FavoriteButton.vue'
import VotePanel from './VotePanel.vue'
import ModalShell from '@/components/page/ModalShell.vue'
import type { NewsFeedbackStats, VoteOption } from '@/types/engagement'

const props = defineProps<{
  favorited: boolean
  stats: NewsFeedbackStats
  myVote: VoteOption | null
  voteLoading: boolean
  rebuttalLoading: boolean
}>()

const emit = defineEmits<{
  (event: 'toggle-favorite'): void
  (event: 'vote', vote: VoteOption): void
  (event: 'submit-rebuttal', content: string): void
}>()

const dialogVisible = ref(false)
const rebuttalText = ref('')

function submitRebuttal() {
  const content = rebuttalText.value.trim()
  if (!content) {
    ElMessage.warning('请先填写驳斥内容')
    return
  }
  emit('submit-rebuttal', content)
}

function onDialogClosed() {
  if (!props.rebuttalLoading) {
    rebuttalText.value = ''
  }
}

defineExpose({
  closeDialog() {
    dialogVisible.value = false
    rebuttalText.value = ''
  },
})
</script>

<style scoped>
.news-action-bar {
  width: 100%;
}

.action-bar-shell {
  padding: 18px;
  border: 1px solid var(--tech-border-color);
  border-radius: 22px;
  background:
    radial-gradient(circle at top right, rgba(76, 201, 255, 0.1), transparent 38%),
    linear-gradient(180deg, rgba(14, 28, 48, 0.94), rgba(8, 18, 34, 0.96));
  box-shadow: var(--tech-shadow-sm);
  backdrop-filter: blur(18px);
}

.action-bar-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.action-bar-kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--tech-color-primary-strong);
}

.action-bar-title {
  margin: 0;
  font-size: 18px;
  line-height: 1.35;
  color: var(--tech-text-primary);
}

.action-bar-summary {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.summary-pill {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border: 1px solid rgba(76, 201, 255, 0.14);
  border-radius: 999px;
  background: rgba(125, 211, 252, 0.06);
  color: var(--tech-text-secondary);
  font-size: 12px;
  font-weight: 600;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.rebuttal-trigger {
  margin-left: auto;
}

.feedback-stats {
  margin-top: 14px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--tech-text-secondary);
}

:deep(.rebuttal-dialog .el-dialog) {
  border: 1px solid var(--tech-border-color);
  border-radius: 24px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(14, 28, 48, 0.96), rgba(8, 18, 34, 0.98));
}

:deep(.rebuttal-dialog .el-dialog__header) {
  margin: 0;
  padding: 22px 24px 0;
}

:deep(.rebuttal-dialog .el-dialog__title) {
  color: var(--tech-text-primary);
}

:deep(.rebuttal-dialog .el-dialog__body) {
  padding: 12px 20px 20px;
}

@media (max-width: 768px) {
  .action-bar-head {
    flex-direction: column;
  }

  .action-bar-summary {
    justify-content: flex-start;
  }

  .rebuttal-trigger {
    margin-left: 0;
    width: 100%;
  }
}
</style>
