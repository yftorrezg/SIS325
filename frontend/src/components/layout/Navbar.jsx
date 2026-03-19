import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  AcademicCapIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
} from '@heroicons/react/24/outline'
import { useAuthStore } from '../../store/authStore'
import clsx from 'clsx'

const navLinks = [
  { to: '/', label: 'Inicio', icon: AcademicCapIcon },
  { to: '/tramites', label: 'Trámites', icon: DocumentTextIcon },
  { to: '/kardistas', label: 'Kardistas', icon: UserGroupIcon },
]

const studentLinks = [
  { to: '/mis-solicitudes', label: 'Mis Solicitudes', icon: ClipboardDocumentListIcon },
]

const adminLinks = [
  { to: '/admin', label: 'Panel Admin', icon: Cog6ToothIcon },
]

export default function Navbar() {
  const { user, token, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => location.pathname === path || (path !== '/' && location.pathname.startsWith(path))

  const allLinks = [
    ...navLinks,
    ...(token ? studentLinks : []),
    ...(token && ['admin', 'kardista'].includes(user?.role) ? adminLinks : []),
  ]

  return (
    <nav className="bg-blue-900 shadow-lg sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-white font-bold text-lg">
            <AcademicCapIcon className="w-8 h-8 text-yellow-400" />
            <span className="hidden sm:block">
              <span className="text-yellow-400">USFX</span> Trámites
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {allLinks.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={clsx(
                  'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive(to)
                    ? 'bg-blue-700 text-white'
                    : 'text-blue-100 hover:bg-blue-800 hover:text-white'
                )}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </div>

          {/* Auth */}
          <div className="flex items-center gap-2">
            {token ? (
              <div className="flex items-center gap-2">
                <span className="hidden sm:block text-blue-200 text-sm">{user?.full_name?.split(' ')[0]}</span>
                <button onClick={handleLogout} className="flex items-center gap-1 text-blue-200 hover:text-white px-2 py-1 rounded-lg hover:bg-blue-800 transition-colors text-sm">
                  <ArrowRightOnRectangleIcon className="w-4 h-4" />
                  <span className="hidden sm:block">Salir</span>
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn-primary text-sm py-1.5 px-3">
                Iniciar sesión
              </Link>
            )}
            {/* Mobile toggle */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden text-white p-1"
            >
              {mobileOpen ? <XMarkIcon className="w-6 h-6" /> : <Bars3Icon className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-blue-800 border-t border-blue-700 px-4 py-2">
          {allLinks.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-2 py-2 text-blue-100 hover:text-white text-sm"
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
