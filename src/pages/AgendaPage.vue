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
          <q-btn
            v-if="hasAgendaSpeakers(item)"
            class="speaker-button"
            dense
            flat
            no-caps
            @click="showSpeakers(item)"
          >
            About Speakers
          </q-btn>
        </q-timeline-entry>
      </q-timeline>
    </section>

    <q-dialog v-model="speakerDialogOpen">
      <q-card class="speaker-dialog">
        <q-card-section class="speaker-dialog__section">
          <div class="speaker-dialog__title">Speakers</div>
          <q-btn
            v-close-popup
            class="speaker-dialog__close"
            dense
            flat
            icon="close"
            round
          />
        </q-card-section>

        <q-card-section class="speaker-dialog__section speaker-dialog__body">
          <article
            v-for="speaker in activeSpeakers"
            :key="speaker.name"
            class="speaker-dialog__speaker"
          >
            <div class="speaker-dialog__header">
              <img class="speaker-dialog__image" :src="speaker.image" :alt="speaker.name">
              <div>
                <div class="speaker-dialog__label">{{ speaker.label }}</div>
                <h2>{{ speaker.name }}</h2>
              </div>
            </div>
            <p v-for="paragraph in speaker.paragraphs" :key="paragraph">{{ paragraph }}</p>
          </article>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import agendaData from '../../data/sample/agenda.json'
import speakersText from '../../data/event_content/speakers.md?raw'
import davidVanWieImage from '../../data/live/images/dr-david-van-wie.jpg'
import joanHoffmannImage from '../../data/live/images/dr-joan-hoffmann.jpg'
import davidGoldfeinImage from '../../data/live/images/gen-david-goldfein.jpg'

const activeSpeakers = ref([])
const speakerDialogOpen = ref(false)
const speakerImages = {
  'Dr. David Van Wie': davidVanWieImage,
  'Dr. Joan Hoffmann': joanHoffmannImage,
  'Gen. David L. Goldfein': davidGoldfeinImage
}
const speakers = parseSpeakerContent(speakersText)
const speakersByAgendaTitle = {
  'Welcome & Opening Remarks': ['Welcome Speaker', 'Opening Remarks'],
  'Feature Conversation with Gen. David Goldfein': ['Featured Speaker']
}

function parseSpeakerContent(text) {
  const sections = []
  let section = null

  text.split('\n').forEach((line) => {
    const value = line.trim()

    if (!value || value === 'Speakers') {
      return
    }

    if (value.includes(' | ')) {
      const parts = value.split(' | ')

      section = {
        label: parts[0],
        name: parts[1],
        image: speakerImages[parts[1]],
        paragraphs: []
      }
      sections.push(section)
      return
    }

    if (section) {
      section.paragraphs.push(value)
    }
  })

  return sections
}

function getAgendaSpeakers(item) {
  const labels = speakersByAgendaTitle[item.title] || []

  return labels.map((label) => speakers.find((speaker) => speaker.label === label)).filter(Boolean)
}

function hasAgendaSpeakers(item) {
  return getAgendaSpeakers(item).length > 0
}

function showSpeakers(item) {
  activeSpeakers.value = getAgendaSpeakers(item)
  speakerDialogOpen.value = true
}
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

.speaker-button {
  margin-top: 8px;
  background: #79a9ff;
  color: #ffffff;
  font-weight: 800;
}

.speaker-dialog {
  position: relative;
  width: calc(100vw - 32px);
  max-width: 560px;
  max-height: 67vh;
  border-radius: 8px;
}

.speaker-dialog__section {
  padding: 14px 16px;
}

.speaker-dialog__body {
  display: grid;
  gap: 16px;
  max-height: calc(67vh - 112px);
  overflow-y: auto;
  padding-top: 0;
}

.speaker-dialog__title,
.speaker-dialog__speaker h2 {
  margin: 0;
  color: #1f2933;
  letter-spacing: 0;
}

.speaker-dialog__title {
  font-size: 1.25rem;
  font-weight: 800;
}

.speaker-dialog__close {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #1f2933;
}

.speaker-dialog__label {
  color: #294b75;
  font-size: 0.82rem;
  font-weight: 800;
}

.speaker-dialog__header {
  display: flex;
  gap: 12px;
  align-items: center;
}

.speaker-dialog__image {
  width: 64px;
  height: 64px;
  flex: 0 0 auto;
  border-radius: 50%;
  object-fit: cover;
}

.speaker-dialog__speaker h2 {
  margin-top: 2px;
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.25;
}

.speaker-dialog__speaker p {
  margin: 6px 0 0;
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
