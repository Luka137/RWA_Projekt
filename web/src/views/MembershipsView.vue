<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { membershipService } from "@/services/membership.service";
import { userService } from "@/services/user.service";
import { useToastStore } from "@/stores/toast";
import { extractErrorMessage } from "@/services/api";
import {
  formatDate,
  membershipStatusLabel,
  isMembershipActive,
} from "@/utils/format";
import type { Membership, User, MembershipCreatePayload } from "@/types";
import StanjeUcitavanje from "@/components/StanjeUcitavanje.vue";
import StanjeGreska from "@/components/StanjeGreska.vue";
import StanjePrazno from "@/components/StanjePrazno.vue";
import StatusBedz from "@/components/StatusBedz.vue";
import Modal from "@/components/Modal.vue";

const auth = useAuthStore();
const toast = useToastStore();

const clanarine = ref<Membership[]>([]);
const korisnici = ref<User[]>([]); // za admin dropdown
const ucitavanje = ref(true);
const greska = ref("");

const modalOtvoren = ref(false);
const spremanje = ref(false);
const formaGreska = ref("");

// Defaultni datumi: danas + mjesec dana
function danasISO(): string {
  return new Date().toISOString().slice(0, 10);
}
function zaMjesecDana(): string {
  const d = new Date();
  d.setMonth(d.getMonth() + 1);
  return d.toISOString().slice(0, 10);
}

const forma = ref<MembershipCreatePayload>({
  user_id: 0,
  start_date: danasISO(),
  end_date: zaMjesecDana(),
});

async function ucitaj() {
  ucitavanje.value = true;
  greska.value = "";
  try {
    clanarine.value = await membershipService.list();
  } catch (e) {
    greska.value = extractErrorMessage(e, "Greška pri učitavanju članarina.");
  } finally {
    ucitavanje.value = false;
  }
}

async function otvoriModal() {
  formaGreska.value = "";
  forma.value = {
    user_id: 0,
    start_date: danasISO(),
    end_date: zaMjesecDana(),
  };
  modalOtvoren.value = true;
  // Dohvati listu korisnika za odabir (admin only endpoint)
  if (korisnici.value.length === 0) {
    try {
      korisnici.value = await userService.list();
    } catch {
      // ako padne, ostavi prazno - admin moze rucno upisati ID
    }
  }
}

async function kreiraj() {
  formaGreska.value = "";

  if (!forma.value.user_id || forma.value.user_id <= 0) {
    formaGreska.value = "Odaberite korisnika.";
    return;
  }
  if (new Date(forma.value.end_date) <= new Date(forma.value.start_date)) {
    formaGreska.value = "Datum isteka mora biti nakon datuma početka.";
    return;
  }

  spremanje.value = true;
  try {
    await membershipService.create(forma.value);
    toast.success("Članarina je kreirana.");
    modalOtvoren.value = false;
    await ucitaj();
  } catch (e) {
    formaGreska.value = extractErrorMessage(e, "Kreiranje nije uspjelo.");
  } finally {
    spremanje.value = false;
  }
}

async function otkazi(id: number) {
  try {
    await membershipService.cancel(id);
    toast.success("Članarina otkazana.");
    await ucitaj();
  } catch (e) {
    toast.error(extractErrorMessage(e, "Otkazivanje nije uspjelo."));
  }
}

onMounted(ucitaj);
</script>

<template>
  <div class="clanarine">
    <header class="zaglavlje">
      <div>
        <h1 class="naslov-velik">Članarine</h1>
        <p class="tekst-prigusen">
          {{ auth.isAdmin ? "Sve članarine u sustavu" : "Vaše članstvo" }}
        </p>
      </div>
      <button v-if="auth.isAdmin" class="gumb gumb-primarni" @click="otvoriModal">
        + Nova članarina
      </button>
    </header>

    <StanjeUcitavanje v-if="ucitavanje" poruka="Učitavanje članarina..." />

    <StanjeGreska v-else-if="greska" :poruka="greska" @pokusaj-ponovno="ucitaj" />

    <StanjePrazno
      v-else-if="clanarine.length === 0"
      :poruka="
        auth.isAdmin
          ? 'Nema kreiranih članarina.'
          : 'Nemate aktivnu članarinu. Obratite se administratoru.'
      "
    />

    <div v-else class="lista">
      <article
        v-for="m in clanarine"
        :key="m.id"
        class="clanarina-kartica kartica fade-in"
      >
        <div class="kartica-vrh">
          <div class="period">
            <span class="period-oznaka tekst-prigusen">Period</span>
            <span class="period-datumi">
              {{ formatDate(m.start_date) }} — {{ formatDate(m.end_date) }}
            </span>
          </div>
          <StatusBedz
            :status="isMembershipActive(m.status, m.end_date) ? 'active' : m.status === 'cancelled' ? 'cancelled' : 'completed'"
            :label="
              isMembershipActive(m.status, m.end_date)
                ? 'Aktivna'
                : m.status === 'cancelled'
                  ? membershipStatusLabel.cancelled
                  : 'Istekla'
            "
          />
        </div>

        <div class="kartica-dno">
          <span v-if="auth.isAdmin" class="korisnik-id tekst-prigusen">
            Korisnik ID: {{ m.user_id }}
          </span>
          <span v-else></span>
          <button
            v-if="m.status === 'active'"
            class="gumb gumb-mali gumb-opasnost"
            @click="otkazi(m.id)"
          >
            Otkaži
          </button>
        </div>
      </article>
    </div>

    <!-- Modal za kreiranje clanarine (admin) -->
    <Modal v-if="modalOtvoren" naslov="Nova članarina" @zatvori="modalOtvoren = false">
      <form @submit.prevent="kreiraj">
        <div class="polje">
          <label for="user">Korisnik</label>
          <select
            v-if="korisnici.length > 0"
            id="user"
            v-model.number="forma.user_id"
            :disabled="spremanje"
          >
            <option :value="0" disabled>— odaberite korisnika —</option>
            <option v-for="u in korisnici" :key="u.id" :value="u.id">
              {{ u.username }} ({{ u.role }})
            </option>
          </select>
          <input
            v-else
            id="user"
            v-model.number="forma.user_id"
            type="number"
            min="1"
            placeholder="ID korisnika"
            :disabled="spremanje"
          />
        </div>

        <div class="red-polja">
          <div class="polje">
            <label for="start">Početak</label>
            <input
              id="start"
              v-model="forma.start_date"
              type="date"
              :disabled="spremanje"
            />
          </div>
          <div class="polje">
            <label for="end">Istek</label>
            <input
              id="end"
              v-model="forma.end_date"
              type="date"
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.1rem;
}
.clanarina-kartica {
  padding: 1.3rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.kartica-vrh {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}
.period {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.period-oznaka {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.period-datumi {
  font-size: 1.05rem;
  font-weight: 600;
}
.kartica-dno {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.8rem;
  border-top: 1px solid var(--boja-rub);
  font-size: 0.85rem;
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
