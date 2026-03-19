import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MagnifyingGlassIcon, ClockIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline'
import { tramiteService } from '../../services/api'
import clsx from 'clsx'

const CATEGORIES = ['Todos', 'matricula', 'certificados', 'cambios', 'titulacion', 'academico', 'bienestar', 'identificacion']

const CATEGORY_LABELS = {
  matricula: 'Matrícula',
  certificados: 'Certificados',
  cambios: 'Cambios',
  titulacion: 'Titulación',
  academico: 'Académico',
  bienestar: 'Bienestar',
  identificacion: 'Identificación',
}

const CATEGORY_COLORS = {
  matricula: 'bg-blue-50 border-blue-200 hover:border-blue-400',
  certificados: 'bg-green-50 border-green-200 hover:border-green-400',
  cambios: 'bg-purple-50 border-purple-200 hover:border-purple-400',
  titulacion: 'bg-yellow-50 border-yellow-200 hover:border-yellow-400',
  academico: 'bg-orange-50 border-orange-200 hover:border-orange-400',
  bienestar: 'bg-pink-50 border-pink-200 hover:border-pink-400',
  identificacion: 'bg-gray-50 border-gray-200 hover:border-gray-400',
}

export default function TramitesIndex() {
  const [tramites, setTramites] = useState([])
  const [filtered, setFiltered] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('Todos')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    tramiteService.list().then(r => {
      setTramites(r.data)
      setFiltered(r.data)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    let result = tramites
    if (category !== 'Todos') result = result.filter(t => t.category === category)
    if (search) result = result.filter(t => t.name.toLowerCase().includes(search.toLowerCase()) || (t.description || '').toLowerCase().includes(search.toLowerCase()))
    setFiltered(result)
  }, [search, category, tramites])

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Trámites Universitarios</h1>
        <p className="text-gray-500">Facultad de Tecnología USFX</p>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar trámite..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input-field pl-10"
        />
      </div>

      {/* Category filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={clsx(
              'px-3 py-1.5 rounded-full text-sm font-medium transition-colors border',
              category === cat
                ? 'bg-blue-700 text-white border-blue-700'
                : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
            )}
          >
            {cat === 'Todos' ? 'Todos' : CATEGORY_LABELS[cat] || cat}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card p-5 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3" />
              <div className="h-3 bg-gray-100 rounded w-full mb-2" />
              <div className="h-3 bg-gray-100 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <MagnifyingGlassIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No se encontraron trámites</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(t => (
            <Link
              key={t.id}
              to={`/tramites/${t.id}`}
              className={clsx('card p-5 border-2 transition-all hover:shadow-md', CATEGORY_COLORS[t.category] || '')}
            >
              <h3 className="font-semibold text-gray-800 mb-2 text-sm leading-snug">{t.name}</h3>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                {t.duration_days && (
                  <span className="flex items-center gap-1">
                    <ClockIcon className="w-3.5 h-3.5" />
                    {t.duration_days} días
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <CurrencyDollarIcon className="w-3.5 h-3.5" />
                  {t.cost > 0 ? `Bs. ${t.cost}` : 'Gratuito'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
