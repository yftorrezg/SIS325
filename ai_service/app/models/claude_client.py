"""
Claude-powered response generator.
Receives tramite context + aspect + conversation history and produces
a natural, fluid Spanish response for the student.
"""
import logging
import os
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)

_client: Optional[anthropic.Anthropic] = None
_runtime_api_key: Optional[str] = None  # set via admin panel at runtime


def set_runtime_key(key: str) -> None:
    """Activate Claude layer by providing an API key at runtime."""
    global _runtime_api_key, _client
    _runtime_api_key = key.strip() if key else None
    _client = None  # force client recreation with new key
    logger.info("Claude API key updated via admin panel")


def clear_runtime_key() -> None:
    """Deactivate Claude layer."""
    global _runtime_api_key, _client
    _runtime_api_key = None
    _client = None
    logger.info("Claude API key cleared — falling back to templates")


def get_key_status() -> dict:
    """Return current key status without exposing the key itself."""
    if _runtime_api_key:
        return {"active": True, "source": "runtime"}
    env_key = os.getenv("CLAUDE_API_KEY", "")
    if env_key:
        return {"active": True, "source": "env"}
    return {"active": False, "source": "none"}


def _get_client() -> anthropic.Anthropic:
    global _client
    key = _runtime_api_key or os.getenv("CLAUDE_API_KEY", "")
    if not key:
        raise RuntimeError("CLAUDE_API_KEY not set")
    if _client is None:
        _client = anthropic.Anthropic(api_key=key)
    return _client


# Human-readable names for tramite labels
_TRAMITE_NAMES = {
    "TRAMITE_MATRICULA_ALUMNO_NUEVO": "Matrícula para Alumno Nuevo",
    "TRAMITE_MATRICULA_ALUMNO_REGULAR": "Matrícula para Alumno Regular",
    "TRAMITE_DIPLOMA_ACADEMICO": "Diploma Académico",
    "TRAMITE_TITULO_PROVISION_NACIONAL": "Título en Provisión Nacional",
    "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION": "Trámite Simultáneo Diploma + Título en Provisión",
    "PROCESO_MATRICULACION_WEB": "Matriculación en el Sistema Web (SUNIVER)",
    "PROCESO_PROGRAMACION_ACADEMICA": "Programación Académica de Materias",
    "SEGURO_SOCIAL_UNIVERSITARIO": "Seguro Social Universitario Estudiantil (SSUE)",
}

_ASPECT_NAMES = {
    "REQUISITOS": "requisitos y documentos necesarios",
    "PASOS": "pasos del proceso",
    "COSTO": "costo del trámite",
    "PLAZO": "tiempo que tarda el trámite",
    "UBICACION": "dónde se realiza el trámite",
    "CONTACTO": "contacto del responsable",
    "SISTEMA_WEB": "cómo hacerlo en el sistema web",
    "GENERAL": "información general",
}


def _build_tramite_context(tramite_data: Optional[dict], aspect: str = "GENERAL") -> str:
    """Build a context string focused on the detected aspect to minimize token usage."""
    if not tramite_data:
        return ""

    lines = []
    if tramite_data.get("name"):
        lines.append(f"Nombre: {tramite_data['name']}")
    if tramite_data.get("description"):
        lines.append(f"Descripción: {tramite_data['description']}")

    # Always include cost and duration as they are commonly asked in follow-ups
    if tramite_data.get("cost") is not None:
        lines.append(f"Costo: Bs. {tramite_data['cost']}")
    if tramite_data.get("cost_details"):
        lines.append(f"Detalles de pago: {tramite_data['cost_details']}")
    if tramite_data.get("duration_days"):
        lines.append(f"Duración estimada: {tramite_data['duration_days']} días hábiles")
    if tramite_data.get("duration_details"):
        lines.append(f"Detalles del plazo: {tramite_data['duration_details']}")

    # Aspect-specific fields
    if aspect in ("UBICACION", "GENERAL", "CONTACTO"):
        if tramite_data.get("office_location"):
            lines.append(f"Ubicación: {tramite_data['office_location']}")
    if aspect in ("CONTACTO", "GENERAL", "UBICACION"):
        if tramite_data.get("contact_info"):
            lines.append(f"Contacto: {tramite_data['contact_info']}")
    if aspect in ("SISTEMA_WEB", "GENERAL", "PASOS"):
        if tramite_data.get("web_system_url"):
            lines.append(f"Sistema web: {tramite_data['web_system_url']}")
        if tramite_data.get("web_instructions"):
            lines.append(f"Instrucciones web:\n{tramite_data['web_instructions']}")

    # Requirements/steps — include for REQUISITOS, PASOS, and GENERAL
    if aspect in ("REQUISITOS", "PASOS", "GENERAL"):
        requirements = tramite_data.get("requirements", [])
        if requirements:
            lines.append("\nRequisitos/pasos:")
            for req in sorted(requirements, key=lambda r: r.get("step_number", 0)):
                mandatory = "" if req.get("is_mandatory", True) else " (opcional)"
                title = req.get("title", "")
                desc = req.get("description", "")
                doc = req.get("document_name", "")
                note = req.get("notes", "")
                step = f"  {req.get('step_number', '')}. {title}{mandatory}"
                if desc:
                    step += f": {desc}"
                if doc:
                    step += f" [{doc}]"
                if note:
                    step += f" — Nota: {note}"
                lines.append(step)

    return "\n".join(lines)


