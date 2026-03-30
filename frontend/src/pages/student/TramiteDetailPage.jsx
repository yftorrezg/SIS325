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
import { tramiteService, careerService, requestService, kardistaService } from '../../services/api'
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
  const [kardistas, setKardistas] = useState([])

  useEffect(() => {
    Promise.all([
      tramiteService.getById(id),
      careerService.list(),
      kardistaService.list(),
    ]).then(([t, c, k]) => {
      setTramite(t.data)
      setCareers(c.data)
      setKardistas(k.data)
    }).finally(() => setLoading(false))
  }, [id])

  const buildWhatsAppUrl = (number, tramiteName) => {
    const clean = number.replace(/[+\s-]/g, '')
    const msg = encodeURIComponent(`Hola, tengo consulta sobre el trámite de ${tramiteName}.`)
    return `https://wa.me/${clean}?text=${msg}`
  }

  const relevantKardistas = tramite
    ? kardistas.filter(k =>
        tramite.applies_to === 'all' || k.kardex_type === tramite.applies_to
      )
    : []

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

      {/* WhatsApp contact */}
      {relevantKardistas.length > 0 && (
        <div className="card p-4 flex flex-wrap gap-3 items-center">
          <span className="text-sm text-gray-500 font-medium">¿Dudas? Consultá con tu kardista:</span>
          {relevantKardistas.map(k => k.whatsapp && (
            <a
              key={k.id}
              href={buildWhatsAppUrl(k.whatsapp, tramite.name)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-colors"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
              {k.kardex_type === 'tecnologico' ? 'Kardex Tecnológico' : 'Kardex 6x'}
            </a>
          ))}
        </div>
      )}

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
