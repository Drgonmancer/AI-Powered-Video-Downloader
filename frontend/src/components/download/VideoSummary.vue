<template>
  <section v-if="store.parseResult" class="rounded-2xl border border-white/5 bg-[#1A1A2E] overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4 border-b border-white/5">
      <h3 class="text-sm font-bold text-gray-200 flex items-center gap-2">
        <svg class="w-4 h-4 text-[#6C63FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
        AI 视频分析
      </h3>
      <span v-if="store.isSummarizing" class="text-xs text-[#6C63FF] animate-pulse flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        {{ t('summarizing') }}
      </span>
    </div>

    <div class="flex border-b border-white/5 px-2">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="px-4 py-2.5 text-xs font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === tab.id
          ? 'text-[#6C63FF] border-[#6C63FF]'
          : 'text-gray-500 border-transparent hover:text-gray-300'"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="p-5 min-h-[160px]">
      <div v-if="store.isSummarizing" class="flex flex-col items-center justify-center py-10 text-gray-500 text-sm">
        <p>正在调用大模型生成摘要、字幕要点与思维导图…</p>
        <p class="text-xs text-gray-600 mt-2">请先在左侧栏配置大模型 API</p>
      </div>

      <div v-else-if="!aiData?.enabled && aiMessage" class="py-6 text-center">
        <p class="text-amber-400/90 text-sm">{{ aiMessage }}</p>
        <p class="text-gray-600 text-xs mt-2">左侧栏 → 大模型配置 → 添加 API Key</p>
      </div>

      <div v-else-if="activeTab === 'summary'" class="space-y-4">
        <div v-if="summaryMarkdown" class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
            @click="exportSummary('md')"
          >
            {{ t('exportMd') }}
          </button>
          <button
            type="button"
            class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
            @click="exportSummary('txt')"
          >
            {{ t('exportTxt') }}
          </button>
        </div>
        <SummaryRenderer
          v-if="summaryMarkdown"
          :content="summaryMarkdown"
          :fallback="t('summaryError')"
        />
        <p v-else class="text-sm text-gray-500">{{ t('summaryError') }}</p>
        <div v-if="aiData?.provider" class="flex items-center gap-2 pt-1 border-t border-white/5">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] bg-[#6C63FF]/10 text-[#a29bfe] border border-[#6C63FF]/20">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            {{ aiData.provider }}
          </span>
        </div>
      </div>

      <div v-else-if="activeTab === 'transcript'" class="space-y-4">
        <div v-if="transcriptMarkdown" class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
            @click="exportTranscript('md')"
          >
            {{ t('exportMd') }}
          </button>
          <button
            type="button"
            class="px-2.5 py-1 rounded-lg text-[11px] bg-white/5 border border-white/10 text-gray-300 hover:border-[#6C63FF]/40"
            @click="exportTranscript('txt')"
          >
            {{ t('exportTxt') }}
          </button>
        </div>
        <div v-if="subtitleLangs.length" class="flex flex-wrap gap-1.5">
          <span
            v-for="lang in subtitleLangs"
            :key="lang"
            class="px-2 py-0.5 rounded text-[10px] bg-[#6C63FF]/15 text-[#6C63FF]"
          >{{ lang }}</span>
        </div>
        <div
          v-if="transcriptMarkdown"
          class="max-h-72 overflow-y-auto custom-scroll pr-1"
        >
          <SummaryRenderer
            :content="transcriptMarkdown"
            :fallback="t('noTranscript')"
          />
        </div>
        <p v-else class="text-sm text-gray-500">{{ t('noTranscript') }}</p>
      </div>

      <div v-else-if="activeTab === 'mindmap'" class="space-y-3">
        <MindmapViewer
          :markdown="mindmapMarkdown"
          :video-url="videoUrl"
          :title="videoTitle"
          :regenerating="regeneratingMindmap"
          :on-regenerate="handleRegenerateMindmap"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, defineAsyncComponent } from 'vue'
import { useDownloadStore } from '../../stores/download'
import { useI18n } from '../../composables/useI18n'
import {
  downloadTextFile,
  markdownToPlainText,
  safeFilename,
} from '../../utils/exportFile'

