<script setup lang="ts">
withDefaults(
  defineProps<{
    eyebrow: string
    title: string
    description: string
    actionLabel?: string
    variant?: 'empty-search' | 'search-empty-state'
    icon?: string
  }>(),
  {
    actionLabel: undefined,
    variant: 'empty-search',
    icon: '⌕',
  },
)

const emit = defineEmits<{
  action: []
}>()
</script>

<template>
  <div :class="variant">
    <div v-if="icon" class="empty-icon" aria-hidden="true">
      {{ icon }}
    </div>

    <p class="section-label">
      {{ eyebrow }}
    </p>

    <h2>
      {{ title }}
    </h2>

    <p>
      {{ description }}
    </p>

    <button v-if="actionLabel" type="button" class="secondary-button" @click="emit('action')">
      {{ actionLabel }}
    </button>
  </div>
</template>
