<template>
  <div class="max-w-2xl mx-auto space-y-8">
    <div class="mb-6">
      <h2 class="text-xl font-bold gradient-text mb-1">{{ t('settings') }}</h2>
      <p class="text-sm text-gray-500">{{ t('settingsDesc') }}</p>
    </div>

    <div class="space-y-4">
      <div class="rounded-2xl border border-white/5 bg-[#1A1A2E] p-6 space-y-6">
        <h3 class="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-[#6C63FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
          </svg>
          {{ t('general') }}
        </h3>

        <div class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">{{ t('language') }}</label>
            <div class="flex gap-3">
              <button
                @click="form.locale = 'zh'"
                :class="[
                  'px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border',
                  form.locale === 'zh'
                    ? 'bg-[#6C63FF]/15 text-[#6C63FF] border-[#6C63FF]/30'
                    : 'bg-black/20 text-gray-400 border-white/10 hover:border-white/20'
                ]"
              >
                中文
              </button>
              <button
                @click="form.locale = 'en'"
                :class="[
                  'px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border',
                  form.locale === 'en'
                    ? 'bg-[#6C63FF]/15 text-[#6C63FF] border-[#6C63FF]/30'
                    : 'bg-black/20 text-gray-400 border-white/10 hover:border-white/20'
                ]"
              >
                English
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">{{ t('downloadPath') }}</label>
            <input
              v-model="form.download_path"
              type="text"
              class="w-full px-4 py-3 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50 focus:ring-1 focus:ring-[#6C63FF]/25 transition-all placeholder:text-gray-600"
              placeholder="./downloads"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">{{ t('outputFormat') }}</label>
              <select
                v-model="form.output_format"
                class="w-full px-4 py-3 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50 transition-all appearance-none cursor-pointer"
              >
                <option value="mp4">MP4 ({{ locale === 'zh' ? '推荐' : 'Recommended' }})</option>
                <option value="webm">WebM</option>
                <option value="mkv">MKV</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">{{ t('defaultQuality') }}</label>
              <select
                v-model="form.default_quality"
                class="w-full px-4 py-3 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50 transition-all appearance-none cursor-pointer"
              >
                <option value="best">{{ locale === 'zh' ? '最佳画质' : 'Best Available' }}</option>
                <option value="1080">1080p</option>
                <option value="720">720p</option>
                <option value="480">480p</option>
                <option value="audio">{{ locale === 'zh' ? '仅音频' : 'Audio Only' }}</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">{{ t('cookiesLabel') || 'Cookies / SESSDATA' }}</label>
            <textarea
              v-model="form.cookies"
              rows="3"
              class="w-full px-4 py-3 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50 focus:ring-1 focus:ring-[#6C63FF]/25 transition-all placeholder:text-gray-600 resize-none"
              :placeholder="t('cookiesPlaceholder')"
            ></textarea>

            <div class="mt-3">
              <label class="block text-xs font-medium text-gray-500 mb-2">
                {{ locale === 'zh' ? '自动从浏览器读取 Cookie（推荐 Edge）' : 'Auto-read cookies from browser (Edge Recommended)' }}
                <span class="ml-1 px-1.5 py-0.5 rounded text-[9px] bg-[#6C63FF]/20 text-[#6C63FF]">{{ locale === 'zh' ? '无需手动复制' : 'No manual copy' }}</span>
              </label>
              <select
                v-model="form.cookies_from_browser"
                class="w-full px-4 py-2.5 rounded-xl bg-black/30 border border-white/10 text-gray-200 text-sm outline-none focus:border-[#6C63FF]/50 transition-all appearance-none cursor-pointer"
              >
                <option value="edge" class="text-[#6C63FF]">🔵 Microsoft Edge {{ locale === 'zh' ? '（推荐）' : '(Recommended)' }}</option>
                <option value="firefox">🦊 Firefox</option>
                <option value="chrome">🌐 Chrome 浏览器</option>
                <option value="brave">🦁 Brave</option>
                <option value="">{{ locale === 'zh' ? '不使用（手动输入上方Cookie）' : 'Disabled (manual)' }}</option>
              </select>
            </div>

            <p class="text-xs text-gray-600 mt-1.5 leading-relaxed">{{ t('cookiesHint') }}</p>
            <div class="mt-2 rounded-lg bg-gradient-to-r from-blue-500/5 to-purple-500/5 border border-blue-500/10 p-3 space-y-2">
              <p class="text-xs text-blue-300/80 font-medium flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                {{ locale === 'zh' ? 'Edge 专用优化说明' : 'Edge-Specific Instructions' }}
              </p>
              <ol class="text-[11px] text-blue-300/60 space-y-1 list-decimal list-inside pl-1">
                <li>{{ locale === 'zh' ? '首次使用请运行 tools/setup_edge_unlock.py 配置 Edge' : 'Run tools/setup_edge_unlock.py to configure Edge (one-time)' }}</li>
                <li>{{ locale === 'zh' ? '配置后用桌面新快捷方式启动 Edge（带解锁标识）' : 'Launch Edge via the new desktop shortcut (unlocked)' }}</li>
                <li>{{ locale === 'zh' ? '确保 Edge 已登录抖音/B站等网站' : 'Make sure Edge is logged into Douyin/Bilibili etc.' }}</li>
                <li>{{ locale === 'zh' ? '保存此设置后即可自动读取，全程无需手动操作！' : 'Save and enjoy - fully automatic!' }}</li>
              </ol>
              <div class="pt-1.5 mt-1 border-t border-white/5 flex items-start gap-2">
                <span class="text-yellow-400/70 text-[10px] shrink-0">💡</span>
                <div class="text-[10px] text-blue-300/50 leading-relaxed">
                  {{ locale === 'zh' ? '支持平台：抖音、B站、YouTube、TikTok、Twitter、Instagram、快手、小红书 等 1700+ 网站，全部自动识别登录状态' : 'Supports: Douyin, Bilibili, YouTube, TikTok, Twitter, Instagram & 1700+ sites - auto login detection' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-white/5 bg-[#1A1A2E] p-6 space-y-6">
        <h3 class="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-[#6C63FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          {{ t('performance') }}
        </h3>

        <div class="space-y-5">
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-400">{{ t('maxConcurrent') }}</label>
              <span class="text-sm font-mono font-bold text-[#6C63FF]">{{ form.max_concurrent }}</span>
            </div>
            <input
              v-model.number="form.max_concurrent"
              type="range"
              min="1"
              max="5"
              step="1"
              class="w-full h-2 rounded-full appearance-none bg-white/5 cursor-pointer accent-[#6C63FF]"
            />
            <div class="flex justify-between text-[10px] text-gray-600 mt-1">
              <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-400">{{ t('speedLimit') }}</label>
              <span class="text-sm font-mono font-bold text-[#6C63FF]">{{ form.speed_limit ? (form.speed_limit / 1048576).toFixed(0) : t('unlimited') }}</span>
            </div>
            <input
              v-model.number="form.speed_limit"
              type="range"
              min="0"
              max="104857600"
              step="1048576"
              class="w-full h-2 rounded-full appearance-none bg-white/5 cursor-pointer accent-[#6C63FF]"
            />
            <div class="flex justify-between text-[10px] text-gray-600 mt-1">
              <span>{{ t('unlimited') }}</span>
              <span>50 MB/s</span>
              <span>100 MB/s</span>
            </div>
          </div>
        </div>
      </div>

      <button
        @click="saveSettings"
        :disabled="saving"
        class="w-full py-4 rounded-xl font-semibold text-sm transition-all duration-300 flex items-center justify-center gap-2"
        :class="
          saving
            ? 'bg-gray-700/30 text-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-[#6C63FF] to-[#3B82F6] text-white shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.01]'
        "
      >
        <svg v-if="!saving" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ saving ? t('saving') : t('saveSettings') }}
      </button>

      <div v-if="saved" class="text-center py-2">
        <span class="text-emerald-400 text-sm font-medium flex items-center justify-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          {{ t('settingsSaved') }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useDownloadStore } from '../stores/download'
import { useI18n } from '../composables/useI18n'

const store = useDownloadStore()
const { t, setLocale, locale } = useI18n()
const saving = ref(false)
const saved = ref(false)

const form = reactive({
  download_path: '',
  output_format: 'mp4',
  default_quality: 'best',
  max_concurrent: 3,
  speed_limit: 0,
  cookies: '',
  cookies_from_browser: 'edge',
  locale: 'zh',
})

function loadSettings() {
  if (store.settings) {
    Object.assign(form, store.settings)
  }
  form.locale = locale.value
}

async function saveSettings() {
  saving.value = true
  saved.value = false
  try {
    const data = { ...form }
    await store.updateSettings(data)
    setLocale(form.locale)
    saved.value = true
    setTimeout(() => { saved.value = false }, 2500)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
