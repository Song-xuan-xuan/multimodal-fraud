export interface RagSourceMetadata {
  item_id?: string
  item_type?: string
  fraud_type?: string
  source?: string
  tags?: string[]
}

export interface RagSource {
  text: string
  score: number
  metadata?: RagSourceMetadata
}

export interface RagSourceDetail {
  id: string
  type: string
  title: string
  content: string
  source: string
}

export function sourceTypeLabel(type?: string) {
  switch (type) {
    case 'case':
      return '案例'
    case 'law':
      return '法规'
    case 'guideline':
      return '指南'
    case 'notice':
      return '公告'
    default:
      return '资料'
  }
}

function extractField(text: string, labels: string[]) {
  for (const label of labels) {
    const marker = label + ':'
    const start = text.indexOf(marker)
    if (start < 0) continue

    const valueStart = start + marker.length
    const lines = text.slice(valueStart).split('\n')
    const firstLine = (lines[0] || '').trim()
    if (firstLine) return firstLine
  }

  return ''
}

function extractContent(text: string) {
  const startLabels = ['正文', '姝ｆ枃']
  const endLabels = ['结论', '缁撹', '建议', '寤鸿', '来源', '鏉ユ簮']

  for (const label of startLabels) {
    const marker = label + ':'
    const start = text.indexOf(marker)
    if (start < 0) continue

    let content = text.slice(start + marker.length).trim()
    let endIndex = content.length
    for (const endLabel of endLabels) {
      const endMarker = '\n' + endLabel + ':'
      const currentIndex = content.indexOf(endMarker)
      if (currentIndex >= 0 && currentIndex < endIndex) {
        endIndex = currentIndex
      }
    }

    content = content.slice(0, endIndex).trim()
    if (content) return content
  }

  return text.trim()
}

export function parseRagSourceDetail(source: RagSource): RagSourceDetail {
  const text = source.text || ''
  const metadata = source.metadata || {}

  return {
    id: metadata.item_id || '-',
    type: sourceTypeLabel(metadata.item_type),
    title: extractField(text, ['标题', '鏍囬']) || '未提供标题',
    content: extractContent(text) || '未提供内容',
    source: metadata.source || extractField(text, ['来源', '鏉ユ簮']) || '未提供来源',
  }
}
