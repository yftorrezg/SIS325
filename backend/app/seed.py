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
        "requirements": [
            {"step_number": 1, "title": "Formulario de solicitud", "description": "Llenar el formulario de solicitud de carnet universitario en secretaría de la facultad", "document_name": "Formulario carnet", "is_mandatory": True},
            {"step_number": 2, "title": "Fotocopia de CI", "document_name": "Fotocopia CI", "is_mandatory": True},
            {"step_number": 3, "title": "2 fotos carnet actualizadas", "description": "Dos fotografías tamaño carnet actualizadas con fondo blanco", "document_name": "Fotos carnet", "is_mandatory": True},
            {"step_number": 4, "title": "Comprobante de matrícula vigente", "description": "Presentar comprobante de estar matriculado en el semestre actual", "document_name": "Comprobante de matrícula", "is_mandatory": True},
            {"step_number": 5, "title": "Pago de arancel", "description": "Cancelar el arancel de carnet en tesorería", "document_name": "Comprobante de pago", "is_mandatory": True, "notes": "En caso de extravío o deterioro, adjuntar declaración jurada"},
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
