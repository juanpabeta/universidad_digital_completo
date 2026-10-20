# Módulo 11 de 12. DevOps y despliegue profesional

## Clase 4. Tutoría: validación de pipelines CI/CD reales

**Duración propuesta:** 180 minutos, siguiendo la duración de las clases del módulo. **Punto de partida:** la Clase 3 dejó el workflow `backend-cicd.yml`, una API en Railway y PostgreSQL remoto; esta tutoría verifica su comportamiento y refactoriza condiciones. Si un estudiante todavía no completó el despliegue, trabaja con sus ejecuciones de GitHub y documenta de forma explícita qué parte remota no se pudo comprobar. El backend académico se recibe terminado; esta sesión no lo reconstruye.

**Objetivos.** Demostrar con ejecuciones reales qué dispara cada trabajo, provocar y reparar fallos controlados, diferenciar un fallo legítimo de una configuración incorrecta, personalizar los disparadores y las condiciones sin abrir rutas de despliegue inseguras, y comparar un workflow redactado manualmente con una propuesta generada por IA mediante criterios verificables.

| Minutos | Tutoría y práctica | Resultado observable |
|---|---|---|
| 0–20 | Línea base de GitHub y Railway | Commit y despliegue identificados. |
| 20–65 | Fallo controlado de test, reparación | `test` rojo; `build` y `deploy` omitidos; nuevo run verde. |
| 65–95 | Desencadenadores y condiciones | PR y ejecución manual comparados. |
| 95–125 | Diagnóstico de fallo de configuración sin revelar secretos | Matriz de síntoma, causa, evidencia y remedio. |
| 125–160 | Refactorización y comparación con IA | Diff comentado y decisión argumentada. |
| 160–180 | Validación final y evaluación | Evidencias y plan de reversión. |

## 1. Establecer una línea base verificable

Abra **Actions → Backend CI/CD** y elija una ejecución exitosa de `main`. Anote el identificador corto del commit, la hora, el evento `push`, la duración y el resultado de `test`, `build` y `deploy`. En Railway abra el despliegue correspondiente; observe la tarea previa, el arranque y el healthcheck. Lea `/health/live`, `/health/ready` y `/docs` sobre el dominio HTTPS. Un código HTTP 200 de `/health/live` solo indica que FastAPI responde; `/health/ready` además consulta PostgreSQL. La ejecución de GitHub, el estado de Railway y la respuesta remota deben corresponder a un cambio que usted pueda identificar, no solo a una captura antigua.

Construya la siguiente matriz de expectativas antes de modificar nada:

| Cambio o evento | `test` | `build` | `deploy` | Motivo |
|---|---|---|---|---|
| Pull request hacia `main` con cambio en `backend/` | Sí | Sí si pasa test | No | El PR propone código; no publica. |
| Push en `main` con cambio en `backend/` | Sí | Sí si pasa test | Sí si ambos pasan | Rama aprobada. |
| Push en `main` solo en `docs/` | No | No | No | El filtro `paths` no coincide. |
| Run workflow en `main`, `deploy=false` | Sí | Sí si pasa test | No | Comprobación manual segura. |
| Run workflow en `main`, `deploy=true` | Sí | Sí si pasa test | Sí | Publicación manual explícita. |
| Run workflow en rama de trabajo, `deploy=true` | Sí | Sí si pasa test | No | La condición exige `main`. |

Observe que `needs` controla dependencias entre trabajos y `if` decide si un trabajo es elegible. Una omisión intencional figura como **skipped**, no como error. `concurrency` agrupa ejecuciones por rama; `cancel-in-progress: false` evita cancelar automáticamente una ejecución activa. En un proyecto con varias ramas, esto no equivale a una cola global de migraciones. Discuta qué cambiaría antes de aceptar despliegues de varias ramas al mismo entorno.

## 2. Simular un fallo de pruebas sin tocar datos reales

