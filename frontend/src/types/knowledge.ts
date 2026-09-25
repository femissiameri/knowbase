export type Tab = 'search' | 'documents'

export type SearchMode = 'hybrid' | 'semantic' | 'keyword'

export interface LocalFile {
  name: string
  path: string
  size: number
  type: string
}

export interface IndexedDocument {
  id: number
  name: string
  path: string
  size: number
  content_type: string | null
  extension: string
  text_length: number
  text_preview: string
  chunk_count: number
}

export interface SearchResult {
  chunk_id: number
  document_id: number
  document_name: string
  document_path: string
  chunk_index: number
  content: string
  page_number: number | null
  section: string | null
}

export interface SemanticSearchResult extends SearchResult {
  similarity: number
}

export interface HybridSearchResult extends SearchResult {
  similarity: number | null
  matched_by: string[]
}

export type SearchResultItem = SearchResult | SemanticSearchResult | HybridSearchResult

export interface SyncResult {
  created: number
  updated: number
  unchanged: number
  deleted: number
  documents: IndexedDocument[]
}

export interface SyncSummary {
  created: number
  updated: number
  unchanged: number
  deleted: number
}

export interface RAGSource {
  reference: number
  chunk_id: number
  document_id: number
  document_name: string
  document_path: string
  chunk_index: number
  page_number: number | null
  section: string | null
}

export interface RAGAnswerResponse {
  query: string
  answer: string
  sources: RAGSource[]
}
