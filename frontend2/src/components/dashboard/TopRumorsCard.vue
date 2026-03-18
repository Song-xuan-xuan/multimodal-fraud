<template>
  <section class="rumor-card">
    <div class="rumor-card__header">
      <div>
        <p class="rumor-card__eyebrow">重点线索</p>
        <h3>待优先核查内容</h3>
      </div>
      <el-button text type="primary" @click="$emit('navigate', '/news')">查看全部</el-button>
    </div>

    <div class="rumor-card__list">
      <article
        v-for="item in items"
        :key="item.news_id"
        :class="['rumor-card__item', item.iscredit ? 'is-success' : 'is-danger']"
        @click="$emit('open-news', item.news_id)"
      >
        <div class="rumor-card__meta">
          <span>{{ item.platform || '未知来源' }}</span>
          <span>{{ item.publish_time || '-' }}</span>
        </div>
        <h4>{{ item.title }}</h4>
        <p>{{ item.summary }}</p>
        <div class="rumor-card__footer">
          <el-tag :type="item.iscredit ? 'success' : 'danger'">{{ item.label || (item.iscredit ? '可信' : '待核查') }}</el-tag>
          <span>{{ item.location || '地域待补充' }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  navigate: [path: string]
  'open-news': [newsId: string]
}>()

defineProps<{
  items: Array<{
    news_id: string
    title: string
    summary: string
    label: string
    platform: string
    publish_time: string
    location: string
    iscredit: boolean
  }>
}>()
</script>

<style scoped lang="scss">
.rumor-card {
  height: 100%;
  padding: 22px;
  border: 1px solid var(--app-border-default);
  border-radius: 28px;
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
}

.rumor-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.rumor-card__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.rumor-card__header h3,
.rumor-card__item h4,
.rumor-card__item p {
  margin: 0;
}

.rumor-card__list {
  display: grid;
  gap: 12px;
}

.rumor-card__item {
  display: grid;
  gap: 10px;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--app-border-default);
  background: color-mix(in srgb, var(--app-surface-card) 92%, white 8%);
  cursor: pointer;
  transition:
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    background var(--tech-duration-fast) var(--tech-ease-out),
    transform var(--tech-duration-fast) var(--tech-ease-out);
}

.rumor-card__item.is-danger {
  border-color: color-mix(in srgb, var(--tech-color-danger) 24%, transparent);
  background: color-mix(in srgb, var(--app-status-danger-soft) 36%, white 64%);
}

.rumor-card__item.is-success {
  border-color: color-mix(in srgb, var(--tech-color-success) 24%, transparent);
  background: color-mix(in srgb, var(--app-status-success-soft) 32%, white 68%);
}

.rumor-card__item:hover {
  transform: translateY(-1px);
}

.rumor-card__meta,
.rumor-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.rumor-card__item h4 {
  font-size: 16px;
  color: var(--app-text-primary);
}

.rumor-card__item.is-danger h4 {
  color: var(--tech-text-danger);
}

.rumor-card__item.is-success h4 {
  color: var(--tech-text-success);
}

.rumor-card__item p {
  color: var(--app-text-secondary);
  line-height: 1.6;
}
</style>
