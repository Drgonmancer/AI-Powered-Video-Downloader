<template>
  <div class="border-t border-white/5 pt-3 mt-2 space-y-3">
    <button
      type="button"
      class="w-full flex items-center justify-between text-xs font-bold text-gray-400 uppercase tracking-wider px-1"
      @click="expanded = !expanded"
    >
      <span class="flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5 text-[#6C63FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        {{ locale === 'zh' ? '大模型配置' : 'LLM Config' }}
      </span>
      <svg
        class="w-4 h-4 transition-transform"
        :class="expanded ? 'rotate-180' : ''"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <div v-show="expanded" class="space-y-3 max-h-[320px] overflow-y-auto pr-1 custom-scroll">
      <div v-if="!authStore.isLoggedIn" class="text-[11px] text-gray-500 px-1">
        {{ locale === 'zh' ? '登录后可保存 API 配置' : 'Login to save API configs' }}
      </div>

      <template v-else>
        <ul v-if="providers.length" class="space-y-2">
          <li
            v-for="p in providers"
            :key="p.id"
            class="rounded-lg bg-black/25 border border-white/5 p-2.5 text-[11px]"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-1.5">
                  <span class="font-semibold text-gray-200 truncate">{{ p.display_name }}</span>
                  <span
                    v-if="p.is_default"
                    class="shrink-0 px-1 py-0.5 rounded text-[9px] bg-[#6C63FF]/20 text-[#6C63FF]"
                  >默认</span>
                </div>
                <p class="text-gray-500 truncate mt-0.5">{{ p.model }}</p>
                <p class="text-gray-600 truncate">{{ p.api_key_masked }}</p>
              </div>
              <div class="flex flex-col gap-1 shrink-0">
                <button
                  v-if="!p.is_default"
                  type="button"
                  class="text-[10px] text-[#6C63FF] hover:underline"
                  @click="setDefault(p.id)"
                >默认</button>
                <button
                  type="button"
                  class="text-[10px] text-red-400 hover:underline"
                  @click="removeProvider(p.id)"
                >删除</button>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="text-[11px] text-gray-500 px-1">暂无配置，请添加</p>

        <div class="space-y-2">
          <input
            v-model="form.display_name"
            type="text"
            maxlength="80"
            :placeholder="locale === 'zh' ? '显示名称，如 DeepSeek' : 'Display name'"
            class="w-full px-2.5 py-1.5 rounded-lg bg-black/30 border border-white/10 text-gray-200 text-[11px] outline-none focus:border-[#6C63FF]/40"
          />
          <input
            v-model="form.model"
            type="text"
            :placeholder="locale === 'zh' ? '模型 ID，如 deepseek-chat' : 'Model ID'"
            class="w-full px-2.5 py-1.5 rounded-lg bg-black/30 border border-white/10 text-gray-200 text-[11px] outline-none focus:border-[#6C63FF]/40"
          />
          <input
            v-model="form.base_url"
            type="text"
            placeholder="API Base URL（可选）"
            class="w-full px-2.5 py-1.5 rounded-lg bg-black/30 border border-white/10 text-gray-200 text-[11px] outline-none focus:border-[#6C63FF]/40"
          />
          <input
            v-model="form.api_key"
            type="password"
            :placeholder="locale === 'zh' ? 'API Key' : 'API Key'"
            class="w-full px-2.5 py-1.5 rounded-lg bg-black/30 border border-white/10 text-gray-200 text-[11px] outline-none focus:border-[#6C63FF]/40"
          />
          <button
            type="button"
            :disabled="saving"
            class="w-full py-1.5 rounded-lg text-[11px] font-medium text-white bg-[#6C63FF]/80 hover:bg-[#6C63FF] disabled:opacity-50"
            @click="addProvider"
          >
            {{ saving ? '保存中...' : (locale === 'zh' ? '添加配置' : 'Add') }}
          </button>
        </div>
        <p v-if="error" class="text-[10px] text-red-400 px-1">{{ error }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useI18n } from '../../composables/useI18n'
import { llmApi } from '../../api/llmApi'

const authStore = useAuthStore()
const { locale } = useI18n()

const expanded = ref(true)
const providers = ref([])
const saving = ref(false)
const error = ref('')

const form = reactive({
  display_name: '',
  api_key: '',
  base_url: 'https://api.deepseek.com/v1',
  model: 'deepseek-chat',
})

async function loadProviders() {
  if (!authStore.token) {
    providers.value = []
    return
  }
  error.value = ''
  try {
    const res = await llmApi.list(authStore.token)
    providers.value = res.data || []
  } catch (e) {
    error.value = e.message
  }
}

async function addProvider() {
  if (!authStore.token) return
  saving.value = true
  error.value = ''
  try {
    await llmApi.create(authStore.token, { ...form })
    form.display_name = ''
    form.api_key = ''
    await loadProviders()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function removeProvider(id) {
  if (!confirm(locale.value === 'zh' ? '确定删除该配置？' : 'Delete this config?')) return
  try {
    await llmApi.remove(authStore.token, id)
    await loadProviders()
  } catch (e) {
    error.value = e.message
  }
}

async function setDefault(id) {
  try {
    await llmApi.setDefault(authStore.token, id)
    await loadProviders()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(loadProviders)
watch(() => authStore.token, loadProviders)
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 4px;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>