def _build_system_prompt(
    intent: str,
    aspect: str,
    tramite_data: Optional[dict],
    tramite_template: Optional[dict],
) -> str:
    tramite_name = _TRAMITE_NAMES.get(intent, intent)
    aspect_name = _ASPECT_NAMES.get(aspect, "información general")
    tramite_ctx = _build_tramite_context(tramite_data, aspect)

    # Fallback: use template description if no DB data
    template_info = ""
    if tramite_template:
        template_info = f"""
Información de referencia del trámite:
{tramite_template.get('description', '')}
"""

    return f"""Eres el asistente virtual de la Facultad de Tecnología de la Universidad San Francisco Xavier (USFX) en Sucre, Bolivia.

Tu tarea es responder preguntas de estudiantes sobre trámites universitarios de forma clara, amigable y natural, como si fuera una conversación real.

TRÁMITE IDENTIFICADO: {tramite_name}
ASPECTO QUE PREGUNTA: {aspect_name}

{"DATOS OFICIALES DEL TRÁMITE (base de datos):" + chr(10) + tramite_ctx if tramite_ctx else ""}
{template_info}

REGLAS IMPORTANTES:
- Responde SIEMPRE en español boliviano informal pero respetuoso (usa "vos" o "tú", evita "usted" salvo que el estudiante lo use).
- Sé conciso pero completo. No hagas listas enormes si no es necesario.
- Si el estudiante pregunta algo específico sobre el aspecto detectado, enfócate en eso.
- Si no tienes información exacta sobre algo (como horarios o teléfonos específicos), dilo claramente y sugiere que vaya a la facultad o al sistema SUNIVER.
- Puedes usar emojis con moderación para hacer la respuesta más amigable.
- NO inventes datos, costos, plazos o requisitos que no estén en la información provista.
- Si el estudiante hace una pregunta de seguimiento sobre el mismo trámite, responde de forma coherente con el historial de la conversación.
- Mantén respuestas de máximo 4-5 líneas salvo que el tema requiera más detalle (ej. lista completa de requisitos).
- Al final de tu respuesta, puedes invitar brevemente a seguir preguntando, pero sin ser repetitivo."""


async def generate_response(
    intent: str,
    aspect: str,
    user_message: str,
    history: list[dict],
    tramite_data: Optional[dict] = None,
    tramite_template: Optional[dict] = None,
) -> str:
    """Call Claude to generate a natural response."""
    try:
        client = _get_client()

        system_prompt = _build_system_prompt(intent, aspect, tramite_data, tramite_template)

        # Build messages: last 8 turns of history + current user message
        messages = []
        for turn in history[-8:]:
            role = turn.get("role", "user")
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})

        response = await _call_claude(client, system_prompt, messages)
        return response

    except Exception as e:
        logger.error(f"Claude error: {e}")
        return None  # caller will fall back to template


async def _call_claude(
    client: anthropic.Anthropic,
    system_prompt: str,
    messages: list[dict],
) -> str:
    import asyncio
    loop = asyncio.get_event_loop()

    def _sync_call():
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=messages,
        )
        return resp.content[0].text

    return await loop.run_in_executor(None, _sync_call)
