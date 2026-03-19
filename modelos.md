# Documentación: Base de Datos y Modelos de IA
**Proyecto: Asistente Virtual USFX – Facultad de Tecnología**

---

## 1. BASE DE DATOS POSTGRESQL

### Resumen actual
| Tabla | Registros | Notas |
|---|---|---|
| `tramites` | 16 total / **8 activos** | 8 desactivados son categorías pendientes |
| `requirements` | 53 | Requisitos/pasos de los tramites activos |
| `tramite_aspects` | 0 | Nueva tabla, pendiente de llenar |
| `training_samples` | **687** | Frases verificadas para entrenar la IA |
| `model_versions` | 6 total / 1 activo | Versiones del modelo BERT entrenadas |
| `users` | 3 | admin + 2 kardistas |
| `careers` | 11 | Carreras de tecnología |
| `kardistas` | 2 | Kardista tecnológico + 6x |
| `conversations` | 0 | Se llena cuando usuarios chatean |
| `conversation_messages` | 0 | Mensajes individuales del chat |
| `student_requests` | 0 | Solicitudes de trámites enviadas |
| `notifications` | 0 | Notificaciones a estudiantes |

---

## 2. DIAGRAMA DE TABLAS Y RELACIONES

```
┌──────────────────────────────────────────────────────────────────┐
│                         USUARIOS Y ROLES                          │
├──────────────────┐                                               │
│     users        │                                               │
│──────────────────│                                               │
│ id (PK)          │                                               │
│ email (UNIQUE)   │──────────────────────────────────────────┐   │
│ hashed_password  │                                          │   │
│ full_name        │──────────────┐                           │   │
│ role             │              │                           │   │
│  admin           │         ┌───▼──────────┐                │   │
│  kardista        │         │  kardistas   │                │   │
│  student         │         │──────────────│                │   │
│ is_active        │         │ id (PK)      │                │   │
│ created_at       │         │ user_id (FK) │                │   │
│ updated_at       │         │ kardex_type  │◄───────────────┼─┐ │
└──────────────────┘         │  tecnologico │                │ │ │
         │                   │  6x          │                │ │ │
         │                   │ office_loc   │                │ │ │
         │                   │ phone        │                │ │ │
         │                   │ whatsapp     │                │ │ │
         │                   │ email_contact│                │ │ │
         │                   │ schedule     │                │ │ │
         │                   │  (JSONB)     │                │ │ │
         │                   └──────────────┘                │ │ │
         │                                                   │ │ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        TRÁMITES                                   │
├──────────────────┐                                               │
│    tramites      │                                               │
│──────────────────│                                               │
│ id (PK)          │──────────────────────────────┐               │
│ code (UNIQUE)    │              ┌────────────────┘               │
│  TRAMITE_MAT...  │         ┌───▼──────────────┐                 │
│ name             │         │   requirements   │                 │
│ description      │         │──────────────────│                 │
│ category         │         │ id (PK)          │                 │
│  matricula       │         │ tramite_id (FK)  │                 │
│  titulacion      │         │ step_number      │                 │
│  academico       │         │ title            │                 │
│  bienestar       │         │ description      │                 │
│ duration_days    │         │ document_name    │                 │
│ cost             │         │ is_mandatory     │                 │
│ is_active        │         │ notes            │                 │
│ applies_to       │         └──────────────────┘                 │
│  todos           │                                               │
│  tecnologico     │──────────────────────────────┐               │
│  6x              │              ┌────────────────┘               │
│ order_index      │         ┌───▼──────────────┐                 │
│ icon             │         │ tramite_aspects  │ ← NUEVA TABLA   │
└──────────────────┘         │──────────────────│                 │
         │                   │ id (PK)          │                 │
         │                   │ tramite_id (FK)  │                 │
         │                   │ key              │                 │
         │                   │  costo           │                 │
         │                   │  fecha_inicio    │                 │
         │                   │  paso_1          │                 │
         │                   │  cuenta_bancaria │                 │
         │                   │ label            │                 │
         │                   │ value            │                 │
         │                   │ value_type       │                 │
         │                   │  text            │                 │
         │                   │  markdown        │                 │
         │                   │  date            │                 │
         │                   │  number          │                 │
         │                   │  url             │                 │
         │                   │ order_index      │                 │
         │                   └──────────────────┘                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     SOLICITUDES DE TRÁMITES                       │
│                                                                   │
│  users ──────────────► student_requests ◄──── tramites           │
│  (student_id)          │                      (tramite_id)        │
│                        │ id (PK)                                  │
│  users ──────────────► │ student_id (FK)                         │
│  (kardista user)       │ tramite_id (FK)                         │
│                        │ career_id (FK) ◄──── careers             │
│  kardistas ──────────► │ assigned_kardista_id (FK)               │
│                        │ status                                   │
│                        │  pendiente                               │
│                        │  en_proceso                              │
│                        │  completado                              │
│                        │  rechazado                               │
│                        │  cancelado                               │
│                        │ student_data (JSONB)                     │
│                        │ notes                                    │
│                        │ admin_notes                              │
│                        │ submitted_at                             │
│                        │ completed_at                             │
│                        └──────────────────────┐                  │
│                                               │                  │
│                   ┌───────────────────────────┘                  │
│              ┌────▼─────────────────────────┐                    │
│              │  request_status_history      │                    │
│              │──────────────────────────────│                    │
│              │ id                           │                    │
│              │ request_id (FK)              │                    │
│              │ previous_status              │                    │
│              │ new_status                   │                    │
│              │ changed_by_id (FK → users)   │                    │
│              │ notes                        │                    │
│              │ changed_at                   │                    │
│              └──────────────────────────────┘                    │
│                                                                   │
│  student_requests ──────────────────────────► notifications      │
│                                               │ id               │
│                                               │ user_id (FK)     │
│                                               │ request_id (FK)  │
│                                               │ type             │
│                                               │ title            │
│                                               │ message          │
│                                               │ is_read          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    CONVERSACIONES DEL CHATBOT                     │
│                                                                   │
│  users ──────────────► conversations ──────► tramites            │
│  (user_id, opcional)   │ id (PK)             (resolved_tramite)  │
│                        │ session_id          ← qué trámite       │
│                        │ user_id (FK)          resolvió la conv.  │
│                        │ started_at                              │
│                        │ ended_at                                 │
│                        │ resolved                                 │
│                        └──────────────────────┐                  │
│                                               │                  │
│                              ┌────────────────┘                  │
│                         ┌────▼─────────────────────────────┐    │
│                         │  conversation_messages           │    │
│                         │──────────────────────────────────│    │
│                         │ id (PK)                          │    │
│                         │ conversation_id (FK)             │    │
│                         │ role: user | assistant           │    │
│                         │ content (texto del mensaje)      │    │
│                         │ input_type: text | audio         │    │
│                         │ audio_file_path                  │    │
│                         │ classified_intent  ← LA IA pone │    │
│                         │   TRAMITE_DIPLOMA_ACADEMICO      │    │
│                         │ confidence_score   ← 0.0 – 1.0  │    │
│                         └────────────────────┬─────────────┘    │
│                                              │ (opcional)        │
│                              ┌───────────────┘                   │
│                         ┌────▼───────────────────────────┐      │
│                         │  training_samples              │      │
│                         │────────────────────────────────│      │
│                         │ id                             │      │
│                         │ text        ← frase            │      │
│                         │ label       ← etiqueta BERT    │      │
│                         │ source                         │      │
│                         │  jsonl_import                  │      │
│                         │  admin                         │      │
│                         │  conversation (auto-capturado) │      │
│                         │ verified    ← bool             │      │
│                         │ verified_by_id (FK → users)    │      │
│                         │ conversation_message_id (FK)   │      │
│                         └────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    VERSIONES DEL MODELO IA                        │
│                                                                   │
│            model_versions                                         │
│            ───────────────────────────────────                    │
│            id (PK)                                                │
│            version_tag     ← "v1.0.0", "v1.1.0"                  │
│            model_path      ← ruta en disco /app/data/models/...  │
│            training_samples_count                                 │
│            val_samples_count                                      │
│            accuracy        ← ej. 0.9234 (92.3%)                  │
│            f1_score        ← ej. 0.9187                          │
│            confusion_matrix (JSONB)                               │
│            classification_report (JSONB)                          │
│            base_model      ← "dccuchile/bert-base-spanish..."     │
│            hyperparams (JSONB)                                    │
│              { epochs: 3, batch_size: 16, lr: 2e-5, ... }        │
│            is_active       ← solo uno activo a la vez            │
│            trained_at                                             │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               CARRERAS Y KARDISTAS                       │
│                                                          │
│  careers                    kardistas                    │
│  ─────────────────          ─────────────────────────   │
│  id (PK)                    id (PK)                      │
│  name                       user_id (FK → users)         │
│  code                       kardex_type                  │
│  kardex_type  ──────────────  tecnologico                │
│   tecnologico              │  6x                         │
│   6x          ◄────────────┘ office_location             │
│  is_active                  phone / whatsapp             │
│                             email_contact                │
│  career.kardex_type         schedule (JSONB)             │
│  determina qué kardista     ─────────────────────────   │
│  procesa la solicitud       Kardista tecnológico:        │
│                              maneja las 5 carreras       │
│                              con kardex tecnológico      │
│                             Kardista 6x:                 │
│                              maneja las 6 carreras       │
│                              con kardex 6x               │
└─────────────────────────────────────────────────────────┘
```

