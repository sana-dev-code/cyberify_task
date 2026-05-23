import { useNavigate } from 'react-router-dom'

import { AuthForm } from '../components/AuthForm'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  return (
    <AuthForm
      title="Welcome back"
      submitLabel="Continue"
      loadingLabel="Signing in..."
      footerText="No account?"
      footerLink="/register"
      footerLinkLabel="Sign up"
      onSubmit={async (email, password) => {
        await login(email, password)
        navigate('/', { replace: true })
      }}
    />
  )
}
