# Backend de Universidad Digital

Para las Clases 3 y 4 de CI/CD, utilice el workflow `../.github/workflows/backend-cicd.yml` y la guía `../docs/GUIA_CICD_RAILWAY.md`. Railway ejecuta las migraciones y el bootstrap como comando previo al despliegue; PostgreSQL remoto se configura por referencias `DB_*` en el servicio API. El `compose.yaml` de esta carpeta corresponde a la práctica local de la Clase 1.

API FastAPI con PostgreSQL 18, SQLAlchemy 2, Pydantic 2 y Alembic. Es el **material previo** de la Clase 1 del Módulo 11. Las capas por dominio están en `app/auth`, `users`, `subjects`, `periods`, `enrollments`, `grades` y `reports`; `app/core` contiene configuración, conexión, hashing, tokens y errores. Las rutas delegan las reglas y transacciones a `services.py`.

## Requisitos y arranque con Docker

Instale Docker Desktop y confirme `docker version` y `docker compose version`. Desde esta carpeta:

```powershell
Copy-Item .env.example .env
# Abra .env y cambie DB_PASSWORD, JWT_SECRET y ADMIN_PASSWORD.
docker compose config
docker compose up --build -d
docker compose ps
docker compose exec api python -m app.bootstrap
```

Abra <http://127.0.0.1:8000/docs>. Verifique <http://127.0.0.1:8000/health/live> y <http://127.0.0.1:8000/health/ready>. `migrate` ejecuta Alembic una vez después de que PostgreSQL reporte estado saludable; `api` espera a que esa tarea termine correctamente. La base no publica el puerto 5432 en el equipo anfitrión; se accede mediante `docker compose exec db psql -U universidad -d universidad`. El volumen `pgdata` mantiene datos entre reinicios.

`docker compose down` detiene y elimina contenedores, conservando el volumen. **`docker compose down -v` borra el volumen y los datos locales.** No ejecute esta última orden para una demostración con datos que deba conservar.

El comando de bootstrap crea los tres roles fijos y el primer administrador con los valores de `ADMIN_EMAIL` y `ADMIN_PASSWORD`; es idempotente si el usuario ya existe. No registre claves reales en Git ni comparta `.env`. El backend no se conecta a una cuenta externa ni despliega en Railway o Vercel durante esta clase.

## Primer recorrido en Swagger

1. Abra `POST /api/v1/auth/token`. En el campo `username` use `ADMIN_EMAIL` y en `password` use `ADMIN_PASSWORD`. Copie el token en el botón **Authorize** de Swagger. También puede usar la ventana de autorización OAuth2 del propio Swagger.
2. Cree un usuario docente y uno estudiante con `POST /api/v1/users`, con `roles: ["DOCENTE"]` y `roles: ["ESTUDIANTE"]` respectivamente. Las contraseñas tienen al menos 12 caracteres.
3. Cree una materia (`POST /api/v1/subjects`) asignando `id_docente` al docente. Cree un período abierto (`POST /api/v1/periods`) cuyas fechas incluyan el día actual.
4. Autentíquese como estudiante y cree una inscripción. Autentíquese como docente asignado y registre una nota de 0 a 100. Consulte `GET /api/v1/reports/periods/{period_id}/subjects` como docente o administrador.

Las respuestas de usuario omiten `password_hash`. El navegador no debe guardar el bearer token en `localStorage`; el mecanismo seguro para el frontend se tratará al implementarlo. Este paquete solo contiene backend.

## Contrato y reglas de dominio

| Dominio | Rutas principales | Regla principal |
|---|---|---|
| Auth | `POST /api/v1/auth/token` | Verificación de contraseña Argon2 y JWT con expiración. |
| Usuarios | `GET /users/me`, administración de usuarios y roles | Solo ADMINISTRADOR crea y administra cuentas. |
| Materias | CRUD con desactivación lógica | Código único; docente asignado activo y con rol DOCENTE. |
| Períodos | Crear, consultar y actualizar | Fecha final no anterior a inicial; estado ABIERTO o CERRADO. |
| Inscripciones | Crear, consultar y cancelar | Estudiante activo; materia activa; período abierto y vigente; unicidad estudiante materia período. |
| Calificaciones | Crear, consultar, actualizar y borrar | Nota 0–100; docente asignado o administrador escribe; estudiante solo lee las suyas. |
| Reportes | Resumen por materia y período | Administrador ve todas las materias; docente solo las asignadas. |

El diseño fuente del Módulo 9 no incluía un vínculo entre materia y docente. `id_docente` es una extensión explícita del MVP para hacer cumplir autorización por asignación. Una materia tiene un docente responsable en esta versión; una oferta con secciones y varios docentes requeriría otra entidad. La cancelación de inscripciones es lógica. No se incluyen auditoría de cambios de notas, recuperación de contraseña, renovación o revocación de tokens, limitación de intentos de login, matrícula por cupos, ni notificaciones; deben diseñarse antes de usar el software con datos institucionales reales.

## Ejecución local sin Docker

Use PostgreSQL 18 disponible localmente y cree un rol y una base acordes con las variables `DB_*` de `.env`. En Windows, dentro de `backend/`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
# Cambie DB_HOST=localhost y las contraseñas de .env.
alembic upgrade head
python -m app.bootstrap
python -m uvicorn app.main:app --reload
```

`alembic upgrade head` crea el esquema; la aplicación no llama `Base.metadata.create_all` durante el arranque. El único `create_all` está en las pruebas con una base SQLite desechable. El archivo `requirements.lock` fija dependencias para construir la imagen Linux de la clase; `requirements.txt` declara rangos para trabajo local.

## Pruebas y diagnóstico

Con el entorno de desarrollo activo: `python -m pytest -q`. Las pruebas usan SQLite en memoria, ejercitan autenticación, permisos, materia, período, inscripción, notas y reporte. No sustituyen una prueba integral con PostgreSQL y Docker: antes de un despliegue real debe ejecutarse también esa integración.

Comandos de laboratorio: `docker build -t universidad-api:clase1 .`, `docker image ls`, `docker run --rm universidad-api:clase1 python --version`, `docker compose up --build -d`, `docker compose ps`, `docker compose logs -f api`, `docker compose logs migrate`, `docker compose exec db psql -U universidad -d universidad`. Para comprobar las variables sin revelar secretos use `docker compose config --quiet`. En PowerShell, `Invoke-RestMethod http://127.0.0.1:8000/health/ready` devuelve la disponibilidad de la conexión.

Si `api` no inicia, consulte primero los logs de `db` y `migrate`; `depends_on` y el healthcheck evitan iniciar la API antes de la migración, pero no reparan una contraseña incorrecta. Si la respuesta es 401, revise autenticación y expiración. Un 403 indica que el usuario autenticado no tiene el rol o asignación requerida. Un 409 indica una regla de negocio o unicidad. No vuelque `.env` ni tokens completos en capturas o prompts a una IA.

## Archivos de contenedores

`Dockerfile` instala dependencias bloqueadas antes de copiar código para aprovechar la caché, ejecuta con un usuario sin privilegios y arranca en el puerto de `PORT` o 8000. `.dockerignore` excluye entorno local, pruebas y credenciales. `compose.yaml` define API, migración de una sola ejecución, PostgreSQL 18, un healthcheck y un volumen persistente. En PostgreSQL 18 el volumen oficial se monta en `/var/lib/postgresql`, conforme a la documentación de la imagen.

La ejecución de `docker build` y `docker compose` requiere Docker en el equipo del estudiante. Las pruebas de API y sintaxis fueron ejecutadas antes de entregar el paquete; no se afirma que un despliegue externo ya esté realizado.
