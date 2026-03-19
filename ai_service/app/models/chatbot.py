"""
3-layer chatbot pipeline:
  Layer 1 — BERT classifier: identifies the tramite intent
  Layer 2 — Aspect classifier: detects what aspect the user is asking about
  Layer 3 — Claude (Haiku): generates a natural, fluid Spanish response

Falls back to static templates if Claude is unavailable.
"""
from typing import Optional
import httpx
from app.models.classifier import classifier_model
from app.models.aspect_classifier import classify_aspect
from app.models.claude_client import generate_response
from app.config import settings

# ---------------------------------------------------------------------------
# Static templates (fallback when Claude is unavailable)
# ---------------------------------------------------------------------------
TRAMITE_TEMPLATES = {
    "TRAMITE_MATRICULA_ALUMNO_NUEVO": {
        "greeting": "Te ayudo con la **inscripción y matriculación para estudiantes nuevos**.",
        "description": (
            "Este trámite es para bachilleres admitidos por preuniversitario, mejores bachilleres, mérito deportivo, olimpiadas científicas o examen de admisión.\n\n"
            "**Documentos a subir en admision.usfx.bo:**\n"
            "• Diploma de Bachiller legalizado por SEDUCA (anverso y reverso)\n"
            "• Libreta de 6to de secundaria o certificado de egreso\n"
            "• Cédula de identidad (anverso y reverso)\n"
            "• Fotografía tipo carnet con fondo blanco\n\n"
            "**Proceso de pago:**\n"
            "Depositar en Banco Unión Cta. 1-33340493 (UMSFX – REC. PROPIOS – MATRÍCULAS) o pagar con QR en universitarios.usfx.bo."
        ),
        "cta": "¿Quieres ver el paso a paso completo del proceso de inscripción?",
    },
    "TRAMITE_MATRICULA_ALUMNO_REGULAR": {
        "greeting": "Te ayudo con la **matriculación para estudiantes regulares**.",
        "description": (
            "Este trámite es para estudiantes que ya cursaron al menos un semestre en la USFX.\n\n"
            "**Proceso:**\n"
            "1. Ingresar a universitarios.usfx.bo → opción **MATRICULARME**\n"
            "2. Generar el importe a pagar\n"
            "3. Depositar en Banco Unión Cta. 1-33340493 o pagar con QR\n"
            "4. Registrar número de depósito bancario en el sistema\n\n"
            "⚠️ Si el depósito no aparece, puede tardar **hasta 4 horas** en actualizarse."
        ),
        "cta": "¿Necesitas ayuda con algún paso en particular?",
    },
    "TRAMITE_DIPLOMA_ACADEMICO": {
        "greeting": "Te guío en el trámite del **Diploma Académico**.",
        "description": (
            "**Requisitos principales:**\n"
            "• Fotocopia CI vigente\n"
            "• Carnet universitario vigente\n"
            "• Certificados originales de notas / kardex firmado por kardixta\n"
            "• Certificado de Conclusión de Estudios\n"
            "• Certificado de Nacimiento original actualizado\n"
            "• Solvencia Universitaria (válida 48 horas desde primera firma)\n"
            "• Fotocopia legalizada del Diploma de Bachiller\n"
            "• Certificado de aprobación de modalidad de graduación\n"
            "• 3 fotografías 4×4 fondo rojo, sobre, funda plástica oficio, papel valorado\n\n"
            "**Proceso:** Ingresar a universitarios.usfx.bo → Trámites → Diploma Académico → generar formulario → presentar en Caja."
        ),
        "cta": "¿Quieres conocer el proceso completo en el sistema SUNIVER?",
    },
    "TRAMITE_TITULO_PROVISION_NACIONAL": {
        "greeting": "Te ayudo con el trámite del **Título en Provisión Nacional**.",
        "description": (
            "**Requisitos:**\n"
            "• Fotocopia legalizada del Diploma Académico\n"
            "• Fotocopia simple del Certificado de Nacimiento\n"
            "• Fólder universitario\n"
            "• 3 fotografías 4×4 fondo rojo\n"
            "• Valores universitarios\n"
            "• Sobre para fotografías\n\n"
            "**Proceso:** Ingresar al sistema SUNIVER (si2.usfx.bo/suniver) → Trámites Académicos → Título en Provisión Nacional → generar formulario → presentar en Caja."
        ),
        "cta": "¿Tienes dudas sobre algún requisito específico?",
    },
    "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION": {
        "greeting": "Te informo sobre el **trámite simultáneo: Diploma Académico + Título en Provisión Nacional**.",
        "description": (
            "Puedes obtener ambos al mismo tiempo. Requiere documentos combinados:\n\n"
            "• Fotocopia CI, Diploma Bachiller legalizado\n"
            "• Solvencia Universitaria (válida 48 horas)\n"
            "• Certificado de Nacimiento original actualizado\n"
            "• Certificados originales de notas / kardex firmado\n"
            "• Certificado de Conclusión de Estudios\n"
            "• Carnet universitario vigente\n"
            "• **6 fotografías** 4×4 fondo rojo (3 por cada título)\n"
            "• Fólder universitario, funda plástica oficio, papel valorado, sobre, valores universitarios\n\n"
            "**Proceso:** SUNIVER → Trámites → seleccionar opción simultánea."
        ),
        "cta": "¿Quieres saber los costos de ambos trámites juntos?",
    },
    "PROCESO_MATRICULACION_WEB": {
        "greeting": "Te explico cómo **matricularte en el sistema web de la USFX**.",
        "description": (
            "**Sistema:** universitarios.usfx.bo (o si2.usfx.bo/suniver)\n\n"
            "**Pasos:**\n"
            "1. Iniciar sesión con tu usuario y contraseña\n"
            "2. Ir a menú **Matrículas** → **Matricularme**\n"
            "3. Elegir modalidad de pago:\n"
            "   • **Depósito Bancario:** deposita en Banco Unión e ingresa el número de papeleta\n"
            "   • **Pago QR:** genera el código QR y paga (confirmación inmediata)\n"
            "4. Verificar en Matrículas → **Mis Matrículas**\n\n"
            "⚠️ **Importante:** No se aceptan transferencias bancarias. El depósito puede tardar hasta **4 horas** en aparecer en el sistema."
        ),
        "cta": "¿Tienes algún problema con el depósito o el sistema?",
    },
    "PROCESO_PROGRAMACION_ACADEMICA": {
        "greeting": "Te explico cómo hacer tu **programación académica de materias**.",
        "description": (
            "La programación académica es donde inscribes tus materias para el semestre. **Primero debes tener matrícula vigente.**\n\n"
            "**Pasos:**\n"
            "1. Ingresar a si2.usfx.bo/suniver con tu usuario y contraseña\n"
            "2. Ir al menú **Programaciones** → **Programarme**\n"
            "3. Seguir las instrucciones según tu tipo:\n"
            "   • **Automática:** el sistema asigna materias automáticamente\n"
            "   • **Manual:** necesitas tu kardex de la facultad\n"
            "4. Revisar y confirmar tu programación\n"
            "5. Verificar en Programaciones → **Mis Programaciones**"
        ),
        "cta": "¿Tu carrera tiene programación automática o manual?",
    },
    "SEGURO_SOCIAL_UNIVERSITARIO": {
        "greeting": "Te ayudo con el **Seguro Social Universitario Estudiantil (SSUE)**.",
        "description": (
            "Para recibir atención médica en el SSU necesitas una **ficha de atención médica vigente**.\n\n"
            "**Cómo obtener tu ficha:**\n"
            "1. Ir a ssu-sucre.org/ficha\n"
            "2. Hacer clic en **EMITIR FICHA ESTUDIANTIL**\n"
            "3. Ingresar tu carnet universitario y contraseña\n"
            "4. Seleccionar la fecha de consulta\n"
            "5. Elegir la especialidad (hay 18 disponibles)\n"
            "6. Elegir el horario disponible y confirmar\n\n"
            "⚠️ Es **obligatorio** presentar el Carnet Universitario en todas las atenciones."
        ),
        "cta": "¿Necesitas saber qué especialidades están disponibles?",
    },
    "SALUDO_BIENVENIDA": {
        "greeting": "¡Hola! 👋 Bienvenido al asistente virtual de la **USFX Facultad de Tecnología**.",
        "description": "Estoy aquí para ayudarte con trámites universitarios como matrículas, diplomas, títulos, programación académica, seguro universitario y más.",
        "cta": "¿En qué puedo ayudarte hoy?",
    },
    "DESPEDIDA": {
        "greeting": "¡Hasta luego! 👋",
        "description": "Fue un gusto ayudarte. Si tienes más dudas sobre trámites universitarios, no dudes en volver.",
        "cta": "¡Éxitos en tus trámites! 🎓",
    },
    "AGRADECIMIENTO": {
        "greeting": "¡Con gusto! 😊",
        "description": "Para eso estoy aquí. Si necesitas más información sobre otro trámite universitario, puedes preguntarme.",
        "cta": "¿Hay algo más en lo que pueda ayudarte?",
    },
    "FALLBACK": {
        "greeting": "No entendí completamente tu consulta 😅",
        "description": (
            "Puedo ayudarte con:\n"
            "• **Matrícula** (nuevo ingreso o regular)\n"
            "• **Diploma Académico** y **Título en Provisión Nacional**\n"
            "• **Programación académica** de materias\n"
            "• **Seguro Social Universitario** (SSUE)\n"
            "• Proceso de matriculación en el **sistema web**"
        ),
        "cta": "¿Podrías reformular tu pregunta o elegir uno de los temas de arriba?",
    },
}

