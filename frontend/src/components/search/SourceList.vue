<script setup lang="ts">
import type { RAGSource } from '@/types/knowledge'

defineProps<{
  sources: RAGSource[]
}>()
</script>

<template>
  <div class="sources-section">
    <div class="sources-header">
      <p class="section-label">SOURCES</p>

      <span>
        {{ sources.length }}
        source{{ sources.length === 1 ? '' : 's' }}
      </span>
    </div>

    <div class="sources-list">
      <article v-for="source in sources" :key="source.reference" class="source-card">
        <div class="source-number">
          {{ source.reference }}
        </div>

        <div class="source-info">
          <h3>{{ source.document_name }}</h3>

          <p>{{ source.document_path }}</p>

          <div class="source-meta">
            <span v-if="source.page_number !== null"> Page {{ source.page_number }} </span>

            <span v-if="source.section">
              {{ source.section }}
            </span>

            <span> Chunk {{ source.chunk_index + 1 }} </span>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>
