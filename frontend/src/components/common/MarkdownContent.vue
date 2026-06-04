<template>
  <article
    v-if="html"
    class="markdown-body custom-scroll"
    :class="{ 'markdown-body--compact': compact, 'markdown-body--scroll': scrollable }"
    v-html="html"
  />
  <p v-else-if="fallback" class="text-sm text-gray-500">{{ fallback }}</p>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  content: { type: String, default: '' },
  fallback: { type: String, default: '' },
  compact: { type: Boolean, default: false },
  scrollable: { type: Boolean, default: false },
})

marked.setOptions({
  breaks: true,
  gfm: true,
})

const html = computed(() => {
  const text = (props.content || '').trim()
  if (!text) return ''
  const raw = marked.parse(text, { async: false })
  return DOMPurify.sanitize(raw, {
    ADD_ATTR: ['target', 'rel'],
  })
})
</script>

<style scoped>
.markdown-body {
  font-size: 0.875rem;
  line-height: 1.75;
  color: rgb(209 213 219);
}

.markdown-body--scroll {
  max-height: 18rem;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.markdown-body :deep(h1) {
  font-size: 1.125rem;
  font-weight: 700;
  color: rgb(243 244 246);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.markdown-body :deep(h2) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #a29bfe;
  margin: 1.25rem 0 0.625rem;
}

.markdown-body :deep(h2:first-child) {
  margin-top: 0;
}

.markdown-body :deep(h3) {
  font-size: 0.8125rem;
  font-weight: 600;
  color: rgb(229 231 235);
  margin: 1rem 0 0.5rem;
}

.markdown-body :deep(p) {
  margin: 0.5rem 0;
  color: rgb(209 213 219);
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.5rem 0 0.75rem;
  padding-left: 0;
  list-style: none;
}

.markdown-body :deep(ul > li),
.markdown-body :deep(ol > li) {
  position: relative;
  padding-left: 1.25rem;
  margin: 0.375rem 0;
}

.markdown-body :deep(ul > li::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0.65em;
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
}

.markdown-body :deep(ol) {
  counter-reset: md-ol;
}

.markdown-body :deep(ol > li) {
  counter-increment: md-ol;
}

.markdown-body :deep(ol > li::before) {
  content: counter(md-ol);
  position: absolute;
  left: 0;
  top: 0.1em;
  min-width: 1rem;
  font-size: 0.6875rem;
  font-weight: 700;
  color: #6c63ff;
}

.markdown-body :deep(blockquote) {
  margin: 0.75rem 0;
  padding: 0.75rem 1rem;
  border-left: 3px solid rgba(108, 99, 255, 0.65);
  border-radius: 0 0.5rem 0.5rem 0;
  background: rgba(108, 99, 255, 0.08);
  color: rgb(229 231 235);
}

.markdown-body :deep(blockquote p) {
  margin: 0;
}

.markdown-body :deep(strong) {
  color: rgb(243 244 246);
  font-weight: 600;
}

.markdown-body :deep(em) {
  color: rgb(167 139 250);
  font-style: normal;
}

.markdown-body :deep(code) {
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: rgba(0, 0, 0, 0.35);
  color: #c4b5fd;
  font-size: 0.8125em;
}

.markdown-body :deep(pre) {
  margin: 0.75rem 0;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: rgba(0, 0, 0, 0.35);
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
}

.markdown-body :deep(hr) {
  margin: 1rem 0;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.markdown-body :deep(a) {
  color: #a29bfe;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.markdown-body :deep(a:hover) {
  color: #c4b5fd;
}

.markdown-body--compact :deep(h2) {
  margin-top: 0.875rem;
}

.custom-scroll::-webkit-scrollbar {
  width: 4px;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>
