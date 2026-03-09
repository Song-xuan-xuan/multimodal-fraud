<template>
  <div class="vote-panel">
    <el-button-group>
      <el-button
        :type="myVote === 'agree' ? 'success' : 'default'"
        :loading="loading"
        @click="emit('vote', 'agree')"
      >
        认同 ({{ stats.vote_agree }})
      </el-button>
      <el-button
        :type="myVote === 'disagree' ? 'danger' : 'default'"
        :loading="loading"
        @click="emit('vote', 'disagree')"
      >
        驳斥 ({{ stats.vote_disagree }})
      </el-button>
    </el-button-group>
    <span class="vote-total">总投票 {{ stats.vote_total }}</span>
  </div>
</template>

<script setup lang="ts">
import type { NewsFeedbackStats, VoteOption } from '@/types/engagement'

defineProps<{
  stats: NewsFeedbackStats
  myVote: VoteOption | null
  loading: boolean
}>()

const emit = defineEmits<{
  (event: 'vote', vote: VoteOption): void
}>()
</script>

<style scoped>
.vote-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.vote-total {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
