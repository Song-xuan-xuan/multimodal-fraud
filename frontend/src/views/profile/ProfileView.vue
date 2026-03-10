<template>
  <div class="page-shell profile-view">
    <!-- 用户画像卡 -->
    <section class="profile-hero tech-panel">
      <div class="profile-hero__header">
        <div class="profile-avatar">
          <span class="profile-avatar__letter">{{ avatarLetter }}</span>
        </div>
        <div class="profile-hero__info">
          <h2>{{ authStore.username }}</h2>
          <div class="profile-hero__tags" v-if="hasProfile">
            <el-tag v-if="profileData.age_group" type="info" effect="dark" size="small">{{ profileData.age_group }}</el-tag>
            <el-tag v-if="profileData.gender && profileData.gender !== '保密'" effect="dark" size="small">{{ profileData.gender }}</el-tag>
            <el-tag v-if="profileData.occupation" type="info" effect="dark" size="small">{{ profileData.occupation }}</el-tag>
            <el-tag v-if="profileData.region" type="info" effect="dark" size="small">{{ profileData.region }}</el-tag>
          </div>
          <div class="profile-hero__concern" v-if="profileData.concern_tags.length">
            <el-tag
              v-for="tag in profileData.concern_tags"
              :key="tag"
              size="small"
              effect="dark"
              class="profile-hero__concern-tag"
            >{{ tag }}</el-tag>
          </div>
          <p v-if="!hasProfile" class="profile-hero__guide">完善画像，获取个性化防护建议</p>
        </div>
        <div class="profile-hero__actions">
          <el-button type="primary" @click="showEditDialog = true">编辑画像</el-button>
          <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        </div>
      </div>
    </section>

    <!-- 主体 Tabs -->
    <el-tabs v-model="activeTab" class="profile-tabs">
      <!-- Tab 1: 角色防护策略 -->
      <el-tab-pane label="角色防护策略" name="defense">
        <section class="profile-defense tech-panel" v-if="hasProfile">
          <div class="profile-defense__head">
            <div>
              <el-tag type="warning" effect="dark" size="large">{{ roleDefense.role_label }}</el-tag>
              <p class="profile-defense__summary">{{ roleDefense.risk_summary }}</p>
            </div>
          </div>
          <div class="profile-defense__risks">
            <p class="profile-defense__section-title">高风险诈骗类型</p>
            <div class="profile-defense__risk-tags">
              <el-tag
                v-for="rt in roleDefense.high_risk_types"
                :key="rt"
                type="danger"
                effect="dark"
                size="small"
              >{{ rt }}</el-tag>
            </div>
          </div>
          <div class="profile-defense__tips">
            <p class="profile-defense__section-title">差异化防御策略</p>
            <div class="profile-defense__tip-list">
              <div
                class="profile-defense__tip tech-surface"
                v-for="(tip, idx) in roleDefense.defense_tips"
                :key="idx"
              >
                <span class="profile-defense__tip-num">{{ idx + 1 }}</span>
                <p>{{ tip }}</p>
              </div>
            </div>
          </div>
        </section>
        <section class="profile-defense-empty tech-panel" v-else>
          <p>完善个人画像后，系统将根据您的角色特点生成差异化的防护策略</p>
          <el-button type="primary" @click="showEditDialog = true">去完善</el-button>
        </section>
      </el-tab-pane>

      <!-- Tab 2: 我的活动 -->
      <el-tab-pane label="我的活动" name="activity">
        <div class="profile-activity">
          <!-- 统计概览 + 雷达图 -->
          <section class="profile-stats tech-panel">
            <p class="profile-section-eyebrow">行为统计</p>
            <div class="profile-stats__body">
              <div class="profile-stats__cards">
                <div class="profile-stat-card tech-surface" v-for="card in statCards" :key="card.label">
                  <span class="profile-stat-card__value">{{ card.value }}</span>
                  <span class="profile-stat-card__label">{{ card.label }}</span>
                </div>
              </div>
              <div class="profile-stats__radar">
                <div ref="radarChartRef" class="profile-stats__radar-chart"></div>
              </div>
            </div>
          </section>

          <!-- 举报记录 -->
          <section class="profile-section tech-panel" v-if="behaviorStats.recent_reports.length">
            <p class="profile-section-eyebrow">我的举报 ({{ behaviorStats.report_count }})</p>
            <div class="profile-section__list">
              <div
                class="profile-activity-item tech-surface"
                v-for="r in behaviorStats.recent_reports"
                :key="r.report_id"
              >
                <div class="profile-activity-item__main">
                  <el-tag :type="reportStatusType(r.status)" effect="dark" size="small">{{ reportStatusLabel(r.status) }}</el-tag>
                  <span class="profile-activity-item__type">{{ r.type }}</span>
                  <span class="profile-activity-item__desc">{{ r.description }}</span>
                </div>
                <div class="profile-activity-item__actions">
                  <span class="profile-activity-item__time">{{ formatTime(r.created_at) }}</span>
                  <el-button
                    v-if="r.status === 'pending'"
                    type="danger"
                    text
                    size="small"
                    @click="handleWithdraw(r.report_id)"
                  >撤回</el-button>
                </div>
              </div>
            </div>
          </section>

          <!-- 检测记录 -->
          <section class="profile-section tech-panel" v-if="behaviorStats.recent_detections.length">
            <p class="profile-section-eyebrow">检测记录 ({{ behaviorStats.detection_count }})</p>
            <div class="profile-section__list">
              <div
                class="profile-activity-item tech-surface"
                v-for="(item, idx) in behaviorStats.recent_detections"
                :key="idx"
              >
                <div class="profile-activity-item__main">
                  <el-tag :type="riskTagType(item.risk_level)" effect="dark" size="small">
                    {{ detectionTypeLabel(item.detection_type) }}
                  </el-tag>
                  <span class="profile-activity-item__desc">{{ riskLabel(item.risk_level) }}</span>
                </div>
                <span class="profile-activity-item__time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </section>

          <!-- 证据贡献 -->
          <section class="profile-section tech-panel" v-if="behaviorStats.recent_evidences.length">
            <p class="profile-section-eyebrow">证据贡献 ({{ behaviorStats.evidence_count }})</p>
            <div class="profile-section__list">
              <div
                class="profile-activity-item tech-surface"
                v-for="e in behaviorStats.recent_evidences"
                :key="e.id"
              >
                <div class="profile-activity-item__main">
                  <el-tag :type="reportStatusType(e.status)" effect="dark" size="small">{{ reportStatusLabel(e.status) }}</el-tag>
                  <span class="profile-activity-item__desc">{{ e.content }}</span>
                </div>
                <span class="profile-activity-item__time">{{ formatTime(e.submitted_at) }}</span>
              </div>
            </div>
          </section>

          <!-- AI 对话记录 -->
          <section class="profile-section tech-panel" v-if="behaviorStats.recent_chats.length">
            <p class="profile-section-eyebrow">AI 咨询 ({{ behaviorStats.chat_count }})</p>
            <div class="profile-section__list">
              <div
                class="profile-activity-item tech-surface"
                v-for="c in behaviorStats.recent_chats"
                :key="c.id"
              >
                <div class="profile-activity-item__main">
                  <el-tag type="info" effect="dark" size="small">{{ c.message_count }} 条消息</el-tag>
                  <span class="profile-activity-item__desc">{{ c.title }}</span>
                </div>
                <span class="profile-activity-item__time">{{ formatTime(c.created_at) }}</span>
              </div>
            </div>
          </section>

          <!-- 空状态 -->
          <section class="profile-section tech-panel" v-if="isActivityEmpty">
            <p class="profile-activity-empty">暂无活动记录，快去使用检测、举报、AI 咨询等功能吧</p>
          </section>
        </div>
      </el-tab-pane>

      <!-- Tab 3: 个性化建议 -->
      <el-tab-pane label="个性化建议" name="suggestions">
        <section class="profile-suggestions tech-panel">
          <div class="profile-suggestions__head">
            <div>
              <p class="profile-section-eyebrow">LLM 智能推荐</p>
              <h3>基于画像与行为的个性化反诈建议</h3>
            </div>
            <el-button :loading="suggestionsLoading" @click="loadSuggestions">刷新建议</el-button>
          </div>
          <div v-if="!hasProfile" class="profile-suggestions__empty">
            <p>请先完善个人画像，即可获取个性化反诈建议</p>
            <el-button type="primary" @click="showEditDialog = true">去完善</el-button>
          </div>
          <div v-else-if="suggestionsLoading" class="profile-suggestions__loading">
            <el-skeleton :rows="4" animated />
          </div>
          <div v-else class="profile-suggestions__list">
            <div
              class="profile-suggestion-card tech-surface"
              v-for="(s, idx) in suggestions"
              :key="idx"
            >
              <span class="profile-suggestion-card__num">{{ idx + 1 }}</span>
              <p>{{ s }}</p>
            </div>
          </div>
        </section>
      </el-tab-pane>
    </el-tabs>

    <!-- 画像编辑弹窗 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人画像"
      width="520px"
      destroy-on-close
    >
      <el-form label-width="80px" :model="editForm">
        <el-form-item label="年龄段">
          <el-select v-model="editForm.age_group" placeholder="请选择" clearable>
            <el-option label="青少年" value="青少年" />
            <el-option label="青年" value="青年" />
            <el-option label="中年" value="中年" />
            <el-option label="老年" value="老年" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
            <el-radio value="保密">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="职业">
          <el-select v-model="editForm.occupation" placeholder="请选择" clearable>
            <el-option label="学生" value="学生" />
            <el-option label="上班族" value="上班族" />
            <el-option label="自由职业" value="自由职业" />
            <el-option label="退休" value="退休" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-select v-model="editForm.region" placeholder="请选择" clearable filterable>
            <el-option v-for="r in regionOptions" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="关注领域">
          <div class="profile-edit__tags">
            <el-check-tag
              v-for="tag in concernTagOptions"
              :key="tag"
              :checked="editForm.concern_tags.includes(tag)"
              @change="toggleConcernTag(tag)"
            >{{ tag }}</el-check-tag>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { useAuthStore } from '@/stores/auth'
