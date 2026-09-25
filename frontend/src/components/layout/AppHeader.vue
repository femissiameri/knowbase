<script setup lang="ts">
import type { Tab } from '@/types/knowledge'

defineProps<{
  activeTab: Tab
  documentCount: number
}>()

const emit = defineEmits<{
  'update:activeTab': [tab: Tab]
}>()
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">K</div>

      <div>
        <p class="brand-name">KnowBase</p>
        <p class="brand-subtitle">Private AI knowledge</p>
      </div>
    </div>

    <nav class="main-nav" aria-label="Primary navigation">
      <button
        type="button"
        class="nav-button"
        :class="{ active: activeTab === 'search' }"
        @click="emit('update:activeTab', 'search')"
      >
        Search
      </button>

      <button
        type="button"
        class="nav-button"
        :class="{ active: activeTab === 'documents' }"
        @click="emit('update:activeTab', 'documents')"
      >
        Documents

        <span v-if="documentCount > 0" class="nav-count">
          {{ documentCount }}
        </span>
      </button>
    </nav>
  </header>
</template>
