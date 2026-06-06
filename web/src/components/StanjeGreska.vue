<script setup lang="ts">
defineProps<{ poruka: string }>();
const emit = defineEmits<{ pokusajPonovno: [] }>();
</script>

<template>
  <div class="stanje-greska kartica">
    <div class="ikona">!</div>
    <p>{{ poruka }}</p>
    <button class="gumb gumb-mali" @click="emit('pokusajPonovno')">
      Pokušaj ponovno
    </button>
  </div>
</template>

<style scoped>
.stanje-greska {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
  padding: 2.5rem 1.5rem;
  text-align: center;
  border-color: rgba(214, 69, 60, 0.3);
}
.ikona {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(214, 69, 60, 0.12);
  color: var(--boja-greska);
  font-family: var(--font-naslov);
  font-size: 1.6rem;
}
</style>
