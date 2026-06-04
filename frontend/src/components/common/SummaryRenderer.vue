<template>
  <div v-if="sections.length" class="summary-renderer space-y-4">
    <section
      v-for="(sec, idx) in sections"
      :key="idx"
      class="summary-section rounded-xl border border-white/[0.06] bg-white/[0.02] overflow-hidden"
    >
      <header class="flex items-center gap-2.5 px-4 py-3 border-b border-white/[0.05] bg-gradient-to-r from-[#6C63FF]/8 to-transparent">
        <span class="section-icon" :class="`section-icon--${sec.icon}`" aria-hidden="true">
          <svg v-if="sec.icon === 'overview'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else-if="sec.icon === 'points'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          <svg v-else-if="sec.icon === 'audience'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <svg v-else-if="sec.icon === 'timeline'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </span>
        <h3 class="text-sm font-bold text-gray-100 tracking-wide">{{ sec.title }}</h3>
      </header>

      <div class="px-4 py-3 space-y-3">
        <p
          v-for="(para, pi) in sec.paragraphs"
          :key="'p' + pi"
          class="text-[13px] leading-7 text-gray-300"
        >
          <InlineSegments :segments="para" />
        </p>

        <ul v-if="sec.bullets.length" class="space-y-2.5">
          <li
            v-for="(item, bi) in sec.bullets"
            :key="'b' + bi"
            :class="item.kind === 'subhead' ? 'subhead-item' : 'bullet-item'"
          >
            <template v-if="item.kind === 'subhead'">
              <span class="timestamp-badge" v-if="extractTimestamp(item.segments)">
                {{ extractTimestamp(item.segments) }}
              </span>
              <span class="text-xs font-semibold text-[#a29bfe]">
                <InlineSegments :segments="stripTimestamp(item.segments)" />
              </span>
            </template>
            <template v-else>
              <span class="bullet-dot" aria-hidden="true" />
              <span class="text-[13px] leading-6 text-gray-300 flex-1">
                <InlineSegments :segments="item.segments" />
              </span>
            </template>
          </li>
        </ul>

        <div v-if="sec.quote" class="quote-box">
          <svg class="w-4 h-4 text-[#6C63FF] shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.996 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.984zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.432.917-3.995 3.638-3.995 5.849h3.983v10h-9.984z"/>
          </svg>
          <p class="text-[13px] leading-6 text-gray-200">
            <InlineSegments :segments="sec.quote" />
          </p>
        </div>
      </div>
    </section>
  </div>
  <p v-else-if="fallback" class="text-sm text-gray-500">{{ fallback }}</p>
</template>

<script setup>
import { computed } from 'vue'
import { parseMarkdownSections } from '../../utils/parseMarkdownSections'
import InlineSegments from './InlineSegments.vue'

const props = defineProps({
  content: { type: String, default: '' },
  fallback: { type: String, default: '' },
})

const sections = computed(() => parseMarkdownSections(props.content))

function extractTimestamp(segments) {
  const text = segments.map((s) => s.value).join('')
  const m = text.match(/\[(\d{1,2}:\d{2}(?::\d{2})?)\]/)
  return m ? m[1] : ''
}

function stripTimestamp(segments) {
  return segments.map((s) => ({
    ...s,
    value: s.value.replace(/\[\d{1,2}:\d{2}(?::\d{2})?\]\s*/, '').trim(),
  })).filter((s) => s.value)
}
</script>

<style scoped>
.section-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: rgba(108, 99, 255, 0.15);
  color: #a29bfe;
}

.bullet-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
}

.bullet-dot {
  flex-shrink: 0;
  width: 6px;
  height: 6px;
  margin-top: 0.55em;
  border-radius: 9999px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
}

.subhead-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.25rem;
}

.timestamp-badge {
  font-size: 10px;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: rgba(108, 99, 255, 0.2);
  color: #c4b5fd;
}

.quote-box {
  display: flex;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: 0.5rem;
  border-left: 3px solid rgba(108, 99, 255, 0.6);
  background: linear-gradient(90deg, rgba(108, 99, 255, 0.12), transparent);
}
</style>
