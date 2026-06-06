<script setup lang="ts">
defineProps<{ poruka?: string }>();
</script>

<template>
  <div class="ucitavanje">
    <div class="spinner"></div>
    <p v-if="poruka" class="tekst-prigusen">{{ poruka }}</p>
  </div>
</template>

<style scoped>
.ucitavanje {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem 1rem;
}
.spinner {
  width: 38px;
  height: 38px;
  border: 3px solid var(--boja-rub);
  border-top-color: var(--boja-akcent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
</style>
