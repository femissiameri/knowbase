<script setup lang="ts">
import { computed, ref } from 'vue'

interface LocalFile {
  name: string
  path: string
  size: number
  type: string
}

const supportedExtensions = new Set(['txt', 'md', 'pdf', 'doc', 'docx']);

const folderInput = ref<HTMLInputElement | null>(null)
const files = ref<LocalFile[]>([])
const folderName = ref<string|undefined>('')

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
    folderName.value = firstPath.split('/')[0]
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

      <input
        ref="folderInput"
        type="file"
        webkitdirectory
        directory
        multiple
        hidden
        @change="handleFolderChange"
      />

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
      </div>
    </section>
  </main>
</template>

<style scoped></style>
