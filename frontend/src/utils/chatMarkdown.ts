function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderInlineMarkdown(value: string) {
  let html = escapeHtml(value)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
  return html
}

function renderParagraph(lines: string[]) {
  const text = lines.join('<br />')
  if (!text.trim()) {
    return ''
  }
  return `<p>${renderInlineMarkdown(text)}</p>`
}

export function renderChatMarkdown(markdown: string) {
  const normalized = String(markdown || '').replace(/\r\n/g, '\n').trim()
  if (!normalized) {
    return ''
  }

  const lines = normalized.split('\n')
  const blocks: string[] = []
  let paragraphLines: string[] = []
  let listItems: string[] = []
  let listType: 'ul' | 'ol' | null = null
  let inCodeBlock = false
  let codeLines: string[] = []

  const flushParagraph = () => {
    const paragraph = renderParagraph(paragraphLines)
    if (paragraph) {
      blocks.push(paragraph)
    }
    paragraphLines = []
  }

  const flushList = () => {
    if (!listType || !listItems.length) {
      listItems = []
      listType = null
      return
    }

    blocks.push(`<${listType}>${listItems.join('')}</${listType}>`)
    listItems = []
    listType = null
  }

  const flushCodeBlock = () => {
    if (!inCodeBlock) {
      return
    }
    blocks.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`)
    codeLines = []
    inCodeBlock = false
  }

  for (const line of lines) {
    const trimmed = line.trim()

    if (trimmed.startsWith('```')) {
      flushParagraph()
      flushList()
      if (inCodeBlock) {
        flushCodeBlock()
      } else {
        inCodeBlock = true
        codeLines = []
      }
      continue
    }

    if (inCodeBlock) {
      codeLines.push(line)
      continue
    }

    if (!trimmed) {
      flushParagraph()
      flushList()
      continue
    }

    const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/)
    if (headingMatch) {
      flushParagraph()
      flushList()
      const level = Math.min(headingMatch[1].length, 3)
      blocks.push(`<h${level}>${renderInlineMarkdown(headingMatch[2])}</h${level}>`)
      continue
    }

    const orderedMatch = trimmed.match(/^\d+\.\s+(.+)$/)
    if (orderedMatch) {
      flushParagraph()
      if (listType && listType !== 'ol') {
        flushList()
      }
      listType = 'ol'
      listItems.push(`<li>${renderInlineMarkdown(orderedMatch[1])}</li>`)
      continue
    }

    const unorderedMatch = trimmed.match(/^[-*]\s+(.+)$/)
    if (unorderedMatch) {
      flushParagraph()
      if (listType && listType !== 'ul') {
        flushList()
      }
      listType = 'ul'
      listItems.push(`<li>${renderInlineMarkdown(unorderedMatch[1])}</li>`)
      continue
    }

    if (trimmed.startsWith('>')) {
      flushParagraph()
      flushList()
      blocks.push(`<blockquote>${renderInlineMarkdown(trimmed.replace(/^>\s?/, ''))}</blockquote>`)
      continue
    }

    if (listType) {
      flushList()
    }
    paragraphLines.push(trimmed)
  }

  flushParagraph()
  flushList()
  flushCodeBlock()

  return blocks.join('')
}
