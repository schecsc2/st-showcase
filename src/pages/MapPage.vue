<template>
  <q-page class="map-page">
    <div ref="mapElement" class="map-canvas" />

    <q-input
      ref="searchElement"
      v-model="search"
      bg-color="white"
      borderless
      class="map-search"
      clearable
      dense
      :placeholder="selectedSearchResult ? '' : 'Search'"
      @focus="searchFocused = true"
    >
      <template #prepend>
        <q-icon name="search" />
        <q-chip
          v-if="selectedSearchResult"
          class="map-search-selection"
          dense
          removable
          square
          @remove="clearSearchSelection"
        >
          {{ selectedSearchResult.title }}
        </q-chip>
      </template>
    </q-input>

    <q-btn-dropdown
      v-if="!selectedSearchResult && !(search || '').trim()"
      class="map-quick-filters"
      content-class="map-quick-filters-menu"
      dense
      dropdown-icon="add"
      label="Quick Filters"
      menu-anchor="bottom start"
      :menu-offset="[0, 0]"
      menu-self="top start"
      no-caps
      unelevated
    >
      <q-list dense>
        <q-item
          v-for="filter in mapSearchCategories"
          :key="filter.key"
          clickable
          @click="selectType(filter.type)"
        >
          <q-item-section avatar>
            <q-checkbox
              :model-value="activeTypes.includes(filter.type)"
              class="map-quick-filter-checkbox"
              dense
              @click.stop
              @update:model-value="selectType(filter.type)"
            />
          </q-item-section>
          <q-item-section>{{ filter.title }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-btn
              class="map-quick-filters__clear"
              dense
              flat
              label="Clear"
              no-caps
              @click="clearTypes"
            />
          </q-item-section>
        </q-item>
      </q-list>
    </q-btn-dropdown>

    <div
      v-if="mapSearchResults.length"
      ref="searchResultsElement"
      class="map-search-results"
    >
      <button
        v-for="result in mapSearchResults"
        :key="result.key"
        class="map-search-result"
        type="button"
        @click="selectSearchResult(result)"
      >
        <span
          :class="{ 'map-search-result__title--bold': result.kind !== 'poster' }"
          class="map-search-result__title"
        >
          <template v-if="result.kind === 'poster'">
            <span class="map-search-result__prefix">{{ result.neighborhood.title }} &gt;</span>
            {{ result.poster.title }}
          </template>
          <template v-else>{{ result.title }}</template>
        </span>
      </button>
    </div>

    <q-card
      v-if="selectedMapCard"
      :class="{ 'map-popup-card--compact': selectedMapCard.type }"
      class="map-popup-card"
    >
      <q-card-section class="map-popup-card__section">
        <div
          :class="{ 'map-popup-card__title--neighborhood': selectedMapCard.posters?.length }"
          class="map-popup-card__title"
        >
          {{ selectedMapCard.title }}
        </div>
        <div v-if="selectedMapCard.subtitle" class="map-popup-card__subtitle">{{ selectedMapCard.subtitle }}</div>
      </q-card-section>
      <q-carousel
        v-if="selectedMapCard.posters?.length"
        v-model="activePosterSlide"
        animated
        arrows
        class="map-poster-carousel"
        control-color="blue-grey-9"
        height="176px"
        infinite
      >
        <q-carousel-slide
          v-for="poster in selectedMapCard.posters"
          :key="poster.id"
          :name="poster.id"
          class="map-poster-slide"
        >
          <div class="map-poster-title">{{ poster.title }}</div>
          <div class="map-poster-authors">{{ poster.authors }}</div>
          <p class="map-poster-description">{{ poster.description }}</p>
        </q-carousel-slide>
      </q-carousel>
    </q-card>

    <div class="map-zoom">
      <q-btn
        class="map-zoom__button"
        icon="add"
        unelevated
        @click="zoomIn"
      />
      <q-btn
        class="map-zoom__button"
        icon="remove"
        unelevated
        @click="zoomOut"
      />
    </div>

  </q-page>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as L from 'leaflet'
import { useRoute } from 'vue-router'
import mapImage from '../../data/live/map/map.png'
import mapData from '../../data/live/map/locations.json'

const neighborhoodGeometryFiles = import.meta.glob('../../data/live/map/geometries/neighborhoods/*', {
  query: '?raw',
  import: 'default',
  eager: true
})
const demoGeometryFiles = import.meta.glob('../../data/live/map/geometries/demos/*', {
  query: '?raw',
  import: 'default',
  eager: true
})

const mapElement = ref(null)
const searchElement = ref(null)
const searchResultsElement = ref(null)
const search = ref('')
const searchFocused = ref(false)
const selectedSearchResult = ref(null)
const activeTypes = ref([])
const selectedMapCard = ref(null)
const activePosterSlide = ref('')
const markers = []
const geometryLayers = []
const posterLayers = []
const minAllowedZoom = -10
const maxZoomSteps = 3
const geometryWidth = 11000
const geometryHeight = 8500
const mapSearchCategories = [
  {
    key: 'type-neighborhood',
    type: 'neighborhood',
    title: 'Neighborhoods'
  },
  {
    key: 'type-demo',
    type: 'demo',
    title: 'Demos'
  },
  {
    key: 'type-sct',
    type: 'sct',
    title: 'Feature Booths'
  },
  {
    key: 'type-help',
    type: 'help',
    title: 'Help'
  },
  {
    key: 'type-restroom',
    type: 'restroom',
    title: 'Restrooms'
  },
  {
    key: 'type-food',
    type: 'food',
    title: 'Food/Drink'
  },
]
const neighborhoodsById = Object.fromEntries(mapData.neighborhoods.map((neighborhood) => [neighborhood.id, neighborhood]))
const demosById = Object.fromEntries(mapData.demos.map((demoArea) => [demoArea.id, demoArea]))
const neighborhoodGeometries = Object.keys(neighborhoodGeometryFiles).sort().map((path) => ({
  id: getFileId(path),
  title: neighborhoodsById[getFileId(path)]?.title,
  posters: neighborhoodsById[getFileId(path)]?.posters || [],
  geometry: neighborhoodGeometryFiles[path]
}))
const demoGeometries = Object.keys(demoGeometryFiles).sort().map((path) => ({
  id: getFileId(path),
  title: demosById[getFileId(path)]?.title,
  posters: demosById[getFileId(path)]?.demos || [],
  itemLabel: 'demos',
  geometry: demoGeometryFiles[path]
}))
const mapSearchResults = computed(() => {
  if (!searchFocused.value || selectedSearchResult.value) {
    return []
  }

  const query = (search.value || '').trim().toLowerCase()

  if (!query) {
    return []
  }

  const neighborhoodResults = mapData.neighborhoods.filter((neighborhood) => {
    return neighborhood.title.toLowerCase().includes(query)
  }).map((neighborhood) => ({
    key: `neighborhood-${neighborhood.id}`,
    kind: 'neighborhood',
    title: neighborhood.title,
    neighborhood
  }))
  const posterResults = mapData.neighborhoods.flatMap((neighborhood) => {
    return neighborhood.posters.filter((poster) => {
      return getPosterSearchText(poster).includes(query)
    }).map((poster) => ({
      key: `poster-${poster.id}`,
      kind: 'poster',
      title: `${neighborhood.title} > ${poster.title}`,
      neighborhood,
      poster
    }))
  })
  const sctResults = mapData.scts.filter((sct) => {
    return sct.title.toLowerCase().includes(query)
  }).map((sct) => ({
    key: `sct-${sct.id}`,
    kind: 'sct',
    title: sct.title,
    sct
  }))
  const demoResults = mapData.demos.filter((demo) => {
    return demo.shape === 'circle' && demo.title.toLowerCase().includes(query)
  }).map((demo) => ({
    key: `demo-${demo.id}`,
    kind: 'demo',
    title: demo.title,
    demo
  }))

  return neighborhoodResults.concat(sctResults, demoResults, posterResults)
})
let selectedMarker = null
let selectedGeometryPath = null
let map
const route = useRoute()

onMounted(() => {
  const bounds = getMapBounds()

  map = L.map(mapElement.value, {
    crs: L.CRS.Simple,
    minZoom: minAllowedZoom,
    zoomSnap: 0,
    zoomDelta: 1,
    wheelPxPerZoomLevel: 8,
    wheelDebounceTime: 20,
    maxBounds: bounds,
    maxBoundsViscosity: 1,
    zoomControl: false,
    attributionControl: false
  })

  L.imageOverlay(mapImage, bounds).addTo(map)
  setZoomLimits(bounds)
  map.fitBounds(bounds)
  map.on('resize', () => setZoomLimits(bounds))
  map.on('click', clearMapHighlight)

  const geometryOverlay = getGeometryOverlay()

  L.svgOverlay(geometryOverlay.svg, bounds, {
    interactive: true
  }).addTo(map)

  geometryOverlay.items.forEach((item) => {
    geometryLayers.push(item)
    addGeometryClick(item)
  })

  mapData.demos.filter((demo) => demo.shape === 'circle').forEach((demo) => {
    const marker = L.marker(getMapPoint(demo), {
      icon: getDemoIcon()
    }).addTo(map)

    const item = {
      node: demo,
      type: 'demo',
      marker
    }

    markers.push(item)
    addMarkerClick(item)
  })

  mapData.bathrooms.forEach((bathroom) => {
    const marker = L.marker(getMapPoint(bathroom), {
      icon: getRestroomIcon()
    }).addTo(map)

    const item = {
      node: bathroom,
      type: 'restroom',
      marker
    }

    markers.push(item)
    addMarkerClick(item)
  })

  mapData.food.forEach((food) => {
    const marker = L.marker(getMapPoint(food), {
      icon: getFoodIcon()
    }).addTo(map)

    const item = {
      node: food,
      type: 'food',
      marker
    }

    markers.push(item)
    addMarkerClick(item)
  })

  mapData.help.forEach((help) => {
    const marker = L.marker(getMapPoint(help), {
      icon: getHelpIcon()
    }).addTo(map)

    const item = {
      node: help,
      type: 'help',
      marker
    }

    markers.push(item)
    addMarkerClick(item)
  })

  mapData.scts.forEach((sct) => {
    const marker = L.marker(getMapPoint(sct), {
      icon: getSctIcon()
    }).addTo(map)

    const item = {
      node: sct,
      type: 'sct',
      marker
    }

    markers.push(item)
    addMarkerClick(item)
  })

  selectRouteLocation()
  document.addEventListener('pointerdown', closeSearchResults)
})

onUnmounted(() => {
  document.removeEventListener('pointerdown', closeSearchResults)

  if (map) {
    map.remove()
    map = null
  }

  markers.length = 0
  geometryLayers.length = 0
  clearPosterMarkers()
})

watch(search, (value) => {
  if ((value || '').trim()) {
    selectedSearchResult.value = null
    activeTypes.value = []
    selectedMarker = null
    selectedGeometryPath = null
    clearPosterMarkers()
    closePopup()
  }

  updateMarkers()
})

watch(activePosterSlide, () => updatePosterMarkers(true))
watch(() => [route.query.neighborhood, route.query.poster, route.query.sct], selectRouteLocation)

function closeSearchResults(event) {
  const target = event.target
  const searchNode = searchElement.value?.$el || searchElement.value
  const resultsNode = searchResultsElement.value

  if (searchNode?.contains(target) || resultsNode?.contains(target)) {
    return
  }

  searchFocused.value = false
}

function getMapPoint(point) {
  return [mapData.image.height - point.y, point.x]
}

function getMapBounds() {
  return [
    [0, 0],
    [mapData.image.height, mapData.image.width]
  ]
}

function getFileId(path) {
  return path.split('/').pop()
}

function getGeometryOverlay() {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  const items = []

  svg.setAttribute('viewBox', `0 0 ${geometryWidth} ${geometryHeight}`)
  svg.setAttribute('preserveAspectRatio', 'none')
  svg.setAttribute('pointer-events', 'auto')

  neighborhoodGeometries.forEach((geometry) => {
    items.push(addGeometryPath(svg, geometry, 'neighborhood', '#2e7d32'))
  })

  demoGeometries.forEach((geometry) => {
    items.push(addGeometryPath(svg, geometry, 'demo', '#002C77'))
  })

  return {
    svg,
    items
  }
}

function addGeometryPath(svg, geometry, type, color) {
  const sourceSvg = new window.DOMParser().parseFromString(geometry.geometry, 'image/svg+xml').documentElement
  const sourceViewBox = getSvgViewBox(sourceSvg)
  const scaleX = geometryWidth / sourceViewBox.width
  const scaleY = geometryHeight / sourceViewBox.height
  const path = sourceSvg.querySelector('path').cloneNode(true)

  path.removeAttribute('id')
  path.querySelectorAll('title').forEach((title) => title.remove())
  path.setAttribute('transform', `matrix(${scaleX} 0 0 ${scaleY} ${-sourceViewBox.x * scaleX} ${-sourceViewBox.y * scaleY})`)
  path.setAttribute('fill', color)
  path.setAttribute('fill-opacity', '0.18')
  path.setAttribute('stroke', color)
  path.setAttribute('stroke-width', '3')
  path.setAttribute('vector-effect', 'non-scaling-stroke')
  path.setAttribute('pointer-events', 'visiblePainted')

  svg.appendChild(path)

  return {
    id: geometry.id,
    path,
    sourceViewBox,
    scaleX,
    scaleY,
    type,
    title: geometry.title || '',
    posters: geometry.posters || [],
    itemLabel: geometry.itemLabel || 'posters'
  }
}

function getSvgViewBox(svg) {
  const values = svg.getAttribute('viewBox').split(/\s+/).map(Number)

  return {
    x: values[0],
    y: values[1],
    width: values[2],
    height: values[3]
  }
}

function setZoomLimits(bounds) {
  map.setMinZoom(minAllowedZoom)
  const minZoom = map.getBoundsZoom(bounds)
  const maxZoom = minZoom + maxZoomSteps

  map.setMinZoom(minZoom)
  map.setMaxZoom(maxZoom)

  if (map.getZoom() < minZoom) {
    map.setZoom(minZoom)
  }

  if (map.getZoom() > maxZoom) {
    map.setZoom(maxZoom)
  }
}

function getRestroomIcon() {
  return L.divIcon({
    className: 'map-node map-node--restroom',
    html: '<span class="material-icons">wc</span>',
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17]
  })
}

