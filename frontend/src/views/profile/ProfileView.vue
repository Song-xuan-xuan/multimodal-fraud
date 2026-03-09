<template>
  <div class="page-shell profile-view">
    <!-- 区域 1: 用户画像卡 -->
    <section class="profile-hero tech-panel">
      <div class="profile-hero__header">
        <div class="profile-avatar">
          <span class="profile-avatar__letter">{{ avatarLetter }}</span>
        </div>
        <div class="profile-hero__info">
          <h2>{{ authStore.username }}</h2>
          <div class="profile-hero__tags" v-if="hasProfile">
            <el-tag v-if="profileData.age_group" type="info" effect="dark" size="small">{{ profileData.age_group }}</el-tag>
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

    <!-- 区域 2: 行为统计仪表盘 -->
    <section class="profile-stats tech-panel">
      <p class="profile-stats__eyebrow">行为统计</p>
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
      <div class="profile-recent" v-if="behaviorStats.recent_detections.length">
        <p class="profile-recent__title">最近检测记录</p>
        <div class="profile-recent__list">
          <div
            class="profile-recent__item tech-surface"
            v-for="(item, idx) in behaviorStats.recent_detections"
            :key="idx"
          >
            <el-tag
              :type="riskTagType(item.risk_level)"
              effect="dark"
              size="small"
            >{{ detectionTypeLabel(item.detection_type) }}</el-tag>
            <span class="profile-recent__risk">{{ riskLabel(item.risk_level) }}</span>
            <span class="profile-recent__time">{{ formatTime(item.created_at) }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 区域 3: 个性化反诈建议 -->
    <section class="profile-suggestions tech-panel">
      <div class="profile-suggestions__head">
        <div>
          <p class="profile-suggestions__eyebrow">个性化防护建议</p>
          <h3>基于画像与行为的智能推荐</h3>
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
          <span class="profile-suggestion-card__icon">🛡️</span>
          <p>{{ s }}</p>
        </div>
      </div>
    </section>

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
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useAuthStore } from '@/stores/auth'
import {
  profileApi,
  type ProfileData,
  type BehaviorStats,
  type ProfileUpdatePayload,
} from '@/api/profile'

const router = useRouter()
const authStore = useAuthStore()

// --- State ---
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
})

const suggestions = ref<string[]>([])
const suggestionsLoading = ref(false)
const showEditDialog = ref(false)
const saving = ref(false)
const loading = ref(true)

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
  { label: '社区贡献', value: behaviorStats.evidence_count + behaviorStats.chat_count },
])

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

const detectionTypeMap: Record<string, string> = {
  'ai-text': 'AI文本',
  'ai-image': 'AI图像',
  'audio-risk': '语音风险',
  'multimodal': '多模态',
  'news': '新闻检测',
  'aggregate': '综合分析',
  'url': 'URL检测',
  'file': '文件检测',
  'segments': '分段检测',
}

function detectionTypeLabel(type: string) {
  return detectionTypeMap[type] || type
}

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

function formatTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function toggleConcernTag(tag: string) {
  const idx = editForm.concern_tags.indexOf(tag)
  if (idx >= 0) {
    editForm.concern_tags.splice(idx, 1)
  } else {
    editForm.concern_tags.push(tag)
  }
}

// --- ECharts radar ---
const radarChartRef = ref<HTMLElement>()
let radarChart: echarts.ECharts | null = null

function renderRadar() {
  if (!radarChartRef.value) return
  if (!radarChart) {
    radarChart = echarts.init(radarChartRef.value)
  }
  const maxVal = Math.max(
    behaviorStats.detection_count,
    behaviorStats.fact_check_count,
    behaviorStats.report_count,
    behaviorStats.evidence_count,
    behaviorStats.chat_count,
    1,
  )
  radarChart.setOption({
    radar: {
      indicator: [
        { name: '检测活跃度', max: maxVal },
        { name: '核查参与', max: maxVal },
        { name: '举报贡献', max: maxVal },
        { name: '社区互动', max: maxVal },
        { name: 'AI咨询', max: maxVal },
      ],
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: 'var(--tech-text-secondary, #a0aec0)',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: { color: 'rgba(255,255,255,0.08)' },
      },
      splitArea: {
        areaStyle: { color: ['rgba(0,0,0,0)', 'rgba(255,255,255,0.02)'] },
      },
      axisLine: {
        lineStyle: { color: 'rgba(255,255,255,0.1)' },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              behaviorStats.detection_count,
              behaviorStats.fact_check_count,
              behaviorStats.report_count,
              behaviorStats.evidence_count,
              behaviorStats.chat_count,
            ],
            name: '行为画像',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.25)',
            },
            lineStyle: {
              color: '#409eff',
              width: 2,
            },
            itemStyle: {
              color: '#409eff',
            },
          },
        ],
      },
    ],
  })
}

