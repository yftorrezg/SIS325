# Sistema de Trámites Universitarios — Facultad de Tecnología USFX

Plataforma web completa para la gestión de trámites universitarios con asistente de inteligencia artificial (BERT + Whisper + Claude). Permite a los estudiantes consultar requisitos, hacer seguimiento de sus solicitudes y obtener respuestas en tiempo real mediante texto o voz.

---

## Tabla de Contenidos

1. [Stack Tecnológico](#1-stack-tecnológico)
2. [Arquitectura General](#2-arquitectura-general)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Base de Datos (PostgreSQL)](#4-base-de-datos-postgresql)
5. [Backend — FastAPI](#5-backend--fastapi)
6. [AI Service — FastAPI + BERT + Whisper](#6-ai-service--fastapi--bert--whisper)
7. [Frontend — React 18](#7-frontend--react-18)
8. [Docker y Docker Compose](#8-docker-y-docker-compose)
9. [Variables de Entorno](#9-variables-de-entorno)
10. [Inicio Rápido](#10-inicio-rápido)
11. [Credenciales Demo](#11-credenciales-demo)
12. [Trámites y Carreras incluidos](#12-trámites-y-carreras-incluidos)
13. [Módulo de IA — Guía Completa](#13-módulo-de-ia--guía-completa)
14. [API Endpoints](#14-api-endpoints)
15. [Agregar un nuevo trámite](#15-agregar-un-nuevo-trámite)
16. [Hardware Recomendado](#16-hardware-recomendado)

---

## 1. Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Frontend | React + Vite + TailwindCSS | 18.3 / 5.4 / 3.4 |
| Backend | Python FastAPI + SQLAlchemy async | 0.115 / 2.0 |
| IA | BERT español (dccuchile) + Whisper (OpenAI) | transformers 4.45 |
| LLM opcional | Claude API (Anthropic) | anthropic 0.40 |
| Base de datos | PostgreSQL | 16 |
| Cache | Redis | 7 |
| Contenedores | Docker + Docker Compose | — |

---

## 2. Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                              │
│              (Estudiante / Kardista / Admin)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP (puerto 5173)
┌─────────────────────▼───────────────────────────────────────┐
│              FRONTEND — React 18 + Vite                      │
│  • Páginas: Home, Trámites, Solicitudes, Panel Admin         │
│  • ChatWidget flotante (texto + voz)                         │
│  • Autenticación JWT persistida en localStorage              │
└──────────────┬──────────────────────────────────────────────┘
               │ REST API (puerto 8000)
┌──────────────▼──────────────────────────────────────────────┐
│           BACKEND — FastAPI + SQLAlchemy async               │
│  • JWT Auth (roles: admin / kardista / student)              │
│  • CRUD trámites, solicitudes, usuarios, kardistas           │
│  • Proxy hacia AI Service                                    │
│  • Almacena conversaciones y muestras de entrenamiento       │
└──────┬───────────────────────────┬──────────────────────────┘
       │                           │
       │ asyncpg                   │ HTTP (puerto 8001)
┌──────▼──────┐        ┌──────────▼──────────────────────────┐
│ PostgreSQL  │        │    AI SERVICE — FastAPI              │
│    :5433    │        │  • Clasificador BERT (20 intents)    │
│  10 tablas  │        │  • Detector de aspecto               │
└─────────────┘        │  • Chatbot FSM 3 capas               │
                       │  • Whisper (voz → texto)             │
┌─────────────┐        │  • Claude API (respuestas enriquecid)│
│   Redis     │        └──────────────────────────────────────┘
│    :6379    │
│  (cache)    │
└─────────────┘
```

**Flujo del chatbot:**
1. Usuario escribe o graba audio
2. Si es audio → Whisper transcribe a texto
3. BERT clasifica la intención (¿qué trámite pregunta?)
4. Detector de aspecto identifica QUÉ quiere saber (costo, requisitos, pasos, etc.)
5. El backend busca el trámite en PostgreSQL
6. Se construye la respuesta (plantilla estructurada o Claude enriquecida)
7. Se devuelve la respuesta con tarjeta del trámite al frontend

---

## 3. Estructura del Proyecto

```
chatbot/
│
├── backend/                          ← API principal (puerto 8000)
│   ├── app/
│   │   ├── api/v1/                  ← Endpoints REST
│   │   │   ├── router.py            ← Router principal (agrupa todos)
│   │   │   ├── auth.py              ← Login / Register / Me
│   │   │   ├── tramites.py          ← CRUD trámites y requisitos
│   │   │   ├── requests.py          ← Solicitudes de estudiantes
│   │   │   ├── careers.py           ← Carreras universitarias
│   │   │   ├── kardistas.py         ← Información y horarios kardistas
│   │   │   ├── training.py          ← Muestras de entrenamiento
│   │   │   ├── admin.py             ← Estadísticas panel admin
│   │   │   ├── notifications.py     ← Notificaciones de usuario
│   │   │   ├── model_versions.py    ← Versiones del modelo IA
│   │   │   └── ai_proxy.py          ← Proxy hacia AI Service
│   │   ├── models/                  ← Modelos SQLAlchemy (tablas BD)
│   │   │   ├── user.py              ← Tabla users
│   │   │   ├── tramite.py           ← Tablas tramites + requirements
│   │   │   ├── student_request.py   ← Tablas student_requests + historial
│   │   │   ├── career.py            ← Tabla careers
│   │   │   ├── kardista.py          ← Tabla kardistas
│   │   │   ├── conversation.py      ← Tablas conversations + messages
│   │   │   ├── notification.py      ← Tabla notifications
│   │   │   ├── training_sample.py   ← Tabla training_samples
│   │   │   └── model_version.py     ← Tabla model_versions
│   │   ├── schemas/                 ← Schemas Pydantic v2 (validación)
│   │   │   ├── tramite.py
│   │   │   ├── student_request.py
│   │   │   ├── user.py
│   │   │   ├── kardista.py
│   │   │   └── ai.py
│   │   ├── core/
│   │   │   ├── security.py          ← JWT, bcrypt
│   │   │   └── permissions.py       ← Decoradores de roles
│   │   ├── main.py                  ← App FastAPI + CORS + startup
│   │   ├── config.py                ← Settings (env vars)
│   │   ├── database.py              ← Motor async SQLAlchemy
│   │   ├── seed.py                  ← Datos iniciales (trámites, users)
│   │   └── seed_training.py         ← Muestras de entrenamiento iniciales
│   ├── Dockerfile
│   └── requirements.txt
│
├── ai_service/                       ← Servicio IA (puerto 8001)
│   ├── app/
│   │   ├── api/
│   │   │   ├── classify.py          ← POST /classify
│   │   │   ├── transcribe.py        ← POST /transcribe
│   │   │   ├── chat.py              ← POST /chat
│   │   │   ├── training_api.py      ← POST /train, GET /train/{job_id}
│   │   │   └── metrics_api.py       ← GET /metrics/model-info
│   │   ├── models/
│   │   │   ├── classifier.py        ← Clasificador BERT (20 clases)
│   │   │   ├── aspect_classifier.py ← Detector de aspecto (8 aspectos)
│   │   │   ├── chatbot.py           ← Chatbot FSM 3 capas
│   │   │   ├── claude_client.py     ← Integración Claude API
│   │   │   └── transcriber.py       ← Whisper STT
│   │   ├── training/
│   │   │   └── trainer.py           ← Pipeline fine-tuning BERT
│   │   ├── data/
│   │   │   └── training/
│   │   │       ├── tramites_dataset.jsonl  ← Dataset inicial (180 muestras)
│   │   │       └── nuevas_muestras.jsonl   ← Muestras adicionales
│   │   ├── main.py
│   │   └── config.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                         ← React 18 (puerto 5173)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── student/
│   │   │   │   ├── Home.jsx              ← Página de inicio
│   │   │   │   ├── TramitesIndex.jsx     ← Lista/búsqueda de trámites
│   │   │   │   ├── TramiteDetailPage.jsx ← Detalle + requisitos + solicitar
│   │   │   │   ├── MyRequests.jsx        ← Mis solicitudes + estado
│   │   │   │   └── KardistasInfo.jsx     ← Contacto y horarios kardistas
│   │   │   ├── admin/
│   │   │   │   ├── Dashboard.jsx         ← Panel de estadísticas
│   │   │   │   ├── TramitesManager.jsx   ← CRUD trámites (admin)
│   │   │   │   ├── RequestsManager.jsx   ← Gestión de solicitudes
│   │   │   │   ├── TrainingManager.jsx   ← Muestras de entrenamiento
│   │   │   │   └── ModelEvaluation.jsx   ← Métricas + entrenar modelo
│   │   │   └── auth/
│   │   │       └── Login.jsx             ← Formulario de login
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Layout.jsx            ← Wrapper con Navbar
│   │   │   │   └── Navbar.jsx            ← Barra de navegación
│   │   │   └── chatbot/
│   │   │       └── ChatWidget.jsx        ← Widget flotante de chat
│   │   ├── services/
│   │   │   └── api.js                   ← Axios + métodos de API
│   │   ├── store/
│   │   │   └── authStore.js             ← Zustand (auth persistido)
│   │   ├── App.jsx                      ← Rutas + ProtectedRoute
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── postgres/
│   └── init/
│       └── 01_extensions.sql            ← CREATE EXTENSION "uuid-ossp"
│
├── database_schema.sql                  ← Script SQL completo (ver sección 4)
├── docker-compose.yml
├── .env
├── .env.example
└── README.md
```

---

## 4. Base de Datos (PostgreSQL)

### ¿Necesito instalar PostgreSQL?

**Si usas Docker: NO.** PostgreSQL corre dentro del contenedor `usfx_postgres` automáticamente.

**Si quieres ver la base de datos visualmente**, instala una herramienta de cliente:
- **pgAdmin 4** — interfaz gráfica completa (recomendado)
- **DBeaver** — cliente universal, muy popular
- **TablePlus** — simple y rápido

Conecta con estos datos (con Docker corriendo):
```
Host:     localhost
Port:     5433          ← nota: 5433, no 5432 (mapeado en docker-compose)
Database: usfx_tramites
User:     usfx_admin
Password: usfx_secret_2024
```

### Diagrama de Tablas

```
users (1) ──────────────── (1) kardistas
  │  │                              │
  │  └── (∞) student_requests ──────┘
  │              │       │
  │          tramites  careers
  │              │
  │         requirements (∞)
  │
  └── (∞) notifications
  └── (∞) conversations
              │
         conversation_messages (∞)
              │
         training_samples (∞, opcional)

model_versions  ← tabla independiente (métricas IA)
```

### Descripción de cada tabla

#### `users` — Usuarios del sistema
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| email | VARCHAR(255) UNIQUE | Correo electrónico (login) |
| hashed_password | VARCHAR(255) | Contraseña hasheada con bcrypt |
| full_name | VARCHAR(255) | Nombre completo |
| role | VARCHAR(50) | `admin` / `kardista` / `student` |
| is_active | BOOLEAN | Cuenta activa o bloqueada |
| created_at | TIMESTAMPTZ | Fecha de registro |
| updated_at | TIMESTAMPTZ | Última actualización |

#### `tramites` — Trámites universitarios
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| code | VARCHAR(100) UNIQUE | Código interno (ej. `MATRICULA_REGULAR`) |
| name | VARCHAR(255) | Nombre del trámite |
| description | TEXT | Descripción larga |
| category | VARCHAR(100) | Categoría (matrícula, certificado, etc.) |
| duration_days | INTEGER | Días estimados de resolución |
| cost | NUMERIC(10,2) | Costo en bolivianos |
| is_active | BOOLEAN | Activo/inactivo (borrado suave) |
| applies_to | VARCHAR(50) | `all` / `tecnologico` / `6x` |
| order_index | INTEGER | Orden de visualización |
| icon | VARCHAR(100) | Nombre del ícono |
| office_location | VARCHAR(255) | Ubicación de la oficina |
| contact_info | VARCHAR(255) | Teléfono/email de contacto |
| cost_details | TEXT | Instrucciones de pago detalladas |
| duration_details | TEXT | Detalles extra de plazo |
| web_system_url | VARCHAR(255) | URL del sistema web (si aplica) |
| web_instructions | TEXT | Pasos para usar el sistema web |
| video_tutorial_url | VARCHAR(500) | Enlace a video tutorial |
| created_at | TIMESTAMPTZ | Fecha de creación |
| updated_at | TIMESTAMPTZ | Última actualización |

#### `requirements` — Requisitos de cada trámite
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| tramite_id | UUID FK → tramites | Trámite al que pertenece |
| step_number | INTEGER | Número de paso/orden |
| title | VARCHAR(500) | Título del requisito |
| description | TEXT | Descripción detallada |
| document_name | VARCHAR(500) | Nombre del documento requerido |
| is_mandatory | BOOLEAN | Si es obligatorio u opcional |
| notes | TEXT | Notas adicionales |
| created_at | TIMESTAMPTZ | Fecha de creación |

#### `careers` — Carreras universitarias
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| name | VARCHAR(255) | Nombre de la carrera |
| code | VARCHAR(50) UNIQUE | Código corto (ej. `ING_SISTEMAS`) |
| kardex_type | VARCHAR(50) | `tecnologico` / `6x` |
| is_active | BOOLEAN | Activa o no |

#### `kardistas` — Personal administrativo
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| user_id | UUID FK → users UNIQUE | Usuario asociado (1:1) |
| kardex_type | VARCHAR(50) | `tecnologico` / `6x` |
| office_location | VARCHAR(255) | Ubicación de su oficina |
| phone | VARCHAR(50) | Teléfono fijo |
| whatsapp | VARCHAR(50) | Número WhatsApp |
| email_contact | VARCHAR(255) | Email de contacto |
| schedule | JSONB | Horario de atención (JSON flexible) |
| created_at | TIMESTAMPTZ | Fecha de creación |

Ejemplo de `schedule` JSON:
```json
{
  "lunes": "08:00 - 12:00 / 14:00 - 18:00",
  "martes": "08:00 - 12:00 / 14:00 - 18:00",
  "miercoles": "08:00 - 12:00",
  "jueves": "08:00 - 12:00 / 14:00 - 18:00",
  "viernes": "08:00 - 12:00"
}
```

#### `student_requests` — Solicitudes de estudiantes
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| student_id | UUID FK → users | Estudiante que la creó |
| tramite_id | UUID FK → tramites | Trámite solicitado |
| career_id | UUID FK → careers | Carrera del estudiante |
| status | VARCHAR(50) | `pendiente` / `en_proceso` / `completado` / `rechazado` / `cancelado` |
| student_data | JSONB | Datos adicionales del formulario |
| notes | TEXT | Notas del estudiante |
| admin_notes | TEXT | Notas del kardista/admin |
| assigned_kardista_id | UUID FK → kardistas | Kardista asignado automáticamente |
| submitted_at | TIMESTAMPTZ | Fecha de envío |
| updated_at | TIMESTAMPTZ | Última actualización |
| completed_at | TIMESTAMPTZ | Fecha de resolución |

#### `request_status_history` — Historial de cambios de estado
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| request_id | UUID FK → student_requests CASCADE | Solicitud |
| previous_status | VARCHAR(50) | Estado anterior |
| new_status | VARCHAR(50) | Nuevo estado |
| changed_by_id | UUID FK → users | Quién hizo el cambio |
| notes | TEXT | Motivo del cambio |
| changed_at | TIMESTAMPTZ | Fecha del cambio |

#### `conversations` — Sesiones de chat
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| session_id | VARCHAR(255) INDEX | ID de sesión del frontend |
| user_id | UUID FK → users NULL | Usuario si está autenticado |
| started_at | TIMESTAMPTZ | Inicio de la conversación |
| ended_at | TIMESTAMPTZ NULL | Fin de la conversación |
| resolved | BOOLEAN | Si el chatbot resolvió la consulta |
| resolved_tramite_id | UUID FK → tramites NULL | Trámite que se identificó |

#### `conversation_messages` — Mensajes del chatbot
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| conversation_id | UUID FK → conversations CASCADE INDEX | Conversación |
| role | VARCHAR(20) | `user` / `assistant` / `system` |
| content | TEXT | Texto del mensaje |
| input_type | VARCHAR(20) | `text` / `voice` |
| audio_file_path | VARCHAR(500) NULL | Ruta del audio si fue por voz |
| classified_intent | VARCHAR(100) NULL | Intención clasificada por BERT |
| confidence_score | FLOAT NULL | Confianza del clasificador (0-1) |
| created_at | TIMESTAMPTZ | Fecha del mensaje |

#### `notifications` — Notificaciones
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| user_id | UUID FK → users CASCADE INDEX | Usuario destinatario |
| request_id | UUID FK → student_requests NULL | Solicitud relacionada |
| type | VARCHAR(50) | Tipo de notificación |
| title | VARCHAR(255) | Título |
| message | TEXT | Contenido |
| is_read | BOOLEAN | Leída o no |
| created_at | TIMESTAMPTZ | Fecha |

#### `training_samples` — Muestras para entrenar el modelo
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| text | TEXT | Texto de ejemplo |
| label | VARCHAR(100) INDEX | Etiqueta/intención (ej. `MATRICULA_REGULAR`) |
| source | VARCHAR(50) | `manual` / `conversation` / `augmented` |
| verified | BOOLEAN INDEX | Si fue revisada por un admin |
| verified_by_id | UUID FK → users NULL | Admin que verificó |
| conversation_message_id | UUID FK → conversation_messages NULL | Origen si viene de chat |
| created_at | TIMESTAMPTZ | Fecha |

#### `model_versions` — Versiones del modelo IA entrenado
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID PK | Identificador único |
| version_tag | VARCHAR(100) UNIQUE | Nombre de la versión (ej. `v1.0.0`) |
| model_path | VARCHAR(500) | Ruta al modelo guardado |
| training_samples_count | INTEGER | Muestras usadas en entrenamiento |
| val_samples_count | INTEGER | Muestras usadas en validación |
| accuracy | FLOAT | Precisión global |
| f1_score | FLOAT | F1 ponderado |
| confusion_matrix | JSONB | Matriz de confusión |
| classification_report | JSONB | Reporte por clase |
| base_model | VARCHAR(255) | Modelo base utilizado |
| hyperparams | JSONB | Hiperparámetros del entrenamiento |
| trained_at | TIMESTAMPTZ | Fecha de entrenamiento |
| is_active | BOOLEAN | Si es el modelo actualmente en uso |
| notes | TEXT | Notas adicionales |

### Script SQL — Ver `database_schema.sql`

En la raíz del proyecto se incluye el archivo `database_schema.sql` con todas las sentencias `CREATE TABLE` listas para ejecutar en PostgreSQL. Útil para inspeccionar la BD sin Docker.

---

## 5. Backend — FastAPI

### Tecnologías
- **FastAPI 0.115** — Framework async de alto rendimiento
- **SQLAlchemy 2.0 async** + **asyncpg** — ORM con soporte nativo async
- **Pydantic v2** — Validación y serialización de datos
- **python-jose** — JWT tokens (access 15 min + refresh 7 días)
- **passlib/bcrypt** — Hash seguro de contraseñas
- **httpx** — Cliente HTTP async (para comunicarse con AI Service)
- **Redis** — Cache y cola de trabajos

### Autenticación y Roles

El sistema usa **JWT Bearer tokens**. Tres roles:

| Rol | Puede hacer |
|-----|------------|
| `student` | Ver trámites, crear solicitudes, ver sus solicitudes, usar chatbot |
| `kardista` | Ver solicitudes asignadas, cambiar estado de solicitudes |
| `admin` | Todo lo anterior + CRUD trámites, ver todos los datos, gestionar entrenamiento |

**Flujo de login:**
1. `POST /api/v1/auth/login` con email y contraseña
2. Responde con `access_token` (15 min), `refresh_token` (7 días) y datos del usuario
3. El frontend guarda el token en localStorage (Zustand persistido)
4. Cada request lleva el header `Authorization: Bearer <token>`

### Schemas Pydantic (validación)

Todos los endpoints validan entrada y salida con schemas Pydantic v2:

```
schemas/
├── tramite.py         → TramiteCreate, TramiteUpdate, TramiteOut, RequirementCreate...
├── student_request.py → RequestCreate, RequestStatusUpdate, RequestOut...
├── user.py            → UserCreate, LoginRequest, TokenResponse, UserOut...
├── kardista.py        → KardistaOut, KardistaUpdate...
└── ai.py              → ClassifyRequest, ChatRequest, ChatResponse, TranscribeResponse...
```

### Inicialización de la BD

```bash
# Primera vez (con Docker corriendo):
docker-compose exec backend python -m app.seed          # Trámites, usuarios, kardistas
docker-compose exec backend python -m app.seed_training # 180 muestras de entrenamiento
```

`seed.py` crea:
- 10 carreras (5 tecnológico + 5 de 6x)
- 10+ trámites con todos sus requisitos y metadatos
- 3 usuarios demo (admin, kardista tecnológico, kardista 6x)
- 2 perfiles de kardista con horarios y contactos

---

## 6. AI Service — FastAPI + BERT + Whisper

### Arquitectura del chatbot (3 capas)

```
Mensaje usuario
      │
      ▼
┌─────────────────────────────────┐
│  CAPA 1: Clasificador de Intent │
│  Modelo: BERT español fine-tuned│
│  Clases: 20 (16 trámites +      │
│  SALUDO + DESPEDIDA +           │
│  AGRADECIMIENTO + FALLBACK)     │
│  Umbral confianza: 0.15         │
└──────────────┬──────────────────┘
               │ intent + confidence
               ▼
┌─────────────────────────────────┐
│  CAPA 2: Detector de Aspecto    │
│  ¿Qué quiere saber el usuario?  │
│  • REQUISITOS                   │
│  • PASOS                        │
│  • COSTO                        │
│  • PLAZO                        │
│  • UBICACION                    │
│  • CONTACTO                     │
│  • SISTEMA_WEB                  │
│  • GENERAL                      │
└──────────────┬──────────────────┘
               │ aspecto detectado
               ▼
┌─────────────────────────────────┐
│  CAPA 3: Generador de Respuesta │
│  Consulta trámite en BD         │
│  Construye respuesta con        │
│  datos específicos del aspecto  │
│  (+ Claude si está activado)    │
└─────────────────────────────────┘
```

### Clasificador BERT (`classifier.py`)

- **Modelo base:** `dccuchile/bert-base-spanish-wwm-cased`
- **20 clases de intención:**
  - 16 trámites: `MATRICULA_REGULAR`, `MATRICULA_NUEVO`, `KARDEX`, `CAMBIO_CARRERA`, `CARRERA_SIMULTANEA`, `DIPLOMA_ACADEMICO`, `TITULO_PROVISION_NACIONAL`, `SIMULTANEO_DIPLOMA_PROVISION`, `REPROGRAMACIONES`, `HOMOLOGACION`, `BECAS`, `CARNET_UNIVERSITARIO`, `SEGURO_SOCIAL`, y más
  - Conversacionales: `SALUDO_BIENVENIDA`, `DESPEDIDA`, `AGRADECIMIENTO`
  - `FALLBACK` — cuando no se entiende la consulta
- **Fallback por palabras clave:** si el modelo BERT no está cargado, usa un sistema de keywords básico
- **Fine-tuning:** se entrena con las muestras de la tabla `training_samples`

### Detector de Aspecto (`aspect_classifier.py`)

Detecta qué dimensión específica de un trámite interesa al usuario:

| Aspecto | Palabras clave | Campo BD usado |
|---------|---------------|----------------|
| REQUISITOS | documentos, necesito, pedir, qué necesito | `requirements` |
| PASOS | cómo hago, proceso, pasos, procedimiento | `requirements` |
| COSTO | cuánto cuesta, precio, pago, costo | `cost`, `cost_details` |
| PLAZO | cuánto tiempo, días, demora, plazo | `duration_days`, `duration_details` |
| UBICACION | dónde, oficina, lugar, dirección | `office_location` |
| CONTACTO | teléfono, whatsapp, email, contactar | `contact_info` |
| SISTEMA_WEB | sistema, página web, online, internet | `web_system_url`, `web_instructions` |
| GENERAL | (default) | Todos los campos |

### Chatbot FSM (`chatbot.py`)

Máquina de estados finita que:
1. Clasifica intención
2. Detecta aspecto
3. Para intenciones de trámite: busca datos en el backend via HTTP interno
4. Construye respuesta con plantilla Markdown estructurada
5. Incluye links de WhatsApp del kardista correspondiente
6. Si `claude_enabled=true`: enriquece la respuesta con Claude

### Whisper STT (`transcriber.py`)

- Modelo: `openai/whisper-small`
- Carga **lazy** (solo cuando se necesita, libera VRAM al terminar)
- Idioma configurado: español
- Soporta audio hasta 25 MB (configurable)
- Formatos: WebM, OGG, MP3, WAV, M4A

### Claude API (`claude_client.py`)

- Opcional — requiere `CLAUDE_API_KEY` en `.env`
- Se activa por solicitud (`claude_enabled: true` en el body)
- Genera respuestas más ricas con Markdown, listas, emojis
- Si falla (sin API key, error de red), usa respuesta estructurada como fallback

### Pipeline de Entrenamiento (`trainer.py`)

1. Obtiene muestras verificadas de la BD (`verified=true`)
2. Fallback al dataset JSONL local si no hay suficientes
3. Split 85% train / 15% validación
4. Fine-tuning en GPU (si disponible) o CPU
5. Calcula: accuracy, F1-score, matriz de confusión, reporte por clase
6. Guarda el modelo en `/app/data/models/classifier/`
7. Crea registro en `model_versions` y lo activa automáticamente

---

## 7. Frontend — React 18

### Páginas

#### Para estudiantes

**`/` — Home**
- Presentación del sistema
- Links rápidos a trámites y kardistas
- ChatWidget flotante disponible en todas las páginas

**`/tramites` — Lista de Trámites**
- Grid de todos los trámites activos
- Búsqueda por nombre/descripción en tiempo real
- Filtros por categoría y kardex_type
- Tarjeta con nombre, descripción, costo y duración

**`/tramites/:id` — Detalle de Trámite**
- Información completa del trámite
- Lista ordenada de requisitos (obligatorios y opcionales)
- Datos de contacto de la oficina
- Botón "Solicitar este trámite" → crea una solicitud
- Si tiene sistema web → instrucciones y link

**`/mis-solicitudes` — Mis Solicitudes**
- Lista de solicitudes del estudiante autenticado
- Estado con indicador visual de color
- Notas del kardista/admin
- Historial de cambios de estado

**`/kardistas` — Información Kardistas**
- Tarjeta de cada kardista con contacto completo
- Horarios de atención
- Botón de WhatsApp directo

#### Para administradores

**`/admin` — Dashboard**
- Estadísticas: solicitudes por estado, total trámites, muestras de entrenamiento
- Métricas del modelo IA activo (accuracy, F1)

**`/admin/tramites` — Gestionar Trámites**
- CRUD completo con formulario modal
- Agregar/editar/eliminar requisitos
- Configurar metadatos de aspecto (ubicación, costos, sistema web)

**`/admin/solicitudes` — Gestionar Solicitudes**
- Ver todas las solicitudes
- Cambiar estado (pendiente → en_proceso → completado/rechazado)
- Agregar notas administrativas

**`/admin/training` — Datos de Entrenamiento**
- Ver, agregar, editar muestras de entrenamiento
- Verificar/des-verificar muestras
- Filtrar por etiqueta, fuente, estado verificado

**`/admin/modelo` — Evaluación del Modelo**
- Métricas de la versión activa
- Botón para iniciar nuevo entrenamiento
- Ver historial de versiones y activar una anterior

### ChatWidget (`ChatWidget.jsx`)

Widget flotante en esquina inferior derecha, disponible en todas las páginas:

- Botón de texto: escribe y envía
- Botón de micrófono: graba audio (WebAPI MediaRecorder)
  - Audio enviado como WebM → backend → Whisper → texto transcrito
  - Texto transcrito se muestra y procesa automáticamente
- Historial de conversación (últimos 6 mensajes)
- Toggle "Claude AI" para respuestas más detalladas
- Cuando se identifica un trámite: muestra tarjeta con link directo

### Estado global (`authStore.js`)

```js
// Zustand store persistido en localStorage ('usfx-auth')
{
  user: { id, email, full_name, role },
  token: "eyJ...",
  setAuth: (user, token) => {},
  logout: () => {}
}
```

### Llamadas a la API (`services/api.js`)

Axios configurado con:
- Base URL: `VITE_API_BASE_URL` (default: `http://localhost:8000`)
- Interceptor de request: agrega `Authorization: Bearer <token>` automáticamente
- Interceptor de response: si recibe 401 → limpia auth y redirige a login

Servicios disponibles:
```js
tramiteService.getAll()
tramiteService.getById(id)
tramiteService.create(data)
tramiteService.update(id, data)

requestService.create(data)
requestService.getMy()
requestService.updateStatus(id, data)

aiService.chat(data)
aiService.transcribe(formData)

trainingService.getSamples(filters)
trainingService.createSample(data)
trainingService.verify(id)

kardistaService.getAll()
kardistaService.update(id, data)

authService.login(credentials)
authService.me()
```

---

## 8. Docker y Docker Compose

### Servicios

```yaml
# docker-compose.yml — 4 servicios + volúmenes

services:
  postgres:    # Puerto host 5433 → contenedor 5432
  redis:       # Puerto 6379
  backend:     # Puerto 8000 (FastAPI)
  ai_service:  # Puerto 8001 (FastAPI IA)
  frontend:    # Puerto 5173 (Vite dev server)
```

### Dependencias entre servicios

```
postgres (healthcheck) ←── backend ←── frontend
redis ←── backend
redis ←── ai_service
```

El backend no arranca hasta que postgres responda `pg_isready`.

### Volúmenes persistentes

| Volumen | Contenido |
|---------|-----------|
| `postgres_data` | Datos de PostgreSQL (se conservan entre reinicios) |
| `redis_data` | Datos de Redis |
| `ai_models` | Modelos BERT y Whisper descargados |
| `audio_uploads` | Archivos de audio subidos por usuarios |

### Mounts de desarrollo (hot-reload)

```yaml
backend:
  volumes:
    - ./backend:/app       # Código fuente montado → uvicorn --reload
    - audio_uploads:/app/uploads

ai_service:
  volumes:
    - ./ai_service:/app    # Hot-reload activo
    - ai_models:/app/data/models

frontend:
  volumes:
    - ./frontend:/app      # Vite HMR activo
    - /app/node_modules    # node_modules en volumen anónimo (performance)
```

### GPU (opcional)

Si tienes GPU NVIDIA, el ai_service la usa automáticamente:
```yaml
ai_service:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

Sin GPU, el sistema funciona en CPU con algo más de latencia.

### Comandos Docker útiles

```bash
# Levantar todo
docker-compose up --build

# Solo levantar (sin rebuild)
docker-compose up

# En background
docker-compose up -d

# Ver logs de un servicio
docker-compose logs -f backend
docker-compose logs -f ai_service

# Ejecutar comando dentro de un contenedor
docker-compose exec backend python -m app.seed
docker-compose exec backend python -m app.seed_training

# Ver estado de contenedores
docker-compose ps

# Parar todo
docker-compose down

# Parar y eliminar volúmenes (BORRA DATOS)
docker-compose down -v

# Reconstruir un solo servicio
docker-compose build backend
docker-compose up -d --no-deps backend
```

---

## 9. Variables de Entorno

El archivo `.env` en la raíz configura todos los servicios:

```env
# ── Base de datos ─────────────────────────────────────
POSTGRES_USER=usfx_admin
POSTGRES_PASSWORD=usfx_secret_2024
POSTGRES_DB=usfx_tramites
DATABASE_URL=postgresql+asyncpg://usfx_admin:usfx_secret_2024@postgres:5432/usfx_tramites

# ── Seguridad ─────────────────────────────────────────
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
INTERNAL_API_KEY=usfx-internal-ai-key-2024

# ── Servicios internos ────────────────────────────────
AI_SERVICE_URL=http://ai_service:8001
BACKEND_URL=http://backend:8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# ── Frontend ──────────────────────────────────────────
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# ── IA ────────────────────────────────────────────────
WHISPER_MODEL=small
USE_GPU=true
BERT_MODEL=dccuchile/bert-base-spanish-wwm-cased
MAX_AUDIO_SIZE_MB=25
CLAUDE_API_KEY=                     # Opcional — dejar vacío si no usas Claude
USE_ZERO_SHOT_CLASSIFIER=false      # true = descarga 300MB adicionales
```

> **Nota:** Cambia `SECRET_KEY` en producción. El `CLAUDE_API_KEY` es opcional; sin él el chatbot usa respuestas de plantilla en lugar de Claude.

---

## 10. Inicio Rápido

### Requisitos previos

- **Docker Desktop** instalado y corriendo
- **Git**
- (Opcional) NVIDIA Container Toolkit si tienes GPU NVIDIA

### Paso a paso

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd chatbot

# 2. Crear archivo de entorno
cp .env.example .env
# Edita .env si necesitas cambiar credenciales

# 3. Levantar todos los servicios (primera vez tarda 5-15 min)
docker-compose up --build

# 4. En otra terminal — poblar la base de datos (solo la primera vez)
docker-compose exec backend python -m app.seed
docker-compose exec backend python -m app.seed_training

# 5. Abrir en el navegador
# Frontend:    http://localhost:5173
# API Docs:    http://localhost:8000/docs
# AI Service:  http://localhost:8001/docs
```

### ¿Qué pasa en el primer `docker-compose up --build`?

1. Docker construye las 4 imágenes (backend, ai_service, frontend, descarga Whisper/BERT)
2. PostgreSQL arranca y ejecuta `postgres/init/01_extensions.sql`
3. El backend hace `CREATE TABLE` de todas las tablas al arrancar
4. El ai_service carga el clasificador BERT (modo keywords hasta que se entrene)
5. El frontend compila y sirve con Vite HMR

---

## 11. Credenciales Demo

| Rol | Email | Contraseña | Acceso |
|-----|-------|-----------|--------|
| Administrador | admin@usfx.bo | admin2024 | Panel admin completo |
| Kardista Tecnológico | kardista.tecnologico@usfx.bo | kardex2024 | Gestión solicitudes (TI, Sistemas, etc.) |
| Kardista 6x | kardista.6x@usfx.bo | kardex2024 | Gestión solicitudes (Química, Industrial, etc.) |

Para probar como estudiante: regístrate con cualquier email desde la pantalla de login.

---

## 12. Trámites y Carreras incluidos

### Trámites (10+)

| # | Trámite | Aplica a |
|---|---------|---------|
| 1 | Matrícula alumno regular | Todos |
| 2 | Matrícula alumno nuevo | Todos |
| 3 | Certificado académico / Kardex | Todos |
| 4 | Cambio de carrera | Todos |
| 5 | Carrera simultánea | Todos |
| 6 | Diploma académico | Todos |
| 7 | Título provisión nacional | Todos |
| 8 | Reprogramaciones | Todos |
| 9 | Homologación de materias | Todos |
| 10 | Becas | Todos |
| 11 | Carnet universitario | Todos |
| 12 | Seguro social | Todos |

### Carreras

**Kardex Tecnológico** (kardista.tecnologico@usfx.bo):
- Ingeniería en Telecomunicaciones
- Ingeniería en TI y Seguridad
- Diseño Gráfico y Animación Digital
- Ingeniería en Sistemas
- Ingeniería en Ciencias de la Computación

**Kardex 6x** (kardista.6x@usfx.bo):
- Ingeniería Química
- Ingeniería Industrial
- Ingeniería en Alimentos
- Ingeniería en Petróleo
- Ingeniería Ambiental

---

## 13. Módulo de IA — Guía Completa

### Entrenar el modelo BERT

**Desde el panel admin:**
1. Ve a `http://localhost:5173` y entra como admin
2. Panel Admin → **Datos de Entrenamiento** → revisa y verifica muestras
3. Panel Admin → **Evaluación del Modelo** → presiona **"Iniciar entrenamiento"**
4. El entrenamiento toma 5-20 minutos según hardware
5. El modelo se activa automáticamente al terminar

**Desde la terminal:**
```bash
curl -X POST http://localhost:8001/train \
  -H "Content-Type: application/json" \
  -d '{"min_samples": 5}'

# Ver progreso
curl http://localhost:8001/train/{job_id}
```

### Agregar muestras de entrenamiento

**Vía panel admin:** Admin → Datos de Entrenamiento → "Nueva muestra"

**Vía API:**
```bash
curl -X POST http://localhost:8000/api/v1/training/samples \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Qué necesito para matricularme este semestre",
    "label": "MATRICULA_REGULAR",
    "source": "manual"
  }'
```

**Labels disponibles:**
```
MATRICULA_REGULAR, MATRICULA_NUEVO, KARDEX, CAMBIO_CARRERA,
CARRERA_SIMULTANEA, DIPLOMA_ACADEMICO, TITULO_PROVISION_NACIONAL,
SIMULTANEO_DIPLOMA_PROVISION, REPROGRAMACIONES, HOMOLOGACION,
BECAS, CARNET_UNIVERSITARIO, SEGURO_SOCIAL,
SALUDO_BIENVENIDA, DESPEDIDA, AGRADECIMIENTO, FALLBACK
```

### Dataset inicial

`ai_service/app/data/training/tramites_dataset.jsonl` — 180 muestras (15 por clase)

Formato JSONL:
```json
{"text": "Qué documentos necesito para matricularme", "label": "MATRICULA_REGULAR"}
{"text": "Cuánto cuesta el kardex", "label": "KARDEX"}
```

### Métricas del modelo

Visibles en Panel Admin → Evaluación del Modelo:
- **Accuracy global** — Porcentaje de predicciones correctas
- **F1-score ponderado** — Métrica que balancea precisión y recall
- **Matriz de confusión** — Visualización de qué clases se confunden
- **Reporte por clase** — Precision/Recall/F1 para cada intención

---

## 14. API Endpoints

### Backend — Puerto 8000

Documentación interactiva: `http://localhost:8000/docs`

#### Autenticación (`/api/v1/auth`)
```
POST /login                    → { access_token, refresh_token, user }
POST /register                 → Crear cuenta de estudiante
GET  /me                       → Datos del usuario actual
```

#### Trámites (`/api/v1/tramites`)
```
GET  /                         → Lista todos los trámites activos
GET  /search?q=<texto>         → Búsqueda por texto
GET  /{id}                     → Detalle + requisitos
POST /                         → Crear trámite [admin]
PUT  /{id}                     → Actualizar trámite [admin]
DELETE /{id}                   → Desactivar trámite [admin]
POST /{id}/requirements        → Agregar requisito [admin]
PUT  /{id}/requirements/{rid}  → Actualizar requisito [admin]
DELETE /{id}/requirements/{rid}→ Eliminar requisito [admin]
```

#### Solicitudes (`/api/v1/requests`)
```
POST /                         → Crear solicitud [student]
GET  /my                       → Mis solicitudes [student]
GET  /                         → Todas las solicitudes [kardista/admin]
GET  /{id}                     → Detalle de solicitud
PUT  /{id}/status              → Cambiar estado [kardista/admin]
```

#### Kardistas (`/api/v1/kardistas`)
```
GET  /                         → Lista kardistas con contacto y horarios
PUT  /{id}                     → Actualizar perfil [kardista/admin]
```

#### Carreras (`/api/v1/careers`)
```
GET  /                         → Lista carreras
POST /                         → Crear carrera [admin]
```

#### Entrenamiento (`/api/v1/training`)
```
GET  /samples                  → Lista muestras (filtros: label, verified, q)
POST /samples                  → Agregar muestra [admin]
PUT  /samples/{id}             → Actualizar muestra [admin]
PUT  /samples/{id}/verify      → Verificar muestra [admin]
DELETE /samples/{id}           → Eliminar muestra [admin]
```

#### Admin (`/api/v1/admin`)
```
GET  /stats                    → Estadísticas generales [admin]
```

#### Notificaciones (`/api/v1/notifications`)
```
GET  /                         → Mis notificaciones
PUT  /{id}/read                → Marcar como leída
```

#### Versiones del modelo (`/api/v1/model-versions`)
```
GET  /                         → Lista versiones
GET  /active                   → Versión activa
PUT  /{id}/activate            → Activar versión [admin]
```

#### IA Proxy (`/api/v1/ai`)
```
POST /classify                 → Clasificar texto
POST /chat                     → Chat con chatbot
POST /transcribe               → Audio → texto
```

### AI Service — Puerto 8001

Documentación: `http://localhost:8001/docs`

```
POST /classify                 → Clasificar intención de texto
POST /transcribe               → Transcribir audio (multipart/form-data)
POST /chat                     → Chatbot completo (intent + aspecto + respuesta)
POST /train                    → Iniciar entrenamiento BERT
GET  /train/{job_id}           → Estado del entrenamiento
GET  /metrics/model-info       → Info del modelo activo
```

**Ejemplo — Chat:**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sesion-123",
    "message": "Cuánto cuesta el kardex?",
    "history": [],
    "claude_enabled": false,
    "backend_url": "http://backend:8000",
    "internal_api_key": "usfx-internal-ai-key-2024"
  }'
```

---

## 15. Agregar un nuevo trámite

### Opción A — Panel Admin (recomendado)

1. Login como admin
2. Admin → Gestionar Trámites → "Nuevo Trámite"
3. Completa el formulario con nombre, descripción, costo, duración
4. Agrega los requisitos paso a paso
5. Completa los campos de aspecto (ubicación, contacto, sistema web si aplica)
6. Agrega muestras de entrenamiento con la nueva etiqueta
7. Reentrena el modelo desde Evaluación del Modelo

### Opción B — Via `seed.py`

Edita `backend/app/seed.py` y agrega el trámite al array de datos, luego:
```bash
docker-compose exec backend python -m app.seed
```

### Opción C — API directa

```bash
curl -X POST http://localhost:8000/api/v1/tramites \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MI_NUEVO_TRAMITE",
    "name": "Nombre del Trámite",
    "description": "Descripción completa",
    "cost": 50.00,
    "duration_days": 5,
    "applies_to": "all"
  }'
```

---

## 16. Hardware Recomendado

| Componente | Mínimo | Recomendado |
|-----------|--------|-------------|
| GPU | Sin GPU (CPU fallback) | NVIDIA ≥ 4GB VRAM (RTX 3060 6GB ✅) |
| RAM | 8 GB | 16 GB |
| Almacenamiento | 10 GB libres | 20 GB libres |
| SO | Windows 10/11, Linux, macOS | Linux (mejor soporte Docker GPU) |

**Con GPU:** BERT y Whisper corren en VRAM, respuestas en 1-3 segundos.

**Sin GPU:** Funciona en CPU, respuestas en 5-15 segundos. El clasificador por palabras clave es inmediato.

---

## Información del Proyecto

- **Universidad:** USFX — Facultad de Tecnología
- **Materia:** SIS325
- **Rama:** `main`
