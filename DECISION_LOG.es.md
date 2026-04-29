# Registro de Decisiones Técnicas

Decisiones tomadas durante el diseño e implementación del proyecto.

---

## 1. Arquitectura: Clean Architecture en lugar de MVC

**Decisión:** Clean Architecture de tres capas (Dominio → Aplicación → Infraestructura).

**Justificación:**
- La capa de dominio tiene **cero dependencias de frameworks** — las entidades e interfaces de repositorios son dataclasses y ABCs de Python puro. Esto permite testearlos sin levantar ningún servicio de I/O.
- Los casos de uso codifican las reglas de negocio una sola vez, independientemente del mecanismo de entrega (REST hoy, gRPC o CLI mañana).
- Cambiar PostgreSQL por otra base de datos, o FastAPI por otro framework, solo requiere modificar la capa de Infraestructura.

**Desventaja:** Más archivos y más indirección que una estructura MVC plana. Vale la pena a cualquier escala donde el dominio no es trivial y la testeabilidad importa.

---

## 2. Base de datos: PostgreSQL sobre SQLite / MongoDB

**Decisión:** PostgreSQL 16 con SQLAlchemy 2.x (async) + migraciones con Alembic.

**Justificación:**
- Cumplimiento ACID, tipado fuerte e integridad referencial (claves foráneas con `ON DELETE CASCADE/SET NULL`) encajan naturalmente con los datos relacionales de tareas y usuarios.
- SQLAlchemy 2.x con `asyncpg` ofrece I/O verdaderamente asíncrono sin los problemas de drivers síncronos envueltos en thread pools.
- Alembic provee migraciones reproducibles y revisables — crítico en pipelines de CI/CD.

**Desventaja:** Más pesado de levantar localmente que SQLite. Se mitiga con el `docker-compose.yml` incluido.

---

## 3. Autenticación: JWT sin estado en lugar de sesiones

**Decisión:** JWT con algoritmo HS256 vía `python-jose`, hashing de contraseñas con `passlib[bcrypt]`.

**Justificación:**
- Los tokens sin estado funcionan sin un almacén de sesiones compartido — ideal para escalar horizontalmente (múltiples réplicas del servicio `app` en `docker-compose.prod.yml`).
- bcrypt es el estándar de la industria para hashear contraseñas; su factor de coste ajustable permite adaptarse a mejoras de hardware.

**Desventaja:** La revocación de tokens requiere ya sea expiración corta + refresh tokens, o una denylist (por ejemplo, Redis). Esta implementación usa tokens de vida corta; los refresh tokens son el paso natural siguiente.

---

## 4. Porcentaje de completitud: calculado en consulta, no almacenado

**Decisión:** `completion_percentage` se calcula en cada llamada a `GET /tasks` mediante dos consultas `COUNT`.

**Justificación:**
- Almacenar un porcentaje cacheado exigiría actualizarlo en cada cambio de estado de una tarea — una carga de sincronización que añade complejidad sin beneficio medible para tamaños típicos de listas.
- Dos consultas `COUNT` sobre columnas indexadas son sub-milisegundo. Optimizar antes de tiempo (vistas materializadas, triggers) agregaría complejidad sin beneficio observable.

**Desventaja:** Para listas con millones de tareas, la pre-agregación sería preferible. Una migración futura puede añadir un job en background o un trigger de BD si fuera necesario.

---

## 5. Docker: build multistage con imagen de runtime sin root

**Decisión:** Tres stages — `builder`, `development`, `runtime`.

**Justificación:**
- `builder`: instala `build-essential` y todas las dependencias de Python en un entorno virtual aislado.
- `development`: extiende builder, instala dependencias de desarrollo, monta el código fuente como volumen — habilita hot-reload.
- `runtime`: parte de una imagen limpia `python:3.12-slim`, copia solo el venv y el código fuente. Sin herramientas de compilación, sin deps de desarrollo, sin usuario root. La imagen final pesa ~200 MB menos que un build naïve en un solo stage.
- La instrucción `HEALTHCHECK` permite que Docker y los orquestadores (ECS, Kubernetes) detecten contenedores en mal estado automáticamente.

---

## 6. Dos archivos Compose: dev vs. prod

**Decisión:** `docker-compose.yml` (desarrollo) + `docker-compose.prod.yml` (producción).

