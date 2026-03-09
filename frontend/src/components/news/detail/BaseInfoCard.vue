<template>
  <SectionStateWrapper section-id="base-info" title="基础信息" :has-data="Boolean(baseInfo)">
    <template v-if="baseInfo">
      <h2 class="news-title">{{ baseInfo.title }}</h2>

      <div class="meta-row">
        <el-tag :type="baseInfo.isCredit ? 'success' : 'danger'">{{ baseInfo.label }}</el-tag>
        <el-tag type="info">{{ baseInfo.platform }}</el-tag>
        <el-tag type="warning">{{ baseInfo.location }}</el-tag>
        <el-tag v-if="baseInfo.hashtag">{{ baseInfo.hashtag }}</el-tag>
      </div>

      <el-descriptions :column="3" border class="base-descriptions">
        <el-descriptions-item label="新闻ID">{{ baseInfo.newsId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发布时间">{{ baseInfo.publishTime }}</el-descriptions-item>
        <el-descriptions-item label="核验时间">{{ baseInfo.checkTime }}</el-descriptions-item>
        <el-descriptions-item label="原文链接" :span="3">
          <a :href="baseInfo.url" target="_blank" rel="noopener noreferrer">{{ baseInfo.url }}</a>
        </el-descriptions-item>
      </el-descriptions>

      <el-alert class="block base-alert" title="摘要" type="info" :closable="false" :description="baseInfo.summary" />

      <div class="block">
        <h4>内容</h4>
        <p class="paragraph">{{ baseInfo.content }}</p>
      </div>

      <el-alert
        class="block base-alert"
        title="结论"
        :type="baseInfo.isCredit ? 'success' : 'warning'"
        :description="baseInfo.conclusion"
        :closable="false"
        show-icon
      />
    </template>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
import type { NewsDetailBaseInfoVM } from '@/types/newsDetail'
import SectionStateWrapper from './SectionStateWrapper.vue'

defineProps<{
  baseInfo: NewsDetailBaseInfoVM | null
}>()
</script>

<style scoped>
.news-title {
  margin: 0;
  font-size: 22px;
  color: var(--tech-theme-text-primary);
}

.meta-row {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.base-descriptions {
  margin-top: 16px;
}

.block {
  margin-top: 16px;
}

.base-alert {
  --el-alert-title-color: var(--tech-theme-text-primary);
  --el-alert-description-color: var(--tech-theme-text-secondary);
}

.paragraph {
  margin: 8px 0 0;
  line-height: 1.8;
  white-space: pre-wrap;
  color: var(--tech-theme-text-regular);
}
</style>
