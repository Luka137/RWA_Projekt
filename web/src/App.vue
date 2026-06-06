<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import LayoutGost from "@/layouts/LayoutGost.vue";
import LayoutAplikacija from "@/layouts/LayoutAplikacija.vue";
import ToastSpremnik from "@/components/ToastSpremnik.vue";

const route = useRoute();

// Biraj layout na temelju route.meta.layout
const layout = computed(() =>
  route.meta.layout === "gost" ? LayoutGost : LayoutAplikacija,
);
</script>

<template>
  <component :is="layout">
    <RouterView v-slot="{ Component }">
      <Transition name="ruta" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </component>
  <ToastSpremnik />
</template>

<style>
.ruta-enter-active,
.ruta-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.ruta-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.ruta-leave-to {
  opacity: 0;
}
</style>
