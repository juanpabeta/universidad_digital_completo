# Universidad Digital: guía operativa de GitHub Actions y Railway

Este proyecto parte del backend completo distribuido en la Clase 1. El flujo `.github/workflows/backend-cicd.yml` ejecuta `test → build → deploy → smoke`. Los eventos de pull request hacen pruebas y construcción; un push que modifica el backend en `main` hace además un despliegue; la ejecución manual solo despliega si se activa el campo `deploy`, desde `main`. El frontend y Vercel pertenecen a otra clase.

## Preparación local y repositorio

Compruebe `git --version`. En Windows, si falta Git, descargue Git for Windows de <https://git-scm.com/install/windows>, ejecute el instalador, mantenga las opciones predeterminadas para el laboratorio, cierre y reabra PowerShell y confirme `git --version`. Cree una cuenta en <https://github.com/signup> y verifique su correo. En GitHub cree un repositorio **vacío** llamado `universidad-digital`: sin README, `.gitignore` ni licencia inicial, pues el paquete ya trae archivos. Seleccione la visibilidad conforme a la política docente. En la carpeta `universidad-digital` ejecute, reemplazando usuario y dirección:

```powershell
git init -b main
git config user.name "Nombre Apellido"
git config user.email "correo@ejemplo.com"
git status --short
git add .
git status --short
git commit -m "Proyecto Universidad Digital y CI/CD"
git remote add origin https://github.com/USUARIO/universidad-digital.git
git push -u origin main
```

Antes del commit confirme que **`.env` no aparece** en `git status --short`; está en `.gitignore`. GitHub puede solicitar autenticación mediante el navegador. Nunca pegue una contraseña de GitHub como si fuera el token de Railway. Si ya existe un repositorio, trabaje en ese clon y copie los cambios a su estructura; no reinicialice ni sobrescriba historia existente. Para una clase con repositorio previo, cree primero una rama y abra un pull request.

## Railway: servicio y base de datos

Registre una cuenta en <https://railway.com/> y compruebe en el panel las condiciones vigentes del plan y consumo. Cree un proyecto nuevo y seleccione el entorno `production` o el nombre que haya elegido para su laboratorio. Agregue una base **PostgreSQL** desde `+ New → Database → PostgreSQL`. Espere a que el servicio indique disponibilidad. Agregue **otro servicio vacío** (`+ New → Empty Service`) y llámelo `universidad-api`. No vincule este servicio API al repositorio mediante auto deploy: este material utiliza GitHub Actions y `railway up` como único disparador de publicación.

Abra el servicio API → **Variables**. Cree estas variables mediante el editor y aplique los cambios pendientes; si el servicio PostgreSQL se llama distinto de `Postgres`, reemplace el nombre en cada referencia:

| Variable del servicio API | Valor en el panel de Railway | Finalidad |
|---|---|---|
| `DB_HOST` | `${{Postgres.PGHOST}}` | Red privada de PostgreSQL. |
| `DB_PORT` | `${{Postgres.PGPORT}}` | Puerto de PostgreSQL. |
| `DB_NAME` | `${{Postgres.PGDATABASE}}` | Nombre de la base. |
| `DB_USER` | `${{Postgres.PGUSER}}` | Usuario de la base. |
| `DB_PASSWORD` | `${{Postgres.PGPASSWORD}}` | Contraseña, mediante referencia de servicio. |
| `JWT_SECRET` | Cadena aleatoria exclusiva de al menos 32 caracteres | Firma de tokens del backend. |
| `ADMIN_EMAIL` | Correo de laboratorio controlado por el estudiante | Administrador inicial. |
| `ADMIN_PASSWORD` | Contraseña exclusiva de al menos 12 caracteres | Bootstrap inicial. |
| `CORS_ORIGINS` | Origen permitido del frontend; durante esta clase puede quedar `http://localhost:5173` | No equivale a autenticación. |

Las referencias se insertan con el selector de variables del servicio PostgreSQL o como expresiones del panel. No copie la URL pública de PostgreSQL ni coloque contraseñas en GitHub. `PORT` lo proporciona Railway; `app.run` escucha en `0.0.0.0` y en ese puerto. En **Settings → Deploy**, configure **Pre-deploy Command** como `sh -c 'alembic upgrade head && python -m app.bootstrap'` y **Healthcheck Path** como `/health/ready`. La migración debe terminar antes de iniciar la nueva API; el bootstrap es idempotente al existir el usuario, pero no cambia su contraseña si después modifica `ADMIN_PASSWORD`. Para esa rotación se requiere un procedimiento de cuentas separado. En **Networking**, genere un dominio público HTTPS para la API. Anote su URL sin ruta final, por ejemplo `https://mi-api.up.railway.app`.

No se incluye `railway.json`: la configuración anterior se establece desde el panel. Railway advierte que su Config as Code anterior está deprecado en favor de Infrastructure as Code; no convierta ejemplos antiguos de internet en instrucciones normativas para esta clase.

## Token y variables de GitHub

En Railway abra **Project Settings → Tokens** y genere un **Project Token** para el entorno elegido; cópielo una sola vez. En GitHub abra el repositorio → **Settings → Secrets and variables → Actions**. En **Secrets** cree `RAILWAY_TOKEN` con ese token. En **Variables** cree `RAILWAY_PROJECT_ID` y `RAILWAY_SERVICE_ID` con los identificadores exactos del proyecto y servicio API que aparecen en Railway, y `RAILWAY_API_URL` con el dominio HTTPS de la API, sin barra final. Las variables no contienen contraseñas. Si el entorno no se llama `production`, modifique también el valor `--environment production` del workflow para que coincida con el alcance del Project Token.

Los secretos de GitHub no se entregan a pull requests de forks; además, este workflow solo llama al paso de deploy en `main`. Si su plan y tipo de repositorio permiten protección de entornos, puede convertir el trabajo `deploy` en un entorno protegido y mover allí el secreto, después de comprobar la disponibilidad de esa función en GitHub. Para evitar dobles publicaciones, mantenga el servicio API como **Empty Service** sin conexión GitHub auto deploy.

## Comprobación real

En GitHub abra **Actions → Backend CI/CD**. El primer push a `main` ejecuta `test`, `build` y `deploy`; observe cada trabajo y sus logs. En Railway abra el servicio API → **Deployments** y confirme que la migración previa, el bootstrap y el healthcheck terminaron. Abra `https://SU-DOMINIO/health/live`, `https://SU-DOMINIO/health/ready` y `/docs`. `ready` debe devolver `{"database":"ready"}`. El script del último paso del workflow verifica automáticamente `live` y `ready` durante un máximo aproximado de dos minutos. La API conserva datos en el PostgreSQL remoto; no depende del volumen local de Docker Compose.

Si `test` falla, `build` y `deploy` se omiten. Si `build` falla, `deploy` se omite. Si `deploy` o el smoke test fallan, lea los logs de Actions y Railway y confronte ID, token, variables del servicio, pre-deploy, dominio y puerto. No incluya valores de secretos en evidencias ni solicitudes a herramientas de IA. Ningún resultado puede darse por desplegado hasta que un estudiante configure sus cuentas y vea el estado correcto en ambos paneles.

## Referencias mantenidas por los proveedores

GitHub: <https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax>, <https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets>, <https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments>. Railway: <https://docs.railway.com/cli/up>, <https://docs.railway.com/databases/postgresql>, <https://docs.railway.com/deployments/healthchecks>, <https://docs.railway.com/deployments/pre-deploy-command>, <https://docs.railway.com/variables>.
