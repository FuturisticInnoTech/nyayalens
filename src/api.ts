import type { Answer, Comparison, Document } from './types'
import { firebaseEnabled, getFirebaseToken } from './firebase'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
let sessionPromise: Promise<void> | undefined

async function ensureSession() {
  const firebaseToken = await getFirebaseToken()
  if (firebaseToken) return firebaseToken
  if (firebaseEnabled) throw new Error('Sign in to continue')
  sessionPromise ??= fetch(`${API}/auth/demo`, { method: 'POST', credentials: 'include' }).then(response => {
    if (!response.ok) throw new Error('Could not initialize the demo session')
  })
  await sessionPromise
  return null
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await ensureSession()
  const response = await fetch(`${API}${path}`, { ...init, credentials: 'include', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers } })
  if (!response.ok) throw new Error((await response.json()).detail ?? 'Request failed')
  return response.json() as Promise<T>
}

export const api = {
  documents: () => request<Document[]>('/documents'),
  document: (id: string) => request<Document>(`/documents/${id}`),
  upload: async (file: File) => {
    const token = await ensureSession()
    const response = await fetch(`${API}/documents`, { method: 'POST', credentials: 'include', headers: token ? { Authorization: `Bearer ${token}` } : {}, body: (() => { const form = new FormData(); form.append('file', file); return form })() })
    if (!response.ok) throw new Error((await response.json()).detail ?? 'Upload failed')
    return response.json() as Promise<Document>
  },
  question: (id: string, question: string) => request<Answer>(`/documents/${id}/questions`, { method: 'POST', body: JSON.stringify({ question }) }),
  compare: (left: string, right: string) => request<Comparison>('/comparisons', { method: 'POST', body: JSON.stringify({ left_document_id: left, right_document_id: right }) }),
  exportBrief: async (id: string) => { const token = await ensureSession(); const response = await fetch(`${API}/documents/${id}/export`, { credentials: 'include', headers: token ? { Authorization: `Bearer ${token}` } : {} }); if (!response.ok) throw new Error('Could not export the action brief'); return response.text() },
}
