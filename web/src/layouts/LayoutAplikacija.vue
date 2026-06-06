<script setup lang="ts">
import { ref } from "vue";
import { useRouter, RouterLink, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { roleLabel } from "@/utils/format";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const mobilniMeniOtvoren = ref(false);

function odjava() {
  auth.logout();
  router.push({ name: "login" });
}

// Stavke navigacije; neke su vidljive samo odredenim rolama.
const stavke = [
  { name: "dashboard", label: "Nadzorna ploča", ikona: "▦" },
  { name: "trainings", label: "Treninzi", ikona: "🏋" },
  { name: "memberships", label: "Članarine", ikona: "🎟" },
];
</script>

<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ otvoren: mobilniMeniOtvoren }">
      <div class="sidebar-brend">
        <span class="logo-ikona">⬣</span>
        <span class="logo-tekst">IRON GYM</span>
      </div>

      <nav class="sidebar-nav">
        <RouterLink
          v-for="s in stavke"
          :key="s.name"
          :to="{ name: s.name }"
          class="nav-link"
          @click="mobilniMeniOtvoren = false"
        >
          <span class="nav-ikona">{{ s.ikona }}</span>
          {{ s.label }}
        </RouterLink>

        <!-- Admin-only stavka -->
        <RouterLink
          v-if="auth.isAdmin"
          :to="{ name: 'admin-users' }"
          class="nav-link"
          @click="mobilniMeniOtvoren = false"
        >
          <span class="nav-ikona">👥</span>
          Korisnici
        </RouterLink>
      </nav>

      <div class="sidebar-korisnik">
        <div class="korisnik-info">
          <div class="avatar">{{ auth.user?.username.charAt(0).toUpperCase() }}</div>
          <div class="korisnik-tekst">
            <span class="korisnik-ime">{{ auth.user?.username }}</span>
            <span class="korisnik-uloga tekst-prigusen">
              {{ auth.role ? roleLabel[auth.role] : "" }}
            </span>
          </div>
        </div>
        <button class="gumb gumb-mali odjava-gumb" @click="odjava">
          Odjava
        </button>
      </div>
    </aside>

    <!-- Glavni sadrzaj -->
    <div class="glavni-dio">
      <header class="topbar">
        <button
          class="hamburger"
          @click="mobilniMeniOtvoren = !mobilniMeniOtvoren"
          aria-label="Izbornik"
        >
          ☰
        </button>
        <span class="topbar-ruta">{{ route.meta.layout ? "" : "" }}</span>
      </header>

      <main class="sadrzaj">
        <slot />
      </main>
    </div>

    <!-- Overlay za mobilni meni -->
    <div
      v-if="mobilniMeniOtvoren"
      class="mobilni-overlay"
      @click="mobilniMeniOtvoren = false"
    ></div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  width: 250px;
  flex-shrink: 0;
  background: var(--boja-povrsina);
  border-right: 1px solid var(--boja-rub);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
}
.sidebar-brend {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1.4rem 1.3rem;
  border-bottom: 1px solid var(--boja-rub);
}
.logo-ikona {
  color: var(--boja-akcent);
  font-size: 1.5rem;
}
.logo-tekst {
  font-family: var(--font-naslov);
  font-size: 1.6rem;
  letter-spacing: 1.5px;
}
.sidebar-nav {
  flex: 1;
  padding: 1rem 0.7rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.9rem;
  border-radius: var(--radius);
  color: var(--boja-tekst-prigusen);
  font-weight: 600;
  font-size: 0.92rem;
  transition: var(--tranzicija);
}
.nav-link:hover {
  background: var(--boja-povrsina-2);
  color: var(--boja-tekst);
}
.nav-link.router-link-active {
  background: var(--boja-povrsina-2);
  color: var(--boja-akcent);
  box-shadow: inset 3px 0 0 var(--boja-akcent);
}
.nav-ikona {
  font-size: 1.05rem;
  width: 1.3rem;
  text-align: center;
}
.sidebar-korisnik {
  padding: 1rem;
  border-top: 1px solid var(--boja-rub);
}
.korisnik-info {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.8rem;
}
.avatar {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--boja-akcent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}
.korisnik-tekst {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  overflow: hidden;
}
.korisnik-ime {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.korisnik-uloga {
  font-size: 0.78rem;
}
.odjava-gumb {
  width: 100%;
}

/* Glavni dio */
.glavni-dio {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.topbar {
  display: none;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  background: var(--boja-povrsina);
  border-bottom: 1px solid var(--boja-rub);
  position: sticky;
  top: 0;
  z-index: 50;
}
.hamburger {
  background: none;
  border: 1px solid var(--boja-rub);
  border-radius: var(--radius);
  color: var(--boja-tekst);
  font-size: 1.2rem;
  padding: 0.3rem 0.6rem;
}
.sadrzaj {
  padding: 2rem;
  flex: 1;
  max-width: 1200px;
  width: 100%;
}

.mobilni-overlay {
  display: none;
}

/* Responzivno */
@media (max-width: 860px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }
  .sidebar.otvoren {
    transform: translateX(0);
  }
  .topbar {
    display: flex;
  }
  .mobilni-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: 90;
  }
  .sadrzaj {
    padding: 1.25rem;
  }
}
</style>