// --- Data loading ---
async function loadProfile() {
  try {
    loading.value = true
    const res = await profileApi.getMe()
    Object.assign(profileData, res.profile)
    Object.assign(behaviorStats, res.stats)
    await nextTick()
    renderRadar()
  } catch {
    ElMessage.error('加载个人画像失败')
  } finally {
    loading.value = false
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

// Resize handler
function handleResize() {
  radarChart?.resize()
}

onMounted(async () => {
  await loadProfile()
  if (hasProfile.value) {
    loadSuggestions()
  }
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.profile-view {
  max-width: 960px;
  margin: 0 auto;
}

/* Hero / Profile Card */
.profile-hero {
  padding: 28px 32px;
}

.profile-hero__header {
  display: flex;
  align-items: flex-start;
  gap: 24px;
}

.profile-avatar {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--tech-color-primary, #409eff) 0%, var(--tech-color-primary-strong, #1a73e8) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(64, 158, 255, 0.3);
}

.profile-avatar__letter {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}

.profile-hero__info {
  flex: 1;
  min-width: 0;

  h2 {
    margin: 0 0 8px;
    font-size: 22px;
    color: var(--tech-theme-text-primary, #fff);
  }
}

.profile-hero__tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.profile-hero__concern {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.profile-hero__concern-tag {
  --el-tag-bg-color: rgba(64, 158, 255, 0.15);
}

.profile-hero__guide {
  color: var(--tech-theme-text-secondary, #a0aec0);
  font-size: 14px;
  margin: 4px 0 0;
}

.profile-hero__actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

/* Stats Section */
.profile-stats {
  padding: 24px 32px;
}

.profile-stats__eyebrow {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--tech-theme-text-secondary, #a0aec0);
  margin: 0 0 16px;
}

.profile-stats__body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.profile-stats__cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.profile-stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 12px;
  text-align: center;
}

.profile-stat-card__value {
  font-size: 28px;
  font-weight: 700;
  color: var(--tech-theme-text-primary, #fff);
  line-height: 1.2;
}

.profile-stat-card__label {
  font-size: 13px;
  color: var(--tech-theme-text-secondary, #a0aec0);
  margin-top: 4px;
}

.profile-stats__radar-chart {
  width: 100%;
  height: 240px;
}

/* Recent detections */
.profile-recent {
  margin-top: 20px;
}

.profile-recent__title {
  font-size: 13px;
  color: var(--tech-theme-text-secondary, #a0aec0);
  margin: 0 0 10px;
}

.profile-recent__list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-recent__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
}

.profile-recent__risk {
  font-size: 13px;
  color: var(--tech-theme-text-regular, #ccc);
}

.profile-recent__time {
  margin-left: auto;
  font-size: 12px;
  color: var(--tech-theme-text-tertiary, #718096);
}

/* Suggestions */
.profile-suggestions {
  padding: 24px 32px;
}

.profile-suggestions__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;

  h3 {
    margin: 4px 0 0;
    font-size: 16px;
    color: var(--tech-theme-text-primary, #fff);
  }
}

.profile-suggestions__eyebrow {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--tech-theme-text-secondary, #a0aec0);
  margin: 0;
}

.profile-suggestions__empty {
  text-align: center;
  padding: 40px 0;
  color: var(--tech-theme-text-secondary, #a0aec0);
}

.profile-suggestions__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.profile-suggestion-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;

  p {
    margin: 0;
    font-size: 14px;
    line-height: 1.6;
    color: var(--tech-theme-text-regular, #ccc);
  }
}

.profile-suggestion-card__icon {
  flex-shrink: 0;
  font-size: 20px;
  line-height: 1.4;
}

/* Edit dialog tags */
.profile-edit__tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-hero__header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .profile-hero__actions {
    justify-content: center;
  }

  .profile-stats__body {
    grid-template-columns: 1fr;
  }
}
</style>