CONFIDENCE_THRESHOLD = 0.15
NON_TRAMITE_INTENTS = ("SALUDO_BIENVENIDA", "DESPEDIDA", "AGRADECIMIENTO", "FALLBACK")

# Intents that Claude should also handle (richer conversational responses)
CLAUDE_ENABLED_INTENTS = (
    "SALUDO_BIENVENIDA", "AGRADECIMIENTO", "DESPEDIDA", "FALLBACK"
)


def _build_static_response(intent: str, confidence: float, tramite_data: Optional[dict]) -> dict:
    """Build the static template response (used as fallback)."""
    template = TRAMITE_TEMPLATES.get(intent, TRAMITE_TEMPLATES["FALLBACK"])
    is_low_confidence = confidence < CONFIDENCE_THRESHOLD

    if is_low_confidence:
        response = (
            "No entendí completamente tu consulta 😅 ¿Podrías ser más específico?\n\n"
            "Puedo ayudarte con:\n"
            "• Matrícula (nuevo ingreso o regular)\n"
            "• Diploma Académico y Título en Provisión Nacional\n"
            "• Programación académica de materias\n"
            "• Proceso de matriculación en el sistema web\n"
            "• Seguro Social Universitario (SSUE)"
        )
        return {
            "response": response,
            "classified_intent": intent,
            "tramite_id": None,
            "confidence": confidence,
            "step": None,
            "show_tramite_card": False,
        }

    tramite_id = tramite_data.get("id") if tramite_data else None
    response_parts = [
        template["greeting"],
        "",
        template["description"],
        "",
        template["cta"],
    ]

    if tramite_data:
        response_parts.extend([
            "",
            f"⏱ Tiempo estimado: {tramite_data.get('duration_days', '?')} días hábiles",
            f"💰 Costo: Bs. {tramite_data.get('cost', '0.00')}",
        ])

    return {
        "response": "\n".join(response_parts),
        "classified_intent": intent,
        "tramite_id": str(tramite_id) if tramite_id else None,
        "confidence": confidence,
        "step": 1,
        "show_tramite_card": intent not in NON_TRAMITE_INTENTS,
    }


