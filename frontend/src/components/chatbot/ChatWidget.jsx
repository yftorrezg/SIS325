import { useState, useRef, useEffect } from 'react'
import {
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  MicrophoneIcon,
  StopIcon,
} from '@heroicons/react/24/solid'
import { SparklesIcon, BoltIcon } from '@heroicons/react/24/outline'
import { aiService } from '../../services/api'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import ReactMarkdown from 'react-markdown'

const SESSION_ID = `session_${Math.random().toString(36).slice(2)}`

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '¡Hola! 👋 Soy el asistente virtual de la **Facultad de Tecnología USFX**. ¿En qué puedo ayudarte? Podés escribir o usar el micrófono.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [recording, setRecording] = useState(false)
  const [tramiteLink, setTramiteLink] = useState(null)
  const [claudeEnabled, setClaudeEnabled] = useState(false)
  const mediaRef = useRef(null)
  const chunksRef = useRef([])
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const toggleClaude = () => {
    const next = !claudeEnabled
    setClaudeEnabled(next)
    const msg = next
      ? '✨ **Claude IA activado.** Las respuestas ahora serán generadas por inteligencia artificial avanzada.'
      : '🔵 **Modo estándar activado.** Las respuestas vienen directamente de la base de datos de trámites.'
    setMessages(prev => [...prev, { role: 'assistant', content: msg }])
  }

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return
    const userMsg = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setTramiteLink(null)
    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
      const res = await aiService.chat({
        session_id: SESSION_ID,
        message: text,
        history,
        claude_enabled: claudeEnabled,
      })
      const { response, tramite_id, show_tramite_card } = res.data
      setMessages(prev => [...prev, { role: 'assistant', content: response }])
      if (show_tramite_card && tramite_id) setTramiteLink(tramite_id)
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Lo siento, hubo un error. Por favor intentá de nuevo.' }])
    } finally {
      setLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = e => chunksRef.current.push(e.data)
      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const formData = new FormData()
        formData.append('audio', blob, 'recording.webm')
        try {
          const res = await aiService.transcribe(formData)
          if (res.data.text) sendMessage(res.data.text)
        } catch {
          setMessages(prev => [...prev, { role: 'assistant', content: 'No pude transcribir el audio. Por favor escribí tu consulta.' }])
        }
      }
      recorder.start()
      mediaRef.current = recorder
      setRecording(true)
    } catch {
      alert('No se pudo acceder al micrófono')
    }
  }

  const stopRecording = () => {
    mediaRef.current?.stop()
    setRecording(false)
  }

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setOpen(!open)}
        className={clsx(
          'fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all z-50',
          open ? 'bg-gray-700 hover:bg-gray-800' : 'bg-blue-700 hover:bg-blue-800'
        )}
        aria-label="Chat de ayuda"
      >
        {open ? <XMarkIcon className="w-6 h-6 text-white" /> : <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />}
      </button>

      {/* Chat window */}
      {open && (
        <div className="fixed bottom-24 right-6 w-[360px] max-w-[calc(100vw-24px)] h-[540px] max-h-[80vh] flex flex-col card shadow-2xl z-50 overflow-hidden">
          {/* Header */}
          <div className="bg-blue-800 px-4 py-3 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <SparklesIcon className="w-5 h-5 text-yellow-400" />
              <div>
                <p className="text-white font-semibold text-sm">Asistente Virtual</p>
                <p className="text-blue-300 text-xs">Facultad de Tecnología USFX</p>
              </div>
            </div>
            {/* Claude toggle button */}
            <button
              onClick={toggleClaude}
              title={claudeEnabled ? 'Claude IA activo — clic para desactivar' : 'Activar Claude IA (respuestas más naturales)'}
              className={clsx(
                'flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-semibold transition-all border',
                claudeEnabled
                  ? 'bg-purple-600 border-purple-400 text-white shadow-lg shadow-purple-900/40'
                  : 'bg-transparent border-blue-600 text-blue-300 hover:border-purple-400 hover:text-purple-300'
              )}
            >
              <BoltIcon className={clsx('w-3.5 h-3.5', claudeEnabled ? 'text-yellow-300' : '')} />
              {claudeEnabled ? 'Claude IA' : 'Claude'}
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.map((msg, i) => (
              <div key={i} className={clsx('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div className={clsx('max-w-[88%] px-3 py-2 text-sm', msg.role === 'user' ? 'chat-user' : 'chat-bot')}>
                  <ReactMarkdown className="prose prose-sm max-w-none prose-p:my-0.5 prose-ul:my-0.5 prose-li:my-0">
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="chat-bot px-3 py-2 text-sm text-gray-500 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"/>
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"/>
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"/>
                </div>
              </div>
            )}
            {tramiteLink && (
              <div className="flex justify-start">
                <Link
                  to={`/tramites/${tramiteLink}`}
                  onClick={() => setOpen(false)}
                  className="text-xs bg-blue-50 border border-blue-200 text-blue-700 px-3 py-2 rounded-xl hover:bg-blue-100 transition-colors"
                >
                  Ver requisitos completos del trámite →
                </Link>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-gray-200 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
              placeholder="Escribe tu consulta..."
              className="flex-1 text-sm border border-gray-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading || recording}
            />
            <button
              onClick={recording ? stopRecording : startRecording}
              className={clsx('w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors', recording ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-100 hover:bg-gray-200')}
              title={recording ? 'Detener grabación' : 'Grabar audio'}
            >
              {recording ? <StopIcon className="w-4 h-4 text-white" /> : <MicrophoneIcon className="w-4 h-4 text-gray-600" />}
            </button>
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              className="w-9 h-9 bg-blue-700 hover:bg-blue-800 disabled:opacity-50 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
            >
              <PaperAirplaneIcon className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
