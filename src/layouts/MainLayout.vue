<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <router-view />
    </q-page-container>

    <nav class="bottom-nav" aria-label="Primary">
      <q-btn
        v-for="link in navLinks"
        :key="link.title"
        class="bottom-nav__button"
        no-caps
        unelevated
        @click="navigateTo(link)"
      >
        <q-icon :name="link.icon" size="20px" />
        <span>{{ link.title }}</span>
      </q-btn>
    </nav>
  </q-layout>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navLinks = [
  {
    title: 'Home',
    icon: 'home',
    route: '/'
  },
  {
    title: 'Agenda',
    icon: 'event_note',
    route: '/agenda'
  },
  {
    title: 'Map',
    icon: 'map',
    route: '/map'
  },
  {
    title: 'Explore',
    icon: 'explore',
    route: '/explore'
  },
  {
    title: 'Info',
    icon: 'info',
    route: '/info'
  }
]

async function navigateTo(link) {
  await router.push(link.route)
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  right: 16px;
  bottom: calc(16px + env(safe-area-inset-bottom));
  left: 16px;
  z-index: 1000;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  max-width: 480px;
  margin: 0 auto;
}

.bottom-nav__button {
  min-width: 0;
  min-height: 58px;
  padding: 4px;
  border: 0;
  border-radius: 8px;
  background: #294b75;
  color: #ffffff;
  font-size: 0.75rem;
  opacity: 1;
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.24);
}

.bottom-nav__button :deep(.q-btn__content) {
  flex-direction: column;
  gap: 4px;
  line-height: 1;
}
</style>