function getDemoIcon() {
  return L.divIcon({
    className: 'map-node map-node--demo',
    html: '<span class="material-symbols-outlined">orbit</span>',
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17]
  })
}

function getFoodIcon() {
  return L.divIcon({
    className: 'map-node map-node--food',
    html: '<span class="material-icons">restaurant</span>',
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17]
  })
}

function getHelpIcon() {
  return L.divIcon({
    className: 'map-node map-node--help',
    html: '<span class="material-icons">question_mark</span>',
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17]
  })
}

function getSctIcon() {
  return L.divIcon({
    className: 'map-node map-node--sct',
    html: '<span class="material-icons">lightbulb</span>',
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17]
  })
}

function selectType(type) {
  selectedSearchResult.value = null
  activeTypes.value = activeTypes.value.includes(type)
    ? activeTypes.value.filter((activeType) => activeType !== type)
    : activeTypes.value.concat(type)
  selectedMarker = null
  selectedGeometryPath = null
  clearPosterMarkers()
  closePopup()
  search.value = ''
  updateMarkers()
  map.fitBounds(getMapBounds())
}

function clearTypes() {
  activeTypes.value = []
  updateMarkers()
}

function selectSearchResult(result) {
  searchFocused.value = false
  search.value = ''
  selectedSearchResult.value = result

  if (result.kind === 'sct' || result.kind === 'demo') {
    const node = result[result.kind]
    const item = markers.find(({ node: markerNode, type }) => type === result.kind && markerNode.id === node.id)

    if (item) {
      selectMarker(item)
      selectedSearchResult.value = result
    }
    return
  }

  const item = getNeighborhoodGeometry(result.neighborhood.id)

  if (!item) {
    return
  }

  if (result.kind === 'poster') {
    selectGeometry(item, result.poster.id)
    return
  }

  if (selectedGeometryPath !== item.path) {
    selectGeometry(item)
  }
}

