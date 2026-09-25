<script setup lang="ts">
import type { SearchMode } from '@/types/knowledge'

defineProps<{
  modelValue: string
  mode: SearchMode
  isAsking: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:mode': [value: SearchMode]
  search: []
  ask: []
}>()
</script>

<template>
  <form class="search-panel" @submit.prevent="emit('search')">
    <div class="search-input-wrapper">
      <span class="search-icon" aria-hidden="true">⌕</span>

      <input
        :value="modelValue"
        type="search"
        placeholder="What do you want to find?"
        autocomplete="off"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />

      <kbd>Enter</kbd>
    </div>

    <div class="search-toolbar">
      <div class="search-modes">
        <button
          type="button"
          class="mode-button"
          :class="{ active: mode === 'hybrid' }"
          @click="emit('update:mode', 'hybrid')"
        >
          Hybrid
        </button>

        <button
          type="button"
          class="mode-button"
          :class="{ active: mode === 'semantic' }"
          @click="emit('update:mode', 'semantic')"
        >
          Semantic
        </button>

        <button
          type="button"
          class="mode-button"
          :class="{ active: mode === 'keyword' }"
          @click="emit('update:mode', 'keyword')"
        >
          Keyword
        </button>
      </div>

      <button
        type="button"
        class="primary-button"
        :disabled="isAsking || !modelValue.trim()"
        @click="emit('ask')"
      >
        {{ isAsking ? 'Thinking...' : 'Ask' }}
      </button>
    </div>
  </form>
</template>
