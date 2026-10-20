# Universidad Digital

Material base del Módulo 11. La carpeta `backend/` contiene la API completa que los estudiantes reciben **antes** de la Clase 1 de Docker. El cuaderno de la clase explica y practica la contenerización; no dedica sus tres horas a implementar los dominios académicos.

La estructura y las siete entidades provienen de `01_Modulo_9_Semana_1.ipynb`: Usuario, Rol, Usuario Rol, Materia, Período Académico, Inscripción y Calificación. Para hacer verificable la autorización docente, el MVP agrega `materias.id_docente` como asignación de un docente responsable por materia. El frontend React descrito allí queda fuera de este paquete: el Módulo 11 lo tratará en una clase posterior.

Abra [backend/README.md](backend/README.md) para instalación, dominios, endpoints, migraciones, pruebas y límites de este MVP.

Las Clases 3 y 4 incluyen el flujo real en `.github/workflows/backend-cicd.yml`, una comprobación remota en `backend/scripts/check_deployment.py` y sus cuadernos en `docs/`. Lea [la guía de CI/CD y Railway](docs/GUIA_CICD_RAILWAY.md) antes de configurar cuentas, variables y despliegue. El servicio remoto no se crea con el paquete: cada estudiante lo configura con sus propias cuentas.

Las Clases 5 y 6 agregan el frontend React completo en [`frontend/`](frontend/README.md), con login, pantallas por rol y conexión a la API. Los cuadernos de despliegue y auditoría están en `docs/`. El trabajo de clase comienza con el frontend ya desarrollado; se concentra en Vercel y la validación integral.

Cuadernos: [`Clase 5`](docs/Modulo_11_Clase_5_Vercel_Frontend_Universidad_Digital.ipynb) y [`Clase 6`](docs/Modulo_11_Clase_6_Tutoria_Auditoria_Produccion.ipynb). El proyecto de clase usa datos sintéticos; ningún dominio remoto o cuenta de proveedor se incluye en el paquete.
