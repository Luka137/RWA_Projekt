<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { trainingService } from "@/services/training.service";
import { membershipService } from "@/services/membership.service";
import { roleLabel, isMembershipActive } from "@/utils/format";
import type { Training, Membership } from "@/types";
import StanjeUcitavanje from "@/components/StanjeUcitavanje.vue";

const auth = useAuthStore();

const treninzi = ref<Training[]>([]);
const clanarine = ref<Membership[]>([]);
const ucitavanje = ref(true);

// Broj nadolazecih (zakazanih) treninga
const nadolazeci = computed(
  () => treninzi.value.filter((t) => t.status === "scheduled").length,
);

// Ima li korisnik aktivnu clanarinu
const aktivnaClanarina = computed(() =>
  clanarine.value.some((m) => isMembershipActive(m.status, m.end_date)),
);

async function ucitaj() {
  ucitavanje.value = true;
  try {
    treninzi.value = await trainingService.list();
    // Clanarine dohvati samo ako nije admin (admin bi dobio sve, nebitno za pregled)
    clanarine.value = await membershipService.list();
  } catch {
    // Tihо - dashboard nije kriticna stranica
  } finally {
    ucitavanje.value = false;
  }
}

onMounted(ucitaj);
</script>

<template>
  <div class="dashboard">
    <header class="zaglavlje fade-in">
      <p class="pozdrav tekst-prigusen">Dobrodošli natrag,</p>
      <h1 class="naslov-velik">{{ auth.user?.username }}</h1>
      <span class="bedz bedz-info uloga-bedz">
        {{ auth.role ? roleLabel[auth.role] : "" }}
      </span>
    </header>

    <StanjeUcitavanje v-if="ucitavanje" poruka="Učitavanje pregleda..." />

    <template v-else>
      <div class="statistika">
        <div class="stat-kartica kartica fade-in">
          <span class="stat-broj">{{ treninzi.length }}</span>
          <span class="stat-oznaka tekst-prigusen">Ukupno treninga</span>
        </div>
        <div class="stat-kartica kartica fade-in">
          <span class="stat-broj">{{ nadolazeci }}</span>
          <span class="stat-oznaka tekst-prigusen">Zakazanih</span>
        </div>
        <div v-if="!auth.isAdmin" class="stat-kartica kartica fade-in">
          <span class="stat-broj" :class="aktivnaClanarina ? 'zeleno' : 'crveno'">
            {{ aktivnaClanarina ? "✓" : "✕" }}
          </span>
          <span class="stat-oznaka tekst-prigusen">Aktivna članarina</span>
        </div>
      </div>

      <div class="brze-veze">
        <RouterLink :to="{ name: 'trainings' }" class="veza-kartica kartica">
          <span class="veza-ikona">🏋</span>
          <div>
            <h3>Treninzi</h3>
            <p class="tekst-prigusen">Pregledaj i rezerviraj termine</p>
          </div>
        </RouterLink>

        <RouterLink :to="{ name: 'memberships' }" class="veza-kartica kartica">
          <span class="veza-ikona">🎟</span>
          <div>
            <h3>Članarine</h3>
            <p class="tekst-prigusen">Status i povijest članstva</p>
          </div>
        </RouterLink>

        <RouterLink
          v-if="auth.isAdmin"
          :to="{ name: 'admin-users' }"
          class="veza-kartica kartica"
        >
          <span class="veza-ikona">👥</span>
          <div>
            <h3>Korisnici</h3>
            <p class="tekst-prigusen">Upravljanje korisnicima</p>
          </div>
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<style scoped>
.zaglavlje {
  margin-bottom: 2rem;
}
.pozdrav {
  font-size: 0.95rem;
}
.naslov-velik {
  margin: 0.1rem 0 0.6rem;
}
.uloga-bedz {
  font-size: 0.75rem;
}
.statistika {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-kartica {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.stat-broj {
  font-family: var(--font-naslov);
  font-size: 2.6rem;
  line-height: 1;
  color: var(--boja-akcent);
}
.stat-broj.zeleno {
  color: var(--boja-uspjeh);
}
.stat-broj.crveno {
  color: var(--boja-greska);
}
.stat-oznaka {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.brze-veze {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}
.veza-kartica {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.3rem;
  transition: var(--tranzicija);
}
.veza-kartica:hover {
  border-color: var(--boja-akcent);
  transform: translateY(-2px);
}
.veza-ikona {
  font-size: 1.8rem;
}
.veza-kartica h3 {
  font-size: 1.3rem;
  text-transform: uppercase;
}
.veza-kartica p {
  font-size: 0.85rem;
}
</style>
