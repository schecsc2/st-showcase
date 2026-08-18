<template>
  <q-page class="home-page">
    <section class="home-hero">
      <img class="home-logo" :src="logo" alt="2026 APL S&T Showcase">
      <div class="event-date">{{ eventDate }}</div>
      <p>Johns Hopkins APL South Campus</p>
    </section>

    <section class="status-grid">
      <article class="status-panel status-panel--now">
        <q-chip class="panel-chip" dense square>Happening Now</q-chip>
        <h2>{{ happeningNow.title }}</h2>
        <div class="panel-meta">{{ happeningNow.time }}</div>
        <div class="panel-location">{{ happeningNow.location }}</div>
      </article>

      <article class="status-panel status-panel--next">
        <q-chip class="panel-chip" dense square>Up Next</q-chip>
        <h2>{{ upNext.title }}</h2>
        <div class="panel-meta">{{ upNext.time }}</div>
        <div class="panel-location">{{ upNext.location }}</div>
      </article>
    </section>

    <div class="home-footer">
      <img class="apl-logo" :src="aplLogo" alt="Johns Hopkins Applied Physics Laboratory">
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import logo from '../../data/live/logos/logo-transparent.png'
import aplLogo from '../../data/live/logos/apl_small_horizontal_blue.png'
import agendaData from '../../data/sample/agenda.json'

const eventDate = agendaData.eventDate
const eventDay = agendaData.eventDay
const agenda = agendaData.sessions.flatMap((session) => session.items)
const now = ref(new Date())
const firstAgendaTime = getEventTime(agenda[0].start)
const lastSession = agendaData.sessions[agendaData.sessions.length - 1]
const lastAgendaTime = getEventTime(lastSession.end)
let timer
const currentAgendaItem = computed(() => {
  return agenda.find((item) => {
    return item.end && now.value >= getEventTime(item.start) && now.value < getEventTime(item.end)
  })
})
const nextAgendaItem = computed(() => {
  return agenda.find((item) => now.value < getEventTime(item.start))
})
const happeningNow = computed(() => {
  return currentAgendaItem.value || getDefaultHappeningNow()
})
const upNext = computed(() => {
  return nextAgendaItem.value || {
    title: 'Event Complete',
    time: '4:00 PM',
    location: 'Johns Hopkins APL South Campus'
  }
})

onMounted(() => {
  timer = window.setInterval(() => {
    now.value = new Date()
  }, 30000)
})

onUnmounted(() => {
  window.clearInterval(timer)
})

function getEventTime(time) {
  return new Date(`${eventDay}T${time}:00`)
}

function getDefaultHappeningNow() {
  if (now.value < firstAgendaTime) {
    return {
      title: 'Starts September 15',
      time: '8:30 AM',
      location: 'Johns Hopkins APL South Campus'
    }
  }

  if (now.value > lastAgendaTime) {
    return {
      title: 'Event Complete',
      time: '4:00 PM',
      location: 'Johns Hopkins APL South Campus'
    }
  }

  return {
    title: 'Session Break',
    time: '12:00 PM - 1:00 PM',
    location: 'South Campus'
  }
}
</script>

<style scoped>
.home-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px 120px;
  color: #1f2933;
}

.home-hero {
  padding: 20px 0 24px;
}

.event-date {
  margin-top: 12px;
  color: #1f2933;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0;
}

.home-section h2,
.status-panel h2 {
  margin: 0;
  letter-spacing: 0;
}

.home-logo {
  display: block;
  width: min(100%, 300px);
  height: auto;
}

.home-hero p {
  margin: 12px 0 0;
  color: #5f6b7a;
  font-size: 1.05rem;
}

.status-grid {
  display: grid;
  gap: 12px;
}

.status-panel {
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.panel-chip {
  margin: 0;
  background: #79a9ff;
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 700;
}

.status-panel--now .panel-chip {
  background: #2e7d32;
}

.status-panel--next .panel-chip {
  background: #ef7d00;
}

.status-panel h2 {
  margin-top: 8px;
  font-size: 1.25rem;
  font-weight: 800;
  line-height: 1.2;
}

.panel-meta,
.panel-location {
  margin-top: 8px;
  color: #4c5968;
}

.panel-meta {
  font-weight: 700;
}

.home-footer {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.apl-logo {
  width: min(100%, 300px);
  height: auto;
}

@media (min-width: 700px) {
  .home-page {
    padding: 36px 24px 128px;
  }

  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
