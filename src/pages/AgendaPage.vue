<template>
  <q-page class="agenda-page">
    <section class="agenda-hero">
      <h1>Agenda</h1>
    </section>

    <section v-for="session in agendaData.sessions" :key="session.id" class="agenda-section">
      <div class="session-heading">
        <div>
          <h2>{{ session.title }}</h2>
          <p>{{ session.audience }}</p>
        </div>
        <div class="session-time">{{ session.time }}</div>
      </div>

      <q-timeline color="dark" layout="dense" class="agenda-timeline">
        <q-timeline-entry
          v-for="item in session.items"
          :key="`${session.id}-${item.start}-${item.title}`"
          :title="item.title"
          :subtitle="item.time"
        >
          <p v-if="item.location">{{ item.location }}</p>
        </q-timeline-entry>
      </q-timeline>
    </section>
  </q-page>
</template>

<script setup>
import agendaData from '../../data/sample/agenda.json'
</script>

<style scoped>
.agenda-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px 120px;
  color: #1f2933;
}

.agenda-hero {
  padding: 20px 0 8px;
}

.event-date {
  margin-top: 12px;
  color: #1f2933;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0;
}

.agenda-hero h1,
.agenda-section h2 {
  margin: 0;
  letter-spacing: 0;
}

.agenda-hero h1 {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.05;
}

.agenda-hero p {
  margin: 12px 0 0;
  color: #5f6b7a;
  font-size: 1.05rem;
}

.agenda-section {
  padding: 16px 0 0;
}

.session-heading {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
}

.session-heading h2 {
  font-size: 1.25rem;
  font-weight: 800;
}

.session-heading p {
  margin: 4px 0 0;
  color: #5f6b7a;
}

.session-time {
  flex: 0 0 auto;
  color: #1f2933;
  font-weight: 800;
  text-align: right;
}

.agenda-timeline {
  margin-top: 8px;
}

.agenda-timeline :deep(.q-timeline__dot) {
  color: #79a9ff !important;
}

.agenda-timeline :deep(.q-timeline__dot:before),
.agenda-timeline :deep(.q-timeline__dot:after) {
  background: #79a9ff;
}

.agenda-timeline :deep(.q-timeline__dot:after) {
  opacity: 1;
}

.agenda-timeline :deep(.q-timeline__subtitle) {
  color: #1f2933;
  font-weight: 800;
  opacity: 1;
}

.agenda-timeline :deep(.q-timeline__title) {
  color: #1f2933;
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.25;
}

.agenda-timeline p {
  margin: 4px 0 0;
  color: #5f6b7a;
  line-height: 1.35;
}

@media (min-width: 700px) {
  .agenda-page {
    padding: 36px 24px 128px;
  }

  .agenda-hero h1 {
    font-size: 3rem;
  }
}

@media (max-width: 420px) {
  .agenda-hero h1 {
    font-size: 2rem;
  }

  .session-heading {
    display: grid;
  }

  .session-time {
    text-align: left;
  }
}
</style>
