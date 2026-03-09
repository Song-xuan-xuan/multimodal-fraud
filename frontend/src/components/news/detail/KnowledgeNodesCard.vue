<template>
  <SectionStateWrapper
    section-id="knowledge-nodes"
    title="知识节点与关系"
    :has-data="nodes.length > 0 || edges.length > 0"
    :empty-text="emptyText || '暂无关系网络数据'"
  >
    <div>
      <h4 class="sub-title">知识节点</h4>
      <el-table :data="nodes" size="small" stripe>
        <el-table-column prop="name" label="名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category" label="类别" width="140" />
        <el-table-column prop="value" label="权重" width="100" />
      </el-table>
      <el-empty v-if="!nodes.length" description="暂无知识节点" />
    </div>

    <div id="relation-edges" class="edges-block">
      <h4 class="sub-title">关系连线</h4>
      <el-table :data="edges" size="small" stripe>
        <el-table-column prop="source" label="起点" min-width="160" show-overflow-tooltip />
        <el-table-column prop="target" label="终点" min-width="160" show-overflow-tooltip />
        <el-table-column prop="relation_type" label="关系类型" width="140" />
        <el-table-column prop="weight" label="权重" width="90" />
      </el-table>
      <el-empty v-if="!edges.length" description="暂无关系连线" />
    </div>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
import type { RelationEdge, RelationNode } from '@/api/news'
import SectionStateWrapper from './SectionStateWrapper.vue'

defineProps<{
  nodes: RelationNode[]
  edges: RelationEdge[]
  emptyText?: string
}>()
</script>

<style scoped>
.sub-title {
  margin: 0 0 10px;
  font-size: 15px;
}

.edges-block {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px dashed var(--el-border-color-lighter);
}
</style>
