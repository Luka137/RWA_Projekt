<script setup lang="ts">
defineProps<{ poruka?: string }>();
</script>

<template>
  <div class="stanje-prazno kartica">
    <div class="ikona">∅</div>
    <p class="tekst-prigusen">{{ poruka || "Nema podataka za prikaz." }}</p>
    <slot />
  </div>
</template>

<style scoped>
.stanje-prazno {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
  padding: 3rem 1.5rem;
  text-align: center;
  background: var(--boja-povrsina);
  border-style: dashed;
}
.ikona {
  font-size: 2.2rem;
  color: var(--boja-rub-jaki);
}
</style>
