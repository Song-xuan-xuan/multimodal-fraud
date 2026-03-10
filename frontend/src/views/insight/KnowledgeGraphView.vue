<template>
  <div class="insight-page knowledge-graph-view">
    <PageHero
      eyebrow="专题洞察"
      title="知识图谱洞察"
      description="选择任意新闻作为种子，向外展开关联新闻与关键词网络，探索全局知识关系。"
    >
      <article class="hero-metric tech-panel">
        <span>新闻总量</span>
        <strong>{{ seedTotal }}</strong>
        <small>可选种子候选</small>
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

    <!-- 种子选择区 -->
    <section class="content-section tech-panel">
      <SectionHeader eyebrow="种子检索" title="选择种子新闻" description="搜索关键词筛选新闻，在列表中选择任意一条作为图谱中心。">
        <template #actions>
          <el-input
            v-model="keyword"
            placeholder="按标题搜索新闻"
            class="toolbar-keyword"
            clearable
            @keyup.enter="searchSeeds(1)"
            @clear="searchSeeds(1)"
          />
          <el-button @click="searchSeeds(1)" :loading="loadingSeeds">搜索</el-button>
        </template>
      </SectionHeader>

      <el-table
        :data="seedOptions"
        v-loading="loadingSeeds"
        highlight-current-row
        class="seed-table"
        size="small"
        @current-change="onSeedSelect"
      >
        <el-table-column type="index" width="50" label="#" />
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
        <el-table-column prop="label" label="标签" width="100" />
        <el-table-column prop="platform" label="平台" width="100" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              type="primary"
              text
              size="small"
              :disabled="selectedSeed === row.news_id"
              @click="selectAndLoad(row)"
            >{{ selectedSeed === row.news_id ? '当前' : '选为种子' }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="seed-pager">
        <el-pagination
          background
          layout="total, prev, pager, next, sizes"
          :total="seedTotal"
          :current-page="seedPage"
          :page-size="seedPageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="searchSeeds"
          @size-change="onSeedPageSizeChange"
        />
      </div>
    </section>

    <!-- 图谱控制 + 画布 -->
    <section class="content-section tech-panel graph-section">
      <SectionHeader eyebrow="关系图谱" title="图谱画布" description="以种子新闻为中心，BFS 展开多层关联关系与知识关键词。">
        <template #actions>
          <el-tag v-if="graph.seed_title" type="info" effect="dark" class="seed-tag">{{ graph.seed_title }}</el-tag>
          <el-select v-model="graphDepth" size="small" style="width: 120px" @change="reloadGraph">
            <el-option :value="1" label="展开 1 层" />
            <el-option :value="2" label="展开 2 层" />
            <el-option :value="3" label="展开 3 层" />
          </el-select>
          <el-select v-model="graphMaxNodes" size="small" style="width: 140px" @change="reloadGraph">
            <el-option :value="30" label="最多 30 节点" />
            <el-option :value="60" label="最多 60 节点" />
            <el-option :value="100" label="最多 100 节点" />
            <el-option :value="150" label="最多 150 节点" />
          </el-select>
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

// Seed list with pagination
const seedOptions = ref<SeedNewsOption[]>([])
const seedTotal = ref(0)
const seedPage = ref(1)
const seedPageSize = ref(10)

// Graph controls
const graphDepth = ref(3)
const graphMaxNodes = ref(150)

const graph = reactive<KnowledgeGraphResponse>({
  seed_news_id: '',
  seed_title: '',
  nodes: [],
  edges: [],
})

async function searchSeeds(page = 1) {
  loadingSeeds.value = true
  seedPage.value = page
  try {
    const data = await graphApi.listSeedNews(keyword.value, seedPage.value, seedPageSize.value)
    seedOptions.value = data.items
    seedTotal.value = data.total
    // Auto-select first if nothing selected yet
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

function onSeedPageSizeChange(size: number) {
  seedPageSize.value = size
  searchSeeds(1)
}

function onSeedSelect(row: SeedNewsOption | null) {
  if (row && row.news_id !== selectedSeed.value) {
    selectAndLoad(row)
  }
}

function selectAndLoad(row: SeedNewsOption) {
  selectedSeed.value = row.news_id
  loadGraph()
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
    const data = await graphApi.getKnowledgeGraph(selectedSeed.value, graphDepth.value, graphMaxNodes.value)
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

function reloadGraph() {
  if (selectedSeed.value) loadGraph()
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

/* Seed table dark theme */
.seed-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: rgba(14, 28, 54, 0.6);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.10);
  --el-table-border-color: rgba(76, 201, 255, 0.08);
  --el-table-header-text-color: var(--tech-text-secondary, #a0aec0);
  --el-table-text-color: var(--tech-text-regular, #ccc);
  --el-table-current-row-bg-color: rgba(76, 201, 255, 0.12);
}

.seed-pager {
  display: flex;
  justify-content: flex-end;
}

.seed-pager :deep(.el-pagination button),
.seed-pager :deep(.el-pager li) {
  background: rgba(76, 201, 255, 0.04);
  border-color: rgba(76, 201, 255, 0.12);
  color: var(--tech-text-secondary, #a0aec0);
}

.seed-pager :deep(.el-pager li.is-active) {
  background: rgba(76, 201, 255, 0.14);
  border-color: rgba(76, 201, 255, 0.24);
  color: var(--tech-color-primary-strong, #4cc9ff);
}

.seed-tag {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.graph-section {
  min-height: 640px;
  background: linear-gradient(180deg, rgba(14, 28, 44, 0.72), rgba(7, 15, 28, 0.94));
}

@media (max-width: 640px) {
  .content-section {
    padding: 20px;
  }

  .toolbar-keyword {
    width: 100%;
  }
}
</style>
