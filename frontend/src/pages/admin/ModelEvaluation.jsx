import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { CpuChipIcon, ClockIcon, FolderIcon, BoltIcon, TrophyIcon, TrashIcon, SparklesIcon, KeyIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { modelVersionService } from '../../services/api'

const AI_URL = import.meta.env.VITE_AI_URL || 'http://localhost:8001'

export default function ModelEvaluation() {
  const [modelInfo, setModelInfo] = useState(null)
  const [training, setTraining] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)

  // Claude key state
  const [claudeStatus, setClaudeStatus] = useState(null)
  const [showClaudeModal, setShowClaudeModal] = useState(false)
  const [claudeKey, setClaudeKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [savingKey, setSavingKey] = useState(false)
  const [cfg, setCfg] = useState({
    version_tag: 'v1.0.2',
    base_model: 'dccuchile/bert-base-spanish-wwm-cased',
    epochs: 3,
    batch_size: 16,
    learning_rate: 0.00002,
    dropout: 0.1,
    warmup_ratio: 0.1,
    weight_decay: 0.01,
    max_length: 128,
  })
  const set = (k, v) => setCfg(p => ({ ...p, [k]: v }))
  const [history, setHistory] = useState([])
  const [activating, setActivating] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting, setDeleting] = useState(false)

  const fetchClaudeStatus = () => {
    axios.get(`${AI_URL}/metrics/claude-status`).then(r => setClaudeStatus(r.data)).catch(() => {})
  }

  const handleSaveClaudeKey = async () => {
    if (!claudeKey.trim()) return
    setSavingKey(true)
    try {
      await axios.post(`${AI_URL}/metrics/claude-key`, { api_key: claudeKey.trim() })
      toast.success('Claude activado correctamente')
      setShowClaudeModal(false)
      setClaudeKey('')
      fetchClaudeStatus()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error al activar Claude')
    } finally {
      setSavingKey(false)
    }
  }

  const handleClearClaudeKey = async () => {
    try {
      await axios.delete(`${AI_URL}/metrics/claude-key`)
      toast.success('Claude desactivado')
      fetchClaudeStatus()
    } catch {
      toast.error('Error al desactivar Claude')
    }
  }

  useEffect(() => {
    axios.get(`${AI_URL}/metrics/model-info`).then(r => setModelInfo(r.data)).catch(() => {})
    fetchHistory()
    fetchClaudeStatus()
  }, [])

  const fetchHistory = () => {
    modelVersionService.list()
      .then(r => setHistory(r.data))
      .catch(() => {})
  }

  const handleActivate = async (version) => {
    setActivating(version.id)
    const toastId = toast.loading(`Cargando modelo ${version.version_tag}... (puede tardar 1-2 min)`)
    try {
      await modelVersionService.activate(version.id)
      toast.success(`Modelo ${version.version_tag} activado`, { id: toastId })
      fetchHistory()
      axios.get(`${AI_URL}/metrics/model-info`).then(r => setModelInfo(r.data)).catch(() => {})
    } catch (e) {
      toast.error('Error al activar: ' + (e.response?.data?.detail || e.message), { id: toastId })
    } finally {
      setActivating(null)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await modelVersionService.delete(deleteTarget.id)
      toast.success(`Modelo ${deleteTarget.version_tag} eliminado`)
      setDeleteTarget(null)
      fetchHistory()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error al eliminar')
    } finally {
      setDeleting(false)
    }
  }

  // Encuentra el modelo con mejor F1 (o accuracy si no hay F1)
  const bestId = history.length > 0
    ? history.filter(v => v.f1_score != null).sort((a, b) => b.f1_score - a.f1_score)[0]?.id
    : null

  useEffect(() => {
    if (!jobId) return
    const interval = setInterval(async () => {
      try {
        const r = await axios.get(`${AI_URL}/train/${jobId}`)
        setJobStatus(r.data)
        if (['completed', 'failed'].includes(r.data.status)) {
          clearInterval(interval)
          setTraining(false)
          if (r.data.status === 'completed') {
            toast.success('Entrenamiento completado')
            fetchHistory()
          } else {
            toast.error('Entrenamiento falló: ' + r.data.message)
          }
        }
      } catch {}
    }, 3000)
    return () => clearInterval(interval)
  }, [jobId])

  const startTraining = async () => {
    setTraining(true)
    setJobStatus(null)
    try {
      const payload = {
        ...cfg,
        epochs: parseInt(cfg.epochs),
        batch_size: parseInt(cfg.batch_size),
        learning_rate: parseFloat(cfg.learning_rate),
        dropout: parseFloat(cfg.dropout),
        warmup_ratio: parseFloat(cfg.warmup_ratio),
        weight_decay: parseFloat(cfg.weight_decay),
        max_length: parseInt(cfg.max_length),
      }
      const r = await axios.post(`${AI_URL}/train`, payload)
      setJobId(r.data.job_id)
      setJobStatus(r.data)
      toast.success('Entrenamiento iniciado')
    } catch (e) {
      toast.error('Error al iniciar: ' + (e.response?.data?.detail || e.message))
      setTraining(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Evaluación del Modelo IA</h1>

      {/* Claude API Key card */}
      <div className={`card p-5 mb-4 border-2 ${claudeStatus?.active ? 'border-purple-200 bg-purple-50' : 'border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${claudeStatus?.active ? 'bg-purple-100' : 'bg-gray-100'}`}>
              <SparklesIcon className={`w-5 h-5 ${claudeStatus?.active ? 'text-purple-600' : 'text-gray-400'}`} />
            </div>
            <div>
              <h2 className="font-semibold text-gray-800 flex items-center gap-2">
                Capa 3: Claude AI
                {claudeStatus?.active ? (
                  <span className="inline-flex items-center gap-1 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-medium">
                    ✓ Activo
                    {claudeStatus.source === 'env' && <span className="text-purple-400">(env)</span>}
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                    Inactivo — usando templates estáticos
                  </span>
                )}
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                {claudeStatus?.active
                  ? 'El chatbot genera respuestas naturales con contexto del trámite detectado.'
                  : 'El chatbot responde con plantillas predefinidas. Activa Claude para respuestas más fluidas.'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {claudeStatus?.active && claudeStatus.source === 'runtime' && (
              <button
                onClick={handleClearClaudeKey}
                className="text-xs text-red-500 hover:text-red-700 px-3 py-1.5 rounded-lg border border-red-200 hover:bg-red-50 transition-colors"
              >
                Desactivar
              </button>
            )}
            <button
              onClick={() => setShowClaudeModal(true)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                claudeStatus?.active
                  ? 'bg-purple-100 hover:bg-purple-200 text-purple-700'
                  : 'bg-purple-600 hover:bg-purple-700 text-white'
              }`}
            >
              <KeyIcon className="w-4 h-4" />
              {claudeStatus?.active ? 'Cambiar API Key' : 'Activar Claude'}
            </button>
          </div>
        </div>
        {claudeStatus?.active && (
          <div className="mt-3 pt-3 border-t border-purple-100 grid grid-cols-3 gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-purple-700">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block" />
              Respuestas contextuales
            </div>
            <div className="flex items-center gap-1.5 text-purple-700">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block" />
              Detecta el aspecto preguntado
            </div>
            <div className="flex items-center gap-1.5 text-purple-700">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block" />
              Recuerda el historial de conversación
            </div>
          </div>
        )}
      </div>

      {/* Model info */}
      {modelInfo && (
        <div className="card p-5 mb-4">
          <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <CpuChipIcon className="w-5 h-5 text-blue-600" />
            Estado del modelo activo
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><p className="text-gray-500 text-xs">Estado</p><p className="font-medium">{modelInfo.is_loaded ? '✅ Cargado' : '⚠️ No cargado'}</p></div>
            <div><p className="text-gray-500 text-xs">Versión</p><p className="font-medium">{modelInfo.version}</p></div>
            <div><p className="text-gray-500 text-xs">Método</p><p className="font-medium capitalize">{modelInfo.method}</p></div>
            <div><p className="text-gray-500 text-xs">Dispositivo</p><p className="font-medium uppercase">{modelInfo.device}</p></div>
          </div>
        </div>
      )}

      {/* Training panel */}
      <div className="card p-5 mb-4">
        <h2 className="font-semibold text-gray-800 mb-4">Entrenar modelo</h2>

        {/* Modelo base */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-600 mb-2">Modelo base</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {[
              { id: 'dccuchile/bert-base-spanish-wwm-cased',   name: 'BERT Spanish', desc: 'Recomendado · entrenado en Wikipedia español' },
              { id: 'bertin-project/bertin-roberta-base-spanish', name: 'RoBERTa Spanish (BERTIN)', desc: 'Mayor precisión · RoBERTa entrenado en español' },
              { id: 'xlm-roberta-base',                        name: 'XLM-RoBERTa', desc: 'Multilingüe · muy robusto, más lento' },
              { id: 'distilbert-base-multilingual-cased',      name: 'DistilBERT Multilingual', desc: 'Rápido y ligero · ideal para producción' },
            ].map(m => (
              <button
                key={m.id}
                onClick={() => set('base_model', m.id)}
                className={`text-left px-4 py-3 rounded-lg border-2 transition-all ${cfg.base_model === m.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
              >
                <p className="font-medium text-sm text-gray-800">{m.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{m.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Hiperparámetros */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Versión <span className="text-red-400">*</span></label>
            <input className="input-field w-full" value={cfg.version_tag} onChange={e => set('version_tag', e.target.value)} placeholder="v1.0.0" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Épocas</label>
            <input type="number" min="1" max="20" className="input-field w-full" value={cfg.epochs} onChange={e => set('epochs', e.target.value)} />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Batch size</label>
            <select className="input-field w-full" value={cfg.batch_size} onChange={e => set('batch_size', e.target.value)}>
              {[8, 16, 32].map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Max length</label>
            <select className="input-field w-full" value={cfg.max_length} onChange={e => set('max_length', e.target.value)}>
              {[64, 128, 256].map(v => <option key={v} value={v}>{v} tokens</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Learning rate</label>
            <select className="input-field w-full" value={cfg.learning_rate} onChange={e => set('learning_rate', e.target.value)}>
              <option value={0.00005}>5e-5</option>
              <option value={0.00003}>3e-5</option>
              <option value={0.00002}>2e-5 (default)</option>
              <option value={0.00001}>1e-5</option>
              <option value={0.000005}>5e-6</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Dropout</label>
            <select className="input-field w-full" value={cfg.dropout} onChange={e => set('dropout', e.target.value)}>
              {[0.0, 0.1, 0.2, 0.3].map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Warmup ratio</label>
            <select className="input-field w-full" value={cfg.warmup_ratio} onChange={e => set('warmup_ratio', e.target.value)}>
              {[0.0, 0.06, 0.1, 0.2].map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Weight decay</label>
            <select className="input-field w-full" value={cfg.weight_decay} onChange={e => set('weight_decay', e.target.value)}>
              {[0.0, 0.01, 0.1].map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
        </div>

        <button onClick={startTraining} disabled={training} className="btn-primary w-full sm:w-auto">
          {training ? 'Entrenando...' : 'Iniciar entrenamiento'}
        </button>
        <div className="mt-4">

        {jobStatus && (
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-700">{jobStatus.message}</p>
              <span className="text-sm text-gray-500">{Math.round((jobStatus.progress || 0) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${(jobStatus.progress || 0) * 100}%` }} />
            </div>
            {jobStatus.metrics && (
              <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white rounded-lg p-3 text-center border border-gray-200">
                  <p className="text-xs text-gray-500">Precisión</p>
                  <p className="text-xl font-bold text-green-600">{(jobStatus.metrics.accuracy * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-gray-200">
                  <p className="text-xs text-gray-500">F1-Score</p>
                  <p className="text-xl font-bold text-blue-600">{(jobStatus.metrics.f1_score * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-gray-200">
                  <p className="text-xs text-gray-500">Train samples</p>
                  <p className="text-xl font-bold text-gray-700">{jobStatus.metrics.training_samples}</p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center border border-gray-200">
                  <p className="text-xs text-gray-500">Val samples</p>
                  <p className="text-xl font-bold text-gray-700">{jobStatus.metrics.val_samples}</p>
                </div>
              </div>
            )}
          </div>
        )}
        </div>
      </div>

      {/* Training history */}
      <div className="card p-5 mb-4">
        <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <ClockIcon className="w-5 h-5 text-gray-500" />
          Historial de modelos entrenados
        </h2>
        {history.length === 0 ? (
          <p className="text-sm text-gray-500">Aún no hay modelos entrenados.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
                  <th className="pb-2 pr-4">Versión</th>
                  <th className="pb-2 pr-4">Modelo base</th>
                  <th className="pb-2 pr-4">Precisión</th>
                  <th className="pb-2 pr-4">F1-Score</th>
                  <th className="pb-2 pr-4">Samples</th>
                  <th className="pb-2 pr-4">Config</th>
                  <th className="pb-2 pr-4">Fecha</th>
                  <th className="pb-2 pr-4">Estado</th>
                  <th className="pb-2" />
                </tr>
              </thead>
              <tbody>
                {history.map(v => (
                  <tr key={v.id} className={`border-b border-gray-100 hover:bg-gray-50 ${v.id === bestId ? 'bg-yellow-50' : ''}`}>
                    <td className="py-2 pr-4">
                      <span className="font-mono font-medium text-blue-700">{v.version_tag}</span>
                      {v.id === bestId && (
                        <span className="ml-2 inline-flex items-center gap-0.5 text-xs bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded-full">
                          <TrophyIcon className="w-3 h-3" /> mejor
                        </span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-xs text-gray-500 max-w-[140px]">
                      <span className="truncate block" title={v.base_model}>
                        {v.base_model ? v.base_model.split('/').pop() : '—'}
                      </span>
                    </td>
                    <td className="py-2 pr-4">
                      {v.accuracy != null
                        ? <span className="font-semibold text-green-600">{(v.accuracy * 100).toFixed(1)}%</span>
                        : <span className="text-gray-400">—</span>}
                    </td>
                    <td className="py-2 pr-4">
                      {v.f1_score != null
                        ? <span className="font-semibold text-blue-600">{(v.f1_score * 100).toFixed(1)}%</span>
                        : <span className="text-gray-400">—</span>}
                    </td>
                    <td className="py-2 pr-4 text-gray-700 text-xs">
                      {v.training_samples_count != null ? `${v.training_samples_count}t / ${v.val_samples_count ?? '?'}v` : '—'}
                    </td>
                    <td className="py-2 pr-4 text-xs text-gray-500">
                      {v.hyperparams ? (
                        <span title={JSON.stringify(v.hyperparams, null, 2)} className="cursor-help underline decoration-dotted">
                          e{v.hyperparams.epochs} · bs{v.hyperparams.batch_size} · lr{v.hyperparams.learning_rate}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="py-2 pr-4 text-gray-500">
                      {new Date(v.trained_at).toLocaleString('es-BO', { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="py-2 pr-4">
                      {v.is_active
                        ? <span className="inline-flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">✓ Activo</span>
                        : <span className="inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">Inactivo</span>}
                    </td>
                    <td className="py-2">
                      <div className="flex items-center gap-1">
                        {!v.is_active && (
                          <button
                            onClick={() => handleActivate(v)}
                            disabled={activating === v.id}
                            className="inline-flex items-center gap-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-2 py-1 rounded-lg font-medium disabled:opacity-50"
                          >
                            <BoltIcon className="w-3 h-3" />
                            {activating === v.id ? '...' : 'Activar'}
                          </button>
                        )}
                        {!v.is_active && (
                          <button
                            onClick={() => setDeleteTarget(v)}
                            className="inline-flex items-center gap-1 text-xs bg-red-50 hover:bg-red-100 text-red-600 px-2 py-1 rounded-lg font-medium"
                          >
                            <TrashIcon className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Model storage info */}
      <div className="card p-5">
        <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <FolderIcon className="w-5 h-5 text-gray-500" />
          Ubicación de modelos guardados
        </h2>
        <p className="text-sm text-gray-600 mb-2">
          Los modelos se guardan en el volumen Docker <code className="bg-gray-100 px-1 rounded">ai_models</code>:
        </p>
        <code className="block bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-700">
          /app/data/models/classifier/&lt;version_tag&gt;/
        </code>
        <p className="text-xs text-gray-500 mt-2">Para explorar los archivos desde tu máquina:</p>
        <code className="block bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-xs text-gray-700 mt-1">
          docker exec -it usfx_ai_service ls /app/data/models/classifier/
        </code>
      </div>
      {/* Modal Claude API Key */}
      {showClaudeModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <SparklesIcon className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">Activar Claude AI</h3>
                <p className="text-xs text-gray-500">La key se guarda en memoria — se pierde al reiniciar el servicio.</p>
              </div>
            </div>

            <div className="bg-purple-50 border border-purple-100 rounded-lg p-3 mb-4 text-xs text-purple-700 space-y-1">
              <p className="font-medium">¿Qué cambia al activar Claude?</p>
              <p>• El chatbot responde de forma natural según el aspecto detectado (costo, pasos, requisitos, etc.)</p>
              <p>• Recuerda el contexto de la conversación</p>
              <p>• Sin Claude: usa plantillas estáticas predefinidas</p>
            </div>

            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key de Anthropic
            </label>
            <div className="relative mb-4">
              <input
                type={showKey ? 'text' : 'password'}
                value={claudeKey}
                onChange={e => setClaudeKey(e.target.value)}
                placeholder="sk-ant-api03-..."
                className="input-field w-full pr-10 font-mono text-sm"
                onKeyDown={e => e.key === 'Enter' && handleSaveClaudeKey()}
              />
              <button
                type="button"
                onClick={() => setShowKey(p => !p)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showKey ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
              </button>
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setShowClaudeModal(false); setClaudeKey('') }}
                disabled={savingKey}
                className="btn-secondary"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveClaudeKey}
                disabled={savingKey || !claudeKey.trim()}
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
              >
                <SparklesIcon className="w-4 h-4" />
                {savingKey ? 'Activando...' : 'Activar Claude'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal confirmar eliminación */}
      {deleteTarget && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
            <h3 className="font-semibold text-gray-800 mb-1">¿Eliminar modelo?</h3>
            <p className="text-sm text-gray-500 mb-1">
              Versión: <span className="font-mono font-medium text-blue-700">{deleteTarget.version_tag}</span>
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Esto eliminará los archivos del disco (~400-500 MB) y el registro. No se puede deshacer.
            </p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setDeleteTarget(null)} disabled={deleting} className="btn-secondary">
                Cancelar
              </button>
              <button onClick={handleDelete} disabled={deleting} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50">
                {deleting ? 'Eliminando...' : 'Eliminar y liberar espacio'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
