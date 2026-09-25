import { computed, ref } from 'vue'
import type {
  HybridSearchResult,
  SearchMode,
  SearchResult,
  SearchResultItem,
  SemanticSearchResult,
} from '@/types/knowledge'

export function useSearch() {
  const searchMode = ref<SearchMode>('hybrid')
  const searchQuery = ref('')

  const searchResults = ref<SearchResult[]>([])
  const semanticResults = ref<SemanticSearchResult[]>([])
  const hybridResults = ref<HybridSearchResult[]>([])

  const isSearching = ref(false)
  const searchError = ref('')
  const expandedResultIds = ref<number[]>([])

  const currentSearchResults = computed<SearchResultItem[]>(() => {
    if (searchMode.value === 'semantic') {
      return semanticResults.value
    }

    if (searchMode.value === 'hybrid') {
      return hybridResults.value
    }

    return searchResults.value
  })

  function clearResults() {
    searchResults.value = []
    semanticResults.value = []
    hybridResults.value = []
    expandedResultIds.value = []
  }

  async function searchDocuments() {
    const query = searchQuery.value.trim()

    if (!query) {
      searchResults.value = []
      return
    }

    isSearching.value = true
    searchError.value = ''

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = await response.json()
      searchResults.value = data.results
    } catch (error) {
      searchError.value = error instanceof Error ? error.message : 'Search failed.'
    } finally {
      isSearching.value = false
    }
  }

  async function semanticSearchDocuments() {
    const query = searchQuery.value.trim()

    if (!query) {
      semanticResults.value = []
      return
    }

    isSearching.value = true
    searchError.value = ''

    try {
      const response = await fetch(`/api/search/semantic?q=${encodeURIComponent(query)}`)

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = await response.json()
      semanticResults.value = data.results
    } catch (error) {
      searchError.value = error instanceof Error ? error.message : 'Semantic search failed.'
    } finally {
      isSearching.value = false
    }
  }

  async function hybridSearchDocuments() {
    const query = searchQuery.value.trim()

    if (!query) {
      hybridResults.value = []
      return
    }

    isSearching.value = true
    searchError.value = ''

    try {
      const response = await fetch(`/api/search/hybrid?q=${encodeURIComponent(query)}`)

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = await response.json()
      hybridResults.value = data.results
    } catch (error) {
      searchError.value = error instanceof Error ? error.message : 'Hybrid search failed.'
    } finally {
      isSearching.value = false
    }
  }

  async function performSearch() {
    expandedResultIds.value = []

    if (searchMode.value === 'hybrid') {
      await hybridSearchDocuments()
      return
    }

    if (searchMode.value === 'semantic') {
      await semanticSearchDocuments()
      return
    }

    await searchDocuments()
  }

  async function switchSearchMode(mode: SearchMode) {
    searchMode.value = mode
    clearResults()

    if (searchQuery.value.trim()) {
      await performSearch()
    }
  }

  function toggleResult(resultId: number) {
    if (expandedResultIds.value.includes(resultId)) {
      expandedResultIds.value = expandedResultIds.value.filter((id) => id !== resultId)
      return
    }

    expandedResultIds.value = [...expandedResultIds.value, resultId]
  }

  function isResultExpanded(resultId: number) {
    return expandedResultIds.value.includes(resultId)
  }

  return {
    searchMode,
    searchQuery,
    currentSearchResults,
    isSearching,
    searchError,
    expandedResultIds,
    performSearch,
    switchSearchMode,
    toggleResult,
    isResultExpanded,
  }
}
