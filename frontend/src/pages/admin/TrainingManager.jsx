import { useEffect, useState, useCallback } from 'react'
import { trainingService } from '../../services/api'
import toast from 'react-hot-toast'
import { PlusIcon, CheckIcon, TrashIcon, PencilIcon, MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { TRAMITE_LABELS_MAP } from '../../utils/constants'

const PAGE_SIZE = 25
const LABELS = Object.entries(TRAMITE_LABELS_MAP)

function EditModal({ sample, onClose, onSaved }) {
  const [text, setText] = useState(sample.text)
  const [label, setLabel] = useState(sample.label)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!text.trim() || !label) { toast.error('Completa texto y etiqueta'); return }
    setSaving(true)
    try {
      await trainingService.updateSample(sample.id, { text, label })
      toast.success('Muestra actualizada')
      onSaved()
      onClose()
    } catch { toast.error('Error al guardar') }
    finally { setSaving(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h3 className="font-semibold text-gray-800">Editar muestra</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><XMarkIcon className="w-5 h-5" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Texto del estudiante</label>
            <textarea
              className="input-field w-full h-28 resize-none"
              value={text}
              onChange={e => setText(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Etiqueta</label>
            <select className="input-field w-full" value={label} onChange={e => setLabel(e.target.value)}>
              {LABELS.map(([key, name]) => <option key={key} value={key}>{name}</option>)}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-2 px-5 py-4 border-t">
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      </div>
    </div>
  )
}

function AddModal({ onClose, onSaved }) {
  const [text, setText] = useState('')
  const [label, setLabel] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!text.trim() || !label) { toast.error('Completa texto y etiqueta'); return }
    setSaving(true)
    try {
      await trainingService.createSample({ text, label })
      toast.success('Muestra agregada')
      onSaved()
      onClose()
    } catch { toast.error('Error al agregar') }
    finally { setSaving(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h3 className="font-semibold text-gray-800">Agregar muestra</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><XMarkIcon className="w-5 h-5" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Texto del estudiante</label>
            <textarea
              className="input-field w-full h-28 resize-none"
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Ej: quiero matricularme este semestre"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Etiqueta</label>
            <select className="input-field w-full" value={label} onChange={e => setLabel(e.target.value)}>
              <option value="">Seleccionar etiqueta</option>
              {LABELS.map(([key, name]) => <option key={key} value={key}>{name}</option>)}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-2 px-5 py-4 border-t">
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? 'Guardando...' : 'Agregar'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function TrainingManager() {
  const [samples, setSamples] = useState([])
  const [stats, setStats] = useState({})
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)

  // Filtros
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [filterLabel, setFilterLabel] = useState('')
  const [filterVerified, setFilterVerified] = useState('')

  // Modales
  const [showAdd, setShowAdd] = useState(false)
  const [editSample, setEditSample] = useState(null)
  const [deleteId, setDeleteId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    const params = { limit: PAGE_SIZE, offset: page * PAGE_SIZE }
    if (search) params.search = search
    if (filterLabel) params.label = filterLabel
    if (filterVerified !== '') params.verified = filterVerified === 'true'

    try {
      const [samplesRes, countRes, statsRes] = await Promise.all([
        trainingService.listSamples(params),
        trainingService.countSamples({ search: params.search, label: params.label, verified: params.verified }),
        trainingService.stats(),
      ])
      setSamples(samplesRes.data)
      setTotal(countRes.data.total)
      setStats(statsRes.data.distribution || {})
    } catch { toast.error('Error al cargar muestras') }
    finally { setLoading(false) }
  }, [page, search, filterLabel, filterVerified])

  useEffect(() => { load() }, [load])

  // Reset page when filters change
  useEffect(() => { setPage(0) }, [search, filterLabel, filterVerified])

  const handleSearch = () => setSearch(searchInput)
  const handleClearSearch = () => { setSearchInput(''); setSearch('') }

  const handleVerify = async (id) => {
    try {
      await trainingService.verifySample(id)
      toast.success('Muestra verificada')
      load()
    } catch { toast.error('Error') }
  }

  const handleDelete = async () => {
    try {
      await trainingService.deleteSample(deleteId)
      toast.success('Muestra eliminada')
      setDeleteId(null)
      load()
    } catch { toast.error('Error al eliminar') }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const totalVerified = Object.values(stats).reduce((a, b) => a + b, 0)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Datos de Entrenamiento</h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-1">
          <PlusIcon className="w-4 h-4" /> Agregar muestra
        </button>
      </div>

      {/* Stats por etiqueta */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-6">
        {LABELS.map(([key, name]) => (
          <button
            key={key}
            onClick={() => setFilterLabel(filterLabel === key ? '' : key)}
            className={`card p-3 text-center transition-all hover:shadow-md ${filterLabel === key ? 'ring-2 ring-blue-500' : ''}`}
          >
            <p className="text-xl font-bold text-blue-700">{stats[key] ?? 0}</p>
            <p className="text-xs text-gray-500 leading-tight mt-0.5">{name}</p>
          </button>
        ))}
      </div>

      {/* Filtros y búsqueda */}
      <div className="card p-4 mb-4 flex flex-wrap gap-3 items-end">
        {/* Búsqueda por texto */}
        <div className="flex-1 min-w-48">
          <label className="block text-xs text-gray-500 mb-1">Buscar texto</label>
          <div className="flex gap-1">
            <input
              className="input-field flex-1"
              placeholder="Buscar en muestras..."
              value={searchInput}
              onChange={e => setSearchInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
            />
            {searchInput
              ? <button onClick={handleClearSearch} className="text-gray-400 hover:text-gray-600 px-2"><XMarkIcon className="w-4 h-4" /></button>
              : <button onClick={handleSearch} className="btn-secondary px-3"><MagnifyingGlassIcon className="w-4 h-4" /></button>
            }
          </div>
        </div>

        {/* Filtro etiqueta */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">Etiqueta</label>
          <select className="input-field w-52" value={filterLabel} onChange={e => setFilterLabel(e.target.value)}>
            <option value="">Todas las etiquetas</option>
            {LABELS.map(([key, name]) => <option key={key} value={key}>{name}</option>)}
          </select>
        </div>

        {/* Filtro verificado */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">Estado</label>
          <select className="input-field w-40" value={filterVerified} onChange={e => setFilterVerified(e.target.value)}>
            <option value="">Todos</option>
            <option value="true">Verificadas</option>
            <option value="false">Sin verificar</option>
          </select>
        </div>

        {/* Total */}
        <div className="text-sm text-gray-500 self-end pb-2">
          {total} muestra{total !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Tabla */}
      {loading ? (
        <div className="animate-pulse h-64 bg-gray-100 rounded-xl" />
      ) : samples.length === 0 ? (
        <div className="card p-10 text-center text-gray-400">No se encontraron muestras</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-gray-600 w-1/2">Texto</th>
                <th className="text-left px-4 py-3 text-gray-600">Etiqueta</th>
                <th className="text-left px-4 py-3 text-gray-600">Estado</th>
                <th className="px-4 py-3 w-24" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {samples.map(s => (
                <tr key={s.id} className="hover:bg-gray-50 group">
                  <td className="px-4 py-2 text-gray-700">
                    <p className="line-clamp-2 leading-snug">{s.text}</p>
                  </td>
                  <td className="px-4 py-2">
                    <span className="inline-block text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full whitespace-nowrap">
                      {TRAMITE_LABELS_MAP[s.label] ?? s.label}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    {s.verified
                      ? <span className="text-xs text-green-600 font-medium flex items-center gap-1"><CheckIcon className="w-3.5 h-3.5" />Verificada</span>
                      : <button onClick={() => handleVerify(s.id)} className="text-xs text-blue-600 hover:underline">Verificar</button>
                    }
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setEditSample(s)} className="text-gray-400 hover:text-blue-600">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button onClick={() => setDeleteId(s.id)} className="text-gray-400 hover:text-red-500">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50 text-sm">
              <button
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
                className="btn-secondary disabled:opacity-40"
              >
                ← Anterior
              </button>
              <span className="text-gray-500">
                Página {page + 1} de {totalPages}
              </span>
              <button
                disabled={page >= totalPages - 1}
                onClick={() => setPage(p => p + 1)}
                className="btn-secondary disabled:opacity-40"
              >
                Siguiente →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Modal agregar */}
      {showAdd && <AddModal onClose={() => setShowAdd(false)} onSaved={load} />}

      {/* Modal editar */}
      {editSample && <EditModal sample={editSample} onClose={() => setEditSample(null)} onSaved={load} />}

      {/* Confirmación eliminar */}
      {deleteId && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
            <h3 className="font-semibold text-gray-800 mb-2">¿Eliminar muestra?</h3>
            <p className="text-sm text-gray-500 mb-4">Esta acción no se puede deshacer.</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setDeleteId(null)} className="btn-secondary">Cancelar</button>
              <button onClick={handleDelete} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium">Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
