# Sistema de Trámites Universitarios - Facultad de Tecnología USFX

Plataforma web para gestión de trámites universitarios con asistente de IA (NLP + Whisper).

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + TailwindCSS + Vite |
| Backend | Python FastAPI + SQLAlchemy async |
| IA | BERT español (dccuchile) + Whisper (OpenAI) |
| Base de datos | PostgreSQL 16 |
| Cache/Jobs | Redis 7 |
| Contenedores | Docker + docker-compose |

## Inicio Rápido

### 1. Requisitos
- Docker Desktop con soporte GPU (NVIDIA Container Toolkit)
- Git

### 2. Configurar entorno
```bash
cd chatbot
cp .env.example .env
# Edita .env si necesitas cambiar contraseñas
```

### 3. Levantar servicios
```bash
docker-compose up --build
```

### 4. Poblar base de datos (primera vez)
```bash
docker-compose exec backend python -m app.seed
```

### 5. Acceder
- **Frontend**: http://localhost:5173
- **API docs**: http://localhost:8000/docs
- **AI Service**: http://localhost:8001/docs

## Credenciales Demo

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Administrador | admin@usfx.bo | admin2024 |
| Kardista Tecnológico | kardista.tecnologico@usfx.bo | kardex2024 |
| Kardista 6x | kardista.6x@usfx.bo | kardex2024 |

## Trámites incluidos (10)

1. Matrícula alumno regular
2. Matrícula alumno nuevo
3. Certificado académico / Kardex
4. Cambio de carrera
5. Carrera simultánea
6. Titulación
7. Reprogramaciones
8. Homologación de materias
9. Becas
10. Carnet universitario

## Kardex y Carreras

**Kardex Tecnológico** → Ing. Telecomunicaciones, Ing. TI y Seguridad, Diseño y Animación, Ing. Sistemas, Ing. Ciencias de la Computación

**Kardex 6x** → Ing. Química, Ing. Industrial, Ing. Alimentos, Ing. Petróleo, Ing. Ambiental, Ing. Industrias Alimentarias

## Módulo de IA

### Clasificador de intenciones
- Modelo base: `dccuchile/bert-base-spanish-wwm-cased`
- 12 clases (10 trámites + consulta general + saludo)
- Fallback por palabras clave mientras no hay modelo entrenado

### Transcripción de voz
- Modelo: `openai/whisper-small` (carga lazy, libera VRAM al estar inactivo)
- Idioma: español boliviano

### Chatbot
- FSM rule-based: clasifica → busca trámite en BD → responde con template
- Umbral de confianza: 0.45 (bajo → pide clarificación)

### Entrenar el modelo
1. Ve al **Panel Admin → Datos de Entrenamiento**
2. Agrega o verifica muestras etiquetadas
3. Ve a **Evaluación del Modelo** y presiona "Iniciar entrenamiento"
4. El modelo se activa automáticamente al terminar

### Dataset inicial
`ai_service/app/data/training/tramites_dataset.jsonl` — 180 muestras (15 por clase)

Para reentrenar con más datos, agrega muestras verificadas desde el panel admin.

## Estructura del Proyecto

```
chatbot/
├── backend/          # FastAPI — API principal, BD, auth
│   └── app/
│       ├── api/v1/   # Endpoints REST
│       ├── models/   # SQLAlchemy ORM
│       ├── schemas/  # Pydantic v2
│       └── seed.py   # Datos iniciales
├── ai_service/       # FastAPI — clasificador BERT + Whisper
│   └── app/
│       ├── models/   # Classifier, Transcriber, Chatbot
│       ├── training/ # Pipeline fine-tuning
│       └── data/     # Dataset JSONL + modelos guardados
├── frontend/         # React + TailwindCSS
│   └── src/
│       ├── pages/    # student/, admin/, auth/
│       ├── components/ # layout/, chatbot/
│       └── services/ # API calls (axios)
├── postgres/init/    # Scripts SQL iniciales
└── docker-compose.yml
```

## API Endpoints Principales

### Backend (puerto 8000)
```
POST /api/v1/auth/login          Login
GET  /api/v1/tramites            Listar trámites
GET  /api/v1/tramites/{id}       Detalle + requisitos
POST /api/v1/requests            Crear solicitud
GET  /api/v1/requests/my         Mis solicitudes
PUT  /api/v1/requests/{id}/status Actualizar estado (kardista)
GET  /api/v1/kardistas           Info kardistas + horarios
POST /api/v1/ai/chat             Chat con IA
POST /api/v1/ai/transcribe       Audio → texto
GET  /api/v1/admin/stats         Estadísticas
```

### AI Service (puerto 8001)
```
POST /classify                   Clasificar texto
POST /transcribe                 Audio → texto
POST /chat                       Chatbot
POST /train                      Iniciar entrenamiento
GET  /train/{job_id}             Estado del entrenamiento
GET  /metrics/model-info         Info del modelo activo
```

## Agregar un nuevo trámite

1. **Panel Admin → Gestionar Trámites → Nuevo trámite** (interfaz gráfica)
2. O directamente en BD via `backend/app/seed.py`
3. Agregar muestras de entrenamiento etiquetadas con el código del trámite
4. Reentrenar el modelo desde el panel

## Métricas del modelo

Después de cada entrenamiento se generan:
- Accuracy y F1-score (ponderado)
- Matriz de confusión (JSON)
- Reporte de clasificación por clase

Visible en **Panel Admin → Evaluación del Modelo**.

## Hardware recomendado

- GPU: NVIDIA con ≥4GB VRAM (RTX 3060 6GB ✅)
- RAM: ≥16GB
- Almacenamiento: ≥20GB libres para modelos

La IA se ejecuta en GPU automáticamente si está disponible.
Sin GPU, funciona en CPU con el fallback por palabras clave.
# SIS325
