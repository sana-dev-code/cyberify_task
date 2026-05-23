import { FormEvent, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

type Props = {
  title: string
  submitLabel: string
  loadingLabel: string
  footerText: string
  footerLink: string
  footerLinkLabel: string
  onSubmit: (email: string, password: string) => Promise<void>
}

export function AuthForm({
  title,
  submitLabel,
  loadingLabel,
  footerText,
  footerLink,
  footerLinkLabel,
  onSubmit,
}: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await onSubmit(email, password)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError('Wrong email or password.')
        } else if (typeof err.response?.data?.detail === 'string') {
          setError(err.response.data.detail)
        } else if (!err.response) {
          setError('Cannot reach the server. Start the backend on port 8000.')
        } else {
          setError('Something went wrong. Try again.')
        }
      } else {
        setError('Something went wrong. Try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-chat-bg px-4">
      <div className="w-full max-w-sm">
        <h1 className="mb-8 text-center text-2xl font-semibold text-white">{title}</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-chat-border bg-chat-panel px-4 py-3 text-white placeholder:text-chat-muted focus:border-white/30 focus:outline-none"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full rounded-lg border border-chat-border bg-chat-panel px-4 py-3 text-white placeholder:text-chat-muted focus:border-white/30 focus:outline-none"
          />

          {error && <p className="text-center text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-white py-3 font-medium text-black hover:bg-gray-200 disabled:opacity-60"
          >
            {loading ? loadingLabel : submitLabel}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-chat-muted">
          {footerText}{' '}
          <Link to={footerLink} className="text-white underline hover:no-underline">
            {footerLinkLabel}
          </Link>
        </p>
      </div>
    </div>
  )
}
