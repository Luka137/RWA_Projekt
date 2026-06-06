<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { extractErrorMessage } from "@/services/api";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const greska = ref("");
const ucitavanje = ref(false);

// Klijentska validacija prije slanja
function validiraj(): boolean {
  if (!username.value.trim()) {
    greska.value = "Unesite korisničko ime.";
    return false;
  }
  if (!password.value) {
    greska.value = "Unesite lozinku.";
    return false;
  }
  return true;
}

async function posalji() {
  greska.value = "";
  if (!validiraj()) return;

  ucitavanje.value = true;
  try {
    await auth.login(username.value.trim(), password.value);
    // Vrati korisnika kamo je htio ici (ili na dashboard)
    const redirect = (route.query.redirect as string) || "/";
    router.push(redirect);
  } catch (e) {
    greska.value = extractErrorMessage(e, "Prijava nije uspjela.");
  } finally {
    ucitavanje.value = false;
  }
}
</script>

<template>
  <div class="kartica login-kartica fade-in">
    <h2>Prijava</h2>
    <p class="tekst-prigusen podnaslov">Pristupite svom računu</p>

    <form @submit.prevent="posalji">
      <div class="polje">
        <label for="username">Korisničko ime</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          placeholder="npr. member1"
          :disabled="ucitavanje"
        />
      </div>

      <div class="polje">
        <label for="password">Lozinka</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="••••••••"
          :disabled="ucitavanje"
        />
      </div>

      <p v-if="greska" class="poruka-greska">{{ greska }}</p>

      <button
        type="submit"
        class="gumb gumb-primarni gumb-puni"
        :disabled="ucitavanje"
      >
        {{ ucitavanje ? "Prijava..." : "Prijavi se" }}
      </button>
    </form>

    <p class="prebaci tekst-prigusen">
      Nemate račun?
      <RouterLink :to="{ name: 'register' }">Registrirajte se</RouterLink>
    </p>
  </div>
</template>

<style scoped>
.login-kartica {
  padding: 2rem 1.8rem;
}
h2 {
  font-size: 2rem;
  text-transform: uppercase;
}
.podnaslov {
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}
.gumb-puni {
  width: 100%;
  margin-top: 0.5rem;
}
.poruka-greska {
  background: rgba(214, 69, 60, 0.12);
  border: 1px solid rgba(214, 69, 60, 0.3);
  color: var(--boja-greska);
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius);
  font-size: 0.86rem;
  margin-bottom: 0.9rem;
}
.prebaci {
  margin-top: 1.4rem;
  text-align: center;
  font-size: 0.9rem;
}
.prebaci a {
  color: var(--boja-akcent);
  font-weight: 600;
}
.prebaci a:hover {
  text-decoration: underline;
}
</style>
