import { ref } from 'vue'
import type { RAGAnswerResponse, RAGSource } from '@/types/knowledge'

export function useRag() {
  const ragAnswer = ref('')
  const ragSources = ref<RAGSource[]>([])
  const isAsking = ref(false)
  const ragError = ref('')

  async function ask(query: string) {
    const normalizedQuery = query.trim()

    if (!normalizedQuery) {
      return
    }

    isAsking.value = true
    ragError.value = ''
    ragAnswer.value = ''
    ragSources.value = []

    try {
      const response = await fetch(`/api/rag/answer?q=${encodeURIComponent(normalizedQuery)}`)

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = (await response.json()) as RAGAnswerResponse

      ragAnswer.value = data.answer
      ragSources.value = data.sources
    } catch (error) {
      ragError.value = error instanceof Error ? error.message : 'Failed to generate an answer.'
    } finally {
      isAsking.value = false
    }
  }

  function clear() {
    ragAnswer.value = ''
    ragSources.value = []
    ragError.value = ''
  }

  return {
    ragAnswer,
    ragSources,
    isAsking,
    ragError,
    ask,
    clear,
  }
}
