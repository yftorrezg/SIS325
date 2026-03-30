import { useEffect, useState, useCallback } from 'react'
import { tramiteService } from '../../services/api'
import toast from 'react-hot-toast'
import {
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ListBulletIcon,
  XMarkIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline'

const EMPTY_TRAMITE = {
  code: '', name: '', description: '', category: '', duration_days: '', cost: 0,
  applies_to: 'all', order_index: 0, icon: '', is_active: true,
  office_location: '', contact_info: '', cost_details: '', duration_details: '',
  web_system_url: '', web_instructions: '', video_tutorial_url: '',
}

const EMPTY_REQ = {
  step_number: 1, title: '', description: '', document_name: '',
  is_mandatory: true, notes: '',
}

const CATEGORIES = ['matricula', 'certificados', 'cambios', 'titulacion', 'academico', 'bienestar', 'identificacion']

function Field({ label, children, full }) {
  return (
    <div className={full ? 'col-span-2' : ''}>
      <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{label}</label>
      {children}
    </div>
  )
}

const inp = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
const ta = inp + ' resize-none'

// ── Modal shell ──────────────────────────────────────────────────────────────
function Modal({ title, onClose, children, wide }) {
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-12 bg-black/40 overflow-y-auto">
      <div className={`bg-white rounded-2xl shadow-2xl w-full ${wide ? 'max-w-3xl' : 'max-w-lg'} my-4`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-800 text-lg">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  )
}

// ── Tramite edit modal ───────────────────────────────────────────────────────
function TramiteModal({ tramite, onClose, onSaved }) {
  const [form, setForm] = useState(tramite || EMPTY_TRAMITE)
  const [tab, setTab] = useState('basic')
  const [saving, setSaving] = useState(false)
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSave = async () => {
    if (!form.name || !form.code) { toast.error('Código y nombre son obligatorios'); return }
    setSaving(true)
    try {
      if (tramite?.id) {
        await tramiteService.update(tramite.id, form)
        toast.success('Trámite actualizado')
      } else {
        await tramiteService.create(form)
        toast.success('Trámite creado')
      }
      onSaved()
      onClose()
    } catch {
      toast.error('Error al guardar')
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'basic', label: 'Información General' },
    { id: 'aspectos', label: 'Ubicación / Contacto / Costo' },
    { id: 'web', label: 'Sistema Web / Video' },
  ]

  return (
    <Modal title={tramite?.id ? 'Editar trámite' : 'Nuevo trámite'} onClose={onClose} wide>
      {/* Tabs */}
      <div className="flex gap-1 mb-5 border-b border-gray-100 pb-1">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-3 py-1.5 text-sm font-medium rounded-t-lg transition-colors ${
              tab === t.id ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'basic' && (
        <div className="grid grid-cols-2 gap-4">
          <Field label="Código BERT *">
            <input className={inp} value={form.code} onChange={e => set('code', e.target.value)} placeholder="TRAMITE_EJEMPLO" />
          </Field>
          <Field label="Nombre *">
            <input className={inp} value={form.name} onChange={e => set('name', e.target.value)} />
          </Field>
          <Field label="Categoría">
            <select className={inp} value={form.category} onChange={e => set('category', e.target.value)}>
              <option value="">Seleccionar</option>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </Field>
          <Field label="Aplica a">
            <select className={inp} value={form.applies_to} onChange={e => set('applies_to', e.target.value)}>
              <option value="all">Todos</option>
              <option value="tecnologico">Kardex Tecnológico</option>
              <option value="6x">Kardex 6x</option>
            </select>
          </Field>
          <Field label="Días hábiles">
            <input type="number" className={inp} value={form.duration_days} onChange={e => set('duration_days', e.target.value)} />
          </Field>
          <Field label="Costo (Bs.)">
            <input type="number" step="0.01" className={inp} value={form.cost} onChange={e => set('cost', e.target.value)} />
          </Field>
          <Field label="Orden" >
            <input type="number" className={inp} value={form.order_index} onChange={e => set('order_index', e.target.value)} />
          </Field>
          <Field label="Ícono">
            <input className={inp} value={form.icon} onChange={e => set('icon', e.target.value)} placeholder="academic-cap" />
          </Field>
          <Field label="Descripción" full>
            <textarea className={ta} rows={3} value={form.description} onChange={e => set('description', e.target.value)} placeholder="Descripción general del trámite..." />
          </Field>
          <div className="col-span-2 flex items-center gap-3 pt-1">
            <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
              <input
                type="checkbox"
                className="w-4 h-4 accent-blue-600"
                checked={form.is_active ?? true}
                onChange={e => set('is_active', e.target.checked)}
              />
              <span className="font-medium text-gray-700">Trámite activo (visible para estudiantes)</span>
            </label>
          </div>
        </div>
      )}

      {tab === 'aspectos' && (
        <div className="grid grid-cols-2 gap-4">
          <Field label="📍 Ubicación (dónde se realiza)" full>
            <input className={inp} value={form.office_location} onChange={e => set('office_location', e.target.value)} placeholder="Ej: Kardista — Pabellón C Oficina 201" />
          </Field>
          <Field label="📞 Contacto (teléfono, kardista, email)" full>
            <input className={inp} value={form.contact_info} onChange={e => set('contact_info', e.target.value)} placeholder="Ej: Kardista: Juan Pérez, int. 210, WhatsApp +591 701..." />
          </Field>
          <Field label="💰 Detalle de pago (instrucciones de pago)" full>
            <textarea className={ta} rows={2} value={form.cost_details} onChange={e => set('cost_details', e.target.value)} placeholder="Ej: Pagar en Tesorería de la Facultad y presentar comprobante al kardista..." />
          </Field>
          <Field label="⏱ Detalle del plazo (notas sobre el tiempo)" full>
            <textarea className={ta} rows={2} value={form.duration_details} onChange={e => set('duration_details', e.target.value)} placeholder="Ej: 3 días hábiles desde la entrega. La Solvencia Universitaria tiene solo 48 hs de validez..." />
          </Field>
        </div>
      )}

      {tab === 'web' && (
        <div className="space-y-4">
          <Field label="🌐 URL del sistema web">
            <input className={inp} value={form.web_system_url} onChange={e => set('web_system_url', e.target.value)} placeholder="https://universitarios.usfx.bo" />
          </Field>
          <Field label="📋 Instrucciones paso a paso en el sistema web" full>
            <textarea className={ta} rows={5} value={form.web_instructions} onChange={e => set('web_instructions', e.target.value)} placeholder="1. Ingresá a...\n2. Menú...\n3. ..." />
          </Field>
          <Field label="🎥 URL del video tutorial (YouTube, TikTok, etc.)" full>
            <input className={inp} value={form.video_tutorial_url} onChange={e => set('video_tutorial_url', e.target.value)} placeholder="https://www.youtube.com/watch?v=..." />
          </Field>
          {form.video_tutorial_url && (
            <div className="text-xs text-blue-600">
              <a href={form.video_tutorial_url} target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-800">
                ↗ Verificar enlace del video
              </a>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-3 mt-6 pt-4 border-t border-gray-100">
        <button onClick={handleSave} disabled={saving} className="btn-primary flex-1">
          {saving ? 'Guardando...' : (tramite?.id ? 'Guardar cambios' : 'Crear trámite')}
        </button>
        <button onClick={onClose} className="btn-secondary">Cancelar</button>
      </div>
    </Modal>
  )
}

// ── Requirements modal ───────────────────────────────────────────────────────
function RequirementsModal({ tramite, onClose }) {
  const [reqs, setReqs] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingReq, setEditingReq] = useState(null) // null = new, object = editing
  const [showReqForm, setShowReqForm] = useState(false)
  const [reqForm, setReqForm] = useState(EMPTY_REQ)

  const loadReqs = useCallback(async () => {
    setLoading(true)
    try {
      const res = await tramiteService.getById(tramite.id)
      setReqs(res.data.requirements || [])
    } finally {
      setLoading(false)
    }
  }, [tramite.id])

  useEffect(() => { loadReqs() }, [loadReqs])

  const openNew = () => {
    const nextStep = reqs.length > 0 ? Math.max(...reqs.map(r => r.step_number)) + 1 : 1
    setReqForm({ ...EMPTY_REQ, step_number: nextStep })
    setEditingReq(null)
    setShowReqForm(true)
  }

  const openEdit = (req) => {
    setReqForm({ ...req })
    setEditingReq(req)
    setShowReqForm(true)
  }

  const handleSaveReq = async () => {
    try {
      if (editingReq?.id) {
        await tramiteService.updateRequirement(tramite.id, editingReq.id, reqForm)
        toast.success('Requisito actualizado')
      } else {
        await tramiteService.addRequirement(tramite.id, reqForm)
        toast.success('Requisito agregado')
      }
      setShowReqForm(false)
      loadReqs()
    } catch {
      toast.error('Error al guardar el requisito')
    }
  }

  const handleDeleteReq = async (req) => {
    if (!confirm(`¿Eliminar "${req.title}"?`)) return
    try {
      await tramiteService.deleteRequirement(tramite.id, req.id)
      toast.success('Requisito eliminado')
      loadReqs()
    } catch {
      toast.error('Error al eliminar')
    }
  }

  const setR = (k, v) => setReqForm(f => ({ ...f, [k]: v }))

  return (
    <Modal title={`Requisitos — ${tramite.name}`} onClose={onClose} wide>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">{reqs.length} requisito(s) / paso(s)</p>
        <button onClick={openNew} className="btn-primary text-sm flex items-center gap-1.5">
          <PlusIcon className="w-4 h-4" /> Agregar
        </button>
      </div>

      {/* Inline req form */}
      {showReqForm && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4 space-y-3">
          <h3 className="text-sm font-semibold text-blue-800">{editingReq ? 'Editar requisito' : 'Nuevo requisito'}</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Nº de paso *</label>
              <input type="number" className={inp} value={reqForm.step_number} onChange={e => setR('step_number', parseInt(e.target.value))} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Título *</label>
              <input className={inp} value={reqForm.title} onChange={e => setR('title', e.target.value)} placeholder="Ej: Fotocopia CI vigente" />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Descripción</label>
              <input className={inp} value={reqForm.description} onChange={e => setR('description', e.target.value)} placeholder="Descripción adicional..." />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Nombre del documento</label>
              <input className={inp} value={reqForm.document_name} onChange={e => setR('document_name', e.target.value)} placeholder="Ej: Fotocopia CI" />
            </div>
            <div className="flex items-end pb-1">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" className="w-4 h-4 accent-blue-600" checked={reqForm.is_mandatory} onChange={e => setR('is_mandatory', e.target.checked)} />
                <span className="font-medium text-gray-700">Obligatorio</span>
              </label>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Nota / advertencia</label>
              <input className={inp} value={reqForm.notes} onChange={e => setR('notes', e.target.value)} placeholder="Ej: ¡Solo tiene 48 horas de validez!" />
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <button onClick={handleSaveReq} className="btn-primary text-sm">Guardar</button>
            <button onClick={() => setShowReqForm(false)} className="btn-secondary text-sm">Cancelar</button>
          </div>
        </div>
      )}

      {/* Requirements list */}
      {loading ? (
        <div className="space-y-2">{[...Array(3)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded-lg animate-pulse" />)}</div>
      ) : reqs.length === 0 ? (
        <div className="text-center py-8 text-gray-400 text-sm">Sin requisitos. Agregá el primero.</div>
      ) : (
        <div className="space-y-2">
          {[...reqs].sort((a, b) => a.step_number - b.step_number).map(req => (
            <div key={req.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-xl border border-gray-200">
              <span className="flex-shrink-0 w-7 h-7 bg-blue-700 text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                {req.step_number}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-semibold text-gray-800">{req.title}</p>
                  {!req.is_mandatory && (
                    <span className="text-xs text-gray-400 bg-gray-200 px-2 py-0.5 rounded-full">Opcional</span>
                  )}
                </div>
                {req.description && <p className="text-xs text-gray-500 mt-0.5">{req.description}</p>}
                {req.document_name && <p className="text-xs text-blue-600 mt-0.5 font-medium">{req.document_name}</p>}
                {req.notes && <p className="text-xs text-amber-600 mt-0.5">⚠️ {req.notes}</p>}
              </div>
              <div className="flex gap-1 flex-shrink-0">
                <button onClick={() => openEdit(req)} className="p-1.5 text-blue-600 hover:bg-blue-100 rounded-lg" title="Editar">
                  <PencilIcon className="w-4 h-4" />
                </button>
                <button onClick={() => handleDeleteReq(req)} className="p-1.5 text-red-500 hover:bg-red-100 rounded-lg" title="Eliminar">
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-5 pt-4 border-t border-gray-100">
        <button onClick={onClose} className="btn-secondary w-full">Cerrar</button>
      </div>
    </Modal>
  )
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function TramitesManager() {
  const [tramites, setTramites] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingTramite, setEditingTramite] = useState(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [requirementsFor, setRequirementsFor] = useState(null)
  const [showInactive, setShowInactive] = useState(true)

  const load = useCallback(() => {
    tramiteService.list({ include_inactive: true }).then(r => setTramites(r.data)).finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const handleToggleActive = async (t) => {
    const action = t.is_active ? 'desactivar' : 'activar'
    if (!confirm(`¿${action.charAt(0).toUpperCase() + action.slice(1)} "${t.name}"?`)) return
    try {
      await tramiteService.update(t.id, { is_active: !t.is_active })
      toast.success(`Trámite ${t.is_active ? 'desactivado' : 'activado'}`)
      load()
    } catch {
      toast.error('Error al actualizar')
    }
  }

  const visibleTramites = showInactive ? tramites : tramites.filter(t => t.is_active)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestión de Trámites</h1>
          <p className="text-sm text-gray-500 mt-0.5">Administrá los trámites, sus campos por aspecto y los requisitos paso a paso</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm cursor-pointer select-none text-gray-600">
            <input
              type="checkbox"
              className="w-4 h-4 accent-blue-600"
              checked={showInactive}
              onChange={e => setShowInactive(e.target.checked)}
            />
            Mostrar inactivos
          </label>
          <button
            onClick={() => { setEditingTramite(null); setShowEditModal(true) }}
            className="btn-primary flex items-center gap-2"
          >
            <PlusIcon className="w-4 h-4" /> Nuevo trámite
          </button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(6)].map((_, i) => <div key={i} className="h-14 bg-gray-100 rounded-xl animate-pulse" />)}</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-semibold text-gray-600">Nombre</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600 hidden lg:table-cell">Código</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600 hidden md:table-cell">Categoría</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-600 hidden md:table-cell">Costo</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {visibleTramites.map(t => (
                <tr key={t.id} className={`hover:bg-gray-50 transition-colors ${!t.is_active ? 'opacity-60 bg-gray-50' : ''}`}>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-800">{t.name}</span>
                      {!t.is_active && (
                        <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-medium">Inactivo</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    <code className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{t.code}</code>
                  </td>
                  <td className="px-4 py-3 text-gray-500 hidden md:table-cell capitalize">{t.category}</td>
                  <td className="px-4 py-3 text-gray-500 hidden md:table-cell">
                    {t.cost > 0 ? `Bs. ${t.cost}` : <span className="text-green-600 font-medium">Gratis</span>}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => setRequirementsFor(t)}
                        className="flex items-center gap-1 text-xs text-emerald-600 hover:text-emerald-800 bg-emerald-50 hover:bg-emerald-100 px-2 py-1 rounded-lg transition-colors"
                        title="Gestionar requisitos"
                      >
                        <ListBulletIcon className="w-4 h-4" />
                        <span className="hidden sm:inline">Requisitos</span>
                      </button>
                      <button
                        onClick={() => { setEditingTramite(t); setShowEditModal(true) }}
                        className="p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Editar trámite"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleToggleActive(t)}
                        className={`p-1.5 rounded-lg transition-colors ${t.is_active
                          ? 'text-red-500 hover:text-red-700 hover:bg-red-50'
                          : 'text-green-600 hover:text-green-800 hover:bg-green-50'}`}
                        title={t.is_active ? 'Desactivar trámite' : 'Activar trámite'}
                      >
                        {t.is_active ? <TrashIcon className="w-4 h-4" /> : <ChevronUpIcon className="w-4 h-4" />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {visibleTramites.length === 0 && (
            <div className="text-center py-12 text-gray-400 text-sm">No hay trámites.</div>
          )}
        </div>
      )}

      {showEditModal && (
        <TramiteModal
          tramite={editingTramite}
          onClose={() => setShowEditModal(false)}
          onSaved={load}
        />
      )}

      {requirementsFor && (
        <RequirementsModal
          tramite={requirementsFor}
          onClose={() => setRequirementsFor(null)}
        />
      )}
    </div>
  )
}
