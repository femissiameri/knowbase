<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import DocumentsView from '@/views/DocumentsView.vue'
import SearchView from '@/views/SearchView.vue'
import { useDocuments } from '@/composables/useDocuments'
import type { Tab } from '@/types/knowledge'

const activeTab = ref<Tab>('search')

const {
  files,
  folderName,
  indexedDocuments,
  supportedFiles,
  documentCount,
  isLoadingDocuments,
  isIndexing,
  indexError,
  lastSync,
  selectFolder,
  loadDocuments,
  indexDocuments,
} = useDocuments()

onMounted(loadDocuments)
</script>

<template>
  <main class="app-shell">
    <AppHeader
      :active-tab="activeTab"
      :document-count="documentCount"
      @update:active-tab="activeTab = $event"
    />

    <div class="page">
      <SearchView
        v-if="activeTab === 'search'"
        :document-count="documentCount"
        @manage-documents="activeTab = 'documents'"
      />

      <DocumentsView
        v-else
        :files="files"
        :folder-name="folderName"
        :indexed-documents="indexedDocuments"
        :supported-files="supportedFiles"
        :document-count="documentCount"
        :is-loading-documents="isLoadingDocuments"
        :is-indexing="isIndexing"
        :index-error="indexError"
        :last-sync="lastSync"
        @folder-selected="selectFolder"
        @index-documents="indexDocuments"
      />
    </div>
  </main>
</template>
