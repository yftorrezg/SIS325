import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../../services/api'
import { DocumentTextIcon, ClipboardDocumentListIcon, CpuChipIcon, UserGroupIcon } from '@heroicons/react/24/outline'

const STATUS_LABELS = {
  pendiente: 'Pendiente',
  en_proceso: 'En proceso',
  completado: 'Completado',
  rechazado: 'Rechazado',
}

const STATUS_COLORS = {
  pendiente: 'bg-yellow-100 text-yellow-700',
  en_proceso: 'bg-blue-100 text-blue-700',
  completado: 'bg-green-100 text-green-700',
  rechazado: 'bg-red-100 text-red-700',
}

const adminLinks = [
  { to: '/admin/tramites', label: 'Gestionar Trámites', icon: DocumentTextIcon, desc: 'CRUD de trámites y requisitos' },
  { to: '/admin/solicitudes', label: 'Ver Solicitudes', icon: ClipboardDocumentListIcon, desc: 'Gestionar solicitudes de estudiantes' },
  { to: '/admin/entrenamiento', label: 'Datos de Entrenamiento', icon: CpuChipIcon, desc: 'Gestionar muestras etiquetadas' },
  { to: '/admin/modelo', label: 'Evaluación del Modelo', icon: CpuChipIcon, desc: 'Métricas y entrenamiento del modelo' },
]

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    adminService.stats().then(r => setStats(r.data)).catch(() => {})
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Panel de Administración</h1>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="card p-4">
            <p className="text-xs text-gray-500 mb-1">Trámites activos</p>
            <p className="text-2xl font-bold text-blue-700">{stats.total_tramites}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-gray-500 mb-1">Muestras de entrenamiento</p>
            <p className="text-2xl font-bold text-purple-700">{stats.total_training_samples}</p>
          </div>
          {Object.entries(stats.requests_by_status || {}).map(([status, count]) => (
            <div key={status} className="card p-4">
              <p className="text-xs text-gray-500 mb-1">{STATUS_LABELS[status] || status}</p>
              <p className={`text-2xl font-bold`}>{count}</p>
            </div>
          ))}
        </div>
      )}

      {/* Quick links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {adminLinks.map(({ to, label, icon: Icon, desc }) => (
          <Link key={to} to={to} className="card p-5 hover:shadow-md transition-shadow flex items-center gap-4">
            <Icon className="w-8 h-8 text-blue-600 flex-shrink-0" />
            <div>
              <p className="font-semibold text-gray-800">{label}</p>
              <p className="text-sm text-gray-500">{desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