---

## 3. LOS 8 TRÁMITES ACTIVOS EN LA BD

| # | Código | Nombre | Categoría | Costo |
|---|--------|--------|-----------|-------|
| 1 | `TRAMITE_MATRICULA_ALUMNO_NUEVO` | Inscripción y Matriculación para Estudiantes Nuevos | matricula | Bs. 0 |
| 2 | `TRAMITE_MATRICULA_ALUMNO_REGULAR` | Renovación de Matrícula para Estudiantes Regulares | matricula | Bs. 0 |
| 3 | `PROCESO_MATRICULACION_WEB` | Matriculación en el Sistema Web (SUNIVER) | matricula | Bs. 0 |
| 4 | `PROCESO_PROGRAMACION_ACADEMICA` | Programación Académica de Materias | academico | Bs. 0 |
| 5 | `TRAMITE_DIPLOMA_ACADEMICO` | Diploma Académico | titulacion | Bs. 0 |
| 6 | `TRAMITE_TITULO_PROVISION_NACIONAL` | Título en Provisión Nacional | titulacion | Bs. 0 |
| 7 | `TRAMITE_SIMULTANEO_DIPLOMA_PROVISION` | Trámite Simultáneo: Diploma + Título | titulacion | Bs. 0 |
| 8 | `SEGURO_SOCIAL_UNIVERSITARIO` | Seguro Social Universitario Estudiantil | bienestar | Bs. 0 |