import {
  profileApi,
  type ProfileData,
  type BehaviorStats,
  type RoleDefenseStrategy,
  type ProfileUpdatePayload,
} from '@/api/profile'

const router = useRouter()
const authStore = useAuthStore()

// --- State ---
const activeTab = ref('defense')

const profileData = reactive<ProfileData>({
  age_group: null,
  gender: null,
  occupation: null,
  region: null,
  concern_tags: [],
})

const behaviorStats = reactive<BehaviorStats>({
  detection_count: 0,
  fact_check_count: 0,
  report_count: 0,
  evidence_count: 0,
  chat_count: 0,
  recent_detections: [],
  recent_reports: [],
  recent_evidences: [],
  recent_chats: [],
})

const roleDefense = reactive<RoleDefenseStrategy>({
  role_label: '',
  risk_summary: '',
  high_risk_types: [],
  defense_tips: [],
})

const suggestions = ref<string[]>([])
const suggestionsLoading = ref(false)
const showEditDialog = ref(false)
const saving = ref(false)

const editForm = reactive<{
  age_group: string | null
  gender: string | null
  occupation: string | null
  region: string | null
  concern_tags: string[]
}>({
  age_group: null,
  gender: null,
  occupation: null,
  region: null,
  concern_tags: [],
})

// --- Computed ---
const avatarLetter = computed(() =>
  (authStore.username || 'U').charAt(0).toUpperCase(),
)

