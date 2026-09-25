<script setup lang="ts">
import type { LocalFile } from '@/types/knowledge'
import { formatFileSize, getFileType } from '@/utils/formatters'

defineProps<{
  files: LocalFile[]
  supportedFiles: LocalFile[]
  folderName: string
  isIndexing: boolean
}>()

const emit = defineEmits<{
  index: []
}>()
</script>

<template>
  <section v-if="files.length > 0" class="selected-folder">
    <div class="selected-folder-header">
      <div>
        <p class="section-label">SELECTED FOLDER</p>
        <h2>{{ folderName }}</h2>
      </div>

      <div class="file-stats">
        <span> {{ files.length }} total </span>

        <span> {{ supportedFiles.length }} supported </span>
      </div>
    </div>

    <div v-if="supportedFiles.length === 0" class="empty-state">
      <h3>No supported documents</h3>
      <p>Supported formats: PDF, DOCX, Markdown and TXT.</p>
    </div>

    <div v-else class="file-list">
      <div v-for="file in supportedFiles" :key="file.path" class="file-row">
        <div class="file-main">
          <div class="file-type">
            {{ getFileType(file.name) }}
          </div>

          <div class="file-info">
            <p class="file-name">
              {{ file.name }}
            </p>

            <p class="file-path">
              {{ file.path }}
            </p>
          </div>
        </div>

        <span class="file-size">
          {{ formatFileSize(file.size) }}
        </span>
      </div>
    </div>

    <div class="index-action">
      <div>
        <strong>Ready to synchronize</strong>

        <p>New, changed and deleted documents will be detected automatically.</p>
      </div>

      <button
        type="button"
        class="primary-button"
        :disabled="isIndexing || supportedFiles.length === 0"
        @click="emit('index')"
      >
        {{ isIndexing ? 'Indexing...' : 'Index documents' }}
      </button>
    </div>
  </section>
</template>