> **Nota:** Los costos reales (Bs. 150 diploma, etc.) deben cargarse desde el admin panel o actualizar la BD directamente.

---

## 4. MODELOS DE INTELIGENCIA ARTIFICIAL

El sistema tiene **3 capas de IA** que trabajan en secuencia cuando un estudiante escribe en el chatbot.

---

### CAPA 1 — Clasificador de Tramite (BERT)

**¿Qué hace?**
Identifica de qué trámite está hablando el estudiante.

**¿Cómo funciona?**
```
Estudiante escribe: "quiero saber los documentos para el diploma"
           │
           ▼
    BERT lee la frase completa
    (modelo dccuchile/bert-base-spanish-wwm-cased)
           │
           ▼
    Asigna probabilidades a cada etiqueta:
    TRAMITE_DIPLOMA_ACADEMICO     → 0.87  ← ganador
    TRAMITE_MATRICULA_ALUMNO_NUEVO → 0.04
    FALLBACK                       → 0.02
    ...
           │
           ▼
    Resultado: { label: "TRAMITE_DIPLOMA_ACADEMICO", confidence: 0.87 }
```

**Las 12 etiquetas que clasifica:**
| Etiqueta | Qué detecta |
|---|---|
| `TRAMITE_MATRICULA_ALUMNO_NUEVO` | Preguntas de ingreso por primera vez |
| `TRAMITE_MATRICULA_ALUMNO_REGULAR` | Renovación de matrícula semestral |
| `TRAMITE_DIPLOMA_ACADEMICO` | Tramitación del diploma |
| `TRAMITE_TITULO_PROVISION_NACIONAL` | Tramitación del título profesional |
| `TRAMITE_SIMULTANEO_DIPLOMA_PROVISION` | Tramitar diploma y título juntos |
| `PROCESO_MATRICULACION_WEB` | Uso del sistema web SUNIVER |
| `PROCESO_PROGRAMACION_ACADEMICA` | Inscripción de materias |
| `SEGURO_SOCIAL_UNIVERSITARIO` | SSU, ficha médica, especialidades |
| `SALUDO_BIENVENIDA` | "hola", "buenos días", etc. |
| `DESPEDIDA` | "adiós", "chau", "hasta luego" |
| `AGRADECIMIENTO` | "gracias", "muy útil", etc. |
| `FALLBACK` | Cualquier cosa fuera de contexto |

