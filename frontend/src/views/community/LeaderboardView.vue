<template>
  <div class="leaderboard-view page-shell">
    <h2>排行榜</h2>
    <el-card class="leaderboard-view__card">
      <template #header>用户贡献排名</template>
      <el-table :data="leaderboard" stripe v-loading="loading">
        <el-table-column type="index" label="排名" width="80">
          <template #default="{ $index }">
            <span :class="['leaderboard-view__rank', { 'leaderboard-view__rank--top': $index < 3 }]">
              {{ $index + 1 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" />
        <el-table-column prop="contributions" label="贡献数" sortable />
        <el-table-column prop="accuracy" label="准确率">
          <template #default="{ row }">
            <el-progress :percentage="Math.round((row.accuracy || 0) * 100)" :stroke-width="12" />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !leaderboard.length" description="暂无排行榜数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/index'

const leaderboard = ref<any[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/community/leaderboard')
    leaderboard.value = data.items || data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped lang="scss">
.leaderboard-view__card {
  margin-top: 16px;
}

.leaderboard-view__rank--top {
  color: var(--tech-text-warning);
  font-weight: 700;
}
</style>