function clearSearchSelection() {
  selectedSearchResult.value = null
  search.value = ''
  searchFocused.value = false
  activeTypes.value = []
  selectedMarker = null
  selectedGeometryPath = null
  clearPosterMarkers()
  closePopup()
  updateMarkers()
  map.fitBounds(getMapBounds())
}

function getNeighborhoodGeometry(id) {
  return geometryLayers.find((geometry) => geometry.id === id && geometry.type === 'neighborhood')
}

function zoomIn() {
  map.zoomIn()
}

function zoomOut() {
  map.zoomOut()
}

function closePopup() {
  selectedMapCard.value = null
  activePosterSlide.value = ''
}

function clearSelection() {
  selectedMarker = null
  selectedGeometryPath = null
  clearPosterMarkers()
  closePopup()
  updateMarkers()
}

function clearMapHighlight() {
  selectedSearchResult.value = null
  search.value = ''
  clearSelection()
}

function addMarkerClick(item) {
  item.marker.on('click', () => selectMarker(item))
}

function selectMarker(item) {
  selectedSearchResult.value = null

  if (selectedMarker === item.marker) {
    clearSelection()
    return
  }

  activeTypes.value = []
  selectedMarker = item.marker
  selectedGeometryPath = null
  clearPosterMarkers()
  selectedMapCard.value = {
    type: item.type,
    title: item.node.title,
    subtitle: item.node.location || ''
  }
  map.flyTo(item.marker.getLatLng(), map.getMaxZoom())
  updateMarkers()
}

