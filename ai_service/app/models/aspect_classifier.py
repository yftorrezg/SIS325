"""
Aspect classifier: given a user message already classified to a tramite,
detects WHAT aspect the user is asking about.
Uses keyword matching — fast and no extra model needed.
"""

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

_ASPECT_KEYWORDS: dict[str, list[str]] = {
    "COSTO": [
        "cuánto cuesta", "cuanto cuesta", "precio", "costo", "cuánto vale",
        "cuanto vale", "cuánto se paga", "cuanto se paga", "cuánto es",
        "cuanto es", "valores universitarios", "cuánto cobran", "cuanto cobran",
        "importe", "monto", "cuánto hay que pagar", "bs.", "bolivianos",
    ],
    "PLAZO": [
        "cuánto tarda", "cuanto tarda", "días hábiles", "dias habiles",
        "cuánto tiempo", "cuanto tiempo", "tiempo", "tarda", "demora",
        "cuándo me dan", "cuando me dan", "cuándo sale", "cuando sale",
        "plazo", "días", "dias", "semanas", "meses",
    ],
    "REQUISITOS": [
        "requisitos", "documentos", "papeles", "qué necesito", "que necesito",
        "qué debo", "que debo", "qué hay que llevar", "que hay que llevar",
        "qué se presenta", "que se presenta", "lista de", "fotos", "fotocopia",
        "legalizado", "original", "certificado", "solvencia", "kardex",
        "diploma de bachiller", "carnet", "folder", "funda", "papel valorado",
    ],
    "PASOS": [
        "pasos", "proceso", "cómo se hace", "como se hace", "paso a paso",
        "cómo tramito", "como tramito", "procedimiento", "cómo lo hago",
        "como lo hago", "qué sigue", "que sigue", "siguiente paso",
        "cómo procedo", "como procedo", "instrucciones",
    ],
    "UBICACION": [
        "dónde", "donde", "en qué oficina", "en que oficina", "en qué lugar",
        "en que lugar", "dónde presento", "donde presento", "dónde lo entrego",
        "donde lo entrego", "dónde queda", "donde queda", "ubicación",
        "ubicacion", "dirección", "direccion", "en caja", "secretaría",
        "facultad", "rectoría",
    ],
    "CONTACTO": [
        "contacto", "teléfono", "telefono", "con quién hablo", "con quien hablo",
        "a quién pregunto", "a quien pregunto", "kardista", "encargado",
        "encargada", "whatsapp", "correo", "email", "horario de atención",
        "horario de atencion",
    ],
    "SISTEMA_WEB": [
        "sistema", "suniver", "universitarios.usfx", "si2.usfx", "web",
        "online", "en línea", "en linea", "página", "pagina", "portal",
        "cómo en el sistema", "como en el sistema", "formulario", "genero",
        "generar", "número de depósito", "numero de deposito", "qr",
    ],
}


def classify_aspect(text: str) -> str:
    """Return the detected aspect label for the user message."""
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for aspect, keywords in _ASPECT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[aspect] = score
    if not scores:
        return "GENERAL"
    return max(scores, key=scores.get)
