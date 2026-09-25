<script setup lang="ts">
import type { SyncSummary } from '@/types/knowledge'

defineProps<{
  summary: SyncSummary | null
}>()
</script>

<template>
  <div v-if="summary" class="sync-summary">
    <div>
      <span class="sync-number">
        {{ summary.created }}
      </span>
      <span>added</span>
    </div>

    <div>
      <span class="sync-number">
        {{ summary.updated }}
      </span>
      <span>updated</span>
    </div>

    <div>
      <span class="sync-number">
        {{ summary.unchanged }}
      </span>
      <span>unchanged</span>
    </div>

    <div>
      <span class="sync-number">
        {{ summary.deleted }}
      </span>
      <span>deleted</span>
    </div>
  </div>
</template>
