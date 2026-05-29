<template>
  <div class="flex justify-center items-center min-h-[60vh] px-4">
    <div class="w-full max-w-md rounded-2xl border border-white/10 bg-[#1A1A2E] p-8 text-center space-y-4">
      <div class="w-16 h-16 mx-auto rounded-full bg-orange-500/20 flex items-center justify-center">
        <svg class="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </div>
      <h2 class="text-xl font-bold text-white">支付已取消</h2>
      <p class="text-gray-400 text-sm">您可随时返回套餐页重新选择</p>
      <div class="flex flex-col gap-3 pt-2">
        <router-link
          to="/pricing"
          class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#6C63FF] to-[#3B82F6]"
        >
          返回套餐页
        </router-link>
        <router-link to="/" class="text-[#6C63FF] text-sm hover:underline">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
