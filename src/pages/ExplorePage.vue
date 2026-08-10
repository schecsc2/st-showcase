<template>
  <q-page class="explore-page">
    <section class="explore-hero">
      <h1>Explore</h1>
    </section>

    <q-input
      v-model="search"
      bg-color="white"
      borderless
      class="explore-search"
      dense
      placeholder="Search"
    >
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>

    <section class="explore-grid">
      <div class="neighborhood-list">
        <article
          v-for="neighborhood in filteredNeighborhoods"
          :key="neighborhood.id"
          class="neighborhood-item"
        >
          <q-btn
            :class="{ 'neighborhood-button--active': neighborhood.id === selectedNeighborhoodId }"
            class="neighborhood-button"
            no-caps
            unelevated
            @click="selectedNeighborhoodId = neighborhood.id"
          >
            <span>{{ neighborhood.title }}</span>
            <q-icon :name="neighborhood.id === selectedNeighborhoodId ? 'expand_more' : 'chevron_right'" size="20px" />
          </q-btn>

          <div v-if="neighborhood.id === selectedNeighborhoodId && neighborhood.posters.length" class="poster-list">
            <article v-for="poster in neighborhood.posters" :key="poster.id" class="poster-item">
              <h2>{{ poster.title }}</h2>
              <p>{{ poster.author }}</p>
              <p>{{ poster.description }}</p>
            </article>
          </div>
        </article>
      </div>
    </section>
  </q-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import exploreData from '../../data/sample/explore.json'

const search = ref('')
const selectedNeighborhoodId = ref(null)
const filteredNeighborhoods = computed(() => {
  const query = search.value.trim().toLowerCase()

  if (!query) {
    return exploreData.neighborhoods
  }

  return exploreData.neighborhoods.filter((neighborhood) => {
    return neighborhood.title.toLowerCase().includes(query) || neighborhood.posters.some((poster) => {
      return poster.title.toLowerCase().includes(query) || poster.author.toLowerCase().includes(query)
    })
  })
})
</script>

<style scoped>
.explore-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px 120px;
  color: #1f2933;
}

.explore-hero {
  padding: 20px 0 24px;
}

.explore-hero h1,
.poster-item h2 {
  margin: 0;
  letter-spacing: 0;
}

.explore-hero h1 {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.05;
}

.explore-hero p {
  margin: 12px 0 0;
  color: #5f6b7a;
  font-size: 1.05rem;
}

.explore-search {
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 0 10px;
}

.explore-grid {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}

.neighborhood-list,
.poster-list {
  display: grid;
  gap: 10px;
}

.neighborhood-item {
  display: grid;
  gap: 10px;
}

.neighborhood-button {
  min-height: 52px;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  color: #1f2933;
}

.neighborhood-button :deep(.q-btn__content) {
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  text-align: left;
}

.neighborhood-button--active {
  border-color: #294b75;
  background: #294b75;
  color: #ffffff;
}

.poster-item {
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 14px;
}

.poster-item h2 {
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.25;
}

.poster-item p {
  margin: 4px 0 0;
  color: #5f6b7a;
  line-height: 1.35;
}

@media (min-width: 700px) {
  .explore-page {
    padding: 36px 24px 128px;
  }

  .explore-hero h1 {
    font-size: 3rem;
  }
}

@media (max-width: 420px) {
  .explore-hero h1 {
    font-size: 2rem;
  }
}
</style>
