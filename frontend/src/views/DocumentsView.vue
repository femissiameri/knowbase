<script setup lang="ts">
import FolderPicker from '@/components/documents/FolderPicker.vue'
import IndexedDocumentList from '@/components/documents/IndexedDocumentList.vue'
import SelectedFolder from '@/components/documents/SelectedFolder.vue'
import SyncSummary from '@/components/documents/SyncSummary.vue'
import type { IndexedDocument, LocalFile, SyncSummary as SyncSummaryType } from '@/types/knowledge'

const props = defineProps<{
  files: LocalFile[]
  folderName: string
  indexedDocuments: IndexedDocument[]
  supportedFiles: LocalFile[]
  documentCount: number
  isLoadingDocuments: boolean
  isIndexing: boolean
  indexError: string
  lastSync: SyncSummaryType | null
}>()

const emit = defineEmits<{
  folderSelected: [files: File[]]
  indexDocuments: []
}>()
</script>

<template>
  <section class="page-section">
    <div class="documents-heading">
      <div>
        <p class="eyebrow">KNOWLEDGE BASE</p>

        <h1>Your documents.</h1>

        <p class="page-description">Choose a local folder and keep your knowledge synchronized.</p>
      </div>

      <div class="document-stat">
        <strong>{{ props.documentCount }}</strong>

        <span> indexed document{{ props.documentCount === 1 ? '' : 's' }} </span>
      </div>
    </div>

    <div v-if="props.indexError" class="error-message">
      {{ props.indexError }}
    </div>

    <FolderPicker @selected="emit('folderSelected', $event)">
      <template #folder-name>
        {{ props.folderName || 'Choose a folder' }}
      </template>
    </FolderPicker>

    <SelectedFolder
      :files="props.files"
      :supported-files="props.supportedFiles"
      :folder-name="props.folderName"
      :is-indexing="props.isIndexing"
      @index="emit('indexDocuments')"
    />

    <SyncSummary :summary="props.lastSync" />

    <IndexedDocumentList
      :documents="props.indexedDocuments"
      :is-loading="props.isLoadingDocuments"
    />
  </section>
</template>
