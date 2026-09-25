<script setup lang="ts">
import { ref } from 'vue'

const inputRef = ref<HTMLInputElement | null>(null)

const emit = defineEmits<{
  selected: [files: File[]]
}>()

function openPicker() {
  inputRef.value?.click()
}

function handleChange(event: Event) {
  const input = event.target as HTMLInputElement

  if (!input.files || input.files.length === 0) {
    return
  }

  emit('selected', Array.from(input.files))

  // Allow selecting the same folder again.
  input.value = ''
}
</script>

<template>
  <section class="folder-card">
    <div class="folder-card-content">
      <div class="folder-icon">📁</div>

      <div>
        <p class="section-label">LOCAL SOURCE</p>

        <h2>
          <slot name="folder-name"> Choose a folder </slot>
        </h2>

        <p>Select a folder containing the documents you want to index.</p>
      </div>
    </div>

    <button type="button" class="secondary-button" @click="openPicker">Select folder</button>

    <input
      ref="inputRef"
      type="file"
      webkitdirectory
      directory
      multiple
      hidden
      @change="handleChange"
    />
  </section>
</template>
