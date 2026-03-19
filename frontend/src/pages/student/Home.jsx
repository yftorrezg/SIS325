import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import {
  AcademicCapIcon,
  DocumentTextIcon,
  UserGroupIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { tramiteService } from '../../services/api'

const CATEGORY_COLORS = {
  matricula: 'bg-blue-100 text-blue-800',
  certificados: 'bg-green-100 text-green-800',
  cambios: 'bg-purple-100 text-purple-800',
  titulacion: 'bg-yellow-100 text-yellow-800',
  academico: 'bg-orange-100 text-orange-800',
  bienestar: 'bg-pink-100 text-pink-800',
  identificacion: 'bg-gray-100 text-gray-800',
}

const features = [
  { icon: SparklesIcon, title: 'Asistente IA', desc: 'Chatbot inteligente que te guía en tu trámite usando procesamiento de lenguaje natural.' },
  { icon: UserGroupIcon, title: 'Kardistas Especializados', desc: 'Contacto directo con el kardista de tu carrera: Tecnológico o 6x.' },
  { icon: ClockIcon, title: 'Seguimiento en Tiempo Real', desc: 'Monitorea el estado de tus solicitudes en cualquier momento.' },
  { icon: CheckCircleIcon, title: 'Requisitos Claros', desc: 'Lista detallada de documentos y pasos para cada trámite.' },
]

export default function Home() {
  const [tramites, setTramites] = useState([])

  useEffect(() => {
    tramiteService.list().then(r => setTramites(r.data.slice(0, 6))).catch(() => {})
  }, [])

  return (
    <div className="space-y-10">
      {/* Hero */}
      <section className="bg-gradient-to-br from-blue-900 to-blue-700 rounded-2xl p-8 md:p-12 text-white text-center shadow-xl">
        <AcademicCapIcon className="w-16 h-16 mx-auto text-yellow-400 mb-4" />
        <h1 className="text-3xl md:text-4xl font-bold mb-3">
          Sistema de Trámites
        </h1>
        <p className="text-xl text-blue-100 mb-2 font-medium">Facultad de Tecnología - USFX</p>
        <p className="text-blue-200 mb-8 max-w-2xl mx-auto">
          Gestiona todos tus trámites universitarios de manera rápida y sencilla.
          Nuestro asistente de IA te guiará paso a paso.
        </p>
        <div className="flex flex-wrap gap-3 justify-center">
          <Link to="/tramites" className="bg-yellow-400 hover:bg-yellow-300 text-blue-900 font-bold px-6 py-3 rounded-xl transition-colors">
            Ver todos los trámites
          </Link>
          <Link to="/kardistas" className="bg-white/10 hover:bg-white/20 text-white font-semibold px-6 py-3 rounded-xl border border-white/30 transition-colors">
            Contactar kardista
          </Link>
        </div>
      </section>

      {/* Features */}
      <section>
        <h2 className="text-xl font-bold text-gray-800 mb-4">¿Qué puedes hacer?</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-5 hover:shadow-md transition-shadow">
              <Icon className="w-8 h-8 text-blue-700 mb-3" />
              <h3 className="font-semibold text-gray-800 mb-1">{title}</h3>
              <p className="text-sm text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Tramites grid */}
      {tramites.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-800">Trámites frecuentes</h2>
            <Link to="/tramites" className="text-blue-700 hover:underline text-sm font-medium">Ver todos →</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {tramites.map((t) => (
              <Link key={t.id} to={`/tramites/${t.id}`} className="card p-5 hover:shadow-md transition-shadow group">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-800 group-hover:text-blue-700 transition-colors text-sm leading-snug">{t.name}</h3>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${CATEGORY_COLORS[t.category] || 'bg-gray-100 text-gray-700'}`}>
                    {t.category}
                  </span>
                  {t.duration_days && (
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <ClockIcon className="w-3 h-3" />
                      {t.duration_days}d
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