const hasProfile = computed(() =>
  !!(profileData.age_group || profileData.occupation || profileData.region || profileData.concern_tags.length),
)

const statCards = computed(() => [
  { label: '风险检测', value: behaviorStats.detection_count },
  { label: '事实核查', value: behaviorStats.fact_check_count },
  { label: '线索举报', value: behaviorStats.report_count },
  { label: '证据贡献', value: behaviorStats.evidence_count },
  { label: 'AI 咨询', value: behaviorStats.chat_count },
])

const isActivityEmpty = computed(() =>
  !behaviorStats.recent_detections.length &&
  !behaviorStats.recent_reports.length &&
  !behaviorStats.recent_evidences.length &&
  !behaviorStats.recent_chats.length,
)

// --- Options ---
const concernTagOptions = [
  '电信诈骗', '投资理财', '网购退款', '杀猪盘',
  '冒充公检法', '网络赌博', '刷单返利', '虚假招聘',
]

const regionOptions = [
  '北京', '天津', '河北', '山西', '内蒙古',
  '辽宁', '吉林', '黑龙江', '上海', '江苏',
  '浙江', '安徽', '福建', '江西', '山东',
  '河南', '湖北', '湖南', '广东', '广西',
  '海南', '重庆', '四川', '贵州', '云南',
  '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆',
  '香港', '澳门', '台湾',
]

// --- Helpers ---
const detectionTypeMap: Record<string, string> = {
  'ai-text': 'AI文本', 'ai-image': 'AI图像', 'audio-risk': '语音风险',
  'multimodal': '多模态', 'news': '新闻检测', 'aggregate': '综合分析',
  'url': 'URL检测', 'file': '文件检测', 'segments': '分段检测',
}
function detectionTypeLabel(type: string) { return detectionTypeMap[type] || type }

function riskLabel(level: string | null) {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  return '低风险'
}
function riskTagType(level: string | null) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'success'
}

function reportStatusLabel(status: string) {
  const map: Record<string, string> = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}
function reportStatusType(status: string) {
  const map: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return (map[status] || 'info') as 'warning' | 'success' | 'danger' | 'info'
}

function formatTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function toggleConcernTag(tag: string) {
  const idx = editForm.concern_tags.indexOf(tag)
  if (idx >= 0) editForm.concern_tags.splice(idx, 1)
  else editForm.concern_tags.push(tag)
}

// --- ECharts radar ---
const radarChartRef = ref<HTMLElement>()
let radarChart: echarts.ECharts | null = null

function renderRadar() {
  if (!radarChartRef.value) return
  if (!radarChart) radarChart = echarts.init(radarChartRef.value)
  const maxVal = Math.max(
    behaviorStats.detection_count, behaviorStats.fact_check_count,
    behaviorStats.report_count, behaviorStats.evidence_count,
    behaviorStats.chat_count, 1,
  )
  radarChart.setOption({
    radar: {
      indicator: [
        { name: '检测活跃度', max: maxVal }, { name: '核查参与', max: maxVal },
        { name: '举报贡献', max: maxVal }, { name: '证据互动', max: maxVal },
        { name: 'AI咨询', max: maxVal },
      ],
      shape: 'polygon', splitNumber: 4,
      axisName: { color: 'var(--tech-text-secondary, #a0aec0)', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitArea: { areaStyle: { color: ['rgba(0,0,0,0)', 'rgba(255,255,255,0.02)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          behaviorStats.detection_count, behaviorStats.fact_check_count,
          behaviorStats.report_count, behaviorStats.evidence_count,
          behaviorStats.chat_count,
        ],
        name: '行为画像',
        areaStyle: { color: 'rgba(64, 158, 255, 0.25)' },
        lineStyle: { color: '#409eff', width: 2 },
        itemStyle: { color: '#409eff' },
      }],
    }],
  })
}

// --- Data loading ---
async function loadProfile() {
  try {
    const res = await profileApi.getMe()
    Object.assign(profileData, res.profile)
    Object.assign(behaviorStats, res.stats)
    Object.assign(roleDefense, res.role_defense)
    await nextTick()
    if (activeTab.value === 'activity') renderRadar()
  } catch {
    ElMessage.error('加载个人画像失败')
  }
}

async function loadSuggestions() {
  try {
    suggestionsLoading.value = true
    const res = await profileApi.getSuggestions()
    suggestions.value = res.suggestions
  } catch {
    ElMessage.error('获取建议失败')
  } finally {
    suggestionsLoading.value = false
  }
}

