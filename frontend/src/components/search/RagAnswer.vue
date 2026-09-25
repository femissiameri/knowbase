<script setup lang="ts">
import type { RAGSource } from '@/types/knowledge'
import SourceList from './SourceList.vue'

defineProps<{
  answer: string
  sources: RAGSource[]
  isAsking: boolean
}>()
</script>

<template>
  <section v-if="isAsking || answer" class="answer-section">
    <div class="answer-header">
      <div>
        <p class="section-label">KNOWBASE ANSWER</p>
        <h2>Answer</h2>
      </div>

      <span v-if="isAsking" class="answer-status"> Generating locally </span>
    </div>

    <div v-if="isAsking" class="answer-card answer-loading">
      <div class="loading-indicator"></div>

      <div>
        <strong>Thinking...</strong>
        <p>Searching your documents and generating a grounded answer.</p>
      </div>
    </div>

    <div v-else class="answer-card">
      <div class="answer-content">
        {{ answer }}
      </div>
    </div>

    <SourceList v-if="!isAsking && sources.length > 0" :sources="sources" />
  </section>
</template>
