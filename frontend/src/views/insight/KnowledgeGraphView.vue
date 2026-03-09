<template>
  <div class="insight-page knowledge-graph-view">
    <PageHero
      eyebrow="专题洞察"
      title="知识图谱洞察"
      description="围绕种子新闻构建传播关系图谱，统一专题页的页头、工具栏与图谱容器视觉。"
    >
      <article class="hero-metric tech-panel">
        <span>种子候选</span>
        <strong>{{ seedOptions.length }}</strong>
        <small>当前检索结果</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>节点数量</span>
        <strong>{{ graph.nodes.length }}</strong>
        <small>关系网络规模</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>关系数量</span>
        <strong>{{ graph.edges.length }}</strong>
        <small>边连接总数</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>当前种子</span>
        <strong>{{ graph.seed_title || '-' }}</strong>
        <small>图谱中心新闻</small>
      </article>
    </PageHero>

    <section class="content-section tech-panel">
      <SectionHeader eyebrow="种子检索" title="图谱条件设置" description="统一洞察页工具区，支持按关键词搜索并切换图谱种子新闻。">
        <template #actions>
          <el-input
            v-model="keyword"
            placeholder="按标题检索新闻"
            class="toolbar-keyword"
            clearable
            @keyup.enter="searchSeeds"
            @clear="searchSeeds"
          />
          <el-button @click="searchSeeds" :loading="loadingSeeds">搜索</el-button>
        </template>
      </SectionHeader>

      <el-select
        v-model="selectedSeed"
        filterable
        clearable
        placeholder="请选择新闻"
        class="seed-select"
        :loading="loadingSeeds"
        @change="loadGraph"
      >
        <el-option
          v-for="item in seedOptions"
          :key="item.news_id"
          :label="`${item.title}（${item.platform || '-'}）`"
          :value="item.news_id"
        />
      </el-select>
    </section>

    <section class="content-section tech-panel graph-section">
      <SectionHeader eyebrow="关系图谱" title="图谱画布" description="统一专题页图表容器边界、空态和加载状态，用于承载复杂关系图谱。">
        <template #actions>
          <el-tag v-if="graph.seed_title" type="info" effect="dark">{{ graph.seed_title }}</el-tag>
        </template>
      </SectionHeader>
      <KnowledgeGraphCanvas :graph="graph" :loading="loadingGraph" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { graphApi, type SeedNewsOption } from '@/api/graph'
import type { KnowledgeGraphResponse } from '@/types/insight'
import KnowledgeGraphCanvas from '@/components/insight/KnowledgeGraphCanvas.vue'
import SectionHeader from '@/components/dashboard/SectionHeader.vue'
import PageHero from '@/components/page/PageHero.vue'
import { chartColors } from '@/utils/chartColors'

const heroAccentColor = chartColors.semantic.fake

const keyword = ref('')
const selectedSeed = ref('')

const loadingSeeds = ref(false)
const loadingGraph = ref(false)

const seedOptions = ref<SeedNewsOption[]>([])

const graph = reactive<KnowledgeGraphResponse>({
  seed_news_id: '',
  seed_title: '',
  nodes: [],
  edges: [],
})

async function searchSeeds() {
  loadingSeeds.value = true
  try {
    const data = await graphApi.listSeedNews(keyword.value, 1, 30)
    seedOptions.value = data.items
    if (!selectedSeed.value && data.items.length > 0) {
      selectedSeed.value = data.items[0].news_id
      await loadGraph()
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '种子新闻加载失败')
  } finally {
    loadingSeeds.value = false
  }
}

async function loadGraph() {
  if (!selectedSeed.value) {
    graph.seed_news_id = ''
    graph.seed_title = ''
    graph.nodes = []
    graph.edges = []
    return
  }

  loadingGraph.value = true
  try {
    const data = await graphApi.getKnowledgeGraph(selectedSeed.value)
    graph.seed_news_id = data.seed_news_id
    graph.seed_title = data.seed_title
    graph.nodes = data.nodes
    graph.edges = data.edges
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '知识图谱加载失败')
  } finally {
    loadingGraph.value = false
  }
}

onMounted(async () => {
  await searchSeeds()
})
</script>

<style scoped lang="scss">
.insight-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  font-size: clamp(22px, 3vw, 32px);
  color: var(--tech-text-primary);
}

.hero-metric:first-child strong,
.hero-metric:last-child strong {
  color: v-bind(heroAccentColor);
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
}

.toolbar-keyword {
  width: 260px;
}

.seed-select {
  width: min(100%, 520px);
}

.graph-section {
  min-height: 640px;
  background: linear-gradient(180deg, rgba(14, 28, 44, 0.72), rgba(7, 15, 28, 0.94));
}

@media (max-width: 640px) {
  .content-section {
    padding: 20px;
  }

  .toolbar-keyword,
  .seed-select {
    width: 100%;
  }
}
</style>
