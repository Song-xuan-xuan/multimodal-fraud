<template>
  <div class="edu-view page-shell">
    <div class="edu-view__intro">
      <h2>反诈训练中心</h2>
      <p>进入反诈训练模块，查看模拟演练、风险测试与防骗资料。</p>
    </div>

    <el-row :gutter="20" class="edu-view__grid">
      <el-col :span="8">
        <el-card class="edu-view__card" shadow="hover" @click="$router.push('/education/sandbox')">
          <h3>场景演练</h3>
          <p>在安全环境中体验诈骗场景识别</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="edu-view__card" shadow="hover" @click="$router.push('/education/question')">
          <h3>风险测试</h3>
          <p>测试你的反诈识别能力</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="edu-view__card" shadow="hover" @click="$router.push('/education/stages')">
          <h3>防骗资料</h3>
          <p>了解常见诈骗套路与防范方法</p>
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


