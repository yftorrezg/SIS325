"""
3-layer chatbot pipeline:
  Layer 1 — BERT classifier: identifies the tramite intent
  Layer 2 — Aspect classifier: what aspect is the user asking about?
  Layer 3 — Dynamic DB response: rich structured Markdown from live tramite data
             Claude (optional): activated per-request via claude_enabled flag

No static templates — all responses come from the database.
"""
from typing import Optional
import httpx
from app.models.classifier import classifier_model
from app.models.aspect_classifier import classify_aspect
from app.models.claude_client import generate_response
from app.config import settings

# ---------------------------------------------------------------------------
# Minimal hardcoded strings for non-tramite conversational intents only
# ---------------------------------------------------------------------------
NON_TRAMITE_RESPONSES = {
    "SALUDO_BIENVENIDA": (
        "¡Hola! 👋 Soy el asistente virtual de la **Facultad de Tecnología USFX**.\n\n"
        "Puedo ayudarte con:\n"
        "• 🎓 Matrícula (nuevo ingreso o regular)\n"
        "• 📜 Diploma Académico y Título en Provisión Nacional\n"
        "• 🔄 Cambio de carrera o carrera simultánea\n"
        "• 🏆 Titulación (proceso de graduación)\n"
        "• 📋 Certificado académico / Kardex\n"
        "• 🌐 Matriculación y programación en el sistema web\n"
        "• 💊 Seguro Social Universitario\n"
        "• 🎫 Becas, carnet universitario, reprogramaciones\n\n"
        "¿Sobre qué trámite querés consultar?"
    ),
    "DESPEDIDA": "¡Hasta luego! 👋 Fue un gusto ayudarte. ¡Éxitos en tus trámites! 🎓",
    "AGRADECIMIENTO": "¡Con gusto! 😊 Si tenés más consultas sobre trámites, estoy aquí para ayudarte.",
    "FALLBACK": (
        "No entendí del todo tu consulta 😅\n\n"
        "Podés preguntarme sobre:\n"
        "• **Matrícula** — nueva o regular\n"
        "• **Diploma Académico** o **Título en Provisión Nacional**\n"
        "• **Cambio de carrera** o **carrera simultánea**\n"
        "• **Titulación** (proceso de graduación)\n"
        "• **Kardex** / certificado académico\n"
        "• **Sistema web** (SUNIVER / universitarios.usfx.bo)\n"
        "• **Programación académica** de materias\n"
        "• **Seguro Social** universitario\n"
        "• **Becas**, **carnet**, **reprogramaciones**, **homologaciones**\n\n"
        "¿Podrías reformular tu pregunta o elegir uno de los temas de arriba?"
    ),
}

NON_TRAMITE_INTENTS = set(NON_TRAMITE_RESPONSES.keys())
CONFIDENCE_THRESHOLD = 0.15


# ---------------------------------------------------------------------------
# Dynamic response builder — uses live DB data, no hardcoded text
# ---------------------------------------------------------------------------

