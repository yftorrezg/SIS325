import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ClockIcon, CheckCircleIcon, XCircleIcon, PlayCircleIcon } from '@heroicons/react/24/outline'
import { requestService } from '../../services/api'

const STATUS_CONFIG = {
  pendiente: { label: 'Pendiente', icon: ClockIcon, class: 'bg-yellow-100 text-yellow-800' },
  en_proceso: { label: 'En proceso', icon: PlayCircleIcon, class: 'bg-blue-100 text-blue-800' },
  completado: { label: 'Completado', icon: CheckCircleIcon, class: 'bg-green-100 text-green-800' },
  rechazado: { label: 'Rechazado', icon: XCircleIcon, class: 'bg-red-100 text-red-800' },
  cancelado: { label: 'Cancelado', icon: XCircleIcon, class: 'bg-gray-100 text-gray-800' },
}

export default function MyRequests() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    requestService.myRequests().then(r => setRequests(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="animate-pulse space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="card h-20 bg-gray-100"/>)}</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mis Solicitudes</h1>
      {requests.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <ClockIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No tienes solicitudes aún</p>
          <Link to="/tramites" className="mt-3 inline-block text-blue-700 hover:underline">Ver trámites disponibles</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {requests.map(r => {
            const cfg = STATUS_CONFIG[r.status] || STATUS_CONFIG.pendiente
            const Icon = cfg.icon
            return (
              <div key={r.id} className="card p-5 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-800 text-sm">{r.tramite_id}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{new Date(r.submitted_at).toLocaleDateString('es-BO')}</p>
                  {r.admin_notes && <p className="text-xs text-gray-500 mt-1 italic">"{r.admin_notes}"</p>}
                </div>
                <span className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full font-semibold ${cfg.class}`}>
                  <Icon className="w-3.5 h-3.5" />
                  {cfg.label}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