**¿De dónde aprende?**
De la tabla `training_samples` (687 frases verificadas).
Cada fila es una frase + su etiqueta correcta:
```
text: "cuánto cuesta el diploma académico"  label: "TRAMITE_DIPLOMA_ACADEMICO"
text: "hola buenos días"                    label: "SALUDO_BIENVENIDA"
text: "quiero programarme en materias"      label: "PROCESO_PROGRAMACION_ACADEMICA"
```

**¿Dónde se guarda el modelo?**
```
Docker volume: ai_models
Ruta dentro del contenedor: /app/data/models/classifier/
  ├── v1.0.0/          ← versión entrenada 1
  ├── v1.1.0/          ← versión entrenada 2
  └── active/          ← copia de la versión activa (se carga al iniciar)
```

**¿Qué pasa si no hay modelo entrenado?**
Cae al **keyword fallback**: busca palabras clave en el texto del estudiante.
```
texto contiene "diploma"       → TRAMITE_DIPLOMA_ACADEMICO (confianza 0.5)
texto contiene "hola"          → SALUDO_BIENVENIDA
texto sin coincidencias        → FALLBACK
```

**Umbral de confianza:** `0.15`
Si la confianza es menor a 0.15, se responde con el mensaje de fallback genérico.

---

### CAPA 2 — Clasificador de Aspecto (Keywords)

**¿Qué hace?**
Una vez que sabe el trámite, detecta **qué aspecto específico** está preguntando el estudiante.

**¿Cómo funciona?**
```
Intent detectado: TRAMITE_DIPLOMA_ACADEMICO
Frase: "cuánto cuesta el diploma"
           │
           ▼
    Busca palabras clave por aspecto:
    COSTO: ["cuánto cuesta", "precio", "costo", "cuánto se paga", ...]  → 2 hits ← ganador
    PASOS: ["pasos", "proceso", "cómo se hace", ...]  → 0 hits
    REQUISITOS: ["requisitos", "documentos", ...]  → 0 hits
           │
           ▼
    Resultado: aspecto = "COSTO"
```

**Los 8 aspectos detectables:**
| Aspecto | Ejemplos de frases que lo activan |
|---|---|
| `COSTO` | "cuánto cuesta", "precio", "importe", "cuánto se paga" |
| `REQUISITOS` | "documentos", "requisitos", "papeles", "qué necesito" |
| `PASOS` | "cómo se hace", "paso a paso", "proceso", "instrucciones" |
| `PLAZO` | "cuánto tarda", "días hábiles", "tiempo", "cuándo sale" |
| `UBICACION` | "dónde", "en qué oficina", "dónde presento" |
| `CONTACTO` | "con quién hablo", "teléfono", "kardista", "encargado" |
| `SISTEMA_WEB` | "suniver", "universitarios.usfx", "si2.usfx", "portal" |
| `GENERAL` | (default) cuando no encaja en ninguno |

