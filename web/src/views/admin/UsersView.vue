<script setup lang="ts">
import { ref, onMounted } from "vue";
import { userService } from "@/services/user.service";
import { extractErrorMessage } from "@/services/api";
import { roleLabel } from "@/utils/format";
import type { User } from "@/types";
import StanjeUcitavanje from "@/components/StanjeUcitavanje.vue";
import StanjeGreska from "@/components/StanjeGreska.vue";
import StanjePrazno from "@/components/StanjePrazno.vue";

const korisnici = ref<User[]>([]);
const ucitavanje = ref(true);
const greska = ref("");
const pretraga = ref("");

async function ucitaj() {
  ucitavanje.value = true;
  greska.value = "";
  try {
    korisnici.value = await userService.list();
  } catch (e) {
    greska.value = extractErrorMessage(e, "Greška pri učitavanju korisnika.");
  } finally {
    ucitavanje.value = false;
  }
}

// Filtrirani prikaz po pretrazi
function filtrirani(): User[] {
  const q = pretraga.value.trim().toLowerCase();
  if (!q) return korisnici.value;
  return korisnici.value.filter((u) => u.username.toLowerCase().includes(q));
}

onMounted(ucitaj);
</script>

<template>
  <div class="korisnici">
    <header class="zaglavlje">
      <div>
        <h1 class="naslov-velik">Korisnici</h1>
        <p class="tekst-prigusen">Svi registrirani korisnici sustava</p>
      </div>
    </header>

    <StanjeUcitavanje v-if="ucitavanje" poruka="Učitavanje korisnika..." />

    <StanjeGreska v-else-if="greska" :poruka="greska" @pokusaj-ponovno="ucitaj" />

    <StanjePrazno
      v-else-if="korisnici.length === 0"
      poruka="Nema registriranih korisnika."
    />

    <template v-else>
      <div class="polje pretraga-polje">
        <input
          v-model="pretraga"
          type="text"
          placeholder="🔍 Pretraži po korisničkom imenu..."
        />
      </div>

      <div class="tablica-omot kartica">
        <table class="tablica">
          <thead>
            <tr>
              <th>ID</th>
              <th>Korisničko ime</th>
              <th>Uloga</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filtrirani()" :key="u.id">
              <td class="id-celija">#{{ u.id }}</td>
              <td>
                <div class="ime-celija">
                  <div class="mini-avatar">
                    {{ u.username.charAt(0).toUpperCase() }}
                  </div>
                  {{ u.username }}
                </div>
              </td>
              <td>
                <span class="uloga-tag" :class="`uloga-${u.role}`">
                  {{ roleLabel[u.role] }}
                </span>
              </td>
              <td>
                <span
                  class="bedz"
                  :class="u.is_active ? 'bedz-active' : 'bedz-cancelled'"
                >
                  {{ u.is_active ? "Aktivan" : "Neaktivan" }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<style scoped>
.zaglavlje {
  margin-bottom: 1.75rem;
}
.naslov-velik {
  font-size: clamp(2rem, 4vw, 2.8rem);
}
.pretraga-polje {
  max-width: 360px;
  margin-bottom: 1.25rem;
}
.tablica-omot {
  overflow-x: auto;
}
.tablica {
  width: 100%;
  border-collapse: collapse;
}
.tablica th {
  text-align: left;
  padding: 0.9rem 1.2rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--boja-tekst-prigusen);
  border-bottom: 1px solid var(--boja-rub);
  background: var(--boja-povrsina-2);
}
.tablica td {
  padding: 0.85rem 1.2rem;
  border-bottom: 1px solid var(--boja-rub);
  font-size: 0.92rem;
}
.tablica tbody tr:last-child td {
  border-bottom: none;
}
.tablica tbody tr:hover {
  background: var(--boja-povrsina-2);
}
.id-celija {
  color: var(--boja-tekst-prigusen);
  font-variant-numeric: tabular-nums;
}
.ime-celija {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 600;
}
.mini-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--boja-povrsina-2);
  border: 1px solid var(--boja-rub-jaki);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
}
.uloga-tag {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius);
}
.uloga-admin {
  color: var(--boja-akcent);
  background: rgba(232, 82, 30, 0.12);
}
.uloga-trainer {
  color: var(--boja-info);
  background: rgba(74, 143, 199, 0.12);
}
.uloga-member {
  color: var(--boja-tekst-prigusen);
  background: var(--boja-povrsina-2);
}
</style>