function addGeometryClick(item) {
  item.path.addEventListener('click', (event) => {
    L.DomEvent.stop(event)
    selectedSearchResult.value = null
    selectGeometry(item)
  })
}

function selectRouteLocation() {
  const id = Array.isArray(route.query.neighborhood) ? route.query.neighborhood[0] : route.query.neighborhood
  const posterId = Array.isArray(route.query.poster) ? route.query.poster[0] : route.query.poster
  const sctId = Array.isArray(route.query.sct) ? route.query.sct[0] : route.query.sct

  if (!map) {
    return
  }

  if (sctId) {
    const item = markers.find(({ node, type }) => type === 'sct' && node.id === sctId)

    if (item) {
      selectMarker(item)
    }
    return
  }

  if (!id) {
    return
  }

  const item = getNeighborhoodGeometry(id)

  if (item) {
    selectGeometry(item, posterId)
  }
}

function selectGeometry(item, posterId) {
  if (selectedGeometryPath === item.path && !posterId) {
    clearSelection()
    return
  }

  activeTypes.value = []
  selectedMarker = null
  selectedGeometryPath = item.path
  clearPosterMarkers()
  const center = getGeometryBounds(item).getCenter()
  const posters = item.posters || []

  selectedMapCard.value = item.title
    ? {
        title: item.title,
        subtitle: posters.length ? `${posters.length} ${item.itemLabel}` : '',
        posters
      }
    : null
  activePosterSlide.value = posters.some((poster) => poster.id === posterId) ? posterId : posters[0]?.id || ''

  map.once('moveend', () => {
    if (selectedGeometryPath === item.path) {
      setPosterMarkers(item)
    }
  })
  if (item.type === 'demo') {
    map.flyToBounds(getGeometryBounds(item))
  } else {
    map.flyTo(center, map.getMaxZoom())
  }
  updateMarkers()
}

