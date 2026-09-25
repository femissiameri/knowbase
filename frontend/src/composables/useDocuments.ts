import { computed, ref } from 'vue'
import type { IndexedDocument, LocalFile, SyncResult, SyncSummary } from '@/types/knowledge'

const SUPPORTED_EXTENSIONS = new Set(['md', 'txt', 'pdf', 'docx'])

function toLocalFile(file: File): LocalFile {
  return {
    name: file.name,
    path: file.webkitRelativePath || file.name,
    size: file.size,
    type: file.type,
  }
}

export function useDocuments() {
  const browserFiles = ref<File[]>([])
  const files = ref<LocalFile[]>([])
  const folderName = ref('')
  const indexedDocuments = ref<IndexedDocument[]>([])

  const isLoadingDocuments = ref(false)
  const isIndexing = ref(false)
  const indexError = ref('')
  const lastSync = ref<SyncSummary | null>(null)

  const supportedFiles = computed(() =>
    files.value.filter((file) => {
      const extension = file.name.split('.').pop()?.toLowerCase()

      return extension !== undefined && SUPPORTED_EXTENSIONS.has(extension)
    }),
  )

  const documentCount = computed(() => indexedDocuments.value.length)

  function selectFolder(selectedFiles: File[]) {
    browserFiles.value = selectedFiles
    files.value = selectedFiles.map(toLocalFile)

    const firstPath = selectedFiles[0]?.webkitRelativePath

    folderName.value = firstPath ? firstPath.split('/')[0] : 'Selected folder'

    indexError.value = ''
    lastSync.value = null
  }

  async function loadDocuments() {
    isLoadingDocuments.value = true
    indexError.value = ''

    try {
      const response = await fetch('/api/documents')

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = await response.json()
      indexedDocuments.value = data.documents
    } catch (error) {
      indexError.value = error instanceof Error ? error.message : 'Failed to load documents.'
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

      const metadata = supportedFiles.value.map((file) => ({
        name: file.name,
        path: file.path,
      }))

      for (const localFile of supportedFiles.value) {
        const browserFile = browserFiles.value.find(
          (candidate) => (candidate.webkitRelativePath || candidate.name) === localFile.path,
        )

        if (browserFile) {
          formData.append('files', browserFile)
        }
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

      const result = (await response.json()) as SyncResult

      indexedDocuments.value = result.documents
      lastSync.value = {
        created: result.created,
        updated: result.updated,
        unchanged: result.unchanged,
        deleted: result.deleted,
      }
    } catch (error) {
      indexError.value = error instanceof Error ? error.message : 'Failed to index documents.'
    } finally {
      isIndexing.value = false
    }
  }

  return {
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
  }
}
