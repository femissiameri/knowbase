<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
} from 'vue'

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
}

interface SyncResult {
  created: number
  updated: number
  unchanged: number
  deleted: number
  documents: IndexedDocument[]
}

const supportedExtensions = new Set(['txt', 'md', 'pdf', 'docx']);

const folderInput = ref<HTMLInputElement | null>(null)
const files = ref<LocalFile[]>([])
const folderName = ref<string>('')

const isIndexing = ref(false)
const indexError = ref('')
const indexedDocuments = ref<IndexedDocument[]>([])

const isLoadingDocuments = ref(false)

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


const supportedFiles = computed(() => {
  return files.value.filter(file => {
    const extension = file.name.split('.').pop()?.toLowerCase()

    return extension ? supportedExtensions.has(extension) : false
  })
})

function openFolderPicker() {
  folderInput.value?.click()
}

function handleFolderChange(event: Event) {
  const input = event.target as HTMLInputElement

  if (!input.files || input.files.length === 0) {
    return
  }

  const selectedFiles = Array.from(input.files)

  files.value = selectedFiles.map((file) => ({
    name: file.name,
    path: file.webkitRelativePath || file.name,
    size: file.size,
    type: file.type,
  }))

  const firstPath = selectedFiles.length > 0 ? selectedFiles[0]?.webkitRelativePath : undefined

  if (firstPath) {
    folderName.value = firstPath.split('/')[0] || ''
  } else {
    folderName.value = 'Selected folder'
  }
}


function formatFileSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function indexDocuments() {
  if (supportedFiles.value.length === 0) {
    return
  }

  isIndexing.value = true
  indexError.value = ''

  try {
    const formData = new FormData()

    const metadata = supportedFiles.value.map((file) => ({
      name: file.name,
      path: file.path,
    }))

    for (const file of supportedFiles.value) {
      const localFile = files.value.find(
        (candidate) => candidate.path === file.path,
      )

      if (!localFile) {
        continue
      }

      const inputFiles = folderInput.value?.files

      if (!inputFiles) {
        continue
      }

      const browserFile = Array.from(inputFiles).find(
        (candidate) =>
          (candidate.webkitRelativePath || candidate.name) === file.path,
      )

      if (!browserFile) {
        continue
      }

      formData.append('files', browserFile)
    }

    formData.append('metadata', JSON.stringify(metadata))
    formData.append('folder_name', folderName.value)

    const response = await fetch('/api/documents/sync', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()

    const result = data as SyncResult

    indexedDocuments.value = result.documents

    console.log('Sync result:', {
      created: result.created,
      updated: result.updated,
      unchanged: result.unchanged,
      deleted: result.deleted,
    })

  } catch (error) {
    indexError.value =
      error instanceof Error
        ? error.message
        : 'Failed to index files.'
  } finally {
    isIndexing.value = false
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<template>
  <main class="app">
    <section class="hero">
      <p class="eyebrow">KNOWBASE</p>

      <h1>Your private AI knowledge base.</h1>

      <p class="description">
        Search and understand your documents locally, with your knowledge
        staying on your machine.
      </p>

      <input ref="folderInput" type="file" webkitdirectory directory multiple hidden @change="handleFolderChange" />

      <button class="select-button" type="button" @click="openFolderPicker">
        Select a folder
      </button>


      <div v-if="files.length > 0" class="files-section">
        <div class="files-header">
          <div>
            <p class="folder-name">{{ folderName }}</p>
            <p class="file-count">
              {{ files.length }} total · {{ supportedFiles.length }} supported
            </p>
          </div>
        </div>

        <div v-if="supportedFiles.length === 0" class="empty-state">
          <p>No supported documents found.</p>
          <span>
            Supported formats: PDF, DOCX, DOC, Markdown and TXT.
          </span>
        </div>

        <div v-else class="files-list">
          <div v-for="file in supportedFiles" :key="file.path" class="file-row">
            <div class="file-info">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-path">{{ file.path }}</span>
            </div>

            <span class="file-size">
              {{ formatFileSize(file.size) }}
            </span>
          </div>
        </div>

        <button v-if="supportedFiles.length > 0" class="index-button" type="button" :disabled="isIndexing"
          @click="indexDocuments">
          {{ isIndexing ? 'Indexing...' : 'Index documents' }}
        </button>

        <p v-if="indexError" class="error-message">
          {{ indexError }}
        </p>
      </div>

      <section class="indexed-section">
        <div class="indexed-header">
          <div>
            <p class="indexed-title">Knowledge base</p>

            <p class="indexed-count">
              <template v-if="isLoadingDocuments">
                Loading documents...
              </template>

              <template v-else>
                {{ indexedDocuments.length }}
                document{{ indexedDocuments.length === 1 ? '' : 's' }}
              </template>
            </p>
          </div>
        </div>

        <div v-if="!isLoadingDocuments && indexedDocuments.length === 0" class="empty-state">
          <p>Your knowledge base is empty.</p>

          <span>
            Select a folder and index some documents to get started.
          </span>
        </div>

        <div v-else-if="!isLoadingDocuments" class="indexed-list">
          <div v-for="document in indexedDocuments" :key="document.id" class="indexed-document">
            <div class="indexed-row">
              <div class="file-info">
                <span class="file-name">
                  {{ document.name }}
                </span>

                <span class="file-path">
                  {{ document.path }}
                </span>
              </div>

              <span class="file-size">
                {{ formatFileSize(document.size) }}
              </span>
            </div>

            <div class="indexed-preview">
              <span>
                {{ document.text_length }} characters extracted
              </span>

              <pre>{{ document.text_preview }}</pre>
            </div>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped></style>
