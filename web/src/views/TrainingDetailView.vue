<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { trainingService } from "@/services/training.service";
import { reservationService } from "@/services/reservation.service";
import { useToastStore } from "@/stores/toast";
import { extractErrorMessage } from "@/services/api";
import { formatDateTime, trainingStatusLabel, reservationStatusLabel } from "@/utils/format";
import type { Training, Reservation } from "@/types";
import StanjeUcitavanje from "@/components/StanjeUcitavanje.vue";
import StanjeGreska from "@/components/StanjeGreska.vue";
import StanjePrazno from "@/components/StanjePrazno.vue";
import StatusBedz from "@/components/StatusBedz.vue";

const route = useRoute();
const auth = useAuthStore();
const toast = useToastStore();

const trainingId = Number(route.params.id);

const trening = ref<Training | null>(null);
const rezervacije = ref<Reservation[]>([]);
const ucitavanje = ref(true);
const greska = ref("");
const akcijaUTijeku = ref(false);

// Broj potvrdenih rezervacija
const potvrdjene = computed(
  () => rezervacije.value.filter((r) => r.status === "confirmed").length,
);

// Je li trening pun
const pun = computed(
  () => trening.value !== null && potvrdjene.value >= trening.value.max_capacity,
);

// Je li trenutni korisnik vec rezervirao (ima potvrdenu rezervaciju)
const mojaRezervacija = computed(() =>
  rezervacije.value.find(
    (r) => r.status === "confirmed" && r.user?.id === auth.user?.id,
  ),
);

// Smije li korisnik upravljati treningom (admin ili trener vlasnik)
const mozeUpravljati = computed(() => {
  if (auth.isAdmin) return true;
  if (auth.isTrainer && trening.value?.trainer?.id === auth.user?.id) return true;
  return false;
});

// Smije li clan rezervirati
const mozeRezervirati = computed(
  () =>
    auth.isMember &&
    trening.value?.status === "scheduled" &&
    !mojaRezervacija.value &&
    !pun.value,
);

async function ucitaj() {
  ucitavanje.value = true;
  greska.value = "";
  try {
    trening.value = await trainingService.get(trainingId);
    rezervacije.value = await reservationService.list(trainingId);
  } catch (e) {
    greska.value = extractErrorMessage(e, "Trening nije pronađen.");
  } finally {
    ucitavanje.value = false;
  }
}

// --- Akcije clana ---
async function rezerviraj() {
  akcijaUTijeku.value = true;
  try {
    await reservationService.create(trainingId);
    toast.success("Rezervacija potvrđena!");
    await ucitaj();
  } catch (e) {
    toast.error(extractErrorMessage(e, "Rezervacija nije uspjela."));
  } finally {
    akcijaUTijeku.value = false;
  }
}

async function otkaziRezervaciju(rid: number) {
  akcijaUTijeku.value = true;
  try {
    await reservationService.cancel(trainingId, rid);
    toast.success("Rezervacija otkazana.");
    await ucitaj();
  } catch (e) {
    toast.error(extractErrorMessage(e, "Otkazivanje nije uspjelo."));
  } finally {
    akcijaUTijeku.value = false;
  }
}

// --- Akcije trenera/admina (promjena statusa) ---
async function promijeniStatus(akcija: "start" | "complete" | "cancel") {
  akcijaUTijeku.value = true;
  try {
    if (akcija === "start") await trainingService.start(trainingId);
    else if (akcija === "complete") await trainingService.complete(trainingId);
    else await trainingService.cancel(trainingId);
    toast.success("Status treninga ažuriran.");
    await ucitaj();
  } catch (e) {
    toast.error(extractErrorMessage(e, "Promjena statusa nije uspjela."));
  } finally {
    akcijaUTijeku.value = false;
  }
}

onMounted(ucitaj);
</script>

