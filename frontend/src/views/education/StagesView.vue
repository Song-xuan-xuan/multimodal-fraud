<template>
  <div class="stages-view page-shell">
    <div class="stages-view__intro">
      <h2>学习资料</h2>
      <p>按学习阶段了解典型案例、识别逻辑与处置要点。</p>
    </div>

    <el-row :gutter="20" class="stages-view__grid">
      <el-col :span="8" v-for="stage in stages" :key="stage.stage_id">
        <el-card class="stages-view__stage-card" shadow="hover" @click="selectStage(stage.stage_id)">
          <h3>{{ stage.name }}</h3>
          <p>{{ stage.description }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="detail" class="stages-view__detail-card">
      <h3>{{ detail.name }}</h3>
      <p class="stages-view__detail-description">{{ detail.description }}</p>
      <div v-for="c in detail.cases" :key="c.case_id" class="stages-view__case">
        <h4>{{ c.title }}</h4>
        <p class="stages-view__summary">{{ c.summary }}</p>
        <p class="stages-view__analysis">{{ c.analysis }}</p>
        <div class="stages-view__tips">
          <el-tag v-for="tip in c.tips" :key="tip">{{ tip }}</el-tag>
        </div>
      </div>
      <el-empty v-if="detail.cases.length === 0" description="暂无案例" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { educationApi, type EducationStage, type EducationStageDetail } from '@/api/education'

const stages = ref<EducationStage[]>([])
const detail = ref<EducationStageDetail | null>(null)

onMounted(async () => {
  try {
    const data = await educationApi.getStages()
    stages.value = data
    if (data.length > 0) await selectStage(data[0].stage_id)
  } catch {
    ElMessage.error('加载学习阶段失败')
  }
})

async function selectStage(stageId: string) {
  try {
    detail.value = await educationApi.getStage(stageId)
  } catch {
    ElMessage.error('加载阶段详情失败')
  }
}
</script>

<style scoped lang="scss">
.stages-view__intro p {
  margin-top: 12px;
  color: var(--tech-theme-text-secondary);
}

.stages-view__grid {
  margin-top: 16px;
}

.stages-view__stage-card {
  cursor: pointer;
}

.stages-view__stage-card h3,
.stages-view__detail-card h3,
.stages-view__case h4 {
  color: var(--tech-theme-text-primary);
}

.stages-view__stage-card p,
.stages-view__summary,
.stages-view__detail-description,
.stages-view__analysis {
  margin-top: 8px;
  color: var(--tech-theme-text-secondary);
  line-height: 1.72;
}

.stages-view__detail-card {
  margin-top: 20px;
}

.stages-view__case + .stages-view__case {
  margin-top: 16px;
}

.stages-view__tips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
</style>
