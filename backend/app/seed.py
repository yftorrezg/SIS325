"""
Run this script to seed the database with initial data.
Usage: python -m app.seed
"""
import asyncio
import uuid
from app.database import AsyncSessionLocal, engine, Base
from app.models import *  # noqa
from app.core.security import get_password_hash


CAREERS = [
    # Kardex Tecnológico
    {"name": "Ingeniería en Telecomunicaciones", "code": "ING_TELECO", "kardex_type": "tecnologico"},
    {"name": "Ingeniería en Tecnologías de la Información y Seguridad", "code": "ING_TIS", "kardex_type": "tecnologico"},
    {"name": "Diseño y Animación", "code": "DISENIO_ANIM", "kardex_type": "tecnologico"},
    {"name": "Ingeniería en Sistemas", "code": "ING_SISTEMAS", "kardex_type": "tecnologico"},
    {"name": "Ingeniería en Ciencias de la Computación", "code": "ING_CC", "kardex_type": "tecnologico"},
    # Kardex 6x
    {"name": "Ingeniería Química", "code": "ING_QUIMICA", "kardex_type": "6x"},
    {"name": "Ingeniería Industrial", "code": "ING_INDUSTRIAL", "kardex_type": "6x"},
    {"name": "Ingeniería de Alimentos", "code": "ING_ALIMENTOS", "kardex_type": "6x"},
    {"name": "Ingeniería en Petróleo", "code": "ING_PETROLEO", "kardex_type": "6x"},
    {"name": "Ingeniería Ambiental", "code": "ING_AMBIENTAL", "kardex_type": "6x"},
    {"name": "Ingeniería en Industrias Alimentarias", "code": "ING_IND_ALIM", "kardex_type": "6x"},
]

