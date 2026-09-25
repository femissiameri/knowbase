<script setup lang="ts">
import { computed } from 'vue'
import EmptyState from '@/components/common/EmptyState.vue'
import RagAnswer from '@/components/search/RagAnswer.vue'
import SearchLoading from '@/components/search/SearchLoading.vue'
import SearchPanel from '@/components/search/SearchPanel.vue'
import SearchResults from '@/components/search/SearchResults.vue'
import { useRag } from '@/composables/useRag'
import { useSearch } from '@/composables/useSearch'
import type { SearchMode } from '@/types/knowledge'

const props = defineProps<{
  documentCount: number
}>()

const emit = defineEmits<{
  manageDocuments: []
}>()

const {
  searchMode,
  searchQuery,
  currentSearchResults,
  isSearching,
  searchError,
  expandedResultIds,
  performSearch,
  switchSearchMode,
  toggleResult,
} = useSearch()

const { ragAnswer, ragSources, isAsking, ragError, ask } = useRag()

const hasQuery = computed(() => searchQuery.value.trim().length > 0)

const showNoResults = computed(
  () =>
    !isSearching.value &&
    !isAsking.value &&
    hasQuery.value &&
    !ragAnswer.value &&
    currentSearchResults.value.length === 0 &&
    !searchError.value,
)

const showResults = computed(
  () => !isAsking.value && !ragAnswer.value && currentSearchResults.value.length > 0,
)

const isKnowledgeBaseEmpty = computed(() => props.documentCount === 0 && !hasQuery.value)

async function handleModeChange(mode: SearchMode) {
  ragError.value = ''
  ragAnswer.value = ''
  ragSources.value = []
  await switchSearchMode(mode)
}

async function handleSearch() {
  ragAnswer.value = ''
  ragSources.value = []
  ragError.value = ''
  await performSearch()
}

async function handleAsk() {
  await ask(searchQuery.value)
}

function handleManageDocuments() {
  emit('manageDocuments')
}
</script>

<template>
  <section class="page-section">
    <div class="page-heading">
      <p class="eyebrow">KNOWLEDGE SEARCH</p>

      <h1>Ask your knowledge base.</h1>

      <p class="page-description">
        Search through your indexed documents without leaving your machine.
      </p>
    </div>

    <SearchPanel
      v-model="searchQuery"
      :mode="searchMode"
      :is-asking="isAsking"
      @update:mode="handleModeChange"
      @search="handleSearch"
      @ask="handleAsk"
    />

    <p v-if="searchError" class="error-message">
      {{ searchError }}
    </p>

    <SearchLoading v-if="isSearching" />

    <RagAnswer :answer="ragAnswer" :sources="ragSources" :is-asking="isAsking" />

    <p v-if="ragError" class="error-message">
      {{ ragError }}
    </p>

    <EmptyState
      v-if="showNoResults"
      eyebrow="NO RESULTS"
      title="No relevant knowledge found"
      description="Your indexed documents don't contain enough relevant information for this query."
      action-label="Manage documents"
      @action="handleManageDocuments"
    />

    <SearchResults
      v-if="showResults"
      :results="currentSearchResults"
      :mode="searchMode"
      :expanded-result-ids="expandedResultIds"
      @toggle="toggleResult"
    />

    <EmptyState
      v-if="isKnowledgeBaseEmpty"
      eyebrow="GET STARTED"
      title="Your knowledge base is empty."
      description="Add documents first, then come back here to search them."
      action-label="Add documents"
      variant="search-empty-state"
      @action="handleManageDocuments"
    />
  </section>
</template>