function setPosterMarkers(item) {
  clearPosterMarkers()

  if (!item.posters?.length) {
    return
  }

  const box = getGeometryBox(item)
  const positions = item.id === 'sidewalk'
    ? [
        [0.32, 0.22],
        [0.51, 0.5],
        [0.7, 0.78]
      ]
    : [
        [0.25, 0.3],
        [0.5, 0.3],
        [0.75, 0.3],
        [0.35, 0.68],
        [0.65, 0.68]
      ]
  const color = item.type === 'demo' ? '#002C77' : '#2e7d32'

  item.posters.forEach((poster, index) => {
    const position = positions[index % positions.length]
    const point = getGeometryPoint(box.x + box.width * position[0], box.y + box.height * position[1])
    const marker = L.circleMarker(point, {
      radius: 5,
      color,
      weight: 2,
      fillColor: color,
      fillOpacity: 0.35,
      opacity: 0.35
    }).addTo(map)

    posterLayers.push({
      poster,
      marker
    })
  })

  updatePosterMarkers(true)
}

function clearPosterMarkers() {
  posterLayers.forEach(({ marker }) => {
    marker.remove()
  })
  posterLayers.length = 0
}

function updatePosterMarkers(shouldCenter) {
  let activeMarker = null

  posterLayers.forEach(({ poster, marker }) => {
    const isActive = poster.id === activePosterSlide.value

    marker.setRadius(isActive ? 9 : 5)
    marker.setStyle({
      fillOpacity: isActive ? 1 : 0.35,
      opacity: isActive ? 1 : 0.35
    })

    if (isActive) {
      activeMarker = marker
      marker.bringToFront()
    }
  })

  if (shouldCenter && activeMarker) {
    const zoom = map.getZoom()
    const markerPoint = map.project(activeMarker.getLatLng(), zoom)
    const verticalOffset = Math.min(120, map.getSize().y * 0.18)

    map.panTo(map.unproject(markerPoint.add([0, verticalOffset]), zoom))
  }
}