<template>
  <div class="detalj">
    <RouterLink :to="{ name: 'trainings' }" class="natrag tekst-prigusen">
      ← Natrag na treninge
    </RouterLink>

    <StanjeUcitavanje v-if="ucitavanje" poruka="Učitavanje treninga..." />

    <StanjeGreska
      v-else-if="greska"
      :poruka="greska"
      @pokusaj-ponovno="ucitaj"
    />

    <template v-else-if="trening">
      <!-- Glavna kartica treninga -->
      <div class="trening-glava kartica fade-in">
        <div class="glava-vrh">
          <h1 class="naslov-velik">{{ trening.title }}</h1>
          <StatusBedz
            :status="trening.status"
            :label="trainingStatusLabel[trening.status]"
          />
        </div>

        <div class="meta-mreza">
          <div class="meta-stavka">
            <span class="meta-oznaka tekst-prigusen">Termin</span>
            <span class="meta-vrijednost">{{ formatDateTime(trening.scheduled_at) }}</span>
          </div>
          <div class="meta-stavka">
            <span class="meta-oznaka tekst-prigusen">Trajanje</span>
            <span class="meta-vrijednost">{{ trening.duration_minutes }} min</span>
          </div>
          <div class="meta-stavka">
            <span class="meta-oznaka tekst-prigusen">Trener</span>
            <span class="meta-vrijednost">{{ trening.trainer?.username ?? "—" }}</span>
          </div>
          <div class="meta-stavka">
            <span class="meta-oznaka tekst-prigusen">Popunjenost</span>
            <span class="meta-vrijednost" :class="{ puno: pun }">
              {{ potvrdjene }} / {{ trening.max_capacity }}
            </span>
          </div>
        </div>

        <!-- Akcije za clana -->
        <div v-if="auth.isMember" class="akcije">
          <button
            v-if="mozeRezervirati"
            class="gumb gumb-primarni"
            :disabled="akcijaUTijeku"
            @click="rezerviraj"
          >
            {{ akcijaUTijeku ? "..." : "Rezerviraj mjesto" }}
          </button>
          <button
            v-else-if="mojaRezervacija"
            class="gumb gumb-opasnost"
            :disabled="akcijaUTijeku"
            @click="otkaziRezervaciju(mojaRezervacija.id)"
          >
            Otkaži moju rezervaciju
          </button>
          <p v-else-if="pun && trening.status === 'scheduled'" class="info-tekst tekst-prigusen">
            Trening je popunjen.
          </p>
          <p v-else-if="trening.status !== 'scheduled'" class="info-tekst tekst-prigusen">
            Rezervacije nisu moguće za ovaj status.
          </p>
        </div>

        <!-- Akcije za trenera/admina (promjena statusa) -->
        <div v-if="mozeUpravljati" class="akcije akcije-upravljanje">
          <button
            v-if="trening.status === 'scheduled'"
            class="gumb"
            :disabled="akcijaUTijeku"
            @click="promijeniStatus('start')"
          >
            ▶ Započni
          </button>
          <button
            v-if="trening.status === 'in_progress'"
            class="gumb"
            :disabled="akcijaUTijeku"
            @click="promijeniStatus('complete')"
          >
            ✓ Završi
          </button>
          <button
            v-if="trening.status === 'scheduled' || trening.status === 'in_progress'"
            class="gumb gumb-opasnost"
            :disabled="akcijaUTijeku"
            @click="promijeniStatus('cancel')"
          >
            ✕ Otkaži trening
          </button>
        </div>
      </div>

      <!-- Lista rezervacija -->
      <section class="rezervacije-sekcija">
        <h2 class="sekcija-naslov">
          Rezervacije
          <span class="brojac">{{ potvrdjene }}</span>
        </h2>

        <StanjePrazno
          v-if="rezervacije.length === 0"
          poruka="Još nema rezervacija za ovaj trening."
        />

        <div v-else class="rezervacije-lista kartica">
          <div
            v-for="r in rezervacije"
            :key="r.id"
            class="rezervacija-red"
            :class="{ otkazana: r.status === 'cancelled' }"
          >
            <div class="rez-korisnik">
              <div class="rez-avatar">
                {{ r.user?.username.charAt(0).toUpperCase() ?? "?" }}
              </div>
              <span>{{ r.user?.username ?? "Nepoznat" }}</span>
            </div>
            <div class="rez-desno">
              <StatusBedz
                :status="r.status"
                :label="reservationStatusLabel[r.status]"
              />
              <!-- Otkazivanje: admin/trener mogu otkazati bilo koju, clan samo svoju -->
              <button
                v-if="
                  r.status === 'confirmed' &&
                  (mozeUpravljati || r.user?.id === auth.user?.id)
                "
                class="gumb gumb-mali gumb-opasnost"
                :disabled="akcijaUTijeku"
                @click="otkaziRezervaciju(r.id)"
              >
                Otkaži
              </button>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.natrag {
  display: inline-block;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  transition: var(--tranzicija);
}
.natrag:hover {
  color: var(--boja-akcent);
}
.trening-glava {
  padding: 1.75rem;
  margin-bottom: 2rem;
}
.glava-vrh {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.glava-vrh .naslov-velik {
  font-size: clamp(1.8rem, 4vw, 2.6rem);
}
.meta-mreza {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 1.2rem;
  padding: 1.2rem 0;
  border-top: 1px solid var(--boja-rub);
  border-bottom: 1px solid var(--boja-rub);
}
.meta-stavka {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.meta-oznaka {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.meta-vrijednost {
  font-size: 1.05rem;
  font-weight: 600;
}
.meta-vrijednost.puno {
  color: var(--boja-greska);
}
.akcije {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.3rem;
  flex-wrap: wrap;
}
.akcije-upravljanje {
  margin-top: 0.8rem;
  padding-top: 1.1rem;
  border-top: 1px dashed var(--boja-rub);
}
.info-tekst {
  font-size: 0.9rem;
  font-style: italic;
}
.sekcija-naslov {
  font-size: 1.6rem;
  text-transform: uppercase;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.brojac {
  font-family: var(--font-tekst);
  font-size: 0.85rem;
  font-weight: 700;
  background: var(--boja-akcent);
  color: #fff;
  padding: 0.1rem 0.6rem;
  border-radius: 999px;
}
.rezervacije-lista {
  overflow: hidden;
}
.rezervacija-red {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.2rem;
  border-bottom: 1px solid var(--boja-rub);
}
.rezervacija-red:last-child {
  border-bottom: none;
}
.rezervacija-red.otkazana {
  opacity: 0.5;
}
.rez-korisnik {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  font-weight: 600;
}
.rez-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--boja-povrsina-2);
  border: 1px solid var(--boja-rub);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}
.rez-desno {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
</style>
