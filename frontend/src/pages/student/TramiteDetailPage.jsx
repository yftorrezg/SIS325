import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeftIcon,
  ClockIcon,
  CurrencyDollarIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'
import { tramiteService, careerService, requestService } from '../../services/api'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

export default function TramiteDetailPage() {
  const { id } = useParams()
  const { token } = useAuthStore()
  const [tramite, setTramite] = useState(null)
  const [careers, setCareers] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [selectedCareer, setSelectedCareer] = useState('')
  const [notes, setNotes] = useState('')
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    Promise.all([
      tramiteService.getById(id),
      careerService.list(),
    ]).then(([t, c]) => {
      setTramite(t.data)
      setCareers(c.data)
    }).finally(() => setLoading(false))
  }, [id])

  const handleSubmit = async () => {
    if (!token) { toast.error('Debes iniciar sesión para solicitar un trámite'); return }
    if (!selectedCareer) { toast.error('Selecciona tu carrera'); return }
    setSubmitting(true)
    try {
      await requestService.create({ tramite_id: id, career_id: selectedCareer, notes })
      toast.success('Solicitud enviada correctamente')
      setShowForm(false)
    } catch {
      toast.error('Error al enviar la solicitud')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="animate-pulse space-y-4"><div className="h-8 bg-gray-200 rounded w-1/2"/><div className="h-48 bg-gray-100 rounded"/></div>
  if (!tramite) return <div className="text-center py-12 text-gray-400">Trámite no encontrado</div>

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link to="/tramites" className="inline-flex items-center gap-2 text-blue-700 hover:underline text-sm">
        <ArrowLeftIcon className="w-4 h-4" /> Volver a trámites
      </Link>

      {/* Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-gray-900 mb-2">{tramite.name}</h1>
            {tramite.description && <p className="text-gray-600 text-sm">{tramite.description}</p>}
          </div>
          <DocumentTextIcon className="w-10 h-10 text-blue-300 flex-shrink-0" />
        </div>
        <div className="flex gap-4 mt-4 text-sm text-gray-500">
          {tramite.duration_days && (
            <span className="flex items-center gap-1.5 bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
              <ClockIcon className="w-4 h-4" />
              {tramite.duration_days} días hábiles
            </span>
          )}
          <span className="flex items-center gap-1.5 bg-green-50 text-green-700 px-3 py-1 rounded-full">
            <CurrencyDollarIcon className="w-4 h-4" />
            {tramite.cost > 0 ? `Bs. ${tramite.cost}` : 'Sin costo'}
          </span>
        </div>
      </div>

      {/* Requirements */}
      {tramite.requirements?.length > 0 && (
        <div className="card p-6">
          <h2 className="font-bold text-gray-800 mb-4">Requisitos y pasos</h2>
          <ol className="space-y-3">
            {tramite.requirements.map((req) => (
              <li key={req.id} className="flex gap-3">
                <span className="flex-shrink-0 w-7 h-7 bg-blue-700 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {req.step_number}
                </span>
                <div className="flex-1 pb-3 border-b border-gray-100 last:border-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-gray-800 text-sm">{req.title}</p>
                    {!req.is_mandatory && <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">Opcional</span>}
                  </div>
                  {req.description && <p className="text-gray-500 text-sm mt-0.5">{req.description}</p>}
                  {req.document_name && (
                    <p className="text-blue-600 text-sm mt-1 flex items-center gap-1">
                      <DocumentTextIcon className="w-3.5 h-3.5" />
                      {req.document_name}
                    </p>
                  )}
                  {req.notes && (
                    <p className="text-amber-600 text-xs mt-1 flex items-center gap-1">
                      <ExclamationCircleIcon className="w-3.5 h-3.5" />
                      {req.notes}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Request form */}
      {!showForm ? (
        <button
          onClick={() => token ? setShowForm(true) : toast.error('Inicia sesión para solicitar este trámite')}
          className="btn-primary w-full py-3"
        >
          Iniciar solicitud de trámite
        </button>
      ) : (
        <div className="card p-6 space-y-4">
          <h2 className="font-bold text-gray-800">Enviar solicitud</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tu carrera *</label>
            <select
              value={selectedCareer}
              onChange={e => setSelectedCareer(e.target.value)}
              className="input-field"
            >
              <option value="">Selecciona tu carrera</option>
              {careers.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notas adicionales</label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              rows={3}
              className="input-field resize-none"
              placeholder="Información adicional que el kardista deba saber..."
            />
          </div>
          <div className="flex gap-3">
            <button onClick={handleSubmit} disabled={submitting} className="btn-primary flex-1">
              {submitting ? 'Enviando...' : 'Enviar solicitud'}
            </button>
            <button onClick={() => setShowForm(false)} className="btn-secondary">
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
