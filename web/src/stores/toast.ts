import { defineStore } from "pinia";
import { ref } from "vue";

export type ToastType = "success" | "error" | "info";

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

export const useToastStore = defineStore("toast", () => {
  const toasts = ref<Toast[]>([]);
  let nextId = 1;

  function push(message: string, type: ToastType = "info", durationMs = 4000) {
    const id = nextId++;
    toasts.value.push({ id, type, message });
    setTimeout(() => remove(id), durationMs);
  }

  function remove(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  // Kratke pomocne metode
  const success = (m: string) => push(m, "success");
  const error = (m: string) => push(m, "error");
  const info = (m: string) => push(m, "info");

  return { toasts, push, remove, success, error, info };
});
