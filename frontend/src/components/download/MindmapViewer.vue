<template>
  <div class="space-y-3">
    <div class="flex flex-wrap items-center gap-2">
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
        @click="fitView"
      >
        适应画布
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
        :disabled="!markdown"
        @click="exportMarkdown"
      >
        导出 MD
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
        :disabled="!markdown"
        @click="exportSvg"
      >
        导出 SVG
      </button>
      <button
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
        :disabled="!markdown"
        @click="exportPng"
      >
        导出 PNG
      </button>
      <button
        v-if="onRegenerate"
        type="button"
        class="px-2.5 py-1 rounded-lg text-[11px] bg-[#6C63FF]/20 border border-[#6C63FF]/30 text-[#6C63FF] hover:bg-[#6C63FF]/30 disabled:opacity-50"
        :disabled="regenerating"
        @click="onRegenerate"
      >
        {{ regenerating ? '生成中...' : '重新生成' }}
      </button>
    </div>

    <div
      v-if="markdown"
      class="rounded-xl border border-white/10 bg-[#0d0d18] overflow-hidden"
    >
      <svg ref="svgRef" class="w-full min-h-[380px] max-h-[520px] cursor-grab active:cursor-grabbing"></svg>
    </div>
    <p v-else class="text-sm text-gray-500 py-8 text-center">暂无思维导图，请点击「重新生成」</p>

    <p v-if="markdown && videoUrl" class="text-[11px] text-gray-500">
      提示：点击含 <span class="text-[#6C63FF]">[分:秒]</span> 的节点可跳转至视频对应时间点
    </p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

const props = defineProps({
  markdown: { type: String, default: '' },
  videoUrl: { type: String, default: '' },
  title: { type: String, default: 'mindmap' },
  regenerating: { type: Boolean, default: false },
  onRegenerate: { type: Function, default: null },
})

const svgRef = ref(null)
let markmap = null
let clickHandler = null
let transformer = null

function getTransformer() {
  if (!transformer) transformer = new Transformer()
  return transformer
}

function renderMap() {
  if (!svgRef.value || !props.markdown?.trim()) return

  const { root } = getTransformer().transform(props.markdown)
  if (!markmap) {
    markmap = Markmap.create(svgRef.value, {
      autoFit: true,
      color: (node) => {
        const depth = node.depth || 0
        const colors = ['#6C63FF', '#3B82F6', '#8B5CF6', '#06B6D4', '#10B981']
        return colors[depth % colors.length]
      },
    })
    clickHandler = (e) => handleNodeClick(e)
    svgRef.value.addEventListener('click', clickHandler)
  }
  markmap.setData(root)
  markmap.fit()
}

function fitView() {
  markmap?.fit()
}

function parseTimestamp(text) {
  if (!text) return null
  const m = text.match(/\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]/)
  if (!m) return null
  if (m[3] !== undefined) {
    return parseInt(m[1], 10) * 3600 + parseInt(m[2], 10) * 60 + parseInt(m[3], 10)
  }
  return parseInt(m[1], 10) * 60 + parseInt(m[2], 10)
}

function buildVideoUrlWithTime(url, seconds) {
  if (!url || seconds == null) return url
  try {
    const u = new URL(url)
    const host = u.hostname.toLowerCase()
    if (host.includes('youtube.com') || host.includes('youtu.be')) {
      u.searchParams.set('t', String(seconds))
      return u.toString()
    }
    if (host.includes('bilibili.com')) {
      u.searchParams.set('t', String(seconds))
      return u.toString()
    }
    u.searchParams.set('t', String(seconds))
    return u.toString()
  } catch {
    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}t=${seconds}`
  }
}

function handleNodeClick(e) {
  const nodeEl = e.target.closest?.('.markmap-foreign')
  if (!nodeEl || !props.videoUrl) return
  const text = nodeEl.textContent || ''
  const seconds = parseTimestamp(text)
  if (seconds == null) return
  const jumpUrl = buildVideoUrlWithTime(props.videoUrl, seconds)
  window.open(jumpUrl, '_blank', 'noopener')
}

function downloadBlob(blob, filename) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}

function exportMarkdown() {
  if (!props.markdown) return
  downloadBlob(new Blob([props.markdown], { type: 'text/markdown;charset=utf-8' }), `${safeName()}.md`)
}

function exportSvg() {
  if (!svgRef.value) return
  const clone = svgRef.value.cloneNode(true)
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  const svgData = new XMLSerializer().serializeToString(clone)
  downloadBlob(new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' }), `${safeName()}.svg`)
}

function exportPng() {
  if (!svgRef.value) return
  const svg = svgRef.value
  const rect = svg.getBoundingClientRect()
  const w = Math.max(800, Math.ceil(rect.width))
  const h = Math.max(600, Math.ceil(rect.height))
  const clone = svg.cloneNode(true)
  clone.setAttribute('width', String(w))
  clone.setAttribute('height', String(h))
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  const svgData = new XMLSerializer().serializeToString(clone)
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = w
    canvas.height = h
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#0d0d18'
    ctx.fillRect(0, 0, w, h)
    ctx.drawImage(img, 0, 0)
    canvas.toBlob((blob) => {
      if (blob) downloadBlob(blob, `${safeName()}.png`)
    }, 'image/png')
  }
  img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgData)}`
}

function safeName() {
  return (props.title || 'mindmap').replace(/[\\/:*?"<>|]/g, '_').slice(0, 40)
}

watch(
  () => props.markdown,
  async () => {
    await nextTick()
    renderMap()
  }
)

onMounted(async () => {
  await nextTick()
  renderMap()
})

onBeforeUnmount(() => {
  if (svgRef.value && clickHandler) {
    svgRef.value.removeEventListener('click', clickHandler)
  }
  markmap?.destroy?.()
  markmap = null
})
</script>

<style scoped>
:deep(.markmap-foreign div) {
  color: #e2e8f0;
  font-size: 13px;
}
:deep(svg markmap) {
  width: 100%;
  height: 100%;
}
:deep(.markmap-node circle) {
  stroke-width: 1.5px;
}
</style>
