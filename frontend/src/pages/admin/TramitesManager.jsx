import { useEffect, useState } from 'react'
import { tramiteService } from '../../services/api'
import toast from 'react-hot-toast'
import { PencilIcon, TrashIcon, PlusIcon } from '@heroicons/react/24/outline'

const EMPTY_FORM = { code: '', name: '', description: '', category: '', duration_days: '', cost: 0, applies_to: 'all', order_index: 0 }

export default function TramitesManager() {
  const [tramites, setTramites] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [showForm, setShowForm] = useState(false)

  const load = () => tramiteService.list().then(r => setTramites(r.data)).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const handleEdit = (t) => {
    setEditing(t.id)
    setForm({ code: t.code, name: t.name, description: t.description || '', category: t.category || '', duration_days: t.duration_days || '', cost: t.cost, applies_to: t.applies_to, order_index: t.order_index })
    setShowForm(true)
  }

  const handleSave = async () => {
    try {
      if (editing) {
        await tramiteService.update(editing, form)
        toast.success('Trámite actualizado')
      } else {
        await tramiteService.create(form)
        toast.success('Trámite creado')
      }
      setShowForm(false)
      setEditing(null)
      setForm(EMPTY_FORM)
      load()
    } catch {
      toast.error('Error al guardar')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar este trámite?')) return
    try {
      await tramiteService.delete(id)
      toast.success('Trámite eliminado')
      load()
    } catch {
      toast.error('Error al eliminar')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Trámites</h1>
        <button onClick={() => { setShowForm(true); setEditing(null); setForm(EMPTY_FORM) }} className="btn-primary flex items-center gap-2">
          <PlusIcon className="w-4 h-4" /> Nuevo trámite
        </button>
      </div>

      {showForm && (
        <div className="card p-6 mb-6 space-y-3">
          <h2 className="font-bold text-gray-800">{editing ? 'Editar trámite' : 'Nuevo trámite'}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Código</label><input className="input-field" value={form.code} onChange={e => setForm({...form, code: e.target.value})} placeholder="TRAMITE_EJEMPLO" /></div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Nombre</label><input className="input-field" value={form.name} onChange={e => setForm({...form, name: e.target.value})} /></div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Categoría</label>
              <select className="input-field" value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                <option value="">Seleccionar</option>
                {['matricula','certificados','cambios','titulacion','academico','bienestar','identificacion'].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Días hábiles</label><input type="number" className="input-field" value={form.duration_days} onChange={e => setForm({...form, duration_days: e.target.value})} /></div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Costo (Bs.)</label><input type="number" className="input-field" value={form.cost} onChange={e => setForm({...form, cost: e.target.value})} /></div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Aplica a</label>
              <select className="input-field" value={form.applies_to} onChange={e => setForm({...form, applies_to: e.target.value})}>
                <option value="all">Todos</option>
                <option value="tecnologico">Kardex Tecnológico</option>
                <option value="6x">Kardex 6x</option>
              </select>
            </div>
          </div>
          <div><label className="block text-xs font-medium text-gray-600 mb-1">Descripción</label><textarea className="input-field resize-none" rows={3} value={form.description} onChange={e => setForm({...form, description: e.target.value})} /></div>
          <div className="flex gap-2">
            <button onClick={handleSave} className="btn-primary">Guardar</button>
            <button onClick={() => { setShowForm(false); setEditing(null) }} className="btn-secondary">Cancelar</button>
          </div>
        </div>
      )}

      {loading ? <div className="animate-pulse space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-14 bg-gray-100 rounded-lg"/>)}</div> : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-semibold text-gray-600">Nombre</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600 hidden md:table-cell">Categoría</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600 hidden md:table-cell">Costo</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {tramites.map(t => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">{t.name}</td>
                  <td className="px-4 py-3 text-gray-500 hidden md:table-cell">{t.category}</td>
                  <td className="px-4 py-3 text-gray-500 hidden md:table-cell">{t.cost > 0 ? `Bs. ${t.cost}` : 'Gratis'}</td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => handleEdit(t)} className="text-blue-600 hover:text-blue-800 p-1 mr-1"><PencilIcon className="w-4 h-4" /></button>
                    <button onClick={() => handleDelete(t.id)} className="text-red-500 hover:text-red-700 p-1"><TrashIcon className="w-4 h-4" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
