<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { trainingService } from "@/services/training.service";
import { useToastStore } from "@/stores/toast";
import { extractErrorMessage } from "@/services/api";
import {
  formatDateTime,
  trainingStatusLabel,
  toDatetimeLocal,
  fromDatetimeLocal,
} from "@/utils/format";
import type { Training, TrainingCreatePayload } from "@/types";
import StanjeUcitavanje from "@/components/StanjeUcitavanje.vue";
import StanjeGreska from "@/components/StanjeGreska.vue";
import StanjePrazno from "@/components/StanjePrazno.vue";
import StatusBedz from "@/components/StatusBedz.vue";
import Modal from "@/components/Modal.vue";

const auth = useAuthStore();
const router = useRouter();
const toast = useToastStore();

const treninzi = ref<Training[]>([]);
const ucitavanje = ref(true);
const greska = ref("");

// Modal za kreiranje
const modalOtvoren = ref(false);
const spremanje = ref(false);
const formaGreska = ref("");
const forma = ref<TrainingCreatePayload & { scheduled_local: string }>({
  title: "",
  scheduled_at: "",
  scheduled_local: toDatetimeLocal(),
  duration_minutes: 60,
  max_capacity: 10,
});

async function ucitaj() {
  ucitavanje.value = true;
  greska.value = "";
  try {
    treninzi.value = await trainingService.list();
  } catch (e) {
    greska.value = extractErrorMessage(e, "Greška pri učitavanju treninga.");
  } finally {
    ucitavanje.value = false;
  }
}

function otvoriModal() {
  forma.value = {
    title: "",
    scheduled_at: "",
    scheduled_local: toDatetimeLocal(),
    duration_minutes: 60,
    max_capacity: 10,
  };
  formaGreska.value = "";
  modalOtvoren.value = true;
}

async function kreiraj() {
  formaGreska.value = "";

  // Klijentska validacija
  if (forma.value.title.trim().length < 3) {
    formaGreska.value = "Naziv mora imati barem 3 znaka.";
    return;
  }
  if (!forma.value.scheduled_local) {
    formaGreska.value = "Odaberite datum i vrijeme.";
    return;
  }
  if (new Date(forma.value.scheduled_local) <= new Date()) {
    formaGreska.value = "Termin mora biti u budućnosti.";
    return;
  }
  if (forma.value.duration_minutes <= 0) {
    formaGreska.value = "Trajanje mora biti veće od 0.";
    return;
  }
  if (forma.value.max_capacity <= 0) {
    formaGreska.value = "Kapacitet mora biti veći od 0.";
    return;
  }

  spremanje.value = true;
  try {
    await trainingService.create({
      title: forma.value.title.trim(),
      scheduled_at: fromDatetimeLocal(forma.value.scheduled_local),
      duration_minutes: forma.value.duration_minutes,
      max_capacity: forma.value.max_capacity,
    });
    toast.success("Trening je kreiran.");
    modalOtvoren.value = false;
    await ucitaj();
  } catch (e) {
    formaGreska.value = extractErrorMessage(e, "Kreiranje nije uspjelo.");
  } finally {
    spremanje.value = false;
  }
}

function otvoriDetalje(id: number) {
  router.push({ name: "training-detail", params: { id } });
}

onMounted(ucitaj);
</script>

