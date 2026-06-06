<script setup lang="ts">
import { useToastStore } from "@/stores/toast";
const toast = useToastStore();
</script>

<template>
  <div class="toast-spremnik">
    <TransitionGroup name="toast">
      <div
        v-for="t in toast.toasts"
        :key="t.id"
        class="toast"
        :class="`toast-${t.type}`"
        @click="toast.remove(t.id)"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-spremnik {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-width: 360px;
}
.toast {
  padding: 0.8rem 1.1rem;
  border-radius: var(--radius);
  font-size: 0.9rem;
  font-weight: 500;
  color: #fff;
  box-shadow: var(--sjena-jaka);
  cursor: pointer;
  border-left: 4px solid rgba(255, 255, 255, 0.4);
}
.toast-success {
  background: var(--boja-uspjeh);
}
.toast-error {
  background: var(--boja-greska);
}
.toast-info {
  background: var(--boja-info);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