const SummaryRenderer = defineAsyncComponent(() => import('../common/SummaryRenderer.vue'))
const MindmapViewer = defineAsyncComponent(() => import('./MindmapViewer.vue'))

const store = useDownloadStore()
const { t, locale } = useI18n()
const activeTab = ref('summary')
const regeneratingMindmap = ref(false)

const tabs = computed(() => [
  { id: 'summary', label: locale.value === 'zh' ? '内容摘要' : 'Summary' },
  { id: 'transcript', label: locale.value === 'zh' ? '字幕要点' : 'Transcript' },
  { id: 'mindmap', label: locale.value === 'zh' ? '思维导图' : 'Mind Map' },
])

const aiData = computed(() => store.parseResult?.summary || null)
const aiMessage = computed(() => aiData.value?.message || '')

function looksLikeMarkdown(text) {
  if (!text) return false
  return /^#|\*\*|^-\s|^>\s/m.test(text) || text.includes('##')
}

function toSummaryMarkdown(text) {
  if (!text) return ''
  if (looksLikeMarkdown(text)) return text
  const parts = text.split(/\n+/).map((s) => s.trim()).filter(Boolean)
  if (parts.length > 1) {
    return `## 核心要点\n\n${parts.map((p) => `- ${p}`).join('\n')}`
  }
  return `## 一句话概述\n\n${text}`
}

function toTranscriptMarkdown(text) {
  if (!text) return ''
  if (looksLikeMarkdown(text)) return text
  const lines = text.split(/\n+/).map((s) => s.trim()).filter(Boolean)
  if (lines.length <= 1) return `## 内容脉络\n\n- ${text}`
  return `## 内容脉络\n\n${lines.map((ln) => `- ${ln}`).join('\n')}`
}

const summaryMarkdown = computed(() =>
  toSummaryMarkdown(aiData.value?.summary_md || aiData.value?.summary || '')
)

const transcriptMarkdown = computed(() => {
  const raw = aiData.value?.transcript_md || aiData.value?.transcript
  if (raw) return toTranscriptMarkdown(raw)
  const desc = store.parseResult?.description
  return toTranscriptMarkdown(desc || '')
})

const subtitleLangs = computed(() => {
  const subs = store.parseResult?.subtitles_available || []
  const auto = store.parseResult?.automatic_captions_available || []
  return [...new Set([...subs, ...auto])].slice(0, 10)
})

const mindmapMarkdown = computed(() =>
  aiData.value?.mindmap_md || aiData.value?.mindmap || ''
)

const videoUrl = computed(() =>
  store.lastParsedUrl || store.parseResult?.url || ''
)

const videoTitle = computed(() => store.parseResult?.title || 'video')

function buildExportHeader(sectionLabel) {
  const title = videoTitle.value
  const url = videoUrl.value
  const lines = [`# ${title}`, '']
  if (url) lines.push(`> 视频链接: ${url}`, '')
  if (sectionLabel) lines.push(`---`, '', `## ${sectionLabel}`, '')
  return lines.join('\n')
}

function exportSummary(format) {
  const body = summaryMarkdown.value
  if (!body) return
  const label = locale.value === 'zh' ? '内容摘要' : 'Summary'
  const full = `${buildExportHeader(label)}\n${body}`
  const base = safeFilename(videoTitle.value, 'summary')
  if (format === 'md') {
    downloadTextFile(full, `${base}-summary.md`, 'text/markdown;charset=utf-8')
  } else {
    downloadTextFile(markdownToPlainText(full), `${base}-summary.txt`)
  }
}

function exportTranscript(format) {
  const body = transcriptMarkdown.value
  if (!body) return
  const label = locale.value === 'zh' ? '字幕要点' : 'Transcript'
  const full = `${buildExportHeader(label)}\n${body}`
  const base = safeFilename(videoTitle.value, 'transcript')
  if (format === 'md') {
    downloadTextFile(full, `${base}-transcript.md`, 'text/markdown;charset=utf-8')
  } else {
    downloadTextFile(markdownToPlainText(full), `${base}-transcript.txt`)
  }
}

async function handleRegenerateMindmap() {
  regeneratingMindmap.value = true
  try {
    await store.regenerateMindmap()
  } finally {
    regeneratingMindmap.value = false
  }
}
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
</style>

