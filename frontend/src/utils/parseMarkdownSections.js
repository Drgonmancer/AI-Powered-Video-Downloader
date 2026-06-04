/** 将 Markdown 解析为结构化数据，供 Vue 组件渲染（不显示 ##、** 等语法符号） */

function parseInline(text) {
  const raw = String(text || '').trim()
  if (!raw) return [{ type: 'text', value: '' }]
  const segments = []
  const re = /\*\*([^*]+)\*\*/g
  let last = 0
  let m
  while ((m = re.exec(raw)) !== null) {
    if (m.index > last) segments.push({ type: 'text', value: raw.slice(last, m.index) })
    segments.push({ type: 'bold', value: m[1] })
    last = m.index + m[0].length
  }
  if (last < raw.length) segments.push({ type: 'text', value: raw.slice(last) })
  return segments.length ? segments : [{ type: 'text', value: raw }]
}

export function parseMarkdownSections(markdown) {
  const text = String(markdown || '').replace(/\r\n/g, '\n').trim()
  if (!text) return []

  const chunks = text.split(/\n(?=#{1,3}\s+)/).map((c) => c.trim()).filter(Boolean)
  const sections = []

  for (const chunk of chunks) {
    let title = ''
    let body = chunk
    const h2 = chunk.match(/^##\s+(.+?)(?:\n|$)/)
    const h1 = chunk.match(/^#\s+(.+?)(?:\n|$)/)
    const h3only = chunk.match(/^###\s+(.+?)(?:\n|$)/)

    if (h2) {
      title = h2[1].trim()
      body = chunk.slice(h2[0].length).trim()
    } else if (h1) {
      title = h1[1].trim()
      body = chunk.slice(h1[0].length).trim()
    } else if (h3only && !chunk.includes('\n##')) {
      title = h3only[1].trim()
      body = chunk.slice(h3only[0].length).trim()
    } else {
      title = '概述'
      body = chunk
    }

    const paragraphs = []
    const bullets = []
    let quote = null

    for (const line of body.split('\n')) {
      const t = line.trim()
      if (!t) continue

      if (t.startsWith('>')) {
        quote = parseInline(t.replace(/^>\s*/, '').replace(/^\*\*|\*\*$/g, ''))
        continue
      }

      const bullet = t.match(/^[-*]\s+(.+)/)
      if (bullet) {
        bullets.push({ kind: 'item', segments: parseInline(bullet[1]) })
        continue
      }

      const sub = t.match(/^###\s+(.+)/)
      if (sub) {
        bullets.push({ kind: 'subhead', segments: parseInline(sub[1]) })
        continue
      }

      if (t.startsWith('##')) continue
      paragraphs.push(parseInline(t))
    }

    sections.push({
      title,
      paragraphs,
      bullets,
      quote,
      icon: sectionIcon(title),
    })
  }

  return sections
}

function sectionIcon(title) {
  const t = title.toLowerCase()
  if (t.includes('概述') || t.includes('summary')) return 'overview'
  if (t.includes('要点') || t.includes('核心')) return 'points'
  if (t.includes('人群') || t.includes('适合')) return 'audience'
  if (t.includes('脉络') || t.includes('字幕')) return 'timeline'
  if (t.includes('收获')) return 'insight'
  return 'default'
}