def _build_aspect_response(intent: str, aspect: str, tramite_data: dict, confidence: float) -> dict:
    """Build a rich Markdown response from DB data focused on the detected aspect."""
    name = tramite_data.get("name", intent)
    tramite_id = tramite_data.get("id")
    parts = []

    # Medium confidence: add a clarification note so the user knows what we understood
    if confidence < 0.55:
        parts.append(f"*Entendí que preguntás sobre **{name}***\n")

    if aspect == "COSTO":
        cost = float(tramite_data.get("cost") or 0)
        cost_details = tramite_data.get("cost_details")
        if cost == 0:
            parts.append(f"💰 **{name}** es completamente **gratuito**, no requiere pago.")
        else:
            parts.append(f"💰 El costo del **{name}** es **Bs. {cost:.2f}**.")
        if cost_details:
            parts.append(f"\n{cost_details}")

    elif aspect == "PLAZO":
        duration = tramite_data.get("duration_days")
        duration_details = tramite_data.get("duration_details")
        if duration:
            parts.append(f"⏱ El **{name}** tarda aproximadamente **{duration} días hábiles**.")
        if duration_details:
            parts.append(f"\n{duration_details}")
        if not duration and not duration_details:
            parts.append(
                f"⏱ No tengo el plazo exacto registrado para **{name}**. "
                "Te recomiendo consultar directamente con tu kardista."
            )

    elif aspect == "UBICACION":
        office = tramite_data.get("office_location")
        if office:
            parts.append(f"📍 **¿Dónde realizar el {name}?**\n\n{office}")
        else:
            parts.append(
                f"📍 Debés presentarte al **kardista de tu carrera** en la Facultad de Tecnología USFX.\n\n"
                "Podés ver el contacto y ubicación en la sección **Kardistas** de la plataforma."
            )

    elif aspect == "CONTACTO":
        contact = tramite_data.get("contact_info")
        if contact:
            parts.append(f"📞 **Contacto para {name}:**\n\n{contact}")
        else:
            parts.append(
                f"📞 Para este trámite, contactá al **kardista de tu carrera**. "
                "Podés ver el teléfono y horario en la sección **Kardistas** de esta plataforma."
            )

    elif aspect == "SISTEMA_WEB":
        url = tramite_data.get("web_system_url")
        instructions = tramite_data.get("web_instructions")
        if url or instructions:
            if url:
                parts.append(f"🌐 **Sistema web:** {url}\n")
            if instructions:
                parts.append(f"**Instrucciones paso a paso:**\n\n{instructions}")
        else:
            parts.append(
                f"🌐 El **{name}** no se gestiona en línea. "
                "Debés presentarte personalmente con la documentación requerida."
            )

    elif aspect == "REQUISITOS":
        reqs = sorted(tramite_data.get("requirements", []), key=lambda r: r.get("step_number", 0))
        mandatory = [r for r in reqs if r.get("is_mandatory", True)]
        optional_reqs = [r for r in reqs if not r.get("is_mandatory", True)]
        if mandatory:
            parts.append(f"📋 **Documentos necesarios — {name}:**\n")
            for r in mandatory:
                line = f"• **{r['title']}**"
                if r.get("description") and r["description"] != r["title"]:
                    line += f" — {r['description']}"
                if r.get("document_name"):
                    line += f" `[{r['document_name']}]`"
                if r.get("notes"):
                    line += f"\n  ⚠️ *{r['notes']}*"
                parts.append(line)
        if optional_reqs:
            parts.append(f"\n📎 **Opcionales:**")
            for r in optional_reqs:
                parts.append(f"• {r['title']}")
        if not reqs:
            parts.append(
                f"📋 No tengo los requisitos específicos registrados para **{name}**. "
                "Consultá con tu kardista."
            )

    elif aspect == "PASOS":
        reqs = sorted(tramite_data.get("requirements", []), key=lambda r: r.get("step_number", 0))
        web = tramite_data.get("web_instructions")
        if reqs:
            parts.append(f"📝 **Proceso paso a paso — {name}:**\n")
            for r in reqs:
                step = f"**{r.get('step_number', '')}. {r['title']}**"
                if r.get("description") and r["description"] != r["title"]:
                    step += f"\n   {r['description']}"
                if r.get("notes"):
                    step += f"\n   ⚠️ *{r['notes']}*"
                parts.append(step)
        if web and not reqs:
            parts.append(f"🌐 **En el sistema web:**\n\n{web}")
        if not reqs and not web:
            parts.append(
                f"📝 No tengo los pasos específicos registrados para **{name}**. "
                "Consultá con tu kardista."
            )

    else:  # GENERAL
        desc = tramite_data.get("description", "")
        cost = float(tramite_data.get("cost") or 0)
        duration = tramite_data.get("duration_days")
        reqs = tramite_data.get("requirements", [])

        parts.append(f"ℹ️ **{name}**\n")
        if desc:
            parts.append(f"{desc}\n")

        stat_parts = []
        if duration:
            stat_parts.append(f"⏱ {duration} días hábiles")
        stat_parts.append(f"💰 {'Gratuito' if cost == 0 else f'Bs. {cost:.2f}'}")
        parts.append(" · ".join(stat_parts))

        if reqs:
            parts.append(
                f"\n💬 Podés preguntarme por los **requisitos**, el **costo**, "
                "el **proceso paso a paso**, el **plazo** o **dónde** realizarlo."
            )

    response = "\n\n".join(p for p in parts if p)
    return {
        "response": response,
        "classified_intent": intent,
        "tramite_id": str(tramite_id) if tramite_id else None,
        "confidence": confidence,
        "step": 1,
        "show_tramite_card": True,
    }