**Archivo de configuración:** `ai_service/app/models/aspect_classifier.py`

---

### CAPA 3 — Claude Haiku (Respuesta Natural)

**¿Qué hace?**
Genera la respuesta final al estudiante usando el contexto completo.

**Cómo se construye el contexto que recibe Claude:**
```
Sistema: "Eres el asistente virtual de la Facultad de Tecnología USFX..."
         "Trámite identificado: Diploma Académico"
         "Aspecto detectado: costo del trámite"
         "Datos oficiales del trámite (BD):"
         "  - Nombre: Diploma Académico"
         "  - Costo: Bs. 150"
         "  - Duración: 15 días hábiles"
         "  - Requisito 1: Fotocopia CI..."
         "  - Requisito 2: Carnet universitario..."
         "  - ..."
         "Historial últimos 8 mensajes: [...]"

Usuario: "cuánto cuesta el diploma académico?"

Claude: "El Diploma Académico tiene un costo de Bs. 150 aprox.
         Podés hacer el pago en Caja de la facultad después
         de generar el formulario en universitarios.usfx.bo.
         ¿Querés saber también qué documentos necesitás llevar?"
```

**Estado actual:** INACTIVO por defecto.
Se activa desde el panel admin → Evaluación del Modelo → botón "Activar Claude".
La key se guarda en memoria del servicio (se pierde al reiniciar).

**Fallback si Claude no está activo:** Se usa el template estático de `chatbot.py`.

---

## 5. FLUJO COMPLETO DEL CHATBOT

```
ESTUDIANTE escribe: "qué documentos necesito para el diploma"
         │
         ▼
[FRONTEND React]
  ChatWidget.jsx
  POST /api/v1/ai/chat → Backend (puerto 8000)
         │
         ▼
[BACKEND FastAPI]
  ai_proxy.py → reenvía a AI Service
  POST http://ai_service:8001/chat
         │
         ▼
[AI SERVICE FastAPI] — chatbot.py::process_chat()
         │
         ├─ CAPA 1: classifier_model.predict(mensaje)
         │    ↳ BERT o keyword fallback
         │    ↳ resultado: { label: "TRAMITE_DIPLOMA_ACADEMICO", confidence: 0.87 }
         │
         ├─ Consulta BD: GET /api/v1/tramites?is_active=true
         │    ↳ busca el tramite con code == "TRAMITE_DIPLOMA_ACADEMICO"
         │    ↳ obtiene: nombre, costo, duración, requirements[]
         │
         ├─ CAPA 2: classify_aspect(mensaje)
         │    ↳ keywords → resultado: "REQUISITOS"
         │
         ├─ CAPA 3: generate_response(intent, aspect, mensaje, historial, tramite_data)
         │    ↳ Si Claude activo: llama API Anthropic → respuesta natural
         │    ↳ Si Claude inactivo: usa template estático de TRAMITE_TEMPLATES
         │
         ▼
[RESPUESTA al frontend]
{
  "response": "Para el Diploma Académico necesitás: ...",
  "classified_intent": "TRAMITE_DIPLOMA_ACADEMICO",
  "tramite_id": "uuid-del-tramite",
  "confidence": 0.87,
  "show_tramite_card": true
}
         │
         ▼
[FRONTEND] muestra la respuesta + tarjeta del trámite
```

---

## 6. CÓMO SE ENTRENA EL MODELO BERT (Capa 1)