async def process_chat(session_id: str, message: str, history: list) -> dict:
    """
    Main chatbot pipeline — 3 layers:
      1. BERT: classify intent (tramite)
      2. Aspect classifier: what is the user asking about?
      3. Claude: generate natural response using tramite data + aspect + history
    """
    # --- Layer 1: Intent classification ---
    result = classifier_model.predict(message)
    intent = result["label"]
    confidence = result["confidence"]

    # Low confidence → fallback immediately (no point calling Claude)
    if confidence < CONFIDENCE_THRESHOLD:
        return _build_static_response(intent, confidence, None)

    # --- Fetch tramite data from backend (for tramite-specific intents) ---
    tramite_data = None
    if intent not in NON_TRAMITE_INTENTS:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.backend_url}/api/v1/tramites",
                    params={"is_active": True},
                )
                if resp.status_code == 200:
                    tramites = resp.json()
                    tramite_data = next(
                        (t for t in tramites if t.get("code") == intent), None
                    )
        except Exception:
            pass

    # --- Layer 2: Aspect classification ---
    aspect = classify_aspect(message)

    # --- Layer 3: Claude response ---
    template = TRAMITE_TEMPLATES.get(intent, TRAMITE_TEMPLATES["FALLBACK"])
    claude_response = await generate_response(
        intent=intent,
        aspect=aspect,
        user_message=message,
        history=history,
        tramite_data=tramite_data,
        tramite_template=template,
    )

    # If Claude succeeded, return its response
    if claude_response:
        tramite_id = tramite_data.get("id") if tramite_data else None
        return {
            "response": claude_response,
            "classified_intent": intent,
            "tramite_id": str(tramite_id) if tramite_id else None,
            "confidence": confidence,
            "step": 1,
            "show_tramite_card": intent not in NON_TRAMITE_INTENTS,
        }

    # --- Fallback: static template ---
    return _build_static_response(intent, confidence, tramite_data)
