import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { AcademicCapIcon } from '@heroicons/react/24/outline'
import { authService } from '../../services/api'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authService.login({ email, password })
      setAuth(res.data.user, res.data.access_token)
      toast.success(`Bienvenido, ${res.data.user.full_name.split(' ')[0]}`)
      navigate(res.data.user.role === 'student' ? '/' : '/admin')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Credenciales incorrectas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-700 px-4">
      <div className="card w-full max-w-sm p-8">
        <div className="text-center mb-6">
          <AcademicCapIcon className="w-12 h-12 text-blue-700 mx-auto mb-2" />
          <h1 className="text-xl font-bold text-gray-900">Iniciar sesión</h1>
          <p className="text-sm text-gray-500 mt-1">Facultad de Tecnología USFX</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="input-field"
              placeholder="tu@correo.bo"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="input-field"
              placeholder="••••••••"
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <Link to="/" className="text-sm text-gray-500 hover:text-blue-700">
            ← Volver al inicio
          </Link>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-100 text-xs text-gray-400 text-center space-y-1">
          <p className="font-medium text-gray-500">Demo</p>
          <p>Admin: admin@usfx.bo / admin2024</p>
          <p>Kardista: kardista.tecnologico@usfx.bo / kardex2024</p>
        </div>
      </div>
    </div>
  )
}
