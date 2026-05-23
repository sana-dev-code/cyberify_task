import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from 'react'
import axios from 'axios'

import api from '../lib/api'
import { useAuth } from '../context/AuthContext'

type DocumentItem = {
  id: string
  filename: string
  enabled: boolean
}

type Source = {
  id: string
  filename: string
  chunk_text: string
  page_number?: number | null
  score?: number | null
}

type Message = {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

export function DashboardPage() {
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hi! Upload a PDF or text file from the sidebar, then ask me anything about it.',
    },
  ])
  const [input, setInput] = useState('')
  const [thinking, setThinking] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  async function loadDocuments() {
    try {
      const res = await api.get<{ documents: DocumentItem[] }>('/documents')
      setDocuments(res.data.documents)
    } catch {
      setError('Could not load your files.')
    }
  }

  async function uploadFile(e: FormEvent) {
    e.preventDefault()
    if (!file) return

    setUploading(true)
    setError('')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const count = res.data.chunk_count as number
      if (count < 1) {
        setError('No text found in that file. Try a normal PDF, not a scan.')
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Got it — I indexed "${res.data.filename}" (${count} sections). Ask me something about it.`,
          },
        ])
      }
      setFile(null)
      await loadDocuments()
    } catch {
      setError('Upload failed. Is the backend running?')
    } finally {
      setUploading(false)
    }
  }

  async function sendMessage(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || thinking) return

    setInput('')
    setThinking(true)
    setError('')
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content: text }])

    try {
      const res = await api.post<{ answer: string; sources: Source[] }>('/ask', { question: text })
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: res.data.answer,
          sources: res.data.sources,
        },
      ])
    } catch (err) {
      if (axios.isAxiosError(err) && !err.response) {
        setError('Cannot reach the server.')
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: 'Sorry, I could not answer that. Make sure you uploaded a file and it is turned on in the sidebar.',
          },
        ])
      }
    } finally {
      setThinking(false)
    }
  }

  async function toggleDoc(id: string, enabled: boolean) {
    try {
      await api.patch(`/documents/${id}/enabled`, null, { params: { enabled } })
      setDocuments((docs) => docs.map((d) => (d.id === id ? { ...d, enabled } : d)))
    } catch {
      setError('Could not update that file.')
    }
  }

  async function deleteDoc(id: string) {
    if (!confirm('Delete this file from your knowledge base?')) return
    try {
      await api.delete(`/documents/${id}`)
      setDocuments((docs) => docs.filter((d) => d.id !== id))
    } catch {
      setError('Delete failed.')
    }
  }

  function newChat() {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'New chat started. Ask me about your uploaded documents.',
      },
    ])
    setError('')
  }

  function onComposerKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(e as unknown as FormEvent)
    }
  }

  const enabledCount = documents.filter((d) => d.enabled).length

  return (
    <div className="flex h-full min-h-screen">
      {/* Sidebar */}
      <aside
        className={`flex shrink-0 flex-col overflow-hidden border-r border-chat-border bg-chat-sidebar transition-[width] ${sidebarOpen ? 'w-64' : 'w-0'}`}
      >
        <div className="flex flex-col gap-2 p-3">
          <button
            type="button"
            onClick={newChat}
            className="rounded-lg border border-chat-border px-3 py-2 text-left text-sm hover:bg-chat-panel"
          >
            + New chat
          </button>
        </div>

        <div className="border-t border-chat-border p-3">
          <p className="mb-2 text-xs font-medium text-chat-muted">Upload</p>
          <form onSubmit={uploadFile} className="space-y-2">
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="w-full text-xs text-chat-muted file:mr-2 file:rounded file:border-0 file:bg-white file:px-2 file:py-1 file:text-xs file:text-black"
            />
            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full rounded-lg bg-chat-panel py-2 text-sm hover:bg-[#3a3a3a] disabled:opacity-50"
            >
              {uploading ? 'Indexing...' : 'Upload file'}
            </button>
          </form>
        </div>

        <div className="flex-1 overflow-y-auto border-t border-chat-border p-3">
          <p className="mb-2 text-xs text-chat-muted">
            Your files ({enabledCount} active)
          </p>
          {documents.length === 0 && (
            <p className="text-xs text-chat-muted">No files yet</p>
          )}
          <ul className="space-y-1">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="group flex items-center gap-2 rounded-lg px-2 py-2 text-sm hover:bg-chat-panel"
              >
                <button
                  type="button"
                  onClick={() => toggleDoc(doc.id, !doc.enabled)}
                  title={doc.enabled ? 'Active in search' : 'Click to include in search'}
                  className={`h-2 w-2 shrink-0 rounded-full ${doc.enabled ? 'bg-green-500' : 'bg-gray-600'}`}
                />
                <span className="min-w-0 flex-1 truncate" title={doc.filename}>
                  {doc.filename}
                </span>
                <button
                  type="button"
                  onClick={() => deleteDoc(doc.id)}
                  className="hidden text-xs text-chat-muted group-hover:inline hover:text-red-400"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="border-t border-chat-border p-3">
          <p className="truncate text-xs text-chat-muted">{user?.email}</p>
          <button
            type="button"
            onClick={logout}
            className="mt-2 w-full rounded-lg py-2 text-sm text-chat-muted hover:bg-chat-panel hover:text-white"
          >
            Log out
          </button>
        </div>
      </aside>

      {/* Main chat */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-chat-border px-4 py-3">
          <button
            type="button"
            onClick={() => setSidebarOpen((v) => !v)}
            className="rounded-lg px-2 py-1 text-sm hover:bg-chat-panel"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? 'Hide panel' : 'Show panel'}
          </button>
          <h1 className="text-sm font-medium">Document Chat</h1>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl px-4 py-8">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`mb-8 ${msg.role === 'user' ? 'flex justify-end' : ''}`}
              >
                {msg.role === 'assistant' && (
                  <div className="mb-2 flex h-7 w-7 items-center justify-center rounded-sm bg-[#19c37d] text-xs font-bold text-white">
                    AI
                  </div>
                )}
                <div
                  className={
                    msg.role === 'user'
                      ? 'max-w-[85%] rounded-3xl bg-[#2f2f2f] px-4 py-3 text-[15px] leading-7 text-[#ececec]'
                      : 'text-[15px] leading-7 text-[#ececec]'
                  }
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 space-y-2 border-t border-chat-border pt-4">
                      <p className="text-xs text-chat-muted">Sources</p>
                      {msg.sources.map((s) => (
                        <div
                          key={s.id}
                          className="rounded-lg bg-chat-panel px-3 py-2 text-xs text-chat-muted"
                        >
                          <span className="text-white">{s.filename}</span>
                          {s.page_number != null && ` · p.${s.page_number}`}
                          <p className="mt-1 line-clamp-3">{s.chunk_text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {thinking && (
              <div className="mb-8">
                <div className="mb-2 flex h-7 w-7 items-center justify-center rounded-sm bg-[#19c37d] text-xs font-bold text-white">
                  AI
                </div>
                <p className="text-chat-muted">Thinking...</p>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {error && (
          <p className="mx-auto max-w-3xl px-4 pb-2 text-center text-sm text-red-400">{error}</p>
        )}

        <div className="border-t border-chat-border bg-chat-bg px-4 py-4">
          <form onSubmit={sendMessage} className="mx-auto flex max-w-3xl items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onComposerKeyDown}
              rows={1}
              placeholder="Message Document Chat..."
              className="composer-input max-h-40 min-h-[52px] flex-1 rounded-3xl border border-[#565869] bg-[#40414f] px-4 py-3 text-[15px] leading-6 text-[#ececec] caret-[#ececec] placeholder:text-[#8e8ea0] focus:border-[#8e8ea0] focus:outline-none focus:ring-0"
            />
            <button
              type="submit"
              disabled={thinking || !input.trim()}
              className="rounded-lg bg-white px-4 py-3 text-sm font-medium text-black hover:bg-gray-200 disabled:opacity-40"
            >
              Send
            </button>
          </form>
          <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-chat-muted">
            Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}
