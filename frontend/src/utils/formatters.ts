import type { SearchResultItem } from '@/types/knowledge'

export function getFileType(filename: string): string {
  return filename.split('.').pop()?.toUpperCase() || 'DOC'
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  if (bytes < 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}

export function getResultPreview(content: string, maxLength = 360): string {
  if (content.length <= maxLength) {
    return content
  }

  return `${content.slice(0, maxLength).trim()}...`
}

export function isLongResult(content: string, maxLength = 360): boolean {
  return content.length > maxLength
}

export function getSimilarity(result: SearchResultItem): number | null {
  if ('similarity' in result) {
    return result.similarity
  }

  return null
}

export function formatResultSimilarity(result: SearchResultItem): string {
  const similarity = getSimilarity(result)

  if (similarity === null) {
    return ''
  }

  return `${(similarity * 100).toFixed(1)}%`
}

export function getMatchedBy(result: SearchResultItem): string[] {
  if ('matched_by' in result) {
    return result.matched_by
  }

  if ('similarity' in result) {
    return ['semantic']
  }

  return ['keyword']
}
