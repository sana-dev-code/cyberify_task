import { useNavigate } from 'react-router-dom'

import { AuthForm } from '../components/AuthForm'
import { useAuth } from '../context/AuthContext'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  return (
    <AuthForm
      title="Create your account"
      submitLabel="Sign up"
      loadingLabel="Creating account..."
      footerText="Already have an account?"
      footerLink="/login"
      footerLinkLabel="Log in"
      onSubmit={async (email, password) => {
        await register(email, password)
        navigate('/', { replace: true })
      }}
    />
  )
}
