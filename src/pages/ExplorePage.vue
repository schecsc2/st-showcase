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
      <div v-if="search.trim()" class="poster-list">
        <article v-for="result in posterSearchResults" :key="result.poster.id" class="poster-item">
          <q-chip class="poster-neighborhood-chip" dense square>
            {{ result.neighborhood.title }}
          </q-chip>
          <h2>{{ result.poster.title }}</h2>
          <p>{{ result.poster.authors }}</p>
          <p>{{ result.poster.description }}</p>
          <q-btn
            :to="{ path: '/map', query: { neighborhood: result.neighborhood.id, poster: result.poster.id } }"
            class="poster-map-button"
            dense
            flat
            no-caps
          >
            Show on Map
          </q-btn>
        </article>
      </div>

      <div v-else class="explore-sections">
        <section>
          <h2 class="explore-section-title">Neighborhoods</h2>
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
                @click="selectNeighborhood(neighborhood.id)"
              >
                <span class="neighborhood-button__title">{{ neighborhood.title }} ({{ neighborhood.posters.length }})</span>
                <q-icon
                  class="neighborhood-button__icon"
                  :name="neighborhood.id === selectedNeighborhoodId ? 'expand_more' : 'chevron_right'"
                  size="20px"
                />
              </q-btn>

              <div v-if="neighborhood.id === selectedNeighborhoodId && neighborhood.posters.length" class="poster-list">
                <article v-for="poster in neighborhood.posters" :key="poster.id" class="poster-item">
                  <h2>{{ poster.title }}</h2>
                  <p>{{ poster.authors }}</p>
                  <p>{{ poster.description }}</p>
                  <q-btn
                    :to="{ path: '/map', query: { neighborhood: neighborhood.id, poster: poster.id } }"
                    class="poster-map-button"
                    dense
                    flat
                    no-caps
                  >
                    Show on Map
                  </q-btn>
                </article>
              </div>
            </article>
          </div>
        </section>

        <section>
          <h2 class="explore-section-title">Demos</h2>
          <div class="neighborhood-list">
            <article v-for="demo in mapData.demos" :key="demo.id" class="neighborhood-item">
              <q-btn
                :class="{ 'neighborhood-button--active': demo.id === selectedDemoId }"
                class="neighborhood-button"
                no-caps
                unelevated
                @click="selectDemo(demo.id)"
              >
                <span class="neighborhood-button__title">
                  {{ demo.title }}<template v-if="demo.demos?.length"> ({{ demo.demos.length }})</template>
                </span>
                <q-icon
                  class="neighborhood-button__icon"
                  :name="demo.id === selectedDemoId ? 'expand_more' : 'chevron_right'"
                  size="20px"
                />
              </q-btn>

              <div v-if="demo.id === selectedDemoId" class="poster-list">
                <template v-if="demo.demos?.length">
                  <article v-for="demoItem in demo.demos" :key="demoItem.id" class="poster-item">
                    <h2>{{ demoItem.title }}</h2>
                    <p>{{ demoItem.authors }}</p>
                    <p>{{ demoItem.description }}</p>
                    <q-btn
                      :to="{ path: '/map', query: { demo: demo.id, item: demoItem.id } }"
                      class="poster-map-button"
                      dense
                      flat
                      no-caps
                    >
                      Show on Map
                    </q-btn>
                  </article>
                </template>
                <article v-else class="poster-item">
                  <p>{{ demo.location }}</p>
                  <q-btn
                    :to="{ path: '/map', query: { demo: demo.id } }"
                    class="poster-map-button"
                    dense
                    flat
                    no-caps
                  >
                    Show on Map
                  </q-btn>
                </article>
              </div>
            </article>
          </div>
        </section>

        <section>
          <h2 class="explore-section-title">Feature Booths</h2>
          <div class="neighborhood-list">
            <article v-for="booth in mapData.scts" :key="booth.id" class="neighborhood-item">
              <q-btn
                :class="{ 'neighborhood-button--active': booth.id === selectedFeatureBoothId }"
                class="neighborhood-button"
                no-caps
                unelevated
                @click="selectFeatureBooth(booth.id)"
              >
                <span class="neighborhood-button__title">{{ booth.title }}</span>
                <q-icon
                  class="neighborhood-button__icon"
                  :name="booth.id === selectedFeatureBoothId ? 'expand_more' : 'chevron_right'"
                  size="20px"
                />
              </q-btn>

              <div v-if="booth.id === selectedFeatureBoothId" class="poster-list">
                <article class="poster-item">
                  <p>Placeholder description.</p>
                  <q-btn
                    :to="{ path: '/map', query: { sct: booth.id } }"
                    class="poster-map-button"
                    dense
                    flat
                    no-caps
                  >
                    Show on Map
                  </q-btn>
                </article>
              </div>
            </article>
          </div>
        </section>
      </div>
    </section>
  </q-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import mapData from '../../data/live/map/locations.json'

const search = ref('')
const selectedNeighborhoodId = ref(null)
const selectedDemoId = ref(null)
const selectedFeatureBoothId = ref(null)
const filteredNeighborhoods = computed(() => mapData.neighborhoods)
const posterSearchResults = computed(() => {
  const query = search.value.trim().toLowerCase()

  if (!query) {
    return []
  }

  return mapData.neighborhoods.flatMap((neighborhood) => {
    return neighborhood.posters.filter((poster) => {
      return getPosterSearchText(neighborhood, poster).includes(query)
    }).map((poster) => {
      return {
        neighborhood,
        poster
      }
    })
  })
})

function getPosterSearchText(neighborhood, poster) {
  return `${neighborhood.title} ${poster.title} ${poster.authors} ${poster.description}`.toLowerCase()
}

function selectNeighborhood(id) {
  selectedNeighborhoodId.value = selectedNeighborhoodId.value === id ? null : id
}

function selectDemo(id) {
  selectedDemoId.value = selectedDemoId.value === id ? null : id
}

function selectFeatureBooth(id) {
  selectedFeatureBoothId.value = selectedFeatureBoothId.value === id ? null : id
}
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

.explore-sections {
  display: grid;
  gap: 24px;
}

.explore-section-title {
  margin: 0 0 10px;
  font-size: 1.25rem;
  font-weight: 800;
}

.neighborhood-list,
.poster-list {
  display: grid;
  gap: 10px;
}

.neighborhood-item .poster-list {
  margin-left: 16px;
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
  flex-wrap: nowrap;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  text-align: left;
}

.neighborhood-button__title {
  flex: 1 1 auto;
  min-width: 0;
  white-space: normal;
}

.neighborhood-button__icon {
  flex: 0 0 auto;
}

.neighborhood-button--active {
  position: sticky;
  top: 0;
  z-index: 2;
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

.poster-neighborhood-chip {
  margin: 0 0 8px;
  background: #294b75;
  color: #ffffff;
  font-weight: 800;
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

.poster-map-button {
  margin-top: 10px;
  padding: 0;
  color: #294b75;
  font-weight: 800;
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
