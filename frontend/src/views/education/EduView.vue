<template>
  <div class="edu-view page-shell">
    <div class="edu-view__intro">
      <h2>反诈训练中心</h2>
      <p>训练模块已聚焦为两页：答题训练与反诈教练。</p>
    </div>

    <el-row :gutter="20" class="edu-view__grid">
      <el-col :span="12">
        <el-card class="edu-view__card" shadow="hover" @click="$router.push('/education/question')">
          <h3>答题训练</h3>
          <p>完成阶段题后，获取学习目标、微课卡片与薄弱项建议</p>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="edu-view__card" shadow="hover" @click="$router.push('/education/coach')">
          <h3>反诈教练</h3>
          <p>围绕你的错题和薄弱点，获得个性化训练指导</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.edu-view__intro p {
  margin-top: 12px;
  color: var(--tech-theme-text-secondary);
}

.edu-view__grid {
  margin-top: 16px;
}

.edu-view__card {
  height: 100%;
  cursor: pointer;
}

.edu-view__card h3 {
  color: var(--tech-theme-text-primary);
}

.edu-view__card p {
  margin-top: 8px;
  color: var(--tech-theme-text-secondary);
}
</style>