<template>
  <div class="treninzi">
    <header class="zaglavlje">
      <div>
        <h1 class="naslov-velik">Treninzi</h1>
        <p class="tekst-prigusen">Pregled svih termina treninga</p>
      </div>
      <button
        v-if="auth.isAdmin || auth.isTrainer"
        class="gumb gumb-primarni"
        @click="otvoriModal"
      >
        + Novi trening
      </button>
    </header>

    <StanjeUcitavanje v-if="ucitavanje" poruka="Učitavanje treninga..." />

    <StanjeGreska
      v-else-if="greska"
      :poruka="greska"
      @pokusaj-ponovno="ucitaj"
    />

    <StanjePrazno
      v-else-if="treninzi.length === 0"
      poruka="Trenutno nema zakazanih treninga."
    >
      <button
        v-if="auth.isAdmin || auth.isTrainer"
        class="gumb gumb-mali"
        @click="otvoriModal"
      >
        Kreiraj prvi trening
      </button>
    </StanjePrazno>

    <div v-else class="lista">
      <article
        v-for="t in treninzi"
        :key="t.id"
        class="trening-kartica kartica fade-in"
        @click="otvoriDetalje(t.id)"
      >
        <div class="kartica-vrh">
          <h3>{{ t.title }}</h3>
          <StatusBedz :status="t.status" :label="trainingStatusLabel[t.status]" />
        </div>
        <div class="kartica-detalji">
          <span class="detalj">📅 {{ formatDateTime(t.scheduled_at) }}</span>
          <span class="detalj">⏱ {{ t.duration_minutes }} min</span>
          <span class="detalj">👥 max {{ t.max_capacity }}</span>
        </div>
        <div class="kartica-dno">
          <span class="trener tekst-prigusen">
            Trener: {{ t.trainer?.username ?? "—" }}
          </span>
          <span class="strelica">→</span>
        </div>
      </article>
    </div>

    <!-- Modal za kreiranje treninga -->
    <Modal
      v-if="modalOtvoren"
      naslov="Novi trening"
      @zatvori="modalOtvoren = false"
    >
      <form @submit.prevent="kreiraj">
        <div class="polje">
          <label for="title">Naziv treninga</label>
          <input
            id="title"
            v-model="forma.title"
            type="text"
            placeholder="npr. Jutarnja kardio sesija"
            :disabled="spremanje"
          />
        </div>

        <div class="polje">
          <label for="scheduled">Datum i vrijeme</label>
          <input
            id="scheduled"
            v-model="forma.scheduled_local"
            type="datetime-local"
            :disabled="spremanje"
          />
        </div>

        <div class="red-polja">
          <div class="polje">
            <label for="duration">Trajanje (min)</label>
            <input
              id="duration"
              v-model.number="forma.duration_minutes"
              type="number"
              min="1"
              :disabled="spremanje"
            />
          </div>
          <div class="polje">
            <label for="capacity">Maks. kapacitet</label>
            <input
              id="capacity"
              v-model.number="forma.max_capacity"
              type="number"
              min="1"
              :disabled="spremanje"
            />
          </div>
        </div>

        <p v-if="formaGreska" class="poruka-greska">{{ formaGreska }}</p>

        <div class="modal-akcije">
          <button
            type="button"
            class="gumb"
            :disabled="spremanje"
            @click="modalOtvoren = false"
          >
            Odustani
          </button>
          <button type="submit" class="gumb gumb-primarni" :disabled="spremanje">
            {{ spremanje ? "Spremanje..." : "Kreiraj" }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<style scoped>
.zaglavlje {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
}
.naslov-velik {
  font-size: clamp(2rem, 4vw, 2.8rem);
}
.lista {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.1rem;
}
.trening-kartica {
  padding: 1.3rem;
  cursor: pointer;
  transition: var(--tranzicija);
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}
.trening-kartica:hover {
  border-color: var(--boja-akcent);
  transform: translateY(-3px);
  box-shadow: var(--sjena-jaka);
}
.kartica-vrh {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}
.kartica-vrh h3 {
  font-size: 1.35rem;
  text-transform: uppercase;
  line-height: 1.1;
}
.kartica-detalji {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
}
.kartica-dno {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.7rem;
  border-top: 1px solid var(--boja-rub);
  font-size: 0.85rem;
}
.strelica {
  color: var(--boja-akcent);
  font-size: 1.1rem;
}
.red-polja {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
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
.modal-akcije {
  display: flex;
  gap: 0.7rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
</style>