TRAMITES = [
    {
        "code": "TRAMITE_MATRICULA_ALUMNO_REGULAR",
        "name": "Trámite de Matrícula - Alumno Regular",
        "description": "Proceso de inscripción para estudiantes que ya cursaron al menos un semestre en la facultad.",
        "category": "matricula",
        "duration_days": 3,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 1,
        "icon": "academic-cap",
        "office_location": "Kardista de tu carrera — Pabellón C Oficina 201 (Kardex Tecnológico) o Pabellón D Oficina 105 (Kardex 6x)",
        "contact_info": "Kardista Tecnológico: Juan Pérez, (4) 6454200 int. 210, WhatsApp +591 70123456 | Kardista 6x: María López, (4) 6454200 int. 215, WhatsApp +591 72345678",
        "cost_details": "Trámite gratuito — no requiere pago de arancel",
        "duration_details": "3 días hábiles desde la entrega de documentos al kardista",
        "web_system_url": "https://universitarios.usfx.bo",
        "web_instructions": "1. Ingresá a universitarios.usfx.bo con tu usuario y contraseña. 2. Menú Matrículas → Matricularme. 3. Generá el importe a pagar. 4. Pagá con depósito en Banco Unión Cta. 1-33340493 (UMSFX – REC. PROPIOS – MATRÍCULAS) o con QR. 5. Registrá el número de depósito en el sistema. El depósito puede tardar hasta 4 horas en reflejarse.",
        "requirements": [
            {"step_number": 1, "title": "Verificar deudas pendientes", "description": "Verificar que no tenga deudas con la universidad (biblioteca, laboratorios, etc.)", "is_mandatory": True},
            {"step_number": 2, "title": "Llenar formulario de matrícula", "description": "Completar el formulario de matrícula proporcionado por la facultad", "document_name": "Formulario de matrícula", "is_mandatory": True},
            {"step_number": 3, "title": "Presentar fotocopia de CI", "description": "Fotocopia de cédula de identidad vigente", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 4, "title": "Pago de arancel (si corresponde)", "description": "Cancelar el arancel de matrícula en tesorería si aplica", "is_mandatory": False},
            {"step_number": 5, "title": "Entrega al kardista", "description": "Entregar toda la documentación al kardista correspondiente a su carrera", "is_mandatory": True},
        ],
    },
    {
        "code": "TRAMITE_MATRICULA_ALUMNO_NUEVO",
        "name": "Trámite de Matrícula - Alumno Nuevo",
        "description": "Proceso de inscripción para bachilleres que ingresan por primera vez a la facultad.",
        "category": "matricula",
        "duration_days": 5,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 2,
        "icon": "user-plus",
        "office_location": "Secretaría de Admisiones — Edificio Central USFX, luego al kardista de tu carrera elegida",
        "contact_info": "Admisiones USFX: (4) 6454200 | Kardista Tecnológico: Juan Pérez, int. 210 | Kardista 6x: María López, int. 215",
        "cost_details": "Trámite gratuito — el pago de matrícula se realiza vía sistema web universitarios.usfx.bo o depósito en Banco Unión Cta. 1-33340493",
        "duration_details": "5 días hábiles para completar la inscripción una vez presentados todos los documentos",
        "web_system_url": "https://admision.usfx.bo",
        "web_instructions": "1. Subí tus documentos en admision.usfx.bo: Diploma de Bachiller legalizado por SEDUCA, libreta de 6to, CI y foto carnet fondo blanco. 2. Una vez aceptado, realizá el pago en universitarios.usfx.bo o con QR. 3. Presentate al kardista con el comprobante.",
        "requirements": [
            {"step_number": 1, "title": "Diploma de bachiller original", "description": "Presentar diploma de bachiller original y fotocopia", "document_name": "Diploma de bachiller", "is_mandatory": True},
            {"step_number": 2, "title": "Certificado de nacimiento original", "description": "Certificado de nacimiento original (no más de 3 meses de antigüedad)", "document_name": "Certificado de nacimiento", "is_mandatory": True},
            {"step_number": 3, "title": "Fotocopia de CI", "description": "Fotocopia de cédula de identidad vigente", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 4, "title": "2 fotos carnet", "description": "Dos fotografías tamaño carnet actualizadas", "document_name": "Fotos carnet", "is_mandatory": True},
            {"step_number": 5, "title": "Formulario de inscripción", "description": "Llenar y firmar el formulario de inscripción para alumnos nuevos", "document_name": "Formulario inscripción", "is_mandatory": True},
            {"step_number": 6, "title": "Selección de carrera", "description": "Indicar la carrera de preferencia dentro de la facultad", "is_mandatory": True},
        ],
    },
    {
        "code": "SOLICITUD_CERTIFICADO_KARDEX",
        "name": "Solicitud de Certificado Académico / Kardex",
        "description": "Solicitud del historial académico oficial del estudiante con todas sus calificaciones.",
        "category": "certificados",
        "duration_days": 5,
        "cost": 20.00,
        "applies_to": "all",
        "order_index": 3,
        "icon": "document-text",
        "office_location": "Kardista de tu carrera — Pabellón C Oficina 201 (Tecnológico) o Pabellón D Oficina 105 (6x)",
        "contact_info": "Kardista Tecnológico: Juan Pérez, (4) 6454200 int. 210, WhatsApp +591 70123456 | Kardista 6x: María López, int. 215, WhatsApp +591 72345678",
        "cost_details": "Bs. 20 — pagar en Tesorería de la Facultad y presentar el comprobante al kardista",
        "duration_details": "5 días hábiles desde la entrega de la solicitud y comprobante de pago",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Solicitud escrita dirigida al kardista", "description": "Carta de solicitud dirigida al kardista correspondiente a su carrera, indicando el motivo (trabajo, beca, trámite externo, etc.)", "document_name": "Solicitud escrita", "is_mandatory": True},
            {"step_number": 2, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 3, "title": "Pago de arancel", "description": "Cancelar el arancel correspondiente en tesorería", "document_name": "Comprobante de pago", "is_mandatory": True, "notes": "El costo varía según el tipo de certificado solicitado"},
            {"step_number": 4, "title": "Entrega al kardista", "description": "Presentar todos los documentos al kardista de su kardex", "is_mandatory": True},
        ],
    },
    {
        "code": "SOLICITUD_CAMBIO_CARRERA",
        "name": "Solicitud de Cambio de Carrera",
        "description": "Proceso para que un estudiante cambie de carrera dentro de la Facultad de Tecnología.",
        "category": "cambios",
        "duration_days": 10,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 4,
        "icon": "arrows-right-left",
        "office_location": "Decanato de la Facultad de Tecnología — Edificio principal, planta baja",
        "contact_info": "Secretaría del Decanato: (4) 6454200 int. 200 | Kardista destino según la carrera a la que se cambia",
        "cost_details": "Trámite gratuito",
        "duration_details": "Hasta 10 días hábiles para la resolución del Consejo de Facultad",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Solicitud escrita al Decano", "description": "Carta de solicitud dirigida al Decano de la Facultad indicando el motivo del cambio", "document_name": "Solicitud al Decano", "is_mandatory": True},
            {"step_number": 2, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 3, "title": "Kardex actualizado", "description": "Presentar el kardex académico actualizado de la carrera actual", "document_name": "Kardex actualizado", "is_mandatory": True},
            {"step_number": 4, "title": "Entrevista con el kardista destino", "description": "Coordinar con el kardista de la carrera destino para verificar requisitos", "is_mandatory": True},
            {"step_number": 5, "title": "Resolución de aceptación", "description": "Esperar la resolución del Consejo de Facultad", "is_mandatory": True, "notes": "El proceso puede tardar hasta 10 días hábiles"},
        ],
    },
    {
        "code": "SOLICITUD_CARRERA_SIMULTANEA",
        "name": "Solicitud de Carrera Simultánea",
        "description": "Proceso para inscribirse en una segunda carrera dentro de la Facultad de Tecnología manteniendo la carrera actual.",
        "category": "cambios",
        "duration_days": 15,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 5,
        "icon": "squares-plus",
        "office_location": "Decanato de la Facultad de Tecnología — Edificio principal, planta baja",
        "contact_info": "Secretaría del Decanato: (4) 6454200 int. 200 | Kardistas de ambas carreras",
        "cost_details": "Trámite gratuito",
        "duration_details": "Hasta 15 días hábiles para la aprobación del Consejo de Facultad. Verificá el requisito del índice académico (mínimo 51 puntos) antes de presentar.",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Mínimo 3er año aprobado", "description": "Haber aprobado al menos el tercer año (o 50% del plan de estudios) en la carrera actual", "is_mandatory": True},
            {"step_number": 2, "title": "Índice académico mínimo", "description": "Contar con un índice académico mínimo de 51 puntos", "is_mandatory": True},
            {"step_number": 3, "title": "Solicitud al Decano", "description": "Carta de solicitud dirigida al Decano indicando la segunda carrera elegida", "document_name": "Solicitud al Decano", "is_mandatory": True},
            {"step_number": 4, "title": "Kardex actualizado", "document_name": "Kardex actualizado", "is_mandatory": True},
            {"step_number": 5, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 6, "title": "Resolución del Consejo", "description": "Esperar aprobación del Consejo de Facultad", "is_mandatory": True},
        ],
    },
    {
        "code": "TRAMITE_TITULACION",
        "name": "Trámite de Titulación",
        "description": "Proceso para obtener el título profesional luego de concluir todas las materias del plan de estudios.",
        "category": "titulacion",
        "duration_days": 90,
        "cost": 150.00,
        "applies_to": "all",
        "order_index": 6,
        "icon": "academic-cap",
        "office_location": "Kardista de tu carrera (inicio del proceso), luego Secretaría General USFX para el título",
        "contact_info": "Kardista Tecnológico: Juan Pérez, (4) 6454200 int. 210 | Kardista 6x: María López, int. 215 | Secretaría General: (4) 6454200 int. 100",
        "cost_details": "Bs. 150 — pagadero en Tesorería de la Facultad. El monto puede variar según modalidad de titulación elegida.",
        "duration_details": "Hasta 90 días hábiles dependiendo de la modalidad elegida (Tesis, Proyecto de Grado, Examen de Grado, etc.)",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "1. Ingresá a si2.usfx.bo/suniver. 2. Menú Trámites Académicos → Titulación. 3. Completá el formulario y generá el código de pago. 4. Presentate al kardista con todos los documentos físicos.",
        "requirements": [
            {"step_number": 1, "title": "Concluir todas las materias", "description": "Haber aprobado el 100% de las materias del plan de estudios", "is_mandatory": True},
            {"step_number": 2, "title": "Solicitud de inicio de titulación", "description": "Presentar solicitud escrita al kardista para iniciar el proceso", "document_name": "Solicitud de titulación", "is_mandatory": True},
            {"step_number": 3, "title": "Elección de modalidad de titulación", "description": "Elegir entre: Tesis, Proyecto de Grado, Examen de Grado, Trabajo Dirigido u otras modalidades vigentes", "is_mandatory": True},
            {"step_number": 4, "title": "Kardex definitivo", "description": "Solicitar kardex definitivo con todas las materias aprobadas", "document_name": "Kardex definitivo", "is_mandatory": True},
            {"step_number": 5, "title": "Certificado de no adeudo", "description": "Obtener certificado de no adeudo de todas las dependencias de la universidad", "document_name": "Certificado no adeudo", "is_mandatory": True},
            {"step_number": 6, "title": "Pago de aranceles", "description": "Cancelar los aranceles de titulación en tesorería", "document_name": "Comprobante de pago", "is_mandatory": True},
            {"step_number": 7, "title": "Inscripción y defensa", "description": "Inscribirse para la defensa y presentar el trabajo según modalidad elegida", "is_mandatory": True},
        ],
    },
    {
        "code": "SOLICITUD_REPROGRAMACIONES",
        "name": "Solicitud de Reprogramaciones",
        "description": "Solicitud para reprogramar exámenes parciales o finales por causas justificadas.",
        "category": "academico",
        "duration_days": 2,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 7,
        "icon": "calendar",
        "office_location": "Kardista de tu carrera — Pabellón C Oficina 201 (Tecnológico) o Pabellón D Oficina 105 (6x)",
        "contact_info": "Kardista Tecnológico: Juan Pérez, int. 210, WhatsApp +591 70123456 | Kardista 6x: María López, int. 215, WhatsApp +591 72345678",
        "cost_details": "Trámite gratuito",
        "duration_details": "La solicitud debe presentarse dentro de los 3 días hábiles posteriores al examen. La resolución se emite en 2 días hábiles.",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Solicitud escrita al kardista", "description": "Carta de solicitud dirigida al kardista indicando la materia, examen y fecha que se desea reprogramar", "document_name": "Solicitud de reprogramación", "is_mandatory": True},
            {"step_number": 2, "title": "Justificación documentada", "description": "Presentar documentos que justifiquen la ausencia (certificado médico, citación judicial, etc.)", "document_name": "Documento justificativo", "is_mandatory": True},
            {"step_number": 3, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 4, "title": "Presentación dentro del plazo", "description": "La solicitud debe presentarse dentro de los 3 días hábiles siguientes al examen", "is_mandatory": True, "notes": "Las reprogramaciones sin justificación válida no son aceptadas"},
        ],
    },
    {
        "code": "SOLICITUD_HOMOLOGACION_MATERIAS",
        "name": "Solicitud de Homologación de Materias / Equivalencias",
        "description": "Proceso para reconocer materias aprobadas en otra carrera o institución educativa.",
        "category": "academico",
        "duration_days": 20,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 8,
        "icon": "document-duplicate",
        "office_location": "Decanato de la Facultad de Tecnología — Edificio principal, planta baja",
        "contact_info": "Secretaría del Decanato: (4) 6454200 int. 200",
        "cost_details": "Trámite gratuito",
        "duration_details": "Hasta 20 días hábiles — la comisión académica evalúa la equivalencia de contenidos antes de emitir resolución",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Solicitud escrita al Decano", "description": "Carta de solicitud de homologación dirigida al Decano de la Facultad", "document_name": "Solicitud de homologación", "is_mandatory": True},
            {"step_number": 2, "title": "Certificado de notas original", "description": "Certificado de notas original de la institución de origen (universidad o carrera anterior)", "document_name": "Certificado de notas", "is_mandatory": True},
            {"step_number": 3, "title": "Programas analíticos de materias", "description": "Presentar los programas analíticos (sílabos) de las materias a homologar, certificados por la institución de origen", "document_name": "Programas analíticos", "is_mandatory": True},
            {"step_number": 4, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 5, "title": "Evaluación por comisión", "description": "La comisión académica evalúa la equivalencia de contenidos y emite resolución", "is_mandatory": True, "notes": "El proceso puede tardar hasta 20 días hábiles"},
        ],
    },
    {
        "code": "TRAMITE_BECAS",
        "name": "Trámite de Becas",
        "description": "Solicitud de beca universitaria por excelencia académica, situación económica u otros criterios.",
        "category": "bienestar",
        "duration_days": 30,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 9,
        "icon": "star",
        "office_location": "Bienestar Estudiantil — Edificio Central USFX, 1er piso",
        "contact_info": "Bienestar Estudiantil USFX: (4) 6454200 int. 220 | También consultá con tu kardista para saber si hay convocatoria vigente",
        "cost_details": "Trámite gratuito. Las becas, una vez aprobadas, cubren total o parcialmente el arancel universitario.",
        "duration_details": "Hasta 30 días hábiles para la evaluación y resolución. Verificá las convocatorias activas antes de presentar.",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Verificar convocatoria vigente", "description": "Consultar en la facultad si existe convocatoria de becas activa y sus requisitos específicos", "is_mandatory": True},
            {"step_number": 2, "title": "Índice académico requerido", "description": "Para beca por excelencia: índice académico mínimo de 65 puntos", "is_mandatory": True, "notes": "Los requisitos varían según el tipo de beca"},
            {"step_number": 3, "title": "Solicitud de beca", "description": "Llenar y firmar el formulario de solicitud de beca", "document_name": "Formulario de beca", "is_mandatory": True},
            {"step_number": 4, "title": "Kardex actualizado", "document_name": "Kardex actualizado", "is_mandatory": True},
            {"step_number": 5, "title": "Certificado de situación económica (si aplica)", "description": "Para becas socioeconómicas: certificado de situación económica familiar", "document_name": "Certificado económico", "is_mandatory": False},
            {"step_number": 6, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
        ],
    },
    {
        "code": "CARNET_UNIVERSITARIO",
        "name": "Carnet Universitario",
        "description": "Trámite para obtener o reponer el carnet de identificación universitario.",
        "category": "identificacion",
        "duration_days": 7,
        "cost": 30.00,
        "applies_to": "all",
        "order_index": 10,
        "icon": "identification",
        "office_location": "Secretaría de la Facultad de Tecnología — Edificio principal, planta baja",
        "contact_info": "Secretaría de Facultad: (4) 6454200 int. 205",
        "cost_details": "Bs. 30 — pagar en Tesorería de la Facultad y presentar el comprobante en Secretaría. En caso de extravío adjuntar declaración jurada.",
        "duration_details": "7 días hábiles para la emisión del carnet desde la presentación completa de documentos",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Formulario de solicitud", "description": "Llenar el formulario de solicitud de carnet universitario en secretaría de la facultad", "document_name": "Formulario carnet", "is_mandatory": True},
            {"step_number": 2, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 3, "title": "2 fotos carnet actualizadas", "description": "Dos fotografías tamaño carnet actualizadas con fondo blanco", "document_name": "Fotos carnet", "is_mandatory": True},
            {"step_number": 4, "title": "Comprobante de matrícula vigente", "description": "Presentar comprobante de estar matriculado en el semestre actual", "document_name": "Comprobante de matrícula", "is_mandatory": True},
            {"step_number": 5, "title": "Pago de arancel", "description": "Cancelar el arancel de carnet en tesorería", "document_name": "Comprobante de pago", "is_mandatory": True, "notes": "En caso de extravío o deterioro, adjuntar declaración jurada"},
        ],
    },
    {
        "code": "TRAMITE_DIPLOMA_ACADEMICO",
        "name": "Diploma Académico",
        "description": "Documento oficial que certifica la conclusión de estudios de pregrado. Es el primer título que obtiene el egresado de la Facultad de Tecnología USFX.",
        "category": "titulacion",
        "duration_days": 30,
        "cost": 100.00,
        "applies_to": "all",
        "order_index": 11,
        "icon": "academic-cap",
        "office_location": "Caja de la Facultad de Tecnología — Edificio principal planta baja. El proceso inicia en el sistema SUNIVER.",
        "contact_info": "Kardista de tu carrera + Caja de la Facultad: (4) 6454200 int. 205",
        "cost_details": "Bs. 100 aprox. — pagar en Caja de la Facultad al presentar los documentos. Incluye papel valorado y valores universitarios.",
        "duration_details": "Hasta 30 días hábiles desde la presentación completa de documentos en Caja. La Solvencia Universitaria tiene validez de solo 48 horas desde la primera firma.",
        "web_system_url": "https://universitarios.usfx.bo",
        "web_instructions": "1. Ingresá a universitarios.usfx.bo con tu usuario y contraseña. 2. Menú Trámites → Diploma Académico. 3. Completá el formulario en línea y generá el comprobante. 4. Imprimí el formulario y presentate en Caja con todos los documentos físicos.",
        "requirements": [
            {"step_number": 1, "title": "Fotocopia CI vigente", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 2, "title": "Carnet universitario vigente", "document_name": "Carnet universitario", "is_mandatory": True},
            {"step_number": 3, "title": "Certificados originales de notas / Kardex", "description": "Firmado por el kardista de tu carrera", "document_name": "Certificados de notas", "is_mandatory": True},
            {"step_number": 4, "title": "Certificado de Conclusión de Estudios", "document_name": "Certificado de conclusión", "is_mandatory": True},
            {"step_number": 5, "title": "Certificado de Nacimiento original actualizado", "description": "Con una antigüedad no mayor a 3 meses", "document_name": "Certificado de Nacimiento", "is_mandatory": True},
            {"step_number": 6, "title": "Solvencia Universitaria", "description": "Válida solo 48 horas desde la primera firma. Obtenela el mismo día que presentés los documentos.", "document_name": "Solvencia Universitaria", "is_mandatory": True, "notes": "¡Solo tiene 48 horas de validez desde la primera firma!"},
            {"step_number": 7, "title": "Fotocopia legalizada del Diploma de Bachiller", "document_name": "Diploma de Bachiller legalizado", "is_mandatory": True},
            {"step_number": 8, "title": "Certificado de aprobación de modalidad de graduación", "document_name": "Cert. modalidad graduación", "is_mandatory": True},
            {"step_number": 9, "title": "3 fotografías 4×4 fondo rojo", "document_name": "3 fotos 4×4 fondo rojo", "is_mandatory": True},
            {"step_number": 10, "title": "Sobre, funda plástica oficio y papel valorado", "document_name": "Materiales de presentación", "is_mandatory": True},
        ],
    },
    {
        "code": "TRAMITE_TITULO_PROVISION_NACIONAL",
        "name": "Título en Provisión Nacional",
        "description": "Título profesional expedido por la USFX que habilita el ejercicio de la profesión a nivel nacional. Se tramita después de obtener el Diploma Académico.",
        "category": "titulacion",
        "duration_days": 20,
        "cost": 80.00,
        "applies_to": "all",
        "order_index": 12,
        "icon": "academic-cap",
        "office_location": "Caja de la Facultad de Tecnología, luego Secretaría General USFX para el título definitivo.",
        "contact_info": "Kardista de tu carrera + Secretaría General USFX: (4) 6454200 int. 100",
        "cost_details": "Bs. 80 aprox. — pagar en Caja de la Facultad. Incluye valores universitarios.",
        "duration_details": "Hasta 20 días hábiles desde la presentación en Caja. El título final es emitido por Secretaría General USFX.",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "1. Ingresá a si2.usfx.bo/suniver con tu usuario. 2. Menú Trámites Académicos → Título en Provisión Nacional. 3. Completá el formulario y generá el comprobante. 4. Presentate en Caja con los documentos físicos.",
        "requirements": [
            {"step_number": 1, "title": "Fotocopia legalizada del Diploma Académico", "document_name": "Diploma Académico legalizado", "is_mandatory": True, "notes": "Debe estar legalizado por la USFX antes de tramitar el título"},
            {"step_number": 2, "title": "Fotocopia simple del Certificado de Nacimiento", "document_name": "Copia Certificado Nacimiento", "is_mandatory": True},
            {"step_number": 3, "title": "Fólder universitario", "document_name": "Fólder universitario", "is_mandatory": True},
            {"step_number": 4, "title": "3 fotografías 4×4 fondo rojo", "document_name": "3 fotos 4×4 fondo rojo", "is_mandatory": True},
            {"step_number": 5, "title": "Valores universitarios", "document_name": "Valores universitarios", "is_mandatory": True},
            {"step_number": 6, "title": "Sobre para fotografías", "document_name": "Sobre", "is_mandatory": True},
        ],
    },
    {
        "code": "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION",
        "name": "Trámite Simultáneo: Diploma + Título en Provisión",
        "description": "Permite obtener el Diploma Académico y el Título en Provisión Nacional al mismo tiempo, ahorrando tiempo y trámites. Requiere los documentos combinados de ambos trámites.",
        "category": "titulacion",
        "duration_days": 35,
        "cost": 160.00,
        "applies_to": "all",
        "order_index": 13,
        "icon": "academic-cap",
        "office_location": "Caja de la Facultad de Tecnología + Secretaría General USFX. Proceso inicia en SUNIVER.",
        "contact_info": "Kardista de tu carrera + Secretaría General: (4) 6454200 int. 100 + Caja: int. 205",
        "cost_details": "Bs. 160 aprox. (combinado de ambos trámites) — pagar en Caja de la Facultad.",
        "duration_details": "Hasta 35 días hábiles. La Solvencia Universitaria tiene solo 48 horas de validez. Coordiná bien los plazos.",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "1. Ingresá a si2.usfx.bo/suniver. 2. Menú Trámites → seleccioná la opción simultánea Diploma + Título. 3. Completá ambos formularios y generá los comprobantes. 4. Presentate en Caja con toda la documentación.",
        "requirements": [
            {"step_number": 1, "title": "Fotocopia CI vigente", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 2, "title": "Carnet universitario vigente", "document_name": "Carnet universitario", "is_mandatory": True},
            {"step_number": 3, "title": "Certificados originales de notas / Kardex firmado", "document_name": "Certificados de notas", "is_mandatory": True},
            {"step_number": 4, "title": "Certificado de Conclusión de Estudios", "document_name": "Certificado de conclusión", "is_mandatory": True},
            {"step_number": 5, "title": "Certificado de Nacimiento original actualizado", "description": "Con antigüedad no mayor a 3 meses", "document_name": "Certificado de Nacimiento", "is_mandatory": True},
            {"step_number": 6, "title": "Solvencia Universitaria", "description": "Válida solo 48 horas", "document_name": "Solvencia Universitaria", "is_mandatory": True, "notes": "¡Solo 48 horas de validez! Obtenerla el mismo día de presentación."},
            {"step_number": 7, "title": "Fotocopia legalizada del Diploma de Bachiller", "document_name": "Diploma de Bachiller legalizado", "is_mandatory": True},
            {"step_number": 8, "title": "Certificado de aprobación de modalidad de graduación", "document_name": "Cert. modalidad graduación", "is_mandatory": True},
            {"step_number": 9, "title": "6 fotografías 4×4 fondo rojo", "description": "3 para el Diploma + 3 para el Título", "document_name": "6 fotos 4×4 fondo rojo", "is_mandatory": True},
            {"step_number": 10, "title": "Fólder universitario, funda plástica oficio, papel valorado, sobre, valores universitarios", "document_name": "Materiales de presentación (x2)", "is_mandatory": True},
        ],
    },
    {
        "code": "PROCESO_MATRICULACION_WEB",
        "name": "Matriculación en el Sistema Web (SUNIVER)",
        "description": "Guía paso a paso para completar el proceso de matrícula en la plataforma universitarios.usfx.bo o si2.usfx.bo/suniver. Solo para estudiantes regulares.",
        "category": "matricula",
        "duration_days": 1,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 14,
        "icon": "computer-desktop",
        "office_location": "El proceso es completamente en línea. Si hay problemas con el sistema, consultá en Tesorería de la Facultad.",
        "contact_info": "Soporte técnico SUNIVER: soporte@usfx.bo | Tesorería: (4) 6454200 int. 206",
        "cost_details": "El proceso web en sí es gratuito. El pago de matrícula se realiza vía depósito bancario o QR según el monto generado por el sistema.",
        "duration_details": "El proceso toma minutos en línea. El depósito bancario puede tardar hasta 4 horas en reflejarse en el sistema.",
        "web_system_url": "https://universitarios.usfx.bo",
        "web_instructions": "1. Ingresá a universitarios.usfx.bo con tu usuario y contraseña SUNIVER. 2. Menú Matrículas → Matricularme. 3. El sistema generará el importe a pagar. 4. Elegí modalidad: Depósito en Banco Unión Cta. 1-33340493 (UMSFX – REC. PROPIOS – MATRÍCULAS) o Pago con QR (confirmación inmediata). 5. Si pagaste con depósito, registrá el número de papeleta en el sistema. 6. Verificá en Matrículas → Mis Matrículas.",
        "requirements": [
            {"step_number": 1, "title": "Usuario y contraseña SUNIVER activos", "description": "Si no tenés usuario, solicitalo al kardista de tu carrera", "is_mandatory": True},
            {"step_number": 2, "title": "No tener deudas pendientes", "description": "Verificá que no tenés deudas con biblioteca, laboratorios u otras dependencias", "is_mandatory": True},
            {"step_number": 3, "title": "Generar importe en el sistema", "description": "Ir a Matrículas → Matricularme y generar el código/importe de pago", "is_mandatory": True},
            {"step_number": 4, "title": "Realizar el pago", "description": "Depósito en Banco Unión Cta. 1-33340493 o pago con QR en el sistema", "is_mandatory": True, "notes": "NO se aceptan transferencias bancarias. Solo depósito o QR."},
            {"step_number": 5, "title": "Registrar número de depósito (si aplica)", "description": "Si pagaste con depósito bancario, ingresá el número de papeleta en el sistema. El depósito puede tardar hasta 4 horas en aparecer.", "is_mandatory": False},
            {"step_number": 6, "title": "Verificar matrícula", "description": "Confirmá en Matrículas → Mis Matrículas que el estado sea 'Matriculado'", "is_mandatory": True},
        ],
    },
    {
        "code": "PROCESO_PROGRAMACION_ACADEMICA",
        "name": "Programación Académica de Materias",
        "description": "Proceso para inscribir las materias del semestre en el sistema SUNIVER. Requiere tener matrícula vigente y, para programación manual, el kardex actualizado.",
        "category": "academico",
        "duration_days": 1,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 15,
        "icon": "calendar",
        "office_location": "El proceso es en línea (si2.usfx.bo/suniver). Para programación manual podés necesitar ir al kardista con tu kardex.",
        "contact_info": "Kardista de tu carrera para programación manual y consultas sobre materias habilitadas.",
        "cost_details": "Trámite gratuito.",
        "duration_details": "El proceso online es inmediato. Para programación manual el kardista puede tardar 1-2 días hábiles en procesar.",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "1. Ingresá a si2.usfx.bo/suniver con tu usuario y contraseña. 2. Verificá tener matrícula activa primero. 3. Menú Programaciones → Programarme. 4. Si tu carrera tiene programación automática: el sistema asigna las materias según tu avance. 5. Si es manual: seleccioná las materias habilitadas según tu kardex. 6. Confirmá y verificá en Programaciones → Mis Programaciones.",
        "requirements": [
            {"step_number": 1, "title": "Matrícula vigente del semestre actual", "description": "Debés estar matriculado antes de poder programar materias", "is_mandatory": True},
            {"step_number": 2, "title": "Usuario y contraseña SUNIVER activos", "is_mandatory": True},
            {"step_number": 3, "title": "Kardex actualizado (para programación manual)", "description": "Solicitalo al kardista de tu carrera si tu carrera usa programación manual", "document_name": "Kardex actualizado", "is_mandatory": False, "notes": "Solo requerido para carreras con programación manual"},
            {"step_number": 4, "title": "Ingresar al sistema dentro del período de programación", "description": "La programación tiene fechas específicas cada semestre. Consultá con tu kardista las fechas vigentes.", "is_mandatory": True, "notes": "Pasado el período no se puede programar"},
        ],
    },
    {
        "code": "SEGURO_SOCIAL_UNIVERSITARIO",
        "name": "Seguro Social Universitario Estudiantil (SSUE)",
        "description": "Servicio de atención médica gratuita para estudiantes universitarios activos. Cubre 18 especialidades médicas mediante citas programadas online.",
        "category": "bienestar",
        "duration_days": 0,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 16,
        "icon": "heart",
        "office_location": "SSU Sucre — Av. Germán Mendoza (frente al hospital). Citas solo mediante el sistema online.",
        "contact_info": "SSU Sucre: ssu-sucre.org | Para emergencias presentate directamente con tu carnet universitario",
        "cost_details": "Completamente gratuito para estudiantes activos de la USFX con matrícula vigente.",
        "duration_details": "Las citas se programan online y están disponibles según los horarios de cada especialidad. Llegá puntual a tu cita.",
        "web_system_url": "https://ssu-sucre.org/ficha",
        "web_instructions": "1. Ingresá a ssu-sucre.org/ficha. 2. Clic en EMITIR FICHA ESTUDIANTIL. 3. Ingresá tu número de carnet universitario y contraseña SUNIVER. 4. Seleccioná la fecha de consulta deseada. 5. Elegí la especialidad médica (hay 18 disponibles). 6. Seleccioná el horario disponible y confirmá. 7. Guardá o imprimí tu ficha. 8. Presentate puntualmente con el Carnet Universitario.",
        "requirements": [
            {"step_number": 1, "title": "Carnet universitario vigente", "description": "Es OBLIGATORIO presentarlo en TODAS las atenciones médicas", "document_name": "Carnet universitario", "is_mandatory": True, "notes": "Sin carnet universitario no se brinda atención"},
            {"step_number": 2, "title": "Matrícula activa", "description": "Debés tener matrícula vigente en el semestre actual", "is_mandatory": True},
            {"step_number": 3, "title": "Ficha de atención médica", "description": "Generarla en ssu-sucre.org/ficha antes de ir a la consulta", "document_name": "Ficha de atención", "is_mandatory": True},
        ],
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select, text
        from app.models.tramite import Tramite, Requirement
        from app.models.career import Career
        from app.models.user import User
        from app.models.kardista import Kardista

        existing_tramite = await db.execute(select(Tramite).limit(1))
        has_tramites = existing_tramite.scalar_one_or_none() is not None

        existing_admin = await db.execute(select(User).where(User.role == "admin").limit(1))
        has_admin = existing_admin.scalar_one_or_none() is not None

        if has_tramites and has_admin:
            print("Database already seeded. Skipping.")
            return

        if not has_tramites:
            print("Seeding careers...")
            career_objects = {}
            for c in CAREERS:
                career = Career(**c)
                db.add(career)
                await db.flush()
                career_objects[c["code"]] = career

            print("Seeding tramites and requirements...")
            for t in TRAMITES:
                requirements = t.pop("requirements", [])
                tramite = Tramite(**t)
                db.add(tramite)
                await db.flush()
                for req_data in requirements:
                    req = Requirement(tramite_id=tramite.id, **req_data)
                    db.add(req)
        else:
            print("Tramites already exist, skipping career/tramite seeding...")

        if not has_admin:
            print("Creating admin user...")
            admin = User(
                email="admin@usfx.bo",
                hashed_password=get_password_hash("admin2024"),
                full_name="Administrador USFX",
                role="admin",
            )
            db.add(admin)
            await db.flush()

            print("Creating kardistas...")
            kardista1_user = User(email="kardista.tecnologico@usfx.bo", hashed_password=get_password_hash("kardex2024"), full_name="Juan Pérez Flores", role="kardista")
            kardista2_user = User(email="kardista.6x@usfx.bo", hashed_password=get_password_hash("kardex2024"), full_name="María López Vda. de Mamani", role="kardista")
            db.add(kardista1_user)
            db.add(kardista2_user)
            await db.flush()

            kardista1 = Kardista(
                user_id=kardista1_user.id,
                kardex_type="tecnologico",
                office_location="Pabellón C, Oficina 201 - Facultad de Tecnología",
                phone="(4) 6454200 int. 210",
                whatsapp="+591 70123456",
                email_contact="kardista.tecnologico@usfx.bo",
                schedule={
                    "lunes": "08:00-12:00, 14:30-18:30",
                    "martes": "08:00-12:00, 14:30-18:30",
                    "miercoles": "08:00-12:00, 14:30-18:30",
                    "jueves": "08:00-12:00, 14:30-18:30",
                    "viernes": "08:00-12:00, 14:30-18:30",
                },
            )
            kardista2 = Kardista(
                user_id=kardista2_user.id,
                kardex_type="6x",
                office_location="Pabellón D, Oficina 105 - Facultad de Tecnología",
                phone="(4) 6454200 int. 215",
                whatsapp="+591 72345678",
                email_contact="kardista.6x@usfx.bo",
                schedule={
                    "lunes": "08:00-12:00, 14:30-18:30",
                    "martes": "08:00-12:00, 14:30-18:30",
                    "miercoles": "08:00-12:00, 14:30-18:30",
                    "jueves": "08:00-12:00, 14:30-18:30",
                    "viernes": "08:00-12:00, 14:30-18:30",
                },
            )
            db.add(kardista1)
            db.add(kardista2)

        await db.commit()
        print("Seeding complete!")
        print("\nCredentials:")
        print("  Admin:    admin@usfx.bo / admin2024")
        print("  Kardista Tecnológico: kardista.tecnologico@usfx.bo / kardex2024")
        print("  Kardista 6x: kardista.6x@usfx.bo / kardex2024")


if __name__ == "__main__":
    asyncio.run(seed())
