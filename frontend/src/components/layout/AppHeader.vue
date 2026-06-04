<template>
  <header class="h-16 border-b border-white/5 flex items-center justify-between px-6 shrink-0 bg-[#0F0F1A]/80 backdrop-blur-sm">
    <div class="flex items-center gap-4">
      <h2 class="text-base font-semibold text-gray-300">{{ title }}</h2>
      <span v-if="subtitle.length" class="text-xs text-gray-500">{{ subtitle }}</span>
    </div>

    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/5">
        <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
        <span class="text-xs text-gray-400">{{ t('serverOnline') }}</span>
      </div>

      <!-- Logged In User Info -->
      <div v-if="authStore.isLoggedIn" class="flex items-center gap-3">
        <!-- VIP Badge (if active) -->
        <div 
          v-if="membershipStore.isActive && membershipStore.currentPlan !== 'free'"
          :class="[
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium',
            membershipStore.isPro ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' :
            membershipStore.isBasic ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
            'bg-gray-500/20 text-gray-400 border border-gray-500/30'
          ]"
        >
          <svg v-if="membershipStore.isPro" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
          </svg>
          <svg v-else-if="membershipStore.isBasic" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z"/>
          </svg>
          <span>{{ membershipStore.isPro ? 'PRO' : membershipStore.isBasic ? 'VIP' : '' }}</span>
          <span 
            v-if="membershipStore.membershipTimeRemaining"
            class="text-[10px] opacity-80"
          >
            {{ membershipStore.membershipTimeRemaining }}
          </span>
        </div>

        <!-- User Avatar & Name -->
        <button 
          @click="$router.push('/member/center')"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 hover:bg-[#6C63FF]/10 hover:border-[#6C63FF]/30 transition-all duration-200 group"
        >
          <img 
            v-if="authStore.userAvatar" 
            :src="authStore.userAvatar" 
            alt="avatar" 
            class="w-7 h-7 rounded-full object-cover ring-2 ring-[#6C63FF]/50 group-hover:ring-[#6C63FF]"
          />
          <div 
            v-else 
            class="w-7 h-7 rounded-full bg-gradient-to-br from-[#6C63FF] to-purple-600 flex items-center justify-center text-white text-xs font-bold ring-2 ring-[#6C63FF]/50 group-hover:ring-[#6C63FF]"
          >
            {{ authStore.userName?.charAt(0)?.toUpperCase() || authStore.userEmail?.charAt(0)?.toUpperCase() || '?' }}
          </div>
          <span class="text-sm font-medium text-gray-200 max-w-[100px] truncate group-hover:text-white transition-colors">
            {{ authStore.userName || authStore.userEmail?.split('@')[0] || 'User' }}
          </span>
        </button>

        <!-- User Menu Dropdown -->
        <div class="relative group">
          <button class="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-gray-200 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <div class="absolute right-0 top-full mt-2 w-52 bg-[#1a1a2e] border border-white/10 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999]">
            <div class="p-3 border-b border-white/5">
              <div class="flex items-center gap-3 mb-2">
                <img 
                  v-if="authStore.userAvatar" 
                  :src="authStore.userAvatar" 
                  alt="avatar" 
                  class="w-10 h-10 rounded-full object-cover ring-2 ring-[#6C63FF]"
                />
                <div 
                  v-else 
                  class="w-10 h-10 rounded-full bg-gradient-to-br from-[#6C63FF] to-purple-600 flex items-center justify-center text-white text-base font-bold ring-2 ring-[#6C63FF]"
                >
                  {{ authStore.userName?.charAt(0)?.toUpperCase() || authStore.userEmail?.charAt(0)?.toUpperCase() || '?' }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-semibold text-white truncate">{{ authStore.userName || authStore.userEmail?.split('@')[0] || 'User' }}</div>
                  <div class="text-xs text-gray-400 truncate">{{ authStore.userEmail }}</div>
                </div>
              </div>
              <div 
                :class="[
                  'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium',
                  authStore.role === 'admin' ? 'bg-red-500/20 text-red-300' :
                  membershipStore.isActive && membershipStore.currentPlan !== 'free' ? 'bg-purple-500/20 text-purple-300' :
                  'bg-gray-500/20 text-gray-400'
                ]"
              >
                {{ authStore.role === 'admin' ? '👑 管理员' : membershipStore.isPro ? '⭐ PRO会员' : membershipStore.isBasic ? '💎 VIP会员' : '👤 普通用户' }}
              </div>
            </div>

            <div class="p-2">
              <button
                @click="$router.push('/member/center')"
                class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                {{ locale === 'zh' ? '个人中心' : 'Profile Center' }}
              </button>

              <button
                @click="$router.push('/pricing')"
                class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                {{ locale === 'zh' ? '升级会员' : 'Upgrade Plan' }}
              </button>

              <hr class="my-2 border-white/5">

              <button
                @click="handleLogout"
                class="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
                {{ locale === 'zh' ? '退出登录' : 'Logout' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Language toggle button -->
      <button
        @click="toggleLocale"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 hover:bg-[#6C63FF]/10 hover:border-[#6C63FF]/30 text-gray-400 hover:text-[#6C63FF] transition-all duration-200 text-xs font-medium"
        :title="locale === 'zh' ? 'Switch to English' : '切换为中文'"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/>
        </svg>
        {{ locale === 'zh' ? 'EN' : '中' }}
      </button>

      <button
        @click="$router.push('/settings')"
        class="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-gray-200 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '../../composables/useI18n'
import { useAuthStore } from '../../stores/auth'
import { useMembershipStore } from '../../stores/membership'
import { clearSessionOnLogout } from '../../utils/sessionReset'

const route = useRoute()
const router = useRouter()
const { t, locale, setLocale } = useI18n()
const authStore = useAuthStore()
const membershipStore = useMembershipStore()

function refreshMembership() {
  if (authStore.isLoggedIn) {
    console.log('[Header] Refresh membership status')
    membershipStore.fetchMembershipStatus()
  }
}

function toggleLocale() {
  setLocale(locale.value === 'zh' ? 'en' : 'zh')
}

async function handleLogout() {
  authStore.logout()
  await clearSessionOnLogout()
  router.push('/login')
}

const titles = computed(() => ({
  '/': { title: locale.value === 'zh' ? '控制台' : 'Dashboard', subtitle: locale.value === 'zh' ? '下载和管理视频' : 'Download & manage videos' },
  '/settings': { title: t('settings'), subtitle: t('settingsDesc') },
  '/login': { title: locale.value === 'zh' ? '登录' : 'Login', subtitle: '' },
  '/register': { title: locale.value === 'zh' ? '注册' : 'Register', subtitle: '' },
  '/pricing': { title: locale.value === 'zh' ? '会员套餐' : 'Pricing Plans', subtitle: '' },
  '/member/center': { title: locale.value === 'zh' ? '个人中心' : 'Personal Center', subtitle: '' },
}))

const current = computed(() => titles.value[route.path] || { title: '', subtitle: '' })
const title = computed(() => current.value.title)
const subtitle = computed(() => current.value.subtitle)

onMounted(() => {
  authStore.init()
  refreshMembership()
})

watch(() => route.path, () => {
  refreshMembership()
})
</script>