function getGeometryBounds(item) {
  const box = getGeometryBox(item)

  return L.latLngBounds([
    getGeometryPoint(box.x, box.y + box.height),
    getGeometryPoint(box.x + box.width, box.y)
  ])
}

function getGeometryBox(item) {
  const box = item.path.getBBox()

  return {
    x: (box.x - item.sourceViewBox.x) * item.scaleX,
    y: (box.y - item.sourceViewBox.y) * item.scaleY,
    width: box.width * item.scaleX,
    height: box.height * item.scaleY
  }
}

function getGeometryPoint(x, y) {
  return [
    mapData.image.height - (y / geometryHeight * mapData.image.height),
    x / geometryWidth * mapData.image.width
  ]
}

function updateMarkers() {
  const hasIndividualHighlight = selectedMarker || selectedGeometryPath
  const hasGroupHighlight = activeTypes.value.length > 0

  markers.forEach(({ node, type, marker }) => {
    const isMatch = !hasGroupHighlight || activeTypes.value.includes(type)
    const isActive = hasIndividualHighlight ? selectedMarker === marker : hasGroupHighlight && isMatch
    const element = marker.getElement()

    element.classList.toggle('map-node--active', isActive)
    element.classList.toggle('map-node--muted', hasIndividualHighlight ? selectedMarker !== marker : hasGroupHighlight && !isMatch)
  })

  geometryLayers.forEach(({ path, type }) => {
    const isMatch = !hasGroupHighlight || activeTypes.value.includes(type)
    const isActive = hasIndividualHighlight ? selectedGeometryPath === path : hasGroupHighlight && isMatch

    path.setAttribute('fill-opacity', isActive ? '0.5' : '0.18')
    path.setAttribute('opacity', hasIndividualHighlight ? selectedGeometryPath !== path ? '0.25' : '1' : hasGroupHighlight && !isMatch ? '0.25' : '1')
  })
}

function getPosterSearchText(poster) {
  return `${poster.title} ${poster.authors} ${poster.description}`.toLowerCase()
}
</script>

<style scoped>
.map-page {
  position: relative;
  min-height: 100vh;
  padding-bottom: 120px;
}

.map-canvas {
  height: calc(100vh - 120px);
  min-height: 520px;
  background: #ffffff;
}

.map-search {
  position: fixed;
  top: 16px;
  left: 50%;
  z-index: 500;
  width: calc(100% - 32px);
  max-width: 360px;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 0 10px;
  transform: translateX(-50%);
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.14);
}

.map-search-selection {
  max-width: 220px;
  margin: 0 0 0 8px;
  border: 1px solid #dde3ea;
  background: #ffffff;
  color: #1f2933;
  font-weight: 800;
}

.map-search-selection :deep(.q-chip__content) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-quick-filters {
  position: fixed;
  top: 66px;
  left: max(16px, calc(50% - 180px));
  z-index: 530;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  padding-left: 10px;
  color: #1f2933;
  font-weight: 800;
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.14);
}

.map-quick-filters[aria-expanded='true'] {
  border-radius: 8px 8px 0 0;
}

:global(.map-quick-filters-menu) {
  border: 1px solid #dde3ea;
  border-radius: 0 8px 8px 8px;
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.14);
}

.map-quick-filters__clear {
  color: #002C77;
  font-weight: 800;
}

.map-quick-filter-checkbox :deep(.q-checkbox__inner--truthy) {
  color: #002C77;
}

.map-search-results {
  position: fixed;
  top: 58px;
  left: 50%;
  z-index: 540;
  display: grid;
  width: calc(100% - 32px);
  max-width: 360px;
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  transform: translateX(-50%);
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.14);
}