async function saveProfile() {
  try {
    saving.value = true
    const payload: ProfileUpdatePayload = {
      age_group: editForm.age_group,
      gender: editForm.gender,
      occupation: editForm.occupation,
      region: editForm.region,
      concern_tags: editForm.concern_tags,
    }
    const res = await profileApi.updateMe(payload)
    Object.assign(profileData, res.profile)
    Object.assign(behaviorStats, res.stats)
    Object.assign(roleDefense, res.role_defense)
    showEditDialog.value = false
    ElMessage.success('画像已更新')
    await nextTick()
    renderRadar()
    loadSuggestions()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleWithdraw(reportId: string) {
  try {
    await ElMessageBox.confirm('确定要撤回这条举报吗？', '撤回确认', {
      confirmButtonText: '确定撤回',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await profileApi.withdrawReport(reportId)
    ElMessage.success('举报已撤回')
    loadProfile()
  } catch (e: unknown) {
    if (e !== 'cancel') ElMessage.error('撤回失败')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// Sync edit form when dialog opens
watch(showEditDialog, (open) => {
  if (open) {
    editForm.age_group = profileData.age_group
    editForm.gender = profileData.gender
    editForm.occupation = profileData.occupation
    editForm.region = profileData.region
    editForm.concern_tags = [...profileData.concern_tags]
  }
})

// Render radar when switching to activity tab
watch(activeTab, (tab) => {
  if (tab === 'activity') nextTick(() => renderRadar())
  if (tab === 'suggestions' && !suggestions.value.length && hasProfile.value) loadSuggestions()
})

function handleResize() { radarChart?.resize() }

onMounted(async () => {
  await loadProfile()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.profile-view {
  max-width: 960px;
  margin: 0 auto;
}

/* Hero */
.profile-hero { padding: 28px 32px; }
.profile-hero__header { display: flex; align-items: flex-start; gap: 24px; }
.profile-avatar {
  flex-shrink: 0; width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg, var(--tech-color-primary, #409eff) 0%, var(--tech-color-primary-strong, #1a73e8) 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 20px rgba(64, 158, 255, 0.3);
}
.profile-avatar__letter { font-size: 32px; font-weight: 700; color: #fff; }
.profile-hero__info {
  flex: 1; min-width: 0;
  h2 { margin: 0 0 8px; font-size: 22px; color: var(--tech-theme-text-primary, #fff); }
}
.profile-hero__tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.profile-hero__concern { display: flex; gap: 6px; flex-wrap: wrap; }
.profile-hero__concern-tag { --el-tag-bg-color: rgba(64, 158, 255, 0.15); }
.profile-hero__guide { color: var(--tech-theme-text-secondary, #a0aec0); font-size: 14px; margin: 4px 0 0; }
.profile-hero__actions { flex-shrink: 0; display: flex; gap: 8px; }

/* Tabs */
.profile-tabs { margin-top: 4px; }
.profile-tabs :deep(.el-tabs__header) { padding: 0 16px; }

/* Shared section styling */
.profile-section-eyebrow {
  font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--tech-theme-text-secondary, #a0aec0); margin: 0 0 16px;
}
.profile-section { padding: 24px 32px; }

/* Defense tab */
.profile-defense { padding: 24px 32px; }
.profile-defense__head { margin-bottom: 20px; }
.profile-defense__summary {
  margin: 10px 0 0; font-size: 14px; line-height: 1.6;
  color: var(--tech-theme-text-regular, #ccc);
}
.profile-defense__section-title {
  font-size: 13px; font-weight: 600; margin: 0 0 10px;
  color: var(--tech-theme-text-primary, #fff);
}
.profile-defense__risks { margin-bottom: 24px; }
.profile-defense__risk-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.profile-defense__tip-list { display: flex; flex-direction: column; gap: 8px; }
.profile-defense__tip {
  display: flex; align-items: flex-start; gap: 14px; padding: 14px 20px;
  p { margin: 0; font-size: 14px; line-height: 1.6; color: var(--tech-theme-text-regular, #ccc); }
}
.profile-defense__tip-num {
  flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%;
  background: rgba(64, 158, 255, 0.2); color: #409eff;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.profile-defense-empty {
  padding: 48px 32px; text-align: center;
  p { color: var(--tech-theme-text-secondary, #a0aec0); margin: 0 0 16px; }
}

/* Stats */
.profile-stats { padding: 24px 32px; }
.profile-stats__body { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.profile-stats__cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.profile-stat-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 16px 8px; text-align: center;
}
.profile-stat-card__value {
  font-size: 24px; font-weight: 700; line-height: 1.2;
  color: var(--tech-theme-text-primary, #fff);
}
.profile-stat-card__label {
  font-size: 12px; margin-top: 4px;
  color: var(--tech-theme-text-secondary, #a0aec0);
}
.profile-stats__radar-chart { width: 100%; height: 220px; }

/* Activity items */
.profile-section__list { display: flex; flex-direction: column; gap: 6px; }
.profile-activity-item {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 10px 16px;
}
.profile-activity-item__main {
  display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;
}
.profile-activity-item__type {
  font-size: 13px; color: var(--tech-theme-text-primary, #fff); flex-shrink: 0;
}
.profile-activity-item__desc {
  font-size: 13px; color: var(--tech-theme-text-regular, #ccc);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.profile-activity-item__actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.profile-activity-item__time {
  font-size: 12px; color: var(--tech-theme-text-tertiary, #718096); flex-shrink: 0;
}
.profile-activity-empty {
  text-align: center; padding: 32px 0;
  color: var(--tech-theme-text-secondary, #a0aec0);
}

/* Suggestions */
.profile-suggestions { padding: 24px 32px; }
.profile-suggestions__head {
  display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;
  h3 { margin: 4px 0 0; font-size: 16px; color: var(--tech-theme-text-primary, #fff); }
}
.profile-suggestions__empty {
  text-align: center; padding: 40px 0;
  color: var(--tech-theme-text-secondary, #a0aec0);
}
.profile-suggestions__list { display: flex; flex-direction: column; gap: 10px; }
.profile-suggestion-card {
  display: flex; align-items: flex-start; gap: 14px; padding: 16px 20px;
  p { margin: 0; font-size: 14px; line-height: 1.6; color: var(--tech-theme-text-regular, #ccc); }
}
.profile-suggestion-card__num {
  flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%;
  background: rgba(103, 194, 58, 0.2); color: #67c23a;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}

/* Edit dialog */
.profile-edit__tags { display: flex; gap: 8px; flex-wrap: wrap; }

/* Responsive */
@media (max-width: 768px) {
  .profile-hero__header { flex-direction: column; align-items: center; text-align: center; }
  .profile-hero__actions { justify-content: center; }
  .profile-stats__body { grid-template-columns: 1fr; }
  .profile-stats__cards { grid-template-columns: 1fr 1fr; }
}
</style>