def _fallback_response(intent: str, confidence: float) -> dict:
    return {
        "response": NON_TRAMITE_RESPONSES["FALLBACK"],
        "classified_intent": intent,
        "tramite_id": None,
        "confidence": confidence,
        "step": None,
        "show_tramite_card": False,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

async def process_chat(
    session_id: str,
    message: str,
    history: list,
    claude_enabled: bool = False,
) -> dict:
    """
    Main chatbot pipeline:
      1. BERT → classify intent
      2. Aspect classifier → detect what the user is asking about
      3a. Claude (if claude_enabled=True) → natural language response
      3b. Dynamic DB response (default) → rich structured Markdown
    """
    # --- Layer 1: Intent classification ---
    result = classifier_model.predict(message)
    intent = result["label"]
    confidence = result["confidence"]

    # Conversational intents → quick response, no DB needed
    if intent in NON_TRAMITE_INTENTS:
        if claude_enabled:
            claude_resp = await generate_response(
                intent=intent,
                aspect="GENERAL",
                user_message=message,
                history=history,
                tramite_data=None,
                tramite_template={"description": NON_TRAMITE_RESPONSES.get(intent, "")},
            )
            if claude_resp:
                return {
                    "response": claude_resp,
                    "classified_intent": intent,
                    "tramite_id": None,
                    "confidence": confidence,
                    "step": None,
                    "show_tramite_card": False,
                }
        return {
            "response": NON_TRAMITE_RESPONSES.get(intent, NON_TRAMITE_RESPONSES["FALLBACK"]),
            "classified_intent": intent,
            "tramite_id": None,
            "confidence": confidence,
            "step": None,
            "show_tramite_card": False,
        }

    # Low confidence → general fallback
    if confidence < CONFIDENCE_THRESHOLD:
        return _fallback_response(intent, confidence)

    # --- Fetch full tramite data from backend ---
    tramite_data = None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            list_resp = await client.get(f"{settings.backend_url}/api/v1/tramites")
            if list_resp.status_code == 200:
                summary = next(
                    (t for t in list_resp.json() if t.get("code") == intent), None
                )
                if summary:
                    detail_resp = await client.get(
                        f"{settings.backend_url}/api/v1/tramites/{summary['id']}"
                    )
                    if detail_resp.status_code == 200:
                        tramite_data = detail_resp.json()
                    else:
                        tramite_data = summary
    except Exception:
        pass

    if not tramite_data:
        return _fallback_response(intent, confidence)

    # --- Layer 2: Aspect classification ---
    aspect = classify_aspect(message)

    # --- Layer 3a: Claude (if enabled) ---
    if claude_enabled:
        claude_resp = await generate_response(
            intent=intent,
            aspect=aspect,
            user_message=message,
            history=history,
            tramite_data=tramite_data,
        )
        if claude_resp:
            tramite_id = tramite_data.get("id")
            return {
                "response": claude_resp,
                "classified_intent": intent,
                "tramite_id": str(tramite_id) if tramite_id else None,
                "confidence": confidence,
                "step": 1,
                "show_tramite_card": True,
            }

    # --- Layer 3b: Dynamic DB response ---
    return _build_aspect_response(intent, aspect, tramite_data, confidence)
