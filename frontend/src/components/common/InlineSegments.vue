<template>
  <span class="inline">
    <template v-for="(seg, i) in segments" :key="i">
      <strong v-if="seg.type === 'bold'" class="font-semibold text-gray-100">{{ seg.value }}</strong>
      <span v-else>{{ seg.value }}</span>
    </template>
  </span>
</template>

<script setup>
defineProps({
  segments: { type: Array, default: () => [] },
})
</script>
