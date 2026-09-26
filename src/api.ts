import type { Answer, Comparison, Document } from './types'
import { firebaseEnabled, getFirebaseToken } from './firebase'

const API = (import.meta.env.VITE_API_URL?.trim() || '/api/v1').replace(/\/$/, '')
let sessionPromise: Promise<void> | undefined

async function responseError(response: Response, fallback: string) {
  try {
    const payload = await response.json() as { detail?: string }
    return new Error(payload.detail ?? fallback)
  } catch {
    return new Error(`${fallback} (${response.status})`)
  }
}

function networkError(error: unknown): never {
  if (error instanceof TypeError) {
    throw new Error(`Could not reach the NyayaLens API at ${API}. Configure VITE_API_URL for the deployed API or proxy /api/v1 to it.`)
  }
  throw error
}

async function ensureSession() {
  const firebaseToken = await getFirebaseToken()
  if (firebaseToken) return firebaseToken
  if (firebaseEnabled) throw new Error('Sign in to continue')
  sessionPromise ??= fetch(`${API}/auth/demo`, { method: 'POST', credentials: 'include' }).then(response => {
    if (!response.ok) return responseError(response, 'Could not initialize the demo session').then(error => { throw error })
  }).catch(networkError)
  await sessionPromise
  return null
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await ensureSession()
  let response: Response
  try {
    response = await fetch(`${API}${path}`, { ...init, credentials: 'include', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers } })
  } catch (error) {
    return networkError(error)
  }
  if (!response.ok) throw await responseError(response, 'Request failed')
  return response.json() as Promise<T>
}

export const api = {
  documents: () => request<Document[]>('/documents'),
  document: (id: string) => request<Document>(`/documents/${id}`),
  upload: async (file: File) => {
    const token = await ensureSession()
    let response: Response
    try {
      response = await fetch(`${API}/documents`, { method: 'POST', credentials: 'include', headers: token ? { Authorization: `Bearer ${token}` } : {}, body: (() => { const form = new FormData(); form.append('file', file); return form })() })
    } catch (error) {
      return networkError(error)
    }
    if (!response.ok) throw await responseError(response, 'Upload failed')
    return response.json() as Promise<Document>
  },
  question: (id: string, question: string) => request<Answer>(`/documents/${id}/questions`, { method: 'POST', body: JSON.stringify({ question }) }),
  compare: (left: string, right: string) => request<Comparison>('/comparisons', { method: 'POST', body: JSON.stringify({ left_document_id: left, right_document_id: right }) }),
  exportBrief: async (id: string) => { const token = await ensureSession(); const response = await fetch(`${API}/documents/${id}/export`, { credentials: 'include', headers: token ? { Authorization: `Bearer ${token}` } : {} }); if (!response.ok) throw new Error('Could not export the action brief'); return response.text() },
}