.map-search-result {
  display: grid;
  justify-items: start;
  gap: 6px;
  border: 0;
  border-bottom: 1px solid #dde3ea;
  background: #ffffff;
  padding: 10px 12px;
  color: #1f2933;
  font: inherit;
  text-align: left;
}

.map-search-result:last-child {
  border-bottom: 0;
}

.map-search-result__title {
  line-height: 1.25;
}

.map-search-result__title--bold {
  font-weight: 800;
}

.map-search-result__prefix {
  font-weight: 800;
}

.map-popup-card {
  position: fixed;
  right: 16px;
  bottom: calc(104px + env(safe-area-inset-bottom));
  left: 16px;
  z-index: 520;
  max-width: 360px;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.14);
}

.map-popup-card--compact {
  right: auto;
  left: 50%;
  width: calc(100% - 112px);
  max-width: 220px;
  transform: translateX(-50%);
}

.map-popup-card__section {
  padding: 12px 14px;
}

.map-popup-card--compact .map-popup-card__section {
  padding: 10px 12px;
  text-align: center;
}

.map-popup-card__title {
  color: #1f2933;
  font-size: 14px;
  font-weight: 800;
  line-height: 1.25;
}

.map-popup-card__title--neighborhood {
  font-size: 16px;
}

.map-popup-card__subtitle {
  margin-top: 2px;
  color: #52606d;
  font-size: 12px;
  font-weight: 700;
}

.map-poster-carousel {
  border-top: 1px solid #dde3ea;
  border-radius: 0 0 8px 8px;
}

.map-poster-carousel :deep(.q-carousel__arrow .q-icon) {
  color: #294b75;
}

.map-poster-slide {
  padding: 12px 52px 34px;
}

.map-poster-title {
  color: #1f2933;
  font-size: 14px;
  font-weight: 800;
  line-height: 1.25;
}

.map-poster-authors {
  margin-top: 4px;
  color: #52606d;
  font-size: 12px;
  font-weight: 700;
}

.map-poster-description {
  margin: 8px 0 0;
  color: #52606d;
  font-size: 12px;
  line-height: 1.35;
}

.map-zoom {
  position: fixed;
  top: 112px;
  right: 16px;
  z-index: 510;
  display: grid;
  overflow: hidden;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.14);
}

.map-zoom__button {
  width: 42px;
  height: 42px;
  border-radius: 0;
  background: #ffffff;
  color: #1f2933;
  box-shadow: none;
}

.map-zoom__button + .map-zoom__button {
  border-top: 1px solid #dde3ea;
}

.map-page :deep(.map-node) {
  display: grid;
  place-items: center;
  border: 2px solid #79a9ff;
  border-radius: 50%;
  background: #ffffff;
  color: #79a9ff;
  box-shadow: 0 4px 12px rgba(31, 41, 51, 0.22);
}

.map-page :deep(.map-node .material-icons),
.map-page :deep(.map-node .material-symbols-outlined) {
  font-size: 20px;
  line-height: 1;
}

.map-page :deep(.map-node--active) {
  border-color: #79a9ff;
  background: #79a9ff;
  color: #ffffff;
}

.map-page :deep(.map-node--demo) {
  border-color: #002C77;
  color: #002C77;
}

.map-page :deep(.map-node--demo.map-node--active) {
  border-color: #002C77;
  background: #002C77;
  color: #ffffff;
}

.map-page :deep(.map-node--food) {
  border-color: #ef7d00;
  color: #ef7d00;
}

.map-page :deep(.map-node--food.map-node--active) {
  border-color: #ef7d00;
  background: #ef7d00;
  color: #ffffff;
}

.map-page :deep(.map-node--help) {
  border-color: #d32f2f;
  color: #d32f2f;
}

.map-page :deep(.map-node--help.map-node--active) {
  border-color: #d32f2f;
  background: #d32f2f;
  color: #ffffff;
}

.map-page :deep(.map-node--sct) {
  border-color: #5f1a8b;
  color: #5f1a8b;
}

.map-page :deep(.map-node--sct.map-node--active) {
  border-color: #5f1a8b;
  background: #5f1a8b;
  color: #ffffff;
}

.map-page :deep(.map-node--muted) {
  opacity: 0.25;
}
</style>
