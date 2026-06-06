<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>

<template>
  <div class="not-found fade-in">
    <span class="kod">404</span>
    <h1>Stranica nije pronađena</h1>
    <p class="tekst-prigusen">
      Tražena stranica ne postoji ili je premještena.
    </p>
    <RouterLink :to="{ name: 'dashboard' }" class="gumb gumb-primarni">
      Natrag na početnu
    </RouterLink>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.8rem;
  padding: 4rem 1rem;
  min-height: 50vh;
}
.kod {
  font-family: var(--font-naslov);
  font-size: clamp(5rem, 18vw, 9rem);
  line-height: 0.9;
  color: var(--boja-akcent);
  letter-spacing: 4px;
}
h1 {
  font-size: 1.8rem;
  text-transform: uppercase;
}
.gumb {
  margin-top: 1rem;
}
</style>
