import { useEffect, useState } from 'react'
import { PhoneIcon, EnvelopeIcon, MapPinIcon, ClockIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline'
import { kardistaService } from '../../services/api'

const DAYS = { lunes: 'Lunes', martes: 'Martes', miercoles: 'Miércoles', jueves: 'Jueves', viernes: 'Viernes' }

export default function KardistasInfo() {
  const [kardistas, setKardistas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    kardistaService.list().then(r => setKardistas(r.data)).finally(() => setLoading(false))
  }, [])

  const tecnologico = kardistas.filter(k => k.kardex_type === 'tecnologico')
  const sixX = kardistas.filter(k => k.kardex_type === '6x')

  const KARDEX_CAREERS = {
    tecnologico: ['Ing. Telecomunicaciones', 'Ing. Tecnologías de la Información y Seguridad', 'Diseño y Animación', 'Ing. Sistemas', 'Ing. Ciencias de la Computación'],
    '6x': ['Ing. Química', 'Ing. Industrial', 'Ing. Alimentos', 'Ing. Petróleo', 'Ing. Ambiental', 'Ing. Industrias Alimentarias'],
  }

  const renderKardista = (k) => (
    <div key={k.id} className="card p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-gray-900 text-lg">{k.full_name}</h3>
          <span className={`text-xs px-3 py-1 rounded-full font-semibold ${k.kardex_type === 'tecnologico' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
            Kardex {k.kardex_type === 'tecnologico' ? 'Tecnológico' : '6x'}
          </span>
        </div>
      </div>

      <div className="space-y-2 text-sm">
        {k.phone && <div className="flex items-center gap-2 text-gray-600"><PhoneIcon className="w-4 h-4 text-blue-500" />{k.phone}</div>}
        {k.whatsapp && <a href={`https://wa.me/${k.whatsapp.replace(/\D/g, '')}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-green-600 hover:underline"><ChatBubbleLeftIcon className="w-4 h-4" />WhatsApp: {k.whatsapp}</a>}
        {k.email_contact && <div className="flex items-center gap-2 text-gray-600"><EnvelopeIcon className="w-4 h-4 text-blue-500" />{k.email_contact}</div>}
        {k.office_location && <div className="flex items-center gap-2 text-gray-600"><MapPinIcon className="w-4 h-4 text-red-500" />{k.office_location}</div>}
      </div>

      {k.schedule && (
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1"><ClockIcon className="w-4 h-4" />Horario de atención</p>
          <div className="space-y-1">
            {Object.entries(k.schedule).map(([day, hours]) => (
              <div key={day} className="flex items-center justify-between text-sm">
                <span className="text-gray-500 w-24">{DAYS[day] || day}</span>
                <span className="text-gray-700 font-medium">{hours}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  if (loading) return <div className="animate-pulse space-y-4"><div className="h-48 bg-gray-200 rounded-xl"/><div className="h-48 bg-gray-200 rounded-xl"/></div>

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Kardistas</h1>
        <p className="text-gray-500">Encargados de atender tus trámites universitarios</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-bold text-blue-800 mb-3">Kardex Tecnológico</h2>
          <div className="mb-3 text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
            <strong>Carreras:</strong> {KARDEX_CAREERS.tecnologico.join(', ')}
          </div>
          {tecnologico.map(renderKardista)}
        </div>
        <div>
          <h2 className="text-lg font-bold text-purple-800 mb-3">Kardex 6x</h2>
          <div className="mb-3 text-sm text-gray-600 bg-purple-50 rounded-lg p-3">
            <strong>Carreras:</strong> {KARDEX_CAREERS['6x'].join(', ')}
          </div>
          {sixX.map(renderKardista)}
        </div>
      </div>
    </div>
  )
}
