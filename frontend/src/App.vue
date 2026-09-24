<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
} from 'vue'

type Tab = 'search' | 'documents'
type SearchMode = 'semantic' | 'keyword'

interface LocalFile {
  name: string
  path: string
  size: number
  type: string
}

interface IndexedDocument {
  id: number
  name: string
  path: string
  size: number
  content_type: string | null
  extension: string
  text_length: number
  text_preview: string
  chunk_count: number
}

interface SearchResult {
  chunk_id: number
  document_id: number
  document_name: string
  document_path: string
  chunk_index: number
  content: string
}

interface SemanticSearchResult extends SearchResult {
  similarity: number
}

interface SyncResult {
  created: number
  updated: number
  unchanged: number
  deleted: number
  documents: IndexedDocument[]
}

const activeTab = ref<Tab>('search')
const searchMode = ref<SearchMode>('semantic')

const folderInput = ref<HTMLInputElement | null>(null)

const files = ref<LocalFile[]>([])
const folderName = ref('')

const indexedDocuments = ref<IndexedDocument[]>([])

const isLoadingDocuments = ref(false)
const isIndexing = ref(false)

const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const semanticResults = ref<SemanticSearchResult[]>([])

const isSearching = ref(false)
const searchError = ref('')
const indexError = ref('')

const lastSync = ref<{
  created: number
  updated: number
  unchanged: number
  deleted: number
} | null>(null)

const supportedExtensions = new Set([
  'md',
  'txt',
  'pdf',
  'docx',
])

const supportedFiles = computed(() => {
  return files.value.filter((file) => {
    const extension = file.name
      .split('.')
      .pop()
      ?.toLowerCase()

    return (
      extension !== undefined &&
      supportedExtensions.has(extension)
    )
  })
})

const currentSearchResults = computed(() => {
  return searchMode.value === 'semantic'
    ? semanticResults.value
    : searchResults.value
})

const documentCount = computed(
  () => indexedDocuments.value.length,
)

function openFolderPicker() {
  if (!folderInput.value) {
    return
  }

  // Allows selecting the same folder again.
  folderInput.value.value = ''

  folderInput.value.click()
}

function handleFolderChange(event: Event) {
  const input = event.target as HTMLInputElement

  if (!input.files || input.files.length === 0) {
    return
  }

  const selectedFiles = Array.from(input.files)

  files.value = selectedFiles.map((file) => ({
    name: file.name,
    path:
      file.webkitRelativePath || file.name,
    size: file.size,
    type: file.type,
  }))

  const firstPath =
    selectedFiles[0]?.webkitRelativePath

  folderName.value = firstPath
    ? firstPath.split('/')[0]
    : 'Selected folder'

  indexError.value = ''
  lastSync.value = null

  // Folder selection belongs to Documents.
  activeTab.value = 'documents'
}

async function loadDocuments() {
  isLoadingDocuments.value = true
  indexError.value = ''

  try {
    const response = await fetch('/api/documents')

    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`,
      )
    }

    const data = await response.json()

    indexedDocuments.value = data.documents
  } catch (error) {
    indexError.value =
      error instanceof Error
        ? error.message
        : 'Failed to load documents.'
  } finally {
    isLoadingDocuments.value = false
  }
}

async function indexDocuments() {
  if (supportedFiles.value.length === 0) {
    return
  }

  isIndexing.value = true
  indexError.value = ''
  lastSync.value = null

  try {
    const formData = new FormData()

    const metadata = supportedFiles.value.map(
      (file) => ({
        name: file.name,
        path: file.path,
      }),
    )

    const inputFiles = folderInput.value?.files

    if (!inputFiles) {
      throw new Error(
        'Selected files are no longer available.',
      )
    }

    for (const file of supportedFiles.value) {
      const browserFile = Array.from(inputFiles).find(
        (candidate) =>
          (candidate.webkitRelativePath ||
            candidate.name) === file.path,
      )

      if (!browserFile) {
        continue
      }

      formData.append(
        'files',
        browserFile,
      )
    }

    formData.append(
      'metadata',
      JSON.stringify(metadata),
    )

    formData.append(
      'folder_name',
      folderName.value,
    )

    const response = await fetch(
      '/api/documents/sync',
      {
        method: 'POST',
        body: formData,
      },
    )

    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`,
      )
    }

    const result =
      (await response.json()) as SyncResult

    indexedDocuments.value = result.documents

    lastSync.value = {
      created: result.created,
      updated: result.updated,
      unchanged: result.unchanged,
      deleted: result.deleted,
    }
  } catch (error) {
    indexError.value =
      error instanceof Error
        ? error.message
        : 'Failed to index documents.'
  } finally {
    isIndexing.value = false
  }
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
    const response = await fetch(
      `/api/search?q=${encodeURIComponent(query)}`,
    )

    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`,
      )
    }

    const data = await response.json()

    searchResults.value = data.results
  } catch (error) {
    searchError.value =
      error instanceof Error
        ? error.message
        : 'Search failed.'
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
    const response = await fetch(
      `/api/search/semantic?q=${encodeURIComponent(query)}`,
    )

    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`,
      )
    }

    const data =
      await response.json()

    semanticResults.value =
      data.results
  } catch (error) {
    searchError.value =
      error instanceof Error
        ? error.message
        : 'Semantic search failed.'
  } finally {
    isSearching.value = false
  }
}