**Justificación:**
- Desarrollo necesita hot-reload, Adminer (GUI de BD), puerto de PostgreSQL expuesto y credenciales de dev hardcodeadas — nada de esto tiene lugar en producción.
- Producción necesita límites de recursos, cantidad de réplicas, Nginx como reverse proxy/terminador TLS, logging estructurado y secretos inyectados vía variables de entorno (nunca commiteados).
- Separarlos evita la proliferación de feature flags en un solo archivo y deja claro qué configuraciones son específicas de cada entorno.

---

## 7. Notificaciones simuladas (sin email real)

**Decisión:** `NotificationService` registra un evento estructurado en lugar de llamar a un endpoint SMTP/SES.

**Justificación:**
- Una integración de email real (SES, SendGrid) requiere credenciales externas y acceso a la red, convirtiendo un test unitario/de integración en un test end-to-end con efectos secundarios externos.
- El log estructurado (`structlog`) es observable en tests y en staging. En producción, reemplazar `logger.info(...)` por una llamada HTTP asíncrona al proveedor de email es un cambio localizado en un solo archivo.

---

## 8. Estrategia de testing: unitario + integración, BD real para integración

**Decisión:** Los tests unitarios mockean los repositorios; los tests de integración corren contra una BD PostgreSQL de prueba real con rollback de transacción por test.

**Justificación:**
- El mockeo en tests unitarios aísla la lógica de negocio del I/O, haciéndolos rápidos y deterministas.
- Los tests de integración que hablan con una BD real detectan problemas que los mocks ocultan (mapeo de enums, violaciones de constraints, correctitud de queries).
- El rollback por `SAVEPOINT` mantiene los tests independientes y rápidos sin necesidad de truncar tablas entre ejecuciones.

**Desventaja:** Los tests de integración requieren una instancia de PostgreSQL activa. El `docker-compose.yml` incluido y el service container de GitHub Actions eliminan esta fricción en la práctica.

---

## 9. Pydantic v2 para schemas de API, dataclasses para entidades de dominio

**Decisión:** `BaseModel` de Pydantic se usa solo en la capa de Infraestructura (API); las entidades de dominio son `@dataclass` puras.

**Justificación:**
- Las entidades de dominio no deben depender de Pydantic (ni de ningún framework). Usar dataclasses mantiene el dominio portable.
- Pydantic v2 es la herramienta correcta en el borde de la API: coerción automática de JSON, generación de schemas OpenAPI y mensajes de error de validación listos para usar.

---

## 10. CI/CD: GitHub Actions con estrategia de matrix

**Decisión:** Tres jobs — `lint`, `test` (con servicio de postgres), `docker build`.

**Justificación:**
- Los fallos de linter son baratos de detectar y no deberían bloquear PRs silenciosamente.
- Correr los tests contra un contenedor de servicio PostgreSQL real (no mockeado) refleja el comportamiento en producción.
- Hacer el build de la imagen Docker en CI garantiza que el Dockerfile siempre está en estado compilable, no solo "funciona en mi máquina".
- `docker/build-push-action` con caché de GHA (`cache-from/to: type=gha`) hace que los builds repetidos sean rápidos.

---

## 11. Documentación protegida con HTTP Basic Auth

**Decisión:** `/docs`, `/redoc` y `/openapi.json` se sirven manualmente con una dependencia `HTTPBasic`. La exposición automática que hace FastAPI de estas rutas se deshabilita (`docs_url=None`, `redoc_url=None`, `openapi_url=None`).

**Justificación:**
- El schema OpenAPI expone la superficie completa de la API — cada endpoint, cada forma de request/response, cada código de error. Dejarlo público equivale a entregarle a un atacante un mapa detallado del servicio.
- HTTP Basic Auth añade una barrera liviana pero efectiva: los navegadores solicitan credenciales automáticamente, y las rutas protegidas responden `401 + WWW-Authenticate: Basic` ante un fallo.
- Se usa `secrets.compare_digest` en lugar de una comparación `==` directa para prevenir ataques de enumeración de credenciales basados en tiempo de respuesta (timing attacks).
- Las credenciales se configuran vía `DOCS_USERNAME` / `DOCS_PASSWORD` en el archivo de entorno, por lo que pueden rotarse sin ningún cambio de código.

**Valores por defecto:** `admin` / `admin` para desarrollo. Estos **deben** cambiarse antes de cualquier despliegue. El `.env.prod.example` los marca como `CHANGE_ME`.

**Desventaja:** HTTP Basic Auth transmite las credenciales en cada request (codificadas en Base64, sin cifrado propio). Esto es aceptable cuando el servicio está detrás de TLS (el Nginx del compose de producción gestiona la terminación TLS). Para un entorno zero-trust, bloquear `/docs` y `/redoc` directamente en Nginx es una opción aún más robusta.
