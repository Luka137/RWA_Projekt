<script setup lang="ts">
defineProps<{
  status: string;
  label: string;
}>();
</script>

<template>
  <span class="bedz" :class="`bedz-${status}`">{{ label }}</span>
</template>
