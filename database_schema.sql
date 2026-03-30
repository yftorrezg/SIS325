-- ============================================================
-- USFX Trámites — Schema completo de la base de datos
-- Compatible con PostgreSQL 16
--
-- Para ejecutarlo en pgAdmin o DBeaver:
--   1. Conecta a tu servidor PostgreSQL
--   2. Crea la base de datos: CREATE DATABASE usfx_tramites;
--   3. Abre este archivo y ejecuta todo
--
-- Con Docker (si el sistema ya está corriendo):
--   El backend crea las tablas automáticamente al arrancar.
--   Este script es solo para visualización / uso externo.
-- ============================================================

-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLA: users
-- Usuarios del sistema (estudiantes, kardistas, admins)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(50)  NOT NULL,       -- 'admin' | 'kardista' | 'student'
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

COMMENT ON TABLE  users              IS 'Usuarios del sistema';
COMMENT ON COLUMN users.role         IS 'Roles: admin, kardista, student';
COMMENT ON COLUMN users.is_active    IS 'false = cuenta bloqueada';

-- ============================================================
-- TABLA: careers
-- Carreras universitarias (Tecnológico y 6x)
-- ============================================================
CREATE TABLE IF NOT EXISTS careers (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    code        VARCHAR(50)  NOT NULL UNIQUE,   -- Ej: 'ING_SISTEMAS'
    kardex_type VARCHAR(50)  NOT NULL,           -- 'tecnologico' | '6x'
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE  careers              IS 'Carreras universitarias de la Facultad de Tecnología';
COMMENT ON COLUMN careers.kardex_type  IS 'tecnologico = Kardex Tecnológico, 6x = Kardex 6x';

-- ============================================================
-- TABLA: tramites
-- Trámites universitarios disponibles
-- ============================================================
CREATE TABLE IF NOT EXISTS tramites (
    id                  UUID           PRIMARY KEY DEFAULT uuid_generate_v4(),
    code                VARCHAR(100)   NOT NULL UNIQUE,  -- Ej: 'MATRICULA_REGULAR'
    name                VARCHAR(255)   NOT NULL,
    description         TEXT,
    category            VARCHAR(100),
    duration_days       INTEGER,                          -- Días estimados de resolución
    cost                NUMERIC(10,2)  NOT NULL DEFAULT 0.00,
    is_active           BOOLEAN        NOT NULL DEFAULT TRUE,
    applies_to          VARCHAR(50)    NOT NULL DEFAULT 'all',  -- 'all'|'tecnologico'|'6x'
    order_index         INTEGER        NOT NULL DEFAULT 0,
    icon                VARCHAR(100),

    -- Campos por aspecto (usados por el chatbot para respuestas específicas)
    office_location     VARCHAR(255),   -- Aspecto UBICACION
    contact_info        VARCHAR(255),   -- Aspecto CONTACTO
    cost_details        TEXT,           -- Aspecto COSTO (instrucciones de pago)
    duration_details    TEXT,           -- Aspecto PLAZO (info extra de tiempo)
    web_system_url      VARCHAR(255),   -- Aspecto SISTEMA_WEB (URL)
    web_instructions    TEXT,           -- Aspecto SISTEMA_WEB (pasos)
    video_tutorial_url  VARCHAR(500),   -- Link a video tutorial

    created_at          TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  tramites             IS 'Catálogo de trámites universitarios';
COMMENT ON COLUMN tramites.applies_to  IS 'all = todos, tecnologico = solo kardex tecnológico, 6x = solo kardex 6x';
COMMENT ON COLUMN tramites.cost        IS 'Costo en bolivianos (Bs.)';

-- ============================================================
-- TABLA: requirements
-- Requisitos de cada trámite (relación 1:N con tramites)
-- ============================================================
CREATE TABLE IF NOT EXISTS requirements (
    id            UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    tramite_id    UUID         NOT NULL REFERENCES tramites(id) ON DELETE CASCADE,
    step_number   INTEGER      NOT NULL,
    title         VARCHAR(500) NOT NULL,
    description   TEXT,
    document_name VARCHAR(500),
    is_mandatory  BOOLEAN      NOT NULL DEFAULT TRUE,
    notes         TEXT,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  requirements              IS 'Requisitos/pasos de cada trámite';
COMMENT ON COLUMN requirements.step_number  IS 'Orden del paso dentro del trámite';
COMMENT ON COLUMN requirements.is_mandatory IS 'false = documento opcional';

-- ============================================================
-- TABLA: kardistas
-- Personal administrativo (kardistas) — perfil extendido de users
-- ============================================================
CREATE TABLE IF NOT EXISTS kardistas (
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID         NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    kardex_type     VARCHAR(50)  NOT NULL,    -- 'tecnologico' | '6x'
    office_location VARCHAR(255),
    phone           VARCHAR(50),
    whatsapp        VARCHAR(50),
    email_contact   VARCHAR(255),
    schedule        JSONB,                     -- Horarios por día de la semana
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  kardistas          IS 'Perfil extendido de usuarios con rol kardista';
COMMENT ON COLUMN kardistas.schedule IS 'JSON con horarios: {"lunes": "08:00-12:00", ...}';

-- ============================================================
-- TABLA: student_requests
-- Solicitudes de trámites enviadas por estudiantes
-- ============================================================
CREATE TABLE IF NOT EXISTS student_requests (
    id                   UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id           UUID         REFERENCES users(id),
    tramite_id           UUID         NOT NULL REFERENCES tramites(id),
    career_id            UUID         REFERENCES careers(id),
    status               VARCHAR(50)  NOT NULL DEFAULT 'pendiente',
    -- Estados: pendiente | en_proceso | completado | rechazado | cancelado
    student_data         JSONB,                    -- Datos extras del formulario
    notes                TEXT,                     -- Notas del estudiante
    admin_notes          TEXT,                     -- Notas del kardista/admin
    assigned_kardista_id UUID         REFERENCES kardistas(id),
    submitted_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at         TIMESTAMPTZ              -- Se llena cuando pasa a completado
);

COMMENT ON TABLE  student_requests        IS 'Solicitudes de trámites de los estudiantes';
COMMENT ON COLUMN student_requests.status IS 'pendiente | en_proceso | completado | rechazado | cancelado';

-- ============================================================
-- TABLA: request_status_history
-- Historial de cambios de estado de cada solicitud
-- ============================================================
CREATE TABLE IF NOT EXISTS request_status_history (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id      UUID        NOT NULL REFERENCES student_requests(id) ON DELETE CASCADE,
    previous_status VARCHAR(50),
    new_status      VARCHAR(50) NOT NULL,
    changed_by_id   UUID        REFERENCES users(id),
    notes           TEXT,
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE request_status_history IS 'Auditoría de cambios de estado de solicitudes';

-- ============================================================
-- TABLA: conversations
-- Sesiones del chatbot (una por usuario/visita)
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id                  UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id          VARCHAR(255) NOT NULL,    -- ID generado en el frontend
    user_id             UUID         REFERENCES users(id),
    started_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    resolved            BOOLEAN      NOT NULL DEFAULT FALSE,
    resolved_tramite_id UUID         REFERENCES tramites(id)
);

CREATE INDEX IF NOT EXISTS ix_conversations_session_id ON conversations(session_id);

COMMENT ON TABLE  conversations              IS 'Sesiones de chat con el asistente IA';
COMMENT ON COLUMN conversations.resolved     IS 'true = el chatbot identificó el trámite buscado';

-- ============================================================
-- TABLA: conversation_messages
-- Mensajes individuales dentro de una conversación
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id                UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id   UUID         NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role              VARCHAR(20)  NOT NULL,    -- 'user' | 'assistant' | 'system'
    content           TEXT         NOT NULL,
    input_type        VARCHAR(20)  NOT NULL DEFAULT 'text',  -- 'text' | 'voice'
    audio_file_path   VARCHAR(500),             -- Ruta del archivo de audio si fue por voz
    classified_intent VARCHAR(100),             -- Intención clasificada por BERT
    confidence_score  FLOAT,                    -- Confianza del clasificador (0.0 - 1.0)
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_conversation_messages_conversation_id
    ON conversation_messages(conversation_id);

COMMENT ON TABLE  conversation_messages                  IS 'Mensajes del chatbot';
COMMENT ON COLUMN conversation_messages.classified_intent IS 'Ej: MATRICULA_REGULAR, KARDEX, etc.';
COMMENT ON COLUMN conversation_messages.confidence_score  IS 'Confianza del modelo (0.0 a 1.0)';

-- ============================================================
-- TABLA: notifications
-- Notificaciones para usuarios (cambios de estado, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id         UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_id UUID         REFERENCES student_requests(id),
    type       VARCHAR(50),
    title      VARCHAR(255),
    message    TEXT,
    is_read    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);

COMMENT ON TABLE notifications IS 'Notificaciones de usuario (cambios de estado, avisos)';

-- ============================================================
-- TABLA: training_samples
-- Muestras de texto etiquetadas para entrenar el modelo BERT
-- ============================================================
CREATE TABLE IF NOT EXISTS training_samples (
    id                      UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    text                    TEXT         NOT NULL,
    label                   VARCHAR(100) NOT NULL,   -- Intención: MATRICULA_REGULAR, KARDEX, etc.
    source                  VARCHAR(50)  NOT NULL DEFAULT 'manual',
    -- source: 'manual' | 'conversation' | 'augmented'
    verified                BOOLEAN      NOT NULL DEFAULT FALSE,
    verified_by_id          UUID         REFERENCES users(id),
    conversation_message_id UUID         REFERENCES conversation_messages(id),
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_training_samples_label    ON training_samples(label);
CREATE INDEX IF NOT EXISTS ix_training_samples_verified ON training_samples(verified);

COMMENT ON TABLE  training_samples          IS 'Muestras etiquetadas para fine-tuning del modelo BERT';
COMMENT ON COLUMN training_samples.verified IS 'Solo las muestras verificadas se usan en el entrenamiento';
COMMENT ON COLUMN training_samples.label    IS
    'Clases: MATRICULA_REGULAR, MATRICULA_NUEVO, KARDEX, CAMBIO_CARRERA, '
    'CARRERA_SIMULTANEA, DIPLOMA_ACADEMICO, TITULO_PROVISION_NACIONAL, '
    'SIMULTANEO_DIPLOMA_PROVISION, REPROGRAMACIONES, HOMOLOGACION, '
    'BECAS, CARNET_UNIVERSITARIO, SEGURO_SOCIAL, '
    'SALUDO_BIENVENIDA, DESPEDIDA, AGRADECIMIENTO, FALLBACK';

-- ============================================================
-- TABLA: model_versions
-- Versiones del modelo BERT entrenado, con sus métricas
-- ============================================================
CREATE TABLE IF NOT EXISTS model_versions (
    id                      UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_tag             VARCHAR(100)  NOT NULL UNIQUE,   -- Ej: 'v1.0.0', 'v2.1.3'
    model_path              VARCHAR(500)  NOT NULL,           -- Ruta en el filesystem
    training_samples_count  INTEGER,                          -- Muestras usadas en train
    val_samples_count       INTEGER,                          -- Muestras usadas en validación
    accuracy                FLOAT,                            -- Accuracy global (0.0-1.0)
    f1_score                FLOAT,                            -- F1-score ponderado (0.0-1.0)
    confusion_matrix        JSONB,                            -- Matriz de confusión (JSON)
    classification_report   JSONB,                            -- Reporte por clase (JSON)
    base_model              VARCHAR(255),                     -- Modelo base (dccuchile/bert-...)
    hyperparams             JSONB,                            -- Hiperparámetros usados
    trained_at              TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    is_active               BOOLEAN       NOT NULL DEFAULT FALSE,
    notes                   TEXT
);

COMMENT ON TABLE  model_versions           IS 'Versiones entrenadas del clasificador BERT';
COMMENT ON COLUMN model_versions.is_active IS 'Solo un registro puede ser true a la vez';

-- ============================================================
-- CONSULTAS ÚTILES PARA EXPLORAR LA BD
-- ============================================================

-- Ver todos los trámites con cantidad de requisitos:
-- SELECT t.name, t.code, t.cost, t.duration_days, COUNT(r.id) AS num_requisitos
-- FROM tramites t
-- LEFT JOIN requirements r ON r.tramite_id = t.id
-- GROUP BY t.id
-- ORDER BY t.order_index;

-- Ver kardistas con sus usuarios:
-- SELECT u.full_name, u.email, k.kardex_type, k.phone, k.whatsapp
-- FROM kardistas k
-- JOIN users u ON u.id = k.user_id;

-- Ver solicitudes con detalle:
-- SELECT sr.id, u.full_name AS estudiante, t.name AS tramite,
--        c.name AS carrera, sr.status, sr.submitted_at
-- FROM student_requests sr
-- JOIN users u ON u.id = sr.student_id
-- JOIN tramites t ON t.id = sr.tramite_id
-- LEFT JOIN careers c ON c.id = sr.career_id
-- ORDER BY sr.submitted_at DESC;

-- Ver muestras de entrenamiento por clase:
-- SELECT label, COUNT(*) AS total,
--        SUM(CASE WHEN verified THEN 1 ELSE 0 END) AS verificadas
-- FROM training_samples
-- GROUP BY label
-- ORDER BY label;

-- Ver el modelo activo:
-- SELECT version_tag, accuracy, f1_score, training_samples_count, trained_at
-- FROM model_versions
-- WHERE is_active = TRUE;
