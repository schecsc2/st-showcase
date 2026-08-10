<template>
  <q-page class="info-page">
    <section class="info-hero">
      <h1>Info</h1>
    </section>

    <section class="info-section">
      <h2>Location</h2>

      <article class="info-card">
        <h3>{{ infoData.location.name }}</h3>
        <p>{{ infoData.location.address }}</p>
        <q-btn
          class="info-action"
          :href="infoData.location.directionsUrl"
          label="Directions"
          no-caps
          target="_blank"
          unelevated
        />
      </article>
    </section>

    <section class="info-section">
      <h2>Arrival</h2>

      <div class="info-list">
        <article v-for="item in infoData.arrival" :key="item.title" class="info-item">
          <div>
            <h3>{{ item.title }}</h3>
            <p>
              <template v-for="(part, index) in getTextParts(item.description)" :key="`${item.title}-${index}`">
                <a v-if="part.url" :href="part.url" target="_blank" rel="noreferrer">{{ part.text }}</a>
                <span v-else>{{ part.text }}</span>
              </template>
            </p>
          </div>
          <div v-if="item.time" class="info-time">{{ item.time }}</div>
        </article>
      </div>
    </section>

    <section class="info-section">
      <h2>FAQ</h2>

      <q-list bordered separator class="faq-list">
        <q-expansion-item
          v-for="faq in infoData.faqs"
          :key="faq.question"
          :label="faq.question"
          expand-icon="keyboard_arrow_down"
        >
          <div class="faq-answer">
            <p>
              <template v-for="(part, index) in getTextParts(faq.answer)" :key="`${faq.question}-${index}`">
                <a v-if="part.url" :href="part.url" target="_blank" rel="noreferrer">{{ part.text }}</a>
                <span v-else>{{ part.text }}</span>
              </template>
            </p>
          </div>
        </q-expansion-item>
      </q-list>
    </section>

  </q-page>
</template>

<script setup>
import infoData from '../../data/sample/info.json'

function getTextParts(text) {
  const parts = []
  const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g
  let lastIndex = 0
  let match = linkPattern.exec(text)

  while (match) {
    if (match.index > lastIndex) {
      parts.push({
        text: text.slice(lastIndex, match.index)
      })
    }

    parts.push({
      text: match[1],
      url: match[2]
    })

    lastIndex = match.index + match[0].length
    match = linkPattern.exec(text)
  }

  if (lastIndex < text.length) {
    parts.push({
      text: text.slice(lastIndex)
    })
  }

  return parts
}
</script>

<style scoped>
.info-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px 120px;
  color: #1f2933;
}

.info-hero {
  padding: 20px 0 8px;
}

.info-hero h1,
.info-section h2,
.info-item h3,
.info-card h3 {
  margin: 0;
  letter-spacing: 0;
}

.info-hero h1 {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.05;
}

.info-hero p {
  margin: 12px 0 0;
  color: #5f6b7a;
  font-size: 1.05rem;
}

.info-section {
  padding: 16px 0 0;
}

.info-section h2 {
  font-size: 1.25rem;
  font-weight: 800;
}

.info-list {
  display: grid;
  gap: 10px;
  margin-top: 8px;
}

.info-item,
.info-card {
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 14px;
}

.info-item {
  display: flex;
  gap: 14px;
  align-items: center;
  justify-content: space-between;
}

.info-item h3,
.info-card h3 {
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.25;
}

.info-item p,
.info-card p,
.faq-answer p {
  margin: 4px 0 0;
  color: #5f6b7a;
  line-height: 1.35;
}

.info-time {
  flex: 0 0 auto;
  color: #005ea8;
  font-weight: 800;
  text-align: right;
}

.info-action {
  margin-top: 12px;
  background: #294b75;
  color: #ffffff;
}

.faq-list {
  margin-top: 8px;
  border-color: #dde3ea;
  border-radius: 8px;
  background: #ffffff;
}

.faq-answer {
  padding: 0 16px 16px;
}

.info-item a,
.faq-answer a {
  color: #294b75;
  font-weight: 700;
}

@media (min-width: 700px) {
  .info-page {
    padding: 36px 24px 128px;
  }

  .info-hero h1 {
    font-size: 3rem;
  }
}

@media (max-width: 420px) {
  .info-hero h1 {
    font-size: 2rem;
  }

  .info-item {
    display: grid;
  }

  .info-time {
    text-align: left;
  }
}
</style>