```
ADMIN va a /admin/modelo → "Iniciar Entrenamiento"
         │
         ▼
[BACKEND] POST /api/v1/model-versions (crea registro)
         │
         ▼
[AI SERVICE] training_api.py — inicia job en background
         │
         ├─ fetch_training_data()
         │    ↳ GET /api/v1/training/samples?verified=true
         │    ↳ Obtiene 687 frases de la tabla training_samples
         │    ↳ fallback: lee tramites_dataset.jsonl si la API falla
         │
         ├─ train_test_split(85% train / 15% val)
         │    ↳ ~584 frases para entrenar
         │    ↳ ~103 frases para validar
         │
         ├─ Tokeniza con AutoTokenizer(base_model)
         │
         ├─ Fine-tuning con Hugging Face Trainer
         │    ↳ parámetros configurables: epochs, batch_size, lr, dropout...
         │    ↳ guarda checkpoint por época
         │    ↳ carga el mejor modelo al final
         │
         ├─ Evaluación: accuracy, F1-score, confusion matrix
         │
         ├─ Guarda modelo en disco:
         │    /app/data/models/classifier/<version_tag>/
         │    + copia a /app/data/models/classifier/active/
         │
         ├─ Hot-swap: reemplaza el modelo en memoria sin reiniciar
         │
         └─ POST /api/v1/model-versions (guarda métricas en BD)

ADMIN ve en la tabla: accuracy 92.3%, F1 91.8%, etc.
ADMIN activa una versión anterior si la nueva es peor
```

---

## 7. LA TABLA `tramite_aspects` — PARA QUÉ SIRVE

Esta tabla nueva permite guardar **atributos dinámicos por trámite** de forma flexible.
Cada trámite tiene sus propios aspectos independientes.

**Ejemplo — TRAMITE_MATRICULA_ALUMNO_NUEVO:**
```
key             | label                  | value                          | value_type
─────────────────────────────────────────────────────────────────────────────────────
cuenta_bancaria | Cuenta Bancaria        | Banco Unión Cta. 1-33340493    | text
url_sistema     | Sistema Web            | https://universitarios.usfx.bo | url
fecha_inicio    | Fecha inicio inscr.    | 2025-02-01                     | date
fecha_limite    | Fecha límite inscr.    | 2025-02-28                     | date
paso_1          | Paso 1                 | Ingresar a admision.usfx.bo... | markdown
paso_2          | Paso 2                 | Servicios académicos genera... | markdown
```

**Ejemplo — PROCESO_PROGRAMACION_ACADEMICA (sin costo):**
```
key             | label                  | value                          | value_type
─────────────────────────────────────────────────────────────────────────────────────
fecha_inicio    | Inicio programaciones  | 2025-03-01                     | date
fecha_limite    | Límite programaciones  | 2025-03-15                     | date
tipo_programac  | Tipo de programación   | Automática / Manual            | text
url_sistema     | Sistema               | https://si2.usfx.bo/suniver    | url
```

La IA (Capa 3 Claude) puede usar estos aspectos dinámicos para responder preguntas específicas como "¿cuándo cierran las programaciones?" con la fecha real de la BD.

---

## 8. RESUMEN DE ARCHIVOS CLAVE

| Archivo | Qué hace |
|---|---|
| `ai_service/app/models/classifier.py` | Define las 12 etiquetas, el keyword fallback, carga/descarga el modelo BERT |
| `ai_service/app/models/aspect_classifier.py` | Detecta el aspecto preguntado por keywords |
| `ai_service/app/models/claude_client.py` | Gestiona la llamada a Claude API, construye el system prompt |
| `ai_service/app/models/chatbot.py` | Orquesta las 3 capas, contiene los templates estáticos de fallback |
| `ai_service/app/training/trainer.py` | Pipeline completo de fine-tuning BERT |
| `ai_service/app/data/training/tramites_dataset.jsonl` | 545 frases en formato JSONL (fuente local) |
| `backend/app/models/tramite.py` | Modelos SQLAlchemy: Tramite, Requirement |
| `backend/app/models/training_sample.py` | Modelo TrainingSample para la tabla de frases |
| `backend/app/models/model_version.py` | Registro de versiones entrenadas |
