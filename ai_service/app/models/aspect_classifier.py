"""
Aspect classifier: given a user message already classified to a tramite,
detects WHAT aspect the user is asking about.

Two modes:
- Keyword (default, fast, no extra memory): simple but effective for this domain.
- Zero-Shot NLI (optional): uses mDeBERTa for semantic understanding.
  Activated by setting USE_ZERO_SHOT_CLASSIFIER=true in the environment.
  The model (~300MB) is downloaded on first use and cached by Hugging Face.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

ASPECTS = [
    "REQUISITOS",
    "PASOS",
    "COSTO",
    "PLAZO",
    "UBICACION",
    "CONTACTO",
    "SISTEMA_WEB",
    "GENERAL",
    
]

# ---------------------------------------------------------------------------
# Keyword-based classifier (fast, always available)
# ---------------------------------------------------------------------------
_ASPECT_KEYWORDS: dict[str, list[str]] = {
    "COSTO": [
        "cuánto cuesta", "cuanto cuesta", "precio", "costo", "cuánto vale",
        "cuanto vale", "cuánto se paga", "cuanto se paga", "cuánto es",
        "cuanto es", "valores universitarios", "cuánto cobran", "cuanto cobran",
        "importe", "monto", "cuánto hay que pagar", "cuanto hay que pagar",
        "bs.", "bolivianos", "arancel", "gratuito", "gratis", "cuánto sale",
        "cuanto sale", "tiene costo", "hay que pagar", "pago",
    ],
    "PLAZO": [
        "cuánto tarda", "cuanto tarda", "días hábiles", "dias habiles",
        "cuánto tiempo", "cuanto tiempo", "tiempo", "tarda", "demora",
        "cuándo me dan", "cuando me dan", "cuándo sale", "cuando sale",
        "plazo", "días", "dias", "semanas", "meses", "cuánto demora",
        "cuanto demora", "rápido", "rapido", "urgente", "cuándo está listo",
        "cuando esta listo",
    ],
    "REQUISITOS": [
        "requisitos", "documentos", "papeles", "qué necesito", "que necesito",
        "qué debo", "que debo", "qué hay que llevar", "que hay que llevar",
        "qué se presenta", "que se presenta", "lista de", "fotos", "fotocopia",
        "legalizado", "original", "certificado", "solvencia", "kardex",
        "diploma de bachiller", "carnet", "folder", "funda", "papel valorado",
        "qué documentos", "que documentos", "necesito llevar", "qué traigo",
        "que traigo", "qué presento", "que presento",
    ],
    "PASOS": [
        "pasos", "proceso", "cómo se hace", "como se hace", "paso a paso",
        "cómo tramito", "como tramito", "procedimiento", "cómo lo hago",
        "como lo hago", "qué sigue", "que sigue", "siguiente paso",
        "cómo procedo", "como procedo", "instrucciones", "cómo hago",
        "como hago", "por dónde empiezo", "por donde empiezo",
        "cómo inicio", "como inicio",
    ],
    "UBICACION": [
        "dónde", "donde", "en qué oficina", "en que oficina", "en qué lugar",
        "en que lugar", "dónde presento", "donde presento", "dónde lo entrego",
        "donde lo entrego", "dónde queda", "donde queda", "ubicación",
        "ubicacion", "dirección", "direccion", "en caja", "secretaría",
        "secretaria", "facultad", "rectoría", "rectoria", "pabellón",
        "pabellon", "oficina", "a dónde voy", "a donde voy",
    ],
    "CONTACTO": [
        "contacto", "teléfono", "telefono", "con quién hablo", "con quien hablo",
        "a quién pregunto", "a quien pregunto", "kardista", "encargado",
        "encargada", "whatsapp", "correo", "email", "horario de atención",
        "horario de atencion", "horario", "a quién llamo", "a quien llamo",
        "número de teléfono", "numero de telefono", "quién atiende",
        "quien atiende",
    ],
    "SISTEMA_WEB": [
        "sistema", "suniver", "universitarios.usfx", "si2.usfx", "web",
        "online", "en línea", "en linea", "página", "pagina", "portal",
        "cómo en el sistema", "como en el sistema", "formulario", "genero",
        "generar", "número de depósito", "numero de deposito", "qr",
        "código qr", "codigo qr", "pago qr", "en internet", "plataforma",
        "admision.usfx",
    ],
}

_LABEL_MAP = {
    "requisitos y documentos": "REQUISITOS",
    "pasos y proceso": "PASOS",
    "costo o precio": "COSTO",
    "tiempo y plazo": "PLAZO",
    "ubicación de oficina": "UBICACION",
    "contacto o responsable": "CONTACTO",
    "sistema web o plataforma": "SISTEMA_WEB",
    "información general": "GENERAL",
}

_ZS_LABELS = list(_LABEL_MAP.keys())


def _keyword_classify(text: str) -> str:
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for aspect, keywords in _ASPECT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[aspect] = score
    if not scores:
        return "GENERAL"
    return max(scores, key=scores.get)


# ---------------------------------------------------------------------------
# Zero-Shot classifier (lazy-loaded, optional)
# ---------------------------------------------------------------------------
_zs_pipeline = None
_zs_attempted = False  # avoid retrying if import failed


def _get_zs_pipeline():
    global _zs_pipeline, _zs_attempted
    if _zs_attempted:
        return _zs_pipeline
    _zs_attempted = True
    try:
        from transformers import pipeline as hf_pipeline
        logger.info("Loading Zero-Shot aspect classifier (mDeBERTa)…")
        _zs_pipeline = hf_pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
        )
        logger.info("Zero-Shot classifier ready.")
    except Exception as e:
        logger.warning(f"Could not load Zero-Shot classifier, falling back to keywords: {e}")
        _zs_pipeline = None
    return _zs_pipeline


def _zero_shot_classify(text: str) -> str:
    pipe = _get_zs_pipeline()
    if pipe is None:
        return _keyword_classify(text)
    try:
        result = pipe(text, _ZS_LABELS, multi_label=False)
        top_label: str = result["labels"][0]
        top_score: float = result["scores"][0]
        if top_score < 0.35:
            return "GENERAL"
        return _LABEL_MAP.get(top_label, "GENERAL")
    except Exception as e:
        logger.warning(f"Zero-Shot inference failed, using keywords: {e}")
        return _keyword_classify(text)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
_use_zero_shot: Optional[bool] = None


def _should_use_zero_shot() -> bool:
    global _use_zero_shot
    if _use_zero_shot is None:
        _use_zero_shot = os.getenv("USE_ZERO_SHOT_CLASSIFIER", "false").lower() == "true"
    return _use_zero_shot


def classify_aspect(text: str) -> str:
    """Return the detected aspect label for the user message."""
    if len(text.strip()) < 4:
        return "GENERAL"
    if _should_use_zero_shot():
        return _zero_shot_classify(text)
    return _keyword_classify(text)