Desde un clon local del repositorio cree una rama temporal `tutoria/fallo-pruebas` y un archivo nuevo `backend/tests/test_fallo_controlado.py` con este contenido:

```python
def test_fallo_controlado() -> None:
    assert 2 + 2 == 5, "Fallo didáctico deliberado"
```

Haga commit, push de la rama y abra un pull request hacia `main`. Revise la ejecución asociada. Esperado: `test` falla en esa prueba, `build` queda omitido porque depende de `test` y `deploy` queda omitido por la condición de pull request, además de depender de trabajos exitosos. No haga merge de la rama con el fallo. Quite el archivo didáctico, haga otro commit en la misma rama y empuje: ahora `test` y `build` deben quedar en verde, mientras `deploy` sigue omitido. Compare los dos runs y capture la línea exacta que explica el primer fallo. Cierre el PR o fusione únicamente después de confirmar que no contiene el fallo; elimine la rama temporal conforme a la política del curso.

Este experimento modifica solo código de prueba en una rama. No borra bases, volúmenes, usuarios ni notas académicas. Para verificar las condiciones de despliegue, compare las ejecuciones sin sabotear credenciales ni desconectar la base remota. Si el curso exige una demostración de fallo de despliegue, utilice un entorno de staging separado y datos desechables, con su propio token y servicio.

## 3. Personalizar eventos y condiciones con intención

Abra `.github/workflows/backend-cicd.yml`. Identifique los filtros `branches: [main]`, `paths`, la casilla manual `inputs.deploy` y la condición de `deploy`. La primera personalización consiste en agregar un disparador programado para **probar sin publicar**. GitHub ejecuta `schedule` desde la rama predeterminada y las expresiones cron usan UTC. Antes de cambiar el archivo, explique por qué el `if` actual omite deploy para ese evento. Agregue bajo `on`:

```yaml
  schedule:
    - cron: "0 13 * * 1"
```

La expresión corre los lunes a las 13:00 UTC, que corresponde a las 08:00 de Bogotá mientras Colombia mantenga UTC−5. `test` y `build` se ejecutarán; `deploy` quedará omitido por la condición que solo autoriza `push` o `workflow_dispatch` en `main`. En GitHub Actions las ejecuciones programadas pueden retrasarse o descartarse bajo carga; no basaría una tarea de seguridad crítica en su puntualidad exacta. El `schedule` hace una ejecución futura, así que valide inmediatamente con **Run workflow** y revise la sintaxis del YAML. Si la tutoría no requiere ejecuciones semanales posteriores, retire el disparador en el mismo PR después de la demostración.

La segunda personalización es un control opcional de entorno para organizaciones que dispongan de esa función: configure `railway-production` en **Settings → Environments**, limite ramas a `main` y establezca aprobación si el plan lo permite; añada `environment: railway-production` al trabajo `deploy` y mueva allí `RAILWAY_TOKEN`. Compruebe las posibilidades reales del tipo de repositorio y plan GitHub antes de activarlo: algunas protecciones no están disponibles para repositorios privados en todos los planes. Conserve el secreto de repositorio del ejercicio base mientras verifica la nueva configuración y retírelo cuando el secreto de entorno funcione. La revisión humana sería una compuerta adicional a `needs` y `if`, no una sustitución.

No agregue `pull_request_target` para ejecutar cambios de un PR con el token de despliegue, no entregue `RAILWAY_TOKEN` al trabajo `test`, y no oculte pruebas rojas con `continue-on-error: true`. Revise los efectos de `paths`: si un cambio solamente actualiza `docs/`, no habrá un run de push; un disparador `schedule` no cumple el mismo propósito de validar un PR.

## 4. Diagnosticar un fallo de configuración con evidencia

