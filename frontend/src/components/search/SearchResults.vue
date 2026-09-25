<script setup lang="ts">
import type { SearchMode, SearchResultItem } from '@/types/knowledge'
import SearchResultCard from './SearchResultCard.vue'

defineProps<{
  results: SearchResultItem[]
  mode: SearchMode
  expandedResultIds: number[]
}>()

const emit = defineEmits<{
  toggle: [resultId: number]
}>()

function modeLabel(mode: SearchMode): string {
  if (mode === 'hybrid') {
    return 'Hybrid search'
  }

  if (mode === 'semantic') {
    return 'Semantic search'
  }

  return 'Keyword search'
}
</script>

<template>
  <section class="results-section">
    <div class="results-header">
      <div>
        <p class="section-label">RESULTS</p>

        <h2>
          {{ results.length }}
          result{{ results.length === 1 ? '' : 's' }}
        </h2>
      </div>

      <div class="results-info">
        <span class="results-mode">
          {{ modeLabel(mode) }}
        </span>

        <span class="results-divider">·</span>

        <span>Ranked by relevance</span>
      </div>
    </div>

    <div class="results-list">
      <SearchResultCard
        v-for="result in results"
        :key="result.chunk_id"
        :result="result"
        :expanded="expandedResultIds.includes(result.chunk_id)"
        @toggle="emit('toggle', $event)"
      />
    </div>
  </section>
</template>
