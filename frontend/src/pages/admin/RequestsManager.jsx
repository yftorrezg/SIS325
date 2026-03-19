import { useEffect, useState } from 'react'
import { requestService } from '../../services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const STATUSES = ['pendiente', 'en_proceso', 'completado', 'rechazado', 'cancelado']
const STATUS_COLORS = {
  pendiente: 'bg-yellow-100 text-yellow-800',
  en_proceso: 'bg-blue-100 text-blue-800',
  completado: 'bg-green-100 text-green-800',
  rechazado: 'bg-red-100 text-red-800',
  cancelado: 'bg-gray-100 text-gray-800',
}

export default function RequestsManager() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [updating, setUpdating] = useState(null)

  const load = () => requestService.list(filter ? { status: filter } : {}).then(r => setRequests(r.data)).finally(() => setLoading(false))

  useEffect(() => { load() }, [filter])

  const updateStatus = async (id, status) => {
    setUpdating(id)
    try {
      await requestService.updateStatus(id, { status })
      toast.success('Estado actualizado')
      load()
    } catch {
      toast.error('Error al actualizar')
    } finally {
      setUpdating(null)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Solicitudes de Estudiantes</h1>

      <div className="flex gap-2 mb-4 flex-wrap">
        <button onClick={() => setFilter('')} className={clsx('px-3 py-1.5 rounded-full text-sm border', !filter ? 'bg-blue-700 text-white border-blue-700' : 'border-gray-300 text-gray-600')}>Todas</button>
        {STATUSES.map(s => (
          <button key={s} onClick={() => setFilter(s)} className={clsx('px-3 py-1.5 rounded-full text-sm border capitalize', filter === s ? 'bg-blue-700 text-white border-blue-700' : 'border-gray-300 text-gray-600')}>{s}</button>
        ))}
      </div>

      {loading ? <div className="animate-pulse space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-gray-100 rounded-lg"/>)}</div> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-semibold text-gray-600">Trámite</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600">Estado</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600">Fecha</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600">Cambiar estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {requests.map(r => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800 text-xs max-w-[200px] truncate">{r.tramite_id}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${STATUS_COLORS[r.status]}`}>{r.status}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{new Date(r.submitted_at).toLocaleDateString('es-BO')}</td>
                  <td className="px-4 py-3">
                    <select
                      value={r.status}
                      disabled={updating === r.id}
                      onChange={e => updateStatus(r.id, e.target.value)}
                      className="text-xs border border-gray-300 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                </tr>
              ))}
              {requests.length === 0 && (
                <tr><td colSpan={4} className="text-center py-8 text-gray-400">No hay solicitudes</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
