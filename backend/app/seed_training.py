"""
Seed training samples for BERT fine-tuning.
Usage: python -m app.seed_training

~17 verified examples per label × 20 labels = ~340 samples total.
All samples use natural Bolivian Spanish and cover varied phrasings,
aspects (cost, process, requirements, location) and levels of formality.

Run after `python -m app.seed`. Always re-seeds (deletes old samples first).
"""
import asyncio
from app.database import AsyncSessionLocal, engine, Base
from app.models import *  # noqa


# ---------------------------------------------------------------------------
# Dataset — (text, label) tuples
# Criteria:
#  · Natural Bolivian Spanish (vos/tú, coloquial but clear)
#  · Each label has varied phrasings: questions, keywords, full sentences
#  · Covers multiple aspects: process, cost, requirements, location, contact
#  · Includes common abbreviations and informal spelling
# ---------------------------------------------------------------------------
SAMPLES: list[tuple[str, str]] = [

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_MATRICULA_ALUMNO_NUEVO
    # ════════════════════════════════════════════════════════════════════════
    ("quiero inscribirme por primera vez en la facultad", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("soy bachiller recién y quiero entrar a la usfx", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("cómo me inscribo siendo alumno nuevo", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("qué necesito para matricularme por primera vez", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("acabo de salir del colegio y quiero estudiar ingeniería", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("requisitos para alumno de primer ingreso", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("me admitieron por preuniversitario, cómo me matriculo", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("ingresé por olimpiadas científicas, qué trámite hago", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("cuáles son los documentos para inscripción de nuevo ingreso", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("dónde presento mi diploma de bachiller para inscribirme", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("fui aceptado por mérito deportivo, cómo me matriculo", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("cuándo abren las inscripciones para nuevos estudiantes", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("qué papeles pide la facultad para ingresar por primera vez", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("tengo mi diploma de bachiller legalizado, qué sigue", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("inscripción alumnos nuevos facultad tecnología usfx", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("cómo subo mis documentos en admision.usfx.bo", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),
    ("qué fotos necesito para la inscripción como alumno nuevo", "TRAMITE_MATRICULA_ALUMNO_NUEVO"),

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_MATRICULA_ALUMNO_REGULAR
    # ════════════════════════════════════════════════════════════════════════
    ("cómo renuevo mi matrícula este semestre", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("quiero matricularme, ya cursé el año pasado", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("cuándo abre la matrícula regular para este semestre", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("tengo que renovar mi inscripción para el segundo semestre", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("qué pasos sigo para renovar matrícula", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("ya soy alumno activo, cómo me matriculo para el siguiente semestre", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("me olvidé de matricularme, aún puedo hacerlo", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("cuánto cuesta la matrícula regular en la usfx", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("la matrícula regular es gratuita o tiene costo", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("necesito verificar deudas antes de matricularme", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("qué documentos necesito para renovar matrícula", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("cuándo vence el plazo de matrícula para alumnos regulares", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("cómo sé si ya estoy matriculado este semestre", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("dónde entrego los papeles para la matrícula regular", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("proceso de matrícula para estudiante que ya cursó materias", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("formulario de matrícula regular dónde lo consigo", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),
    ("qué pasa si no me matriculo a tiempo", "TRAMITE_MATRICULA_ALUMNO_REGULAR"),

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_DIPLOMA_ACADEMICO
    # ════════════════════════════════════════════════════════════════════════
    ("cómo saco mi diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("requisitos para el diploma académico usfx", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("qué documentos necesito para tramitar el diploma", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("ya terminé todas las materias, quiero sacar el diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("cuánto tarda el diploma académico una vez presentado", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("cuánto cuesta el diploma académico en la facultad", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("dónde presento los documentos para el diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("qué es la solvencia universitaria y para qué sirve en el diploma", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("proceso para obtener el diploma académico en suniver paso a paso", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("terminé la carrera, cómo empiezo el trámite del diploma", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("cuántas fotos necesito para el diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("la solvencia universitaria vence a las 48 horas", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("necesito el certificado de conclusión de estudios para el diploma", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("dónde genero el formulario del diploma en universitarios.usfx.bo", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("cuánto vale el papel valorado para el diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("necesito legalizar mi diploma de bachiller para el trámite del diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),
    ("qué kardex necesito para sacar el diploma académico", "TRAMITE_DIPLOMA_ACADEMICO"),

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_TITULO_PROVISION_NACIONAL
    # ════════════════════════════════════════════════════════════════════════
    ("cómo tramito el título en provisión nacional", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("qué necesito para sacar el título profesional usfx", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("cuánto cuesta el título en provisión nacional", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("dónde se tramita el título en provisión nacional", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("ya tengo el diploma académico, ahora cómo saco el título", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("requisitos para título en provisión nacional usfx", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("cuánto tiempo tarda el título en provisión nacional", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("qué documentos piden para el título profesional", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("proceso para obtener título en provisión en suniver", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("necesito el título para ejercer mi profesión", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("el título en provisión se tramita después del diploma académico", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("en qué oficina presento los documentos para el título", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("qué es el fólder universitario que piden para el título", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("si2.usfx.bo tramites académicos título provisión nacional", "TRAMITE_TITULO_PROVISION_NACIONAL"),
    ("cuántas fotos fondo rojo necesito para el título profesional", "TRAMITE_TITULO_PROVISION_NACIONAL"),

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_SIMULTANEO_DIPLOMA_PROVISION
    # ════════════════════════════════════════════════════════════════════════
    ("puedo sacar el diploma y el título al mismo tiempo", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("cómo hago el trámite simultáneo diploma y título", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("requisitos para diploma y provisión al mismo tiempo", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("quiero tramitar el diploma y el título juntos para ahorrar tiempo", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("cuánto cuesta hacer el diploma y título en trámite simultáneo", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("puedo hacer diploma académico y provisión nacional a la vez", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("trámite simultáneo usfx facultad tecnología, cómo funciona", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("cuántas fotos necesito para el trámite simultáneo diploma más título", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("es mejor hacer los dos trámites juntos o separados", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("cuánto tiempo tarda el trámite simultáneo", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("qué documentos extras necesito para el trámite simultáneo", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("suniver opción trámite simultáneo diploma y título provisión", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("dónde presento los documentos para los dos títulos a la vez", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("cómo pago el trámite simultáneo en caja", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),
    ("vale la pena hacer el trámite simultáneo o es muy complicado", "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION"),

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_TITULACION
    # ════════════════════════════════════════════════════════════════════════
    ("cómo inicio el proceso de titulación en la facultad", "TRAMITE_TITULACION"),
    ("qué modalidades de titulación hay disponibles", "TRAMITE_TITULACION"),
    ("cuánto cuesta el trámite de titulación", "TRAMITE_TITULACION"),
    ("terminé todas las materias del plan de estudios, cómo me gradúo", "TRAMITE_TITULACION"),
    ("qué es el examen de grado y cómo funciona", "TRAMITE_TITULACION"),
    ("cómo hago para hacer tesis en la usfx", "TRAMITE_TITULACION"),
    ("requisitos para empezar el proceso de graduación", "TRAMITE_TITULACION"),
    ("cuánto tiempo tarda el proceso de titulación completo", "TRAMITE_TITULACION"),
    ("dónde inicio el trámite de titulación con mi kardista", "TRAMITE_TITULACION"),
    ("qué es el proyecto de grado y en qué se diferencia de la tesis", "TRAMITE_TITULACION"),
    ("ya aprobé el 100% de materias, qué sigo para graduarme", "TRAMITE_TITULACION"),
    ("cuáles son las modalidades de titulación disponibles en tecnología", "TRAMITE_TITULACION"),
    ("necesito el kardex definitivo para empezar titulación", "TRAMITE_TITULACION"),
    ("certificado de no adeudo para titulación, dónde lo consigo", "TRAMITE_TITULACION"),
    ("proceso de graduación usfx facultad tecnología paso a paso", "TRAMITE_TITULACION"),
    ("qué es el trabajo dirigido como modalidad de titulación", "TRAMITE_TITULACION"),
    ("cuándo me inscribo para la defensa de tesis", "TRAMITE_TITULACION"),

    # ════════════════════════════════════════════════════════════════════════
    # SOLICITUD_CERTIFICADO_KARDEX
    # ════════════════════════════════════════════════════════════════════════
    ("necesito mi kardex actualizado urgente", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("cómo pido el certificado de notas en la facultad", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("quiero solicitar mi historial académico oficial", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("cuánto cuesta el certificado de kardex", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("dónde pido mi kardex en la facultad de tecnología", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("necesito un certificado académico para presentar en un trabajo", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("cuánto tarda el kardex una vez solicitado", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("qué documentos presento para sacar el certificado de notas", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("necesito mi kardex para tramitar una beca externa", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("cómo solicito el certificado académico al kardista", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("el kardex tiene validez por tiempo determinado", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("necesito constancia de notas para visa o trámite exterior", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("en qué oficina pido el historial académico de mis materias", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("dónde pago el arancel para el certificado de kardex", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("qué información tiene el kardex y para qué sirve", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("solicitar kardex firmado por el kardista", "SOLICITUD_CERTIFICADO_KARDEX"),
    ("cuántos días hábiles tarda en estar listo el kardex", "SOLICITUD_CERTIFICADO_KARDEX"),

    # ════════════════════════════════════════════════════════════════════════
    # SOLICITUD_CAMBIO_CARRERA
    # ════════════════════════════════════════════════════════════════════════
    ("quiero cambiarme de carrera dentro de la facultad", "SOLICITUD_CAMBIO_CARRERA"),
    ("cómo tramito el cambio de carrera en la usfx", "SOLICITUD_CAMBIO_CARRERA"),
    ("qué necesito para cambiar de ingeniería sistemas a telecomunicaciones", "SOLICITUD_CAMBIO_CARRERA"),
    ("puedo cambiarme de carrera dentro de la misma facultad", "SOLICITUD_CAMBIO_CARRERA"),
    ("requisitos para solicitud de cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("cuánto tiempo tarda el proceso de cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("dónde presento la solicitud de cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("el cambio de carrera tiene algún costo", "SOLICITUD_CAMBIO_CARRERA"),
    ("puedo solicitar cambio de carrera en cualquier momento del año", "SOLICITUD_CAMBIO_CARRERA"),
    ("cuándo resuelven la solicitud de cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("necesito llevar mi kardex para solicitar el cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("qué carta escribo al decano para pedir cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("el consejo de facultad aprueba los cambios de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("me quiero transferir a ingeniería ambiental desde sistemas", "SOLICITUD_CAMBIO_CARRERA"),
    ("cuántos días hábiles tarda el cambio de carrera", "SOLICITUD_CAMBIO_CARRERA"),
    ("proceso para cambiarse de carrera usfx tecnología", "SOLICITUD_CAMBIO_CARRERA"),

    # ════════════════════════════════════════════════════════════════════════
    # SOLICITUD_CARRERA_SIMULTANEA
    # ════════════════════════════════════════════════════════════════════════
    ("puedo estudiar dos carreras a la vez en la usfx", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("cómo solicito carrera simultánea en la facultad de tecnología", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("qué requisitos necesito para estudiar dos carreras al mismo tiempo", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("tengo tercer año aprobado, puedo hacer carrera simultánea", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("cuánto índice académico necesito para estudiar doble carrera", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("qué es la carrera simultánea y cómo funciona en la usfx", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("proceso para inscribirse en una segunda carrera", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("requisitos de índice académico para carrera simultánea", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("cuánto tiempo tarda en aprobar la solicitud de carrera simultánea", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("dónde presento la solicitud de doble carrera", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("el trámite de carrera simultánea tiene costo", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("cómo solicito estudiar ingeniería sistemas y telecomunicaciones a la vez", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("cuándo puedo pedir la carrera simultánea, en qué semestre", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("qué porcentaje del plan de estudios necesito para doble carrera", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("el consejo de facultad tiene que aprobar la carrera simultánea", "SOLICITUD_CARRERA_SIMULTANEA"),
    ("puedo llevar materias de las dos carreras al mismo tiempo", "SOLICITUD_CARRERA_SIMULTANEA"),

    # ════════════════════════════════════════════════════════════════════════
    # SOLICITUD_REPROGRAMACIONES
    # ════════════════════════════════════════════════════════════════════════
    ("falté a mi examen parcial, puedo reprogramarlo", "SOLICITUD_REPROGRAMACIONES"),
    ("cómo solicito la reprogramación de un examen", "SOLICITUD_REPROGRAMACIONES"),
    ("me enfermé el día del parcial y no pude dar el examen, qué hago", "SOLICITUD_REPROGRAMACIONES"),
    ("qué documentos necesito para justificar mi falta al examen", "SOLICITUD_REPROGRAMACIONES"),
    ("cuántos días tengo para pedir la reprogramación después del examen", "SOLICITUD_REPROGRAMACIONES"),
    ("dónde presento la solicitud de reprogramación de examen", "SOLICITUD_REPROGRAMACIONES"),
    ("qué documentos piden para justificar una ausencia al examen", "SOLICITUD_REPROGRAMACIONES"),
    ("puedo reprogramar el examen final si tengo justificación", "SOLICITUD_REPROGRAMACIONES"),
    ("me citaron judicialmente el día del parcial, puedo reprogramar", "SOLICITUD_REPROGRAMACIONES"),
    ("el trámite de reprogramación de examen tiene costo", "SOLICITUD_REPROGRAMACIONES"),
    ("en cuántos días me dan respuesta sobre la reprogramación", "SOLICITUD_REPROGRAMACIONES"),
    ("el kardista acepta reprogramaciones sin justificación médica", "SOLICITUD_REPROGRAMACIONES"),
    ("plazo máximo para presentar solicitud de reprogramación", "SOLICITUD_REPROGRAMACIONES"),
    ("qué pasa si se me vence el plazo para reprogramar el examen", "SOLICITUD_REPROGRAMACIONES"),
    ("certificado médico para reprogramación de examen", "SOLICITUD_REPROGRAMACIONES"),
    ("proceso para reprogramar examen por enfermedad en la facultad", "SOLICITUD_REPROGRAMACIONES"),

    # ════════════════════════════════════════════════════════════════════════
    # SOLICITUD_HOMOLOGACION_MATERIAS
    # ════════════════════════════════════════════════════════════════════════
    ("cómo homologo materias aprobadas en otra universidad", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("tengo materias aprobadas en otra carrera, puedo validarlas aquí", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("qué es la homologación de materias en la usfx", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("proceso para reconocer materias de otra institución educativa", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("requisitos para solicitar homologación de materias", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("cuánto tiempo tarda la homologación de materias", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("qué documentos piden para homologar materias equivalentes", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("dónde presento la solicitud de homologación en la facultad", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("puedo homologar materias que aprobé en una universidad privada", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("qué son las equivalencias académicas y cómo se tramitan", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("la comisión académica evalúa las materias para homologar", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("el trámite de homologación tiene algún costo", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("necesito el sílabo de la materia para pedir homologación", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("cambié de carrera y quiero homologar las materias que ya aprobé", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("qué materias pueden ser homologadas entre carreras", "SOLICITUD_HOMOLOGACION_MATERIAS"),
    ("programas analíticos para homologación dónde los consigo", "SOLICITUD_HOMOLOGACION_MATERIAS"),

    # ════════════════════════════════════════════════════════════════════════
    # TRAMITE_BECAS
    # ════════════════════════════════════════════════════════════════════════
    ("cómo solicito una beca universitaria en la usfx", "TRAMITE_BECAS"),
    ("qué tipos de becas existen en la facultad de tecnología", "TRAMITE_BECAS"),
    ("requisitos para beca por excelencia académica usfx", "TRAMITE_BECAS"),
    ("cuánto índice académico necesito para solicitar la beca", "TRAMITE_BECAS"),
    ("hay becas para estudiantes con pocos recursos económicos", "TRAMITE_BECAS"),
    ("dónde presento la solicitud de beca universitaria", "TRAMITE_BECAS"),
    ("cuándo abren las convocatorias de becas en la usfx", "TRAMITE_BECAS"),
    ("qué documentos piden para la beca socioeconómica", "TRAMITE_BECAS"),
    ("cuánto tiempo dura una beca universitaria", "TRAMITE_BECAS"),
    ("la beca universitaria cubre la matrícula completa", "TRAMITE_BECAS"),
    ("tengo índice de 65 puntos, puedo solicitar beca por mérito", "TRAMITE_BECAS"),
    ("cómo sé si hay convocatoria de becas activa este semestre", "TRAMITE_BECAS"),
    ("qué pasos sigo para solicitar una beca estudiantil", "TRAMITE_BECAS"),
    ("en qué oficina de la usfx tramito la beca universitaria", "TRAMITE_BECAS"),
    ("la beca se renueva automáticamente cada semestre", "TRAMITE_BECAS"),
    ("qué es la beca por excelencia y quiénes califican", "TRAMITE_BECAS"),
    ("formulario de solicitud de beca dónde lo consigo", "TRAMITE_BECAS"),

    # ════════════════════════════════════════════════════════════════════════
    # CARNET_UNIVERSITARIO
    # ════════════════════════════════════════════════════════════════════════
    ("cómo saco mi carnet universitario por primera vez", "CARNET_UNIVERSITARIO"),
    ("perdí mi carnet universitario, cómo lo repongo", "CARNET_UNIVERSITARIO"),
    ("cuánto cuesta el carnet universitario usfx", "CARNET_UNIVERSITARIO"),
    ("qué documentos necesito para tramitar el carnet", "CARNET_UNIVERSITARIO"),
    ("dónde tramito el carnet universitario en la facultad", "CARNET_UNIVERSITARIO"),
    ("cuánto tiempo tarda en estar listo el carnet", "CARNET_UNIVERSITARIO"),
    ("mi carnet universitario está deteriorado, cómo lo renuevo", "CARNET_UNIVERSITARIO"),
    ("necesito el carnet para atenderme en el seguro universitario", "CARNET_UNIVERSITARIO"),
    ("qué fotos necesito para el carnet universitario", "CARNET_UNIVERSITARIO"),
    ("el carnet universitario tiene fecha de vencimiento", "CARNET_UNIVERSITARIO"),
    ("dónde pago el arancel para el carnet estudiantil", "CARNET_UNIVERSITARIO"),
    ("se me robaron el carnet, tengo que hacer declaración jurada", "CARNET_UNIVERSITARIO"),
    ("proceso para obtener el carnet universitario paso a paso", "CARNET_UNIVERSITARIO"),
    ("cuánto vale reponer el carnet universitario perdido", "CARNET_UNIVERSITARIO"),
    ("comprobante de matrícula vigente para el carnet dónde lo saco", "CARNET_UNIVERSITARIO"),
    ("el carnet universitario sirve como identificación oficial", "CARNET_UNIVERSITARIO"),
    ("qué tamaño de foto se usa para el carnet universitario", "CARNET_UNIVERSITARIO"),

    # ════════════════════════════════════════════════════════════════════════
    # SEGURO_SOCIAL_UNIVERSITARIO
    # ════════════════════════════════════════════════════════════════════════
    ("cómo saco ficha médica en el seguro universitario", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("qué especialidades cubre el seguro social universitario", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("cómo me atiendo en el ssu siendo estudiante de la usfx", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("cómo genero mi ficha estudiantil en ssu-sucre.org", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("dónde queda el seguro social universitario en sucre", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("necesito una cita médica, cómo la saco en el seguro universitario", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("el seguro universitario es gratuito para estudiantes activos", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("qué necesito para atenderme en el seguro estudiantil", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("cómo uso ssu-sucre.org para programar mi consulta médica", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("puedo ir al seguro universitario sin cita previa", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("qué documentos pide el ssu para darme atención médica", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("cuántas especialidades médicas tiene el seguro universitario", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("cómo accedo al seguro médico siendo estudiante de tecnología", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("necesito matrícula vigente para usar el seguro universitario", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("seguro social universitario estudiantil ssue cómo funciona", "SEGURO_SOCIAL_UNIVERSITARIO"),
    ("mi carnet universitario vence, aún puedo usar el seguro", "SEGURO_SOCIAL_UNIVERSITARIO"),

    # ════════════════════════════════════════════════════════════════════════
    # PROCESO_MATRICULACION_WEB
    # ════════════════════════════════════════════════════════════════════════
    ("cómo entro al sistema universitarios.usfx.bo para matricularme", "PROCESO_MATRICULACION_WEB"),
    ("no me deja matricular en el suniver, qué hago", "PROCESO_MATRICULACION_WEB"),
    ("cómo pago con qr en el sistema web de la usfx", "PROCESO_MATRICULACION_WEB"),
    ("ingresé el número de depósito pero no aparece mi matrícula", "PROCESO_MATRICULACION_WEB"),
    ("cómo uso si2.usfx.bo para hacer mi matrícula en línea", "PROCESO_MATRICULACION_WEB"),
    ("qué hago si el depósito bancario no aparece en el sistema", "PROCESO_MATRICULACION_WEB"),
    ("cuenta banco unión para depositar la matrícula usfx", "PROCESO_MATRICULACION_WEB"),
    ("el sistema me da error al ingresar mi usuario suniver", "PROCESO_MATRICULACION_WEB"),
    ("cómo genero el importe de pago de matrícula en el sistema", "PROCESO_MATRICULACION_WEB"),
    ("cuánto tarda en reflejarse el depósito bancario en suniver", "PROCESO_MATRICULACION_WEB"),
    ("no acepta mi papeleta de depósito en universitarios.usfx.bo", "PROCESO_MATRICULACION_WEB"),
    ("pasos para matricularse en línea en la usfx tecnología", "PROCESO_MATRICULACION_WEB"),
    ("se acepta transferencia bancaria para pagar la matrícula", "PROCESO_MATRICULACION_WEB"),
    ("olvidé mi contraseña del sistema suniver, cómo la recupero", "PROCESO_MATRICULACION_WEB"),
    ("cómo verifico que mi matrícula quedó registrada en el sistema", "PROCESO_MATRICULACION_WEB"),
    ("qr de pago de matrícula, cómo lo genero en universitarios.usfx.bo", "PROCESO_MATRICULACION_WEB"),
    ("la cuenta de banco unión para matrícula es 1-33340493", "PROCESO_MATRICULACION_WEB"),

    # ════════════════════════════════════════════════════════════════════════
    # PROCESO_PROGRAMACION_ACADEMICA
    # ════════════════════════════════════════════════════════════════════════
    ("cómo me programo en materias para este semestre", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("no me aparece la opción de programarme en suniver", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("cuándo abre el período de programación académica", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("cómo inscribo mis materias en el sistema si2.usfx.bo", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("qué diferencia hay entre programación automática y manual", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("ya me matriculé pero no puedo programar materias, qué pasa", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("cómo selecciono las materias del semestre en suniver", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("el sistema no me deja programarme, dice que no tengo matrícula", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("dónde veo mi programación académica confirmada en el sistema", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("necesito mi kardex para la programación manual de materias", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("cómo verifico que quedé programado en mis materias correctamente", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("programación de materias usfx facultad tecnología semestre", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("qué materias puedo programar según mi avance académico", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("en mi carrera la programación es automática o tengo que elegir", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("se me pasó el período de programación, qué puedo hacer", "PROCESO_PROGRAMACION_ACADEMICA"),
    ("menú programaciones programarme suniver cómo funciona", "PROCESO_PROGRAMACION_ACADEMICA"),

    # ════════════════════════════════════════════════════════════════════════
    # SALUDO_BIENVENIDA
    # ════════════════════════════════════════════════════════════════════════
    ("hola", "SALUDO_BIENVENIDA"),
    ("buenos días", "SALUDO_BIENVENIDA"),
    ("buenas tardes", "SALUDO_BIENVENIDA"),
    ("hola, necesito ayuda con un trámite", "SALUDO_BIENVENIDA"),
    ("buenas, alguien me puede orientar", "SALUDO_BIENVENIDA"),
    ("hey qué tal, tengo una pregunta", "SALUDO_BIENVENIDA"),
    ("hola buen día", "SALUDO_BIENVENIDA"),
    ("buenas noches, tengo una consulta urgente", "SALUDO_BIENVENIDA"),
    ("hola qué trámites puedo hacer aquí", "SALUDO_BIENVENIDA"),
    ("buen día, me pueden ayudar", "SALUDO_BIENVENIDA"),
    ("holi, tengo dudas sobre mi trámite", "SALUDO_BIENVENIDA"),
    ("inicio", "SALUDO_BIENVENIDA"),
    ("necesito información sobre trámites universitarios", "SALUDO_BIENVENIDA"),
    ("buenas, qué trámites atienden aquí", "SALUDO_BIENVENIDA"),
    ("hola, en qué me pueden ayudar", "SALUDO_BIENVENIDA"),

    # ════════════════════════════════════════════════════════════════════════
    # DESPEDIDA
    # ════════════════════════════════════════════════════════════════════════
    ("gracias, hasta luego", "DESPEDIDA"),
    ("chau, ya me voy", "DESPEDIDA"),
    ("adiós", "DESPEDIDA"),
    ("hasta pronto", "DESPEDIDA"),
    ("ya está, gracias y chau", "DESPEDIDA"),
    ("bye, fue de mucha ayuda", "DESPEDIDA"),
    ("nos vemos", "DESPEDIDA"),
    ("listo, ya terminé con mis consultas", "DESPEDIDA"),
    ("ya fue, muchas gracias por todo", "DESPEDIDA"),
    ("me retiro, gracias por la información", "DESPEDIDA"),
    ("chau nomás, ya entendí todo", "DESPEDIDA"),
    ("hasta luego, muy amable", "DESPEDIDA"),
    ("ok ya fue, gracias", "DESPEDIDA"),
    ("me voy, era todo lo que necesitaba saber", "DESPEDIDA"),
    ("bye bye, gracias", "DESPEDIDA"),

    # ════════════════════════════════════════════════════════════════════════
    # AGRADECIMIENTO
    # ════════════════════════════════════════════════════════════════════════
    ("muchas gracias por la información", "AGRADECIMIENTO"),
    ("gracias, me ayudaste bastante", "AGRADECIMIENTO"),
    ("mil gracias", "AGRADECIMIENTO"),
    ("grax, ya entendí lo que necesitaba", "AGRADECIMIENTO"),
    ("gracias, muy amable de tu parte", "AGRADECIMIENTO"),
    ("ok gracias, ya está claro", "AGRADECIMIENTO"),
    ("excelente, muchas gracias por explicarme", "AGRADECIMIENTO"),
    ("perfecto, gracias por la ayuda", "AGRADECIMIENTO"),
    ("genial, muchas gracias por la info", "AGRADECIMIENTO"),
    ("thanks, ya me queda claro", "AGRADECIMIENTO"),
    ("gracias, eso era lo que buscaba", "AGRADECIMIENTO"),
    ("muy útil la información, gracias", "AGRADECIMIENTO"),
    ("te agradezco mucho la ayuda", "AGRADECIMIENTO"),
    ("muy bien explicado, gracias", "AGRADECIMIENTO"),
    ("grasias, ya sé qué hacer", "AGRADECIMIENTO"),

    # ════════════════════════════════════════════════════════════════════════
    # FALLBACK
    # ════════════════════════════════════════════════════════════════════════
    ("qué es la usfx exactamente", "FALLBACK"),
    ("cuántas carreras tiene la facultad de tecnología", "FALLBACK"),
    ("quiero hablar con una persona real, no con un bot", "FALLBACK"),
    ("eso no tiene nada que ver con lo que pregunté", "FALLBACK"),
    ("asdfghjkl qwertyuiop", "FALLBACK"),
    ("no entiendo nada de lo que me dicen", "FALLBACK"),
    ("cuál es el teléfono principal de la facultad", "FALLBACK"),
    ("quiero saber sobre el decano de la facultad", "FALLBACK"),
    ("información sobre la biblioteca universitaria", "FALLBACK"),
    ("cuándo hay clases presenciales", "FALLBACK"),
    ("dónde queda la usfx en sucre", "FALLBACK"),
    ("cuánto gana un ingeniero en bolivia", "FALLBACK"),
    ("me puedes hacer la tarea de programación", "FALLBACK"),
    ("qué nota necesito para aprobar una materia", "FALLBACK"),
    ("cuándo son los exámenes finales de este semestre", "FALLBACK"),
]


async def seed_training():
    from sqlalchemy import select, delete
    from app.models.training_sample import TrainingSample

    async with AsyncSessionLocal() as db:
        # Delete all existing samples to start fresh
        existing_count = await db.execute(
            select(TrainingSample).limit(1)
        )
        has_existing = existing_count.scalar_one_or_none() is not None

        if has_existing:
            await db.execute(delete(TrainingSample))
            await db.commit()
            print("Existing samples deleted. Re-seeding...")

        print(f"Seeding {len(SAMPLES)} training samples...")
        for text, label in SAMPLES:
            sample = TrainingSample(
                text=text,
                label=label,
                source="manual",
                verified=True,
            )
            db.add(sample)

        await db.commit()

    # Summary
    from collections import Counter
    counts = Counter(label for _, label in SAMPLES)
    print(f"\nDone! {len(SAMPLES)} verified samples seeded.\n")
    print(f"{'Label':<45} {'Muestras':>8}")
    print("-" * 55)
    for label, count in sorted(counts.items()):
        print(f"  {label:<43} {count:>8}")
    print("-" * 55)
    print(f"  {'TOTAL':<43} {len(SAMPLES):>8}")


if __name__ == "__main__":
    asyncio.run(seed_training())
