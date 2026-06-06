import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authService } from "@/services/auth.service";
import { tokenStorage } from "@/services/api";
import type { User } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const loading = ref(false);
  // Pratimo jesmo li vec pokusali ucitati korisnika na startu aplikacije.
  const initialized = ref(false);

  // --- Geteri (public API store-a, ostaju na engleskom po konvenciji) ---
  const isAuthenticated = computed(() => user.value !== null);
  const isAdmin = computed(() => user.value?.role === "admin");
  const isTrainer = computed(() => user.value?.role === "trainer");
  const isMember = computed(() => user.value?.role === "member");
  const role = computed(() => user.value?.role ?? null);

  // Login: dohvati tokene, spremi ih, pa ucitaj korisnika preko /auth/me.
  async function login(username: string, password: string): Promise<void> {
    const tokens = await authService.login(username, password);
    tokenStorage.set(tokens.access_token, tokens.refresh_token);
    user.value = await authService.me();
  }

  // Ucitaj korisnika ako vec imamo token (npr. nakon refresha stranice).
  async function loadUser(): Promise<void> {
    if (!tokenStorage.getAccess()) {
      initialized.value = true;
      return;
    }
    loading.value = true;
    try {
      user.value = await authService.me();
    } catch {
      // Token nevazeci -> ocisti.
      tokenStorage.clear();
      user.value = null;
    } finally {
      loading.value = false;
      initialized.value = true;
    }
  }

  // Odjava: ocisti tokene i korisnika.
  function logout(): void {
    tokenStorage.clear();
    user.value = null;
  }

  return {
    user,
    loading,
    initialized,
    isAuthenticated,
    isAdmin,
    isTrainer,
    isMember,
    role,
    login,
    loadUser,
    logout,
  };
});
