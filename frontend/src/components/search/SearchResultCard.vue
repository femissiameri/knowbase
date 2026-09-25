<script setup lang="ts">
import type { SearchResultItem } from '@/types/knowledge'
import {
  formatResultSimilarity,
  getFileType,
  getMatchedBy,
  getResultPreview,
  getSimilarity,
  isLongResult,
} from '@/utils/formatters'

defineProps<{
  result: SearchResultItem
  expanded: boolean
}>()

const emit = defineEmits<{
  toggle: [resultId: number]
}>()
</script>

<template>
  <article class="result-card" :class="{ expanded }">
    <div class="result-card-top">
      <div class="result-document">
        <div class="document-icon">
          {{ getFileType(result.document_name) }}
        </div>

        <div class="result-document-info">
          <h3>{{ result.document_name }}</h3>
          <p>{{ result.document_path }}</p>
        </div>
      </div>

      <div class="result-badges">
        <span v-for="method in getMatchedBy(result)" :key="method" class="match-badge">
          {{ method }}
        </span>

        <span v-if="getSimilarity(result) !== null" class="similarity-badge">
          {{ formatResultSimilarity(result) }}
        </span>
      </div>
    </div>

    <div class="result-meta">
      <span> Chunk {{ result.chunk_index + 1 }} </span>

      <template v-if="'page_number' in result && result.page_number !== null">
        <span>·</span>
        <span>Page {{ result.page_number }}</span>
      </template>

      <template v-if="'section' in result && result.section">
        <span>·</span>
        <span>{{ result.section }}</span>
      </template>
    </div>

    <div class="result-content" :class="{ collapsed: !expanded }">
      {{ expanded ? result.content : getResultPreview(result.content) }}
    </div>

    <div class="result-footer">
      <button
        v-if="isLongResult(result.content)"
        type="button"
        class="text-button"
        @click="emit('toggle', result.chunk_id)"
      >
        {{ expanded ? 'Show less' : 'Show more' }}
      </button>

      <button
        type="button"
        class="source-button"
        title="Source navigation will be implemented later"
      >
        View source →
      </button>
    </div>
  </article>
</template>
