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
        "duration_days": "en qr es instantáneo, con depósito en banco union de 1 a 3 días hábiles, maximo 2 semanas",
        "cost": "Trámite matricula 85 bs Otros aportes 17.5 bs QR 0.5 bs Total 103.5 bs.",
        "applies_to": "all",
        "order_index": 1,
        "icon": "academic-cap",
        "office_location": "ve con tu Kardista, aunque la matricula es: pago QR o trasnferencia",
        "contact_info": "Kardista Tecnológico: Juan Pérez, WhatsApp +591 70123456 | Kardista 6x: María López, WhatsApp +591 72345678",
        "cost_details": "Te lo indica el sistema al generar el importe a pagar (link: universitarios.usfx.bo, menu matricula), depende de tu situación, doble carrera, si tienes materias reprobadas, etc",
        "duration_details": "de 1 dia a 3 días hábiles desde el pago por QR o Transferencia en el Banco Union",
        "web_system_url": "https://universitarios.usfx.bo",
        "web_instructions": "1. Ingresá a universitarios.usfx.bo con tu usuario y contraseña. /n 2. Menú Matrículas → Matricularme. /n 3. Generá el importe a pagar. /n 4. Pagá con depósito en Banco Unión Cta. 1-33340493 (UMSFX – REC. PROPIOS – MATRÍCULAS) o con QR. /n 5. Registrá el número de depósito en el sistema. El depósito puede tardar hasta 4 horas en reflejarse.",
        "requirements": [
            {"step_number": 1, "title": "Venerar importe", "description": "Ingresar a universitarios.usfx.bo (menú "MATRICULARME") para obtener el monto a depositar/transferir.", "is_mandatory": True},
            {"step_number": 2, "title": "Realizar pago", "description": "Depositar a la cuenta universitaria del BANCO UNIÓN No 1-33340493 (Titular: UMSFX – REC. PROPIOS – MATRICULAS UNIVERSITARIAS) o pagar mediante el QR generado en universitarios.usfx.bo.", "is_mandatory": True},
            {"step_number": 3, "title": "Registrar pago", "description": "Reingresar a universitarios.usfx.bo (menú "MATRICULARME") para completar los datos del depósito bancario o pago QR", "deposito_bancario": "Registrar el número. Si no aparece, verificar la escritura o esperar la actualización (máximo 4 horas)","deposito_QR": "Se recomienda usar el código en las primeras 24 horas para evitar retrasos en la habilitación e impresión de la matrícula.", "is_mandatory": True},
        ],
        "video_tutorial_url": "https://www.tiktok.com/@usfx.oficial/video/7469895244318870790",
    },
    {
        "code": "TRAMITE_MATRICULA_ALUMNO_NUEVO",
        "name": "Trámite de Matrícula - Alumno Nuevo",
        "description": "Proceso de inscripción para bachilleres que ingresan por primera vez a la facultad.",
        "category": "matricula",
        "duration_days": 3,
        "cost": 115.00,
        "applies_to": "all",
        "order_index": 2,
        "icon": "user-plus",
        "office_location": "Se realiza virtualmente a través del sistema de admisión en línea. universitarios.usfx.bo",
        "cost_details": "Trámite en línea — el pago de matrícula se realiza vía sistema web universitarios.usfx.bo QR o depósito bancario en Banco Unión Cta. 1-33340493",
        "duration_details": "de 1 a 3 días hábiles para completar la matriculacion, maximo 2 semanas dependiendo del tiempo de pago y validación del mismo",
        "web_system_url": "https://admision.usfx.bo",
        "web_instructions": " Subir Documentos Digitales (https://admision.usfx.bo/): Diploma de Bachiller legalizado por SEDUCA o autentificado por la USFX (anverso y reverso). Libreta/Certificado de egreso de sexto de secundaria (o libreta legalizada si no tiene Diploma). Cédula de identidad (anverso y reverso). Fotografía tipo carnet con fondo blanco. Incluir nombre completo, celular vigente y Carrera de admisión.
",
        "requirements": [ 
          {"step_number": 1, "title": "Subir Documentos Digitales (https://admision.usfx.bo/)", "description": "Diploma de Bachiller legalizado por SEDUCA o autentificado por la USFX (anverso y reverso). Libreta/Certificado de egreso de sexto de secundaria (o libreta legalizada si no tiene Diploma). Cédula de identidad (anverso y reverso). Fotografía tipo carnet con fondo blanco. Incluir nombre completo, celular vigente y Carrera de admisión.", "is_mandatory": True},
          {"step_number": 2, "title": "Verificación y Generación de Carnet Universitario (Servicios Académicos)", "description": "Servicios Académicos verifica la documentación y genera el número de Carnet Universitario (Vigente o Provisional).", "is_mandatory": True},
          {"step_number": 3, "title": "Visualizar Carnet Universitario", "description": "Ingresar a https://admision.usfx.bo/ para ver el número asignado.", "is_mandatory": True},
          {"step_number": 4, "title": "Generar Importe de Matrícula", "description": "Entrar a universitarios.usfx.bo, seleccionar MATRICULARME y generar el importe a pagar.", "is_mandatory": True},
          {"step_number": 5, "title": "Realizar Pago de Matrícula", "description": "Depositar o transferir a la cuenta del BANCO UNIÓN No 1-33340493 (Titular UMSFX – REC. PROPIOS – MATRICULAS UNIVERSITARIAS) o pagar mediante QR generado en universitarios.usfx.bo.", "is_mandatory": True},
          {"step_number": 6, "title": "Completar Matriculación", "description": "Ingresar a universitarios.usfx.bo, opción MATRICULARME y llenar campos: Depósito Bancario: Registrar el número de depósito (verifique si no aparece; puede tardar hasta 4 horas). Pago QR: Usar el código dentro de las primeras 24 horas para evitar demoras en la habilitación.", "is_mandatory": True},   
          
        ],
        "video_tutorial_url": "https://www.youtube.com/watch?v=wcyPjXP-vNI"
    },
    {
        "code": "SOLICITUD_CERTIFICADO_KARDEX",
        "name": "Solicitud de Certificado Académico / Kardex",
        "description": "Solicitud del historial académico oficial del estudiante con todas sus calificaciones.",
        "category": "certificados",
        "duration_days": 1,
        "cost":00.00,
        "applies_to": "all",
        "order_index": 3,
        "icon": "document-text",
        "office_location": "Kardista de tu carrera",
        "contact_info": "Kardista Tecnológico: Juan Pérez, (4) 6454200 int. 210, WhatsApp +591 70123456 | Kardista 6x: María López, int. 215, WhatsApp +591 72345678",
        "cost_details": "No tiene costo, es un trámite gratuito.",
        "duration_details": "El certificado te lo imprime el kardista en el momento en que le pides.",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
            {"step_number": 1, "title": "Solicitud personal al kardista", "description": "Te acercas con el Carnet Universitario o Documento de Identidad y te lo imprime", "is_mandatory": True},
            {"step_number": 2, "title": "Verificar datos en el certificado", "description": "Revisar que el certificado de notas (kardex) tenga tus datos correctos y todas las materias actualizadas", "is_mandatory": True},
        ],
        "video_tutorial_url": None,
        
    },
    {
        "code": "SOLICITUD_CAMBIO_CARRERA",
        "name": "Solicitud de Cambio de Carrera",
        "description": "Proceso para que un estudiante cambie de carrera dentro de la Facultad de Tecnología.",
        "category": "cambios",
        "duration_days": 10,
        "cost": 1.00,
        "applies_to": "all",
        "order_index": 4,
        "icon": "arrows-right-left",
        "office_location": "Central, https://maps.app.goo.gl/4sW9Y563Hj2txa5Q7 calle junin",
        "cost_details": "Trámite averiguar",
        "duration_details": "La solicitud debe presentarse dentro de los dias habiles. Fecha inicio: fuera de plazo. Fecha fin: fuera de plazo",
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
        "duration_details": "La solicitud debe presentarse dentro de los dias habiles. Fecha inicio: fuera de plazo. Fecha fin: fuera de plazo.",
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
        "code": "SOLICITUD_REPROGRAMACIONES",
        "name": "Solicitud de Reprogramaciones",
        "description": "Solicitud para reprogramar de las materias ya sea por choque de horarios o motivos justificados.",
        "category": "academico",
        "duration_days": 1,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 7,
        "icon": "calendar",
        "office_location": "Kardista de tu carrera",
        "contact_info": "Kardista Tecnológico: Juan Pérez, int. 210, WhatsApp +591 70123456 | Kardista 6x: María López, int. 215, WhatsApp +591 72345678",
        "cost_details": "Trámite gratuito",
        "duration_details": "La solicitud debe presentarse dentro de los dias habiles de reprogramación. Fecha inicio: fuera de plazo. Fecha fin: fuera de plazo.",
        "web_system_url": None,
        "web_instructions": None,
        "requirements": [
          """ 
          Escribir una carta al director de carrera para cambio de horarios o reprogramacion de materias
          En la carta debe indicar: motivos justificados para la reprogramación
          Adjuntar documentación de respaldo si corresponde (certificados médicos, constancias laborales, etc).
          Presentar la solicitud al kardista de tu carrera para su revisión y seguimiento e implementacion de la reprogramacion.
          """
          {"step_number": 1, "title": "Solicitud escrita al director de carrera", "description": "Carta dirigida al director de carrera indicando los motivos para la reprogramación y adjuntando documentación de respaldo si corresponde (certificados médicos, constancias laborales, etc).", "document_name": "Carta de solicitud", "is_mandatory": True},
          {"step_number": 2, "title": "Presentar solicitud al kardista", "description": "Entregar la carta al kardista de tu carrera para su revisión y seguimiento", "is_mandatory": True},
          {"step_number": 3, "title": "Reprogramación", "description": "El kardista va a implementar la reprogramación si sigue el plazo de reprogramaciones o es aprobada.", "is_mandatory": True},
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
        "duration_details": "La solicitud debe presentarse dentro de los dias habiles. Fecha inicio: fuera de plazo. Fecha fin: fuera de plazo.",
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
        "cost": 50.00,
        "applies_to": "all",
        "order_index": 10,
        "icon": "identification",
        "office_location": "Secretaría de la Facultad de Tecnología — Edificio principal, planta baja",
        "contact_info": "DTIC: whatsapp +591 70123456",
        "cost_details": "Bs. 50 — pagar en Refisur de la Facultad y presentar el comprobante en ventanilla.",
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
        "cost": 1800.00,
        "applies_to": "all",
        "order_index": 11,
        "icon": "academic-cap",
        "office_location": "Caja de la Facultad de Tecnología — Edificio principal/central planta baja. El proceso inicia en el sistema SUNIVER.",
        "contact_info": "Kardista de tu carrera + Caja de la Facultad central: (4) 6454200 int. 205",
        "cost_details": "Bs. 1800 aprox. — pagar en Caja de la Facultad al presentar los documentos. Incluye papel valorado y valores universitarios.",
        "duration_details": "Hasta 30 días hábiles desde la presentación completa de documentos en Caja. La Solvencia Universitaria tiene validez de solo 48 horas desde la primera firma.",
        "web_system_url": "https://universitarios.usfx.bo",
        "web_instructions": "Acceda al Sistema SUNIVER (https://universitarios.usfx.bo/Cuenta/security/login) e inicie sesión. Diríjase a la sección Trámites (menú lateral izquierdo en PC o superior en móvil). Dentro de Trámites Académicos, seleccione la opción para la solicitud de su Diploma Académico. El sistema preguntará: «¿Desea obtener simultáneamente el Diploma Académico y el Título en Provisión Nacional? Tenga en cuenta los costos asociados con ambos trámites.». Seleccione el botón según su necesidad. Revise los requisitos presentados por el sistema; una vez iniciado el trámite, no podrá realizar trámites simultáneos. Al iniciar, el sistema validará sus datos académicos. Si son correctos, continuará. Si hay errores, deberá subsanar las excepciones siguiendo las instrucciones. Si su carrera tiene varias menciones, elija el título específico que necesita. Seleccione los requisitos correspondientes (esto es una declaración de cumplimiento). Revise cuidadosamente los datos declarados, acepte y continúe. El sistema generará el formulario y la carta de solicitud (imprimir en hoja tamaño oficio). Presente estos documentos en la Caja designada para obtener los valores asociados al trámite.
",
        "requirements": [
            {"step_number": 1, "title": "Fotocopia CI vigente o Pasaporte legalizado (extranjeros)", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 2, "title": "Carnet universitario vigente", "document_name": "Carnet universitario", "is_mandatory": True},
            {"step_number": 3, "title": "Sobre para carnet universitario y fotografías", "document_name": "Sobre", "is_mandatory": True},
            {"step_number": 4, "title": "Funda plástica tamaño oficio", "document_name": "Funda plástica", "is_mandatory": True},
            {"step_number": 5, "title": "Certificados originales de notas y kardex firmado", "description": "Incluye certificados del exterior legalizados/apostillados o trámite original/reposición de convalidación de materias si aplica", "document_name": "Certificados de notas", "is_mandatory": True},
            {"step_number": 6, "title": "Certificado de Conclusión de Estudios", "document_name": "Certificado de conclusión", "is_mandatory": True},
            {"step_number": 7, "title": "Certificado de Nacimiento original actualizado (legalizado/apostillado para extranjeros)", "document_name": "Certificado de Nacimiento", "is_mandatory": True},
            {"step_number": 8, "title": "Papel valorado y valores para juramento de Ley", "document_name": "Papel valorado y valores", "is_mandatory": True},
            {"step_number": 9, "title": "Tres fotografías 4x4 idénticas, actuales, a color, con fondo rojo", "document_name": "3 fotos 4x4 fondo rojo", "is_mandatory": True},
            {"step_number": 10, "title": "Solvencia Universitaria llenada (válida por 48 horas desde la primera firma)", "document_name": "Solvencia Universitaria", "is_mandatory": True},
            {"step_number": 11, "title": "Fotocopia legalizada del Diploma de Bachiller o equivalente (legalizada/apostillada/homologada por SEDUCA si es del exterior)", "document_name": "Diploma de Bachiller legalizado", "is_mandatory": True},
            {"step_number": 12, "title": "Certificado de aprobación de la modalidad de graduación (excepto para Técnico Universitario Medio o graduación por excelencia)", "document_name": "Certificado modalidad de graduación", "is_mandatory": False},
        ],
        "video_tutorial_url": "https://www.tiktok.com/@kenia191911/video/7464983718151687429?is_from_webapp=1&sender_device=pc&web_id=7611253499893286421"
    },
    {
        "code": "TRAMITE_TITULO_PROVISION_NACIONAL",
        "name": "Título en Provisión Nacional",
        "description": "Título profesional expedido por la USFX que habilita el ejercicio de la profesión a nivel nacional. Se tramita después de obtener el Diploma Académico.",
        "category": "titulacion",
        "duration_days": 30,
        "cost": 2800.00,
        "applies_to": "all",
        "order_index": 12,
        "icon": "academic-cap",
        "office_location": "Caja de la Facultad de Tecnología, luego Secretaría General USFX para el título definitivo.",
        "contact_info": "Kardista de tu carrera + Secretaría General USFX: (4) 6454200 int. 100",
        "cost_details": "Bs. 1800.00 aprox hasta 5000.00. bs dependiendo de la carrera — pagar en Caja de la Facultad. Incluye valores universitarios.",
        "duration_details": "Hasta 30 días hábiles desde la presentación en Caja. El título final es emitido por Director de Carrera USFX.",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "Ingrese y acceda a SUNIVER (https://si2.usfx.bo/suniver/web/Cuenta/security/login). Vaya a Trámites y seleccione la solicitud de Diploma Académico. Elija si desea el Diploma Académico y Título en Provisión Nacional simultáneamente (considere costos). Lea los requisitos. No podrá iniciar otros trámites simultáneos. El sistema validará sus datos; si hay errores, subsánelos. Si aplica, seleccione la mención/título específico de su carrera. Seleccione (declare cumplimiento) los requisitos. Revise, acepte y continúe. Imprima el formulario y la carta de solicitud (hoja oficio) y preséntelos en Caja para obtener los valores universitarios.
",
        "requirements": [
            {"step_number": 1, "title": "Fotocopia legalizada del Diploma Académico", "document_name": "Diploma Académico legalizado", "is_mandatory": True, "notes": "Debe estar legalizado por la USFX antes de tramitar el título"},
            {"step_number": 2, "title": "Fotocopia simple del Certificado de Nacimiento", "document_name": "Copia Certificado Nacimiento", "is_mandatory": True},
            {"step_number": 3, "title": "Fólder universitario", "document_name": "Fólder universitario", "is_mandatory": True},
            {"step_number": 4, "title": "3 fotografías 4×4 fondo rojo", "document_name": "3 fotos 4×4 fondo rojo", "is_mandatory": True},
            {"step_number": 5, "title": "Valores universitarios", "document_name": "Valores universitarios", "is_mandatory": True},
            {"step_number": 6, "title": "Sobre para fotografías", "document_name": "Sobre", "is_mandatory": True},
        ],
        "video_tutorial_url": "https://www.tiktok.com/@kenia191911/video/7464983718151687429?is_from_webapp=1&sender_device=pc&web_id=7611253499893286421"
        
    },
    {
        "code": "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION",
        "name": "Trámite Simultáneo: Diploma + Título en Provisión",
        "description": "Permite obtener el Diploma Académico y el Título en Provisión Nacional al mismo tiempo, ahorrando tiempo y trámites. Requiere los documentos combinados de ambos trámites.",
        "category": "titulacion",
        "duration_days": 30,
        "cost": 1.00,
        "applies_to": "all",
        "order_index": 13,
        "icon": "academic-cap",
        "office_location": "Central General USFX. Proceso inicia en SUNIVER.",
        "contact_info": "Kardista de tu carrera + Secretaría General: averiguar",
        "cost_details": "Bs. averiguar aprox. — pagar en Caja de la Facultad.",
        "duration_details": "Hasta 30 días hábiles. La Solvencia Universitaria tiene solo 48 horas de validez. Coordiná bien los plazos.",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "Entrar con tu cuenta y contraseña a SUNIVER https://si2.usfx.bo/suniver . Ir a Trámites → Solicitud de simultaneo.  El sistema validará tus datos; si hay errores, subsánalos. Selecciona (declara cumplimiento) los requisitos. Revisa, acepta y continúa. Imprime el formulario y la carta de solicitud (hoja oficio) y preséntalos en Caja para obtener los valores universitarios.",
        "requirements": [

            {"step_number": 1, "title": " Cédula de Identidad vigente (copia simple) o Pasaporte legalizado (extranjeros).", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 2, "title": "Diploma de Bachiller legalizado por autoridad competente o, si es del exterior, legalizado por consulado, Ministerio de Relaciones Exteriores o apostillado y homologado por SEDUCA.", "document_name": "Diploma de Bachiller legalizado", "is_mandatory": True},
            {"step_number": 3, "title": "Solvencia Universitaria debidamente llenada", "document_name": "Solvencia Universitaria", "is_mandatory": True, "notes": "Tiene 48 horas de validez desde la primera firma"},
            {"step_number": 4, "title": "Un Sobre para el carnet universitario y fotografías.", "document_name": "Sobre", "is_mandatory": True},
            {"step_number": 5, "title": "Fotocopia simple del Certificado de Nacimiento.", "document_name": "Copia Certificado Nacimiento", "is_mandatory": False},
            {"step_number": 6, "title": "Valores Universitarios.", "document_name": "Valores universitarios", "is_mandatory": True},
            {"step_number": 7, "title": "Papel valorado y valores para la certificación del juramento de Ley.", "document_name": "Papel valorado y valores", "is_mandatory": True},
            {"step_number": 8, "title": "Certificado de Nacimiento original actualizado (extranjeros: legalizado por consulado de origen y RR.EE. o apostillado).", "document_name": "Certificado de Nacimiento", "is_mandatory": True},
            {"step_number": 9, "title": "Fólder Universitario.", "document_name": "Fólder universitario", "is_mandatory": True},
            {"step_number": 10, "title": "Certificado de Conclusión de Estudios.", "document_name": "Certificado de conclusión", "is_mandatory": False},
            {"step_number": 11, "title": """Certificados de notas originales (cursos, plan de estudios, N° materias, kardex firmado). Cursos en el exterior: Calificaciones originales legalizadas por consulado boliviano y RR.EE. o apostilladas. Convalidaciones: Adjuntar trámite original (o reposición).""", "document_name": "Certificados de notas", "is_mandatory": True},
            {"step_number": 12, "title": "Carnet universitario vigente.", "document_name": "Carnet universitario", "is_mandatory": True},
            {"step_number": 13, "title": "Funda plástica tamaño oficio.", "document_name": "Funda plástica", "is_mandatory": True},
            {"step_number": 14, "title": "Seis fotografías idénticas y actuales a color 4×4 con (fondo rojo).", "document_name": "6 fotos 4x4 fondo rojo", "is_mandatory": True},
        ],
        "video_tutorial_url": "https://www.tiktok.com/@kenia191911/video/7464983718151687429?is_from_webapp=1&sender_device=pc&web_id=7611253499893286421"
        
    },
    {
        "code": "PROCESO_MATRICULACION_WEB",
        "name": "Matriculación en el Sistema Web (SUNIVER)",
        "description": "Guía paso a paso para completar el proceso de matrícula en la plataforma universitarios.usfx.bo o si2.usfx.bo/suniver. Solo para estudiantes regulares.",
        "category": "matricula",
        "duration_days": 2,
        "cost": 103.50,
        "applies_to": "all",
        "order_index": 14,
        "icon": "computer-desktop",
        "office_location": "El proceso es completamente en línea. Si hay problemas con el sistema, consultá con tu kardista o el soporte técnico de SUNIVER.",
        "contact_info": "Soporte Tecnico dtic.soporte@usfx.bo | averiguar, telegram info sunniver",
        "cost_details": "El proceso web en sí es gratuito. El pago de matrícula se realiza vía depósito bancario o QR según el monto generado por el sistema.",
        "duration_details": "El proceso es al instante en línea por QR. El depósito bancario puede tardar hasta 4 horas en reflejarse en el sistema. y maximo 1 o 2 semanas para que se actualice con la matrícula reflejada. Fecha inicio de matriculacion: fuera de plazo. Fecha fin: fuera de plazo.
        ",
        "web_system_url": "https://universitarios.usfx.bo",
        "web_instructions": "1. Ingresá a universitarios.usfx.bo con tu usuario y contraseña SUNIVER. 2. Menú Matrículas → Matricularme. 3. El sistema generará el importe a pagar. 4. Elegí modalidad: Depósito en Banco Unión Cta. 1-33340493 (UMSFX – REC. PROPIOS – MATRÍCULAS) o Pago con QR (confirmación inmediata). 5. Si pagaste con depósito, registrá el número de papeleta en el sistema. 6. Verificá en Matrículas → Mis Matrículas.",
        "requirements": [
            {"step_number": 1, "title": " Accede al sistema (https://si2.usfx.bo/suniver/web/Cuenta/security/login) con tu usuario y contraseña.", "description": "Si no recuerdas recuperalo con tu CI y CU", "is_mandatory": True},
            {"step_number": 2, "title": "Ve a «Matrículas» y selecciona «Matricularme».", "is_mandatory": True},
            {"step_number": 3, "title": "Elige la modalidad de pago: Depósito Bancario o Pago QR.", "description": "Depósito Bancario: Deposita en Banco Unión y registra el código de la papeleta. Pago QR: Genera el QR en el sistema y paga. El proceso es automático.", "is_mandatory": True},
            {"step_number": 4, "title": "⚠ Importante: No se aceptan transferencias bancarias (son diferentes al Pago QR).", "is_mandatory": True},
            {"step_number": 5, "title": "La confirmación del pago es inmediata con Pago QR, mientras que con Depósito Bancario puede tardar hasta 4 horas.", "is_mandatory": True},
            {"step_number": 6, "title": "Verifica tu matrícula en «Matrículas», submenú «Mis Matrículas».", "is_mandatory": True},
            
        ],
        "video_tutorial_url": "https://www.youtube.com/watch?v=AbDdxYpFhCE&t=93s"
        
    },
    {
        "code": "PROCESO_PROGRAMACION_ACADEMICA",
        "name": "Programación Académica de Materias",
        "description": "Proceso para inscribir las materias del semestre en el sistema SUNIVER. Requiere tener matrícula vigente y, para programación manual ir con el kardex.",
        "category": "academico",
        "duration_days": 1,
        "cost": 0.00,
        "applies_to": "all",
        "order_index": 15,
        "icon": "calendar",
        "office_location": "El proceso es online (si2.usfx.bo/suniver). Para programación manual ve con el kardista",
        "contact_info": "Kardista de tu carrera. Soporte Tecnico dtic.soporte@usfx.bo para problemas con el sistema.",
        "cost_details": "Trámite gratuito.",
        "duration_details": "El proceso online es inmediato. Para programación manual con el kardista puedes tardar media hora o menos. Fecha inicio de programación: fuera de plazo. Fecha fin: fuera de plazo.",
        "web_system_url": "https://si2.usfx.bo/suniver",
        "web_instructions": "1. Ingresá a si2.usfx.bo/suniver con tu usuario y contraseña. 2. Verificá tener matrícula activa primero. 3. Menú Programaciones → Programarme. 4. Si tu carrera tiene programación automática: el sistema asigna las materias según tu avance. 5. Si es manual: seleccioná las materias habilitadas según tu kardex. 6. Confirmá y verificá en Programaciones → Mis Programaciones.",
        "requirements": [
            {"step_number": 1, "title": "Matrícula vigente del semestre actual", "description": "Debés estar matriculado antes de poder programar materias", "is_mandatory": True},
            {"step_number": 2, "title": "Acceso al Sistema", "description": "Ingresa a https://si2.usfx.bo/suniver/web/Cuenta/security/login con tu usuario y contraseña.": True},
            {"step_number": 3, "title": "Iniciar Programación", "description": "En el menú derecho, selecciona «Programaciones» y luego «Programarme».", "is_mandatory": True},
            {"step_number": 4, "title": "Tipo de Programación", "description": "Automática: Si tu carrera lo permite, el sistema te guiará paso a paso. Manual: Consulta el kardex de tu facultad para saber qué materias puedes programar según tu avance académico.", "is_mandatory": True},
            {"step_number": 5, "title": "Finalización", "description": "Revisa cuidadosamente la información ingresada y confirma tu programación.", "is_mandatory": True},
            {"step_number": 6, "title": "Verificación", "description": "Corrobora que tu programación se haya registrado correctamente en «Programaciones» → «Mis Programaciones». Si hay errores, contacta a tu kardista o soporte técnico de SUNIVER.", "is_mandatory": True},
        ],
        {"video_tutorial_url": "https://www.tiktok.com/@ce_chat_gpt_usfx/video/7534737440221760774?q=programacion%20usfx&t=1774725843810"}
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
        "office_location": "Calle: Colon No 474, Lugar: Seguro Social Universitario Estudiantil",
        "contact_info": "Número Piloto: 161, 6453135. 64 49659 y 64 49660",
        "cost_details": "Completamente gratuito para estudiantes activos de la USFX con matrícula vigente.",
        "duration_details": "Las citas se programan online: lunes a viernes 7:30 am para consultas en la tarde del mismo dia y de 13:30 pm para el turno de la mañana del dia siguiente. Llegá 15 minutos antes de tu cita.",
        "web_system_url": "https://ssu-sucre.org/ficha",
        "web_instructions": "1. Ingresá a ssu-sucre.org/ficha. 2. Clic en EMITIR FICHA ESTUDIANTIL. 3. Ingresá tu número de carnet universitario y contraseña SUNIVER. 4. Seleccioná la fecha de consulta deseada. 5. Elegí la especialidad médica (hay 18 disponibles). 6. Seleccioná el horario disponible y confirmá. 7. Guardá o imprimí tu ficha. 8. Presentate puntualmente con el Carnet Universitario.",
        "requirements": [
          """ 
                    Acceda a la web del Seguro Social Universitario (https://www.ssu-sucre.org/inicio) o directamente al enlace de fichas (https://www.ssu-sucre.org/ficha).
                    Haga clic en «Adquirir ficha» y luego en <<EMITIR FICHA ESTUDIANTIL>>.
                    Complete el formulario con sus datos, incluyendo Carnet Universitario, Contraseña y la Fecha de Consulta.
                    Elija una de las 18 especialidades.
                    Seleccione el horario disponible y confirme su cita.
  
          """
            {"step_number": 1, "title": "Página web", "description": "Acceda a la web del Seguro Social Universitario (https://www.ssu-sucre.org/inicio) o directamente al enlace de fichas (https://www.ssu-sucre.org/ficha).", "is_mandatory": True},
            {"step_number": 2, "title": "Adquirir ficha", "description": "Haga clic en «Adquirir ficha» y luego en <<EMITIR FICHA ESTUDIANTIL>>.", "is_mandatory": True},
            {"step_number": 3, "title": "Completar formulario", "description": "Complete el formulario con sus datos, incluyendo Carnet Universitario, Contraseña y la Fecha de Consulta.", "is_mandatory": True},
            {"step_number": 4, "title": "Elegir especialidad", "description": "Elija una de las 18 especialidades disponibles según su necesidad médica.", "is_mandatory": True},
            {"step_number": 5, "title": "Seleccionar horario y confirmar", "description": "Seleccione el horario disponible para la especialidad elegida y confirme su cita.", "is_mandatory": True},
            {"step_number": 6, "title": "Guardar ficha", "description": "Guarde o imprima su ficha de cita para presentarla el día de la consulta.", "is_mandatory": True},
            {"step_number": 7, "title": "Presentarse con carnet universitario", "description": "Llegue puntualmente a su cita médica con su Carnet Universitario vigente. Sin él no se brinda atención.", "is_mandatory": True},
        ],
        "video_tutorial_url": "https://www.youtube.com/watch?v=3cCERO2koJM"
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