Sin modificar secretos reales, analice tres situaciones del docente. Para cada una complete **síntoma → evidencia → hipótesis → comprobación → cambio mínimo → nuevo run**. Caso A: `test` falla por `AssertionError`; compare el código cambiado y el resultado local con `python -m pytest -q`. Caso B: Railway construye la imagen, pero el pre-deploy falla con error de conexión; revise referencias `DB_HOST` y demás variables en el servicio API, estado de PostgreSQL y log de Alembic sin copiar contraseñas. Caso C: Railway muestra API activa, pero el smoke test no llega al dominio; compruebe `RAILWAY_API_URL`, dominio generado, HTTPS, `/health/live` y `/health/ready`. Un 401 de un endpoint protegido tiene un diagnóstico distinto de un 503 de readiness.

La persona tutora debe evitar convertir cada error en “reiniciar todo”. Si un log muestra `ModuleNotFoundError`, revise contexto del build y archivos copiados. Si muestra `NOT_AUTHENTICATED`, confirme existencia y alcance del Project Token mediante los paneles, sin imprimir el valor en terminal. Si el healthcheck remoto devuelve 500, consulte el log de la API y del servicio PostgreSQL. Documente qué observación descartaría la primera hipótesis antes de cambiar archivos. Nunca utilice `docker compose down -v` para “reparar” un incidente remoto: ese comando afecta un volumen local y no corrige Railway.

## 5. Comparar un workflow manual con otro generado por IA

Prepare un prompt a una herramienta de IA que incluya **solo** el nombre de los trabajos, un fragmento del YAML sin secretos y los requisitos: PR debe correr test y build; `main` debe desplegar tras ambos; manual solo con casilla; permisos mínimos; proyecto y servicio explícitos; verificación HTTPS. Solicite un YAML alternativo y un argumento por decisión. Guarde el resultado propuesto en un archivo local fuera de `.github/workflows/`, por ejemplo `docs/propuesta_ia.yml`, para que no sea ejecutado automáticamente. No añada secretos, identificadores de cuenta personal o logs sin limpiar al prompt.

Compare ambas versiones con una matriz:

| Criterio | Evidencia que debe buscar |
|---|---|
| Seguridad | Secretos solo en deploy; `contents: read`; nada en el Dockerfile. |
| Control de errores | `needs`, salidas no cero y smoke test que pueda fallar. |
| Eventos | PR sin deploy; push main; manual con casilla y rama. |
| Integridad del backend | Contexto `./backend`; Python 3.12; pruebas reales. |
| Railway | Project Token, proyecto y servicio correctos, entorno, pre-deploy. |
| Legibilidad | Nombres de pasos, indentación, comentarios que explican decisiones. |
| Evidencia | Se comparan runs y endpoints, no promesas del modelo. |

Una propuesta de IA puede verse más corta porque omitió migración, pruebas o condición de rama. Rechácela por el requisito incumplido, no por haber sido generada por IA. Si su mejora es concreta, llévela a un PR, confirme sintaxis y comportamiento con un run real, y registre qué cambió y por qué. Una revisión humana y la evidencia del pipeline deciden la incorporación.

## 6. Cierre de la tutoría

Entregue: dos enlaces de ejecuciones GitHub (fallida y corregida), captura de la dependencia que omitió `build`, tabla de eventos con resultados observados o pendientes, fragmento del diff de una personalización, una matriz comparativa manual/IA, estado del servicio Railway y respuestas de `live` y `ready` si hubo despliegue. La evaluación prioriza causalidad: la persona debe demostrar por qué se activó o no cada trabajo, identificar el paso exacto del error y comprobar la corrección sin revelar credenciales. Si la red, el plan o una cuenta impidió completar una validación remota, describa el impedimento comprobable y no marque la API como desplegada.

**Referencias para resolver dudas.** [GitHub: eventos](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [condiciones](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [entornos](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), [seguridad](https://docs.github.com/en/actions/reference/security/secure-use); [Railway: CLI up](https://docs.railway.com/cli/up), [logs](https://docs.railway.com/cli/logs), [healthchecks](https://docs.railway.com/deployments/healthchecks). Los criterios de fiabilidad, seguridad y mantenibilidad se alinean con ISO/IEC 25010:2023 como guía de calidad, sin presumir certificación.
