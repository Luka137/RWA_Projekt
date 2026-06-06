<script setup lang="ts">
import { ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { authService } from "@/services/auth.service";
import { useToastStore } from "@/stores/toast";
import { extractErrorMessage } from "@/services/api";

const auth = useAuthStore();
const router = useRouter();
const toast = useToastStore();

const username = ref("");
const password = ref("");
const potvrdaLozinke = ref("");
const greska = ref("");
const ucitavanje = ref(false);

// Validacija po pravilima backenda: username min 3, password min 6
function validiraj(): boolean {
  if (username.value.trim().length < 3) {
    greska.value = "Korisničko ime mora imati barem 3 znaka.";
    return false;
  }
  if (password.value.length < 6) {
    greska.value = "Lozinka mora imati barem 6 znakova.";
    return false;
  }
  if (password.value !== potvrdaLozinke.value) {
    greska.value = "Lozinke se ne podudaraju.";
    return false;
  }
  return true;
}

async function posalji() {
  greska.value = "";
  if (!validiraj()) return;

  ucitavanje.value = true;
  try {
    await authService.register(username.value.trim(), password.value);
    // Nakon registracije automatski prijavi korisnika
    await auth.login(username.value.trim(), password.value);
    toast.success("Račun uspješno kreiran!");
    router.push("/");
  } catch (e) {
    greska.value = extractErrorMessage(e, "Registracija nije uspjela.");
  } finally {
    ucitavanje.value = false;
  }
}
</script>

<template>
  <div class="kartica reg-kartica fade-in">
    <h2>Registracija</h2>
    <p class="tekst-prigusen podnaslov">Kreirajte članski račun</p>

    <form @submit.prevent="posalji">
      <div class="polje">
        <label for="username">Korisničko ime</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          placeholder="barem 3 znaka"
          :disabled="ucitavanje"
        />
      </div>

      <div class="polje">
        <label for="password">Lozinka</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="new-password"
          placeholder="barem 6 znakova"
          :disabled="ucitavanje"
        />
      </div>

      <div class="polje">
        <label for="potvrda">Potvrdi lozinku</label>
        <input
          id="potvrda"
          v-model="potvrdaLozinke"
          type="password"
          autocomplete="new-password"
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
        {{ ucitavanje ? "Kreiranje..." : "Registriraj se" }}
      </button>
    </form>

    <p class="prebaci tekst-prigusen">
      Već imate račun?
      <RouterLink :to="{ name: 'login' }">Prijavite se</RouterLink>
    </p>
  </div>
</template>

<style scoped>
.reg-kartica {
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
