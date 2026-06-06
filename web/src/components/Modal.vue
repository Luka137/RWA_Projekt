<script setup lang="ts">
defineProps<{ naslov: string }>();
const emit = defineEmits<{ zatvori: [] }>();
</script>

<template>
  <div class="modal-pozadina" @click.self="emit('zatvori')">
    <div class="modal kartica fade-in">
      <div class="modal-zaglavlje">
        <h3>{{ naslov }}</h3>
        <button class="zatvori-gumb" @click="emit('zatvori')" aria-label="Zatvori">
          ×
        </button>
      </div>
      <div class="modal-tijelo">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-pozadina {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  z-index: 900;
  animation: fadeInUp 0.2s ease;
}
.modal {
  width: 100%;
  max-width: 460px;
  background: var(--boja-povrsina-2);
  max-height: 90vh;
  overflow-y: auto;
}
.modal-zaglavlje {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 1.3rem;
  border-bottom: 1px solid var(--boja-rub);
}
.modal-zaglavlje h3 {
  font-size: 1.5rem;
  text-transform: uppercase;
}
.zatvori-gumb {
  background: none;
  border: none;
  color: var(--boja-tekst-prigusen);
  font-size: 1.8rem;
  line-height: 1;
  transition: var(--tranzicija);
}
.zatvori-gumb:hover {
  color: var(--boja-tekst);
}
.modal-tijelo {
  padding: 1.3rem;
}
</style>
