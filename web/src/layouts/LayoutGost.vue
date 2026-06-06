<script setup lang="ts">
// Layout za neprijavljene korisnike (login, register).
// Centriran sadrzaj, bez navigacije.
</script>

<template>
  <div class="gost-layout">
    <div class="gost-sadrzaj">
      <div class="brend">
        <span class="logo-ikona">⬣</span>
        <span class="logo-tekst">IRON GYM</span>
      </div>
      <slot />
    </div>
    <div class="gost-pozadina"></div>
  </div>
</template>

<style scoped>
.gost-layout {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  position: relative;
}
.gost-sadrzaj {
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 2;
}
.brend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-bottom: 1.75rem;
}
.logo-ikona {
  color: var(--boja-akcent);
  font-size: 1.8rem;
}
.logo-tekst {
  font-family: var(--font-naslov);
  font-size: 2rem;
  letter-spacing: 2px;
}
.gost-pozadina {
  position: fixed;
  inset: 0;
  z-index: 1;
  background-image:
    linear-gradient(rgba(43, 47, 55, 0.4) 1px, transparent 1px),
    linear-gradient(90deg, rgba(43, 47, 55, 0.4) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(circle at center, black, transparent 75%);
  opacity: 0.5;
}
</style>
