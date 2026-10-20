# Frontend de Universidad Digital

Aplicación React/Vite del sistema académico ya implementada para las Clases 5 y 6 del Módulo 11. Usa los endpoints reales del backend (`/api/v1/...`). El estudiante recibe este código **antes** de iniciar la Clase 5: la actividad de tres horas consiste en configurarlo, publicarlo y conectarlo, no en programar sus pantallas.

## Funciones incluidas

| Rol | Secciones y operaciones visibles |
|---|---|
| Administrador | Login, directorio y creación de usuarios, roles y estado; materias, períodos, inscripciones, calificaciones y reportes. |
| Docente | Materias y períodos, inscripciones asignadas, registro y edición de calificaciones de sus materias, reportes. |
| Estudiante | Materias y períodos, inscripción y cancelación propias, consulta de sus notas. |

Las decisiones de permisos se ejecutan otra vez en la API. La navegación del cliente solo mejora la experiencia: no constituye una barrera de autorización. La API devuelve 401/403/409 y el cliente presenta el mensaje sin revelar trazas. El token de acceso se guarda solo en memoria; recargar la página o cerrar sesión obliga a autenticarse de nuevo. El backend aún no ofrece recuperación de contraseña, revocación, renovación de token ni auditoría de cambios de notas: el conjunto es una demostración académica, no un sistema listo para datos institucionales reales. Las listas solicitan hasta 100 registros por página; una institución grande requiere paginación y búsqueda.

## Instalación local

Instale Node.js desde <https://nodejs.org/en/download> y elija una versión compatible con Vite 7 (Node 20.19+ o 22.12+; se sugiere una rama LTS actual). En Windows, descargue el instalador oficial correspondiente a su arquitectura, ejecútelo, mantenga habilitada la integración con PATH, cierre y vuelva a abrir PowerShell. Confirme `node --version` y `npm --version`. En macOS/Linux siga el instalador o gestor recomendado por Node para su sistema. No instale Vite de forma global: `npm ci` instala las dependencias del proyecto desde `package-lock.json`.

En `frontend/`, copie el ejemplo y levante la aplicación:

```powershell
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Abra <http://127.0.0.1:5173>. Para esta modalidad la API debe estar accesible en `http://127.0.0.1:8000`; si está en Compose, `backend/compose.yaml` ya publica ese puerto. En `backend/.env` añada `http://127.0.0.1:5173` al valor de `CORS_ORIGINS` junto con los otros orígenes necesarios (separados por comas), y reinicie el servicio API. En macOS/Linux use `cp .env.example .env.local`. La URL local es pública en el navegador; el archivo no contiene claves.

## Build de producción y Vercel

`vite.config.js` falla de forma explícita si una compilación de producción no tiene `VITE_API_BASE_URL` con prefijo `https://`. Para ensayar el build local, copie `.env.production.example` a `.env.production`, reemplace `https://SU-API.up.railway.app` por el dominio real de la API y ejecute `npm run build` y `npm run preview`. `.env.production` se ignora en Git para que cada entorno use su propia URL. La variable `VITE_API_BASE_URL` queda incrustada en el JavaScript del navegador: **no es un secreto**; jamás ponga JWT, contraseña o `DATABASE_URL` en una variable `VITE_`.

En Vercel importe el mismo repositorio GitHub que contiene el backend. Seleccione **Root Directory = `frontend`**, Framework Preset **Vite**, Install Command `npm ci`, Build Command `npm run build` y Output Directory `dist`. En **Environment Variables** cree `VITE_API_BASE_URL` para **Production**, con el origen HTTPS de Railway sin barra final; si usará **Preview**, defina también un destino adecuado para Preview y autorice el origen exacto de la vista previa en la API. `frontend/vercel.json` envía las rutas internas de React a `index.html` para admitir navegación directa y recarga en `/grades`, `/subjects`, etc.

Después del primer despliegue, copie el dominio de producción Vercel, por ejemplo `https://universidad-digital.vercel.app`, y agréguelo como origen exacto a `CORS_ORIGINS` en el servicio API de Railway, separado por comas de los anteriores. Aplique los cambios para que Railway cree la revisión del servicio. Pruebe login desde el dominio Vercel. Si cambia `VITE_API_BASE_URL`, debe generar un nuevo build y despliegue en Vercel: el valor ya quedó incorporado al bundle anterior. Si cambia CORS en Railway, debe aplicar y desplegar la configuración allí. `http://localhost:5173` no equivale a `http://127.0.0.1:5173`; autorice el origen que realmente muestra el navegador.

Para una vista previa de GitHub, Vercel suele generar un dominio distinto: agregue expresamente ese origen a `CORS_ORIGINS` para la prueba o conecte Preview a un backend de staging. No utilice `*` con credenciales ni copie tokens a variables públicas. El token en memoria es una simplificación del laboratorio; para cuentas reales se debe diseñar y revisar un esquema completo de sesión y protección ante ataques del navegador.

## Estructura

`src/api/client.js` centraliza HTTP y errores; `src/auth/AuthContext.jsx` mantiene el usuario y la sesión; `src/pages/` agrupa pantallas por dominio; `src/components/` contiene estructura y elementos reutilizables; `src/hooks/useResource.js` administra carga, errores y recarga. `vite.config.js` define el build; `vercel.json` soporta rutas de SPA. `package-lock.json` asegura instalaciones reproducibles con `npm ci`.

## Diagnóstico

Si el build informa que falta `VITE_API_BASE_URL`, configure la variable en el entorno correcto y vuelva a desplegar. Si la página carga pero el login informa que no puede conectarse, abra **DevTools → Network** y revise la URL del `POST /api/v1/auth/token`, código, CORS y estado de `/health/ready` en Railway. Un error CORS requiere un origen exacto en el backend; un 401 generalmente indica credenciales inválidas; un 403 indica rol o asignación insuficiente. Si una ruta como `/reports` funciona desde un enlace pero da 404 al recargar, compruebe `vercel.json` y que Root Directory sea `frontend`. No publique capturas que muestren contraseñas, headers Authorization o tokens.

Fuentes: <https://vite.dev/guide/env-and-mode>, <https://vercel.com/docs/frameworks/frontend/vite>, <https://vercel.com/docs/git>, <https://vercel.com/docs/environment-variables>.
