<script setup lang="ts">
import type { IndexedDocument } from '@/types/knowledge'
import { formatFileSize, getFileType } from '@/utils/formatters'

defineProps<{
  documents: IndexedDocument[]
  isLoading: boolean
}>()
</script>

<template>
  <section class="knowledge-section">
    <div class="section-header">
      <div>
        <p class="section-label">INDEXED DOCUMENTS</p>

        <h2>
          {{ documents.length }}
          document{{ documents.length === 1 ? '' : 's' }}
        </h2>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">Loading documents...</div>

    <div v-else-if="documents.length === 0" class="empty-state">
      <h3>No documents indexed yet.</h3>

      <p>Select a folder above to start building your local knowledge base.</p>
    </div>

    <div v-else class="indexed-list">
      <article v-for="document in documents" :key="document.id" class="indexed-card">
        <div class="indexed-card-main">
          <div class="document-icon">
            {{ getFileType(document.name) }}
          </div>

          <div class="indexed-info">
            <h3>{{ document.name }}</h3>
            <p>{{ document.path }}</p>
          </div>
        </div>

        <div class="indexed-meta">
          <span> {{ document.chunk_count }} chunks </span>

          <span>
            {{ formatFileSize(document.size) }}
          </span>
        </div>
      </article>
    </div>
  </section>
</template>