function performSearch() {
  if (searchMode.value === 'semantic') {
    semanticSearchDocuments()
    return
  }

  searchDocuments()
}

function switchSearchMode(
  mode: SearchMode,
) {
  searchMode.value = mode

  searchResults.value = []
  semanticResults.value = []

  if (searchQuery.value.trim()) {
    performSearch()
  }
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  if (bytes < 1024 * 1024 * 1024) {
    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(1)} MB`
  }

  return `${(
    bytes /
    (1024 * 1024 * 1024)
  ).toFixed(1)} GB`
}

function formatSimilarity(
  similarity: number,
) {
  return `${(
    similarity * 100
  ).toFixed(1)}%`
}

onMounted(() => {
  loadDocuments()
})
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">
          K
        </div>

        <div>
          <p class="brand-name">
            KnowBase
          </p>

          <p class="brand-subtitle">
            Private AI knowledge
          </p>
        </div>
      </div>

      <nav class="main-nav">
        <button
          type="button"
          class="nav-button"
          :class="{
            active: activeTab === 'search',
          }"
          @click="activeTab = 'search'"
        >
          Search
        </button>

        <button
          type="button"
          class="nav-button"
          :class="{
            active:
              activeTab === 'documents',
          }"
          @click="
            activeTab = 'documents'
          "
        >
          Documents

          <span
            v-if="documentCount > 0"
            class="nav-count"
          >
            {{ documentCount }}
          </span>
        </button>
      </nav>
    </header>

    <div class="page">

      <!-- SEARCH -->
      <section
        v-if="activeTab === 'search'"
        class="page-section"
      >
        <div class="page-heading">
          <div>
            <p class="eyebrow">
              KNOWLEDGE SEARCH
            </p>

            <h1>
              Ask your knowledge base.
            </h1>

            <p class="page-description">
              Search through your indexed
              documents without leaving your
              machine.
            </p>
          </div>
        </div>

        <form
          class="search-panel"
          @submit.prevent="performSearch"
        >
          <div class="search-input-wrapper">
            <span class="search-icon">
              ⌕
            </span>

            <input
              v-model="searchQuery"
              type="search"
              placeholder="What do you want to find?"
              autocomplete="off"
            />

            <kbd>Enter</kbd>
          </div>

          <div class="search-toolbar">
            <div class="search-modes">
              <button
                type="button"
                class="mode-button"
                :class="{
                  active:
                    searchMode ===
                    'semantic',
                }"
                @click="
                  switchSearchMode(
                    'semantic',
                  )
                "
              >
                Semantic
              </button>

              <button
                type="button"
                class="mode-button"
                :class="{
                  active:
                    searchMode ===
                    'keyword',
                }"
                @click="
                  switchSearchMode(
                    'keyword',
                  )
                "
              >
                Keyword
              </button>
            </div>

            <button
              type="submit"
              class="primary-button"
              :disabled="
                isSearching ||
                !searchQuery.trim()
              "
            >
              {{
                isSearching
                  ? 'Searching...'
                  : 'Search'
              }}
            </button>
          </div>
        </form>

        <p
          v-if="searchError"
          class="error-message"
        >
          {{ searchError }}
        </p>

        <div
          v-if="!isSearching && searchQuery && currentSearchResults.length === 0 && !searchError"
          class="empty-search"
        >
          <div class="empty-icon">
            ⌕
          </div>

          <h2>
            No results found
          </h2>

          <p>
            Try a different question or
            switch search mode.
          </p>
        </div>

        <div
          v-if="currentSearchResults.length > 0"
          class="results-section"
        >
          <div class="results-header">
            <div>
              <p class="section-label">
                RESULTS
              </p>

              <h2>
                {{
                  currentSearchResults.length
                }}
                result{{
                  currentSearchResults.length ===
                  1
                    ? ''
                    : 's'
                }}
              </h2>
            </div>

            <span class="results-mode">
              {{
                searchMode ===
                'semantic'
                  ? 'Semantic search'
                  : 'Keyword search'
              }}
            </span>
          </div>

          <div class="results-list">
            <article
              v-for="result in currentSearchResults"
              :key="
                result.chunk_id
              "
              class="result-card"
            >
              <div
                class="result-card-top"
              >
                <div
                  class="result-document"
                >
                  <div
                    class="document-icon"
                  >
                    {{
                      result.document_name
                        .toLowerCase()
                        .endsWith(
                          '.pdf',
                        )
                        ? 'PDF'
                        : 'DOC'
                    }}
                  </div>

                  <div
                    class="result-document-info"
                  >
                    <h3>
                      {{
                        result.document_name
                      }}
                    </h3>

                    <p>
                      {{
                        result.document_path
                      }}
                    </p>
                  </div>
                </div>

                <div
                  v-if="
                    searchMode ===
                    'semantic'
                  "
                  class="similarity-badge"
                >
                  {{
                    formatSimilarity(
                      (
                        result as SemanticSearchResult
                      ).similarity,
                    )
                  }}
                </div>
              </div>

              <div class="result-content">
                {{
                  result.content
                }}
              </div>

              <div class="result-footer">
                <span>
                  Chunk
                  {{
                    result.chunk_index +
                    1
                  }}
                </span>

                <button
                  type="button"
                  class="source-button"
                >
                  View source
                </button>
              </div>
            </article>
          </div>
        </div>

        <div
          v-if="
            !isLoadingDocuments &&
            indexedDocuments.length === 0
          "
          class="search-empty-state"
        >
          <p class="section-label">
            GET STARTED
          </p>

          <h2>
            Your knowledge base is empty.
          </h2>

          <p>
            Add documents first, then
            come back here to search them.
          </p>

          <button
            type="button"
            class="secondary-button"
            @click="
              activeTab = 'documents'
            "
          >
            Add documents
          </button>
        </div>
      </section>

      <!-- DOCUMENTS -->
      <section
        v-else
        class="page-section"
      >
        <div class="documents-heading">
          <div>
            <p class="eyebrow">
              KNOWLEDGE BASE
            </p>

            <h1>
              Your documents.
            </h1>

            <p class="page-description">
              Choose a local folder and keep
              your knowledge synchronized.
            </p>
          </div>

          <div class="document-stat">
            <strong>
              {{ documentCount }}
            </strong>

            <span>
              indexed document{{
                documentCount === 1
                  ? ''
                  : 's'
              }}
            </span>
          </div>
        </div>

        <div
          v-if="indexError"
          class="error-message"
        >
          {{ indexError }}
        </div>

        <section
          class="folder-card"
        >
          <div class="folder-card-content">
            <div
              class="folder-icon"
            >
              📁
            </div>

            <div>
              <p class="section-label">
                LOCAL SOURCE
              </p>

              <h2>
                {{
                  folderName ||
                  'Choose a folder'
                }}
              </h2>

              <p>
                Select a folder containing
                the documents you want to
                index.
              </p>
            </div>
          </div>

          <button
            type="button"
            class="secondary-button"
            @click="
              openFolderPicker
            "
          >
            Select folder
          </button>

          <input
            ref="folderInput"
            type="file"
            webkitdirectory
            directory
            multiple
            hidden
            @change="
              handleFolderChange
            "
          />
        </section>

        <section
          v-if="files.length > 0"
          class="selected-folder"
        >
          <div
            class="selected-folder-header"
          >
            <div>
              <p class="section-label">
                SELECTED FOLDER
              </p>

              <h2>
                {{ folderName }}
              </h2>
            </div>

            <div class="file-stats">
              <span>
                {{ files.length }}
                total
              </span>

              <span>
                {{
                  supportedFiles.length
                }}
                supported
              </span>
            </div>
          </div>

          <div
            v-if="
              supportedFiles.length ===
              0
            "
            class="empty-state"
          >
            <h3>
              No supported documents
            </h3>

            <p>
              Supported formats:
              PDF, DOCX, Markdown and TXT.
            </p>
          </div>

          <div
            v-else
            class="file-list"
          >
            <div
              v-for="file in supportedFiles"
              :key="file.path"
              class="file-row"
            >
              <div class="file-main">
                <div
                  class="file-type"
                >
                  {{
                    file.name
                      .split('.')
                      .pop()
                      ?.toUpperCase()
                  }}
                </div>

                <div>
                  <p
                    class="file-name"
                  >
                    {{ file.name }}
                  </p>

                  <p
                    class="file-path"
                  >
                    {{ file.path }}
                  </p>
                </div>
              </div>

              <span
                class="file-size"
              >
                {{
                  formatFileSize(
                    file.size,
                  )
                }}
              </span>
            </div>
          </div>

          <div
            class="index-action"
          >
            <div>
              <strong>
                Ready to synchronize
              </strong>

              <p>
                New, changed and deleted
                documents will be detected
                automatically.
              </p>
            </div>

            <button
              type="button"
              class="primary-button"
              :disabled="
                isIndexing ||
                supportedFiles.length ===
                  0
              "
              @click="
                indexDocuments
              "
            >
              {{
                isIndexing
                  ? 'Indexing...'
                  : 'Index documents'
              }}
            </button>
          </div>
        </section>

        <div
          v-if="lastSync"
          class="sync-summary"
        >
          <div>
            <span class="sync-number">
              {{ lastSync.created }}
            </span>

            <span>added</span>
          </div>

          <div>
            <span class="sync-number">
              {{ lastSync.updated }}
            </span>

            <span>updated</span>
          </div>

          <div>
            <span class="sync-number">
              {{ lastSync.unchanged }}
            </span>

            <span>unchanged</span>
          </div>

          <div>
            <span class="sync-number">
              {{ lastSync.deleted }}
            </span>

            <span>deleted</span>
          </div>
        </div>

        <section
          class="knowledge-section"
        >
          <div
            class="section-header"
          >
            <div>
              <p class="section-label">
                INDEXED DOCUMENTS
              </p>

              <h2>
                {{
                  documentCount
                }}
                document{{
                  documentCount ===
                  1
                    ? ''
                    : 's'
                }}
              </h2>
            </div>
          </div>

          <div
            v-if="isLoadingDocuments"
            class="loading-state"
          >
            Loading documents...
          </div>

          <div
            v-else-if="
              indexedDocuments.length ===
              0
            "
            class="empty-state"
          >
            <h3>
              No documents indexed yet.
            </h3>

            <p>
              Select a folder above to
              start building your local
              knowledge base.
            </p>
          </div>

          <div
            v-else
            class="indexed-list"
          >
            <article
              v-for="document in indexedDocuments"
              :key="document.id"
              class="indexed-card"
            >
              <div
                class="indexed-card-main"
              >
                <div
                  class="document-icon"
                >
                  {{
                    document.extension
                      .replace(
                        '.',
                        '',
                      )
                      .toUpperCase()
                  }}
                </div>

                <div
                  class="indexed-info"
                >
                  <h3>
                    {{
                      document.name
                    }}
                  </h3>

                  <p>
                    {{
                      document.path
                    }}
                  </p>
                </div>
              </div>

              <div
                class="indexed-meta"
              >
                <span>
                  {{
                    document.chunk_count
                  }}
                  chunks
                </span>

                <span>
                  {{
                    formatFileSize(
                      document.size,
                    )
                  }}
                </span>
              </div>
            </article>
          </div>
        </section>
      </section>
    </div>
  </main>
</template>
