# Manual de arquitectura técnica

## Control del documento

Título: Manual de arquitectura técnica
Producto: Sistema Nacional de Direccionamiento Digital
Fundador responsable: Benjamin Bob Bechiro
Empresa: BeCorps
Tipo de documento: Manual técnico
Estado: Documento de soporte para preparación de registro de propiedad intelectual en Malabo.

## Finalidad

Este manual describe la arquitectura base del sistema para demostrar estructura, alcance técnico y operación coordinada de sus componentes.

## Arquitectura general

- Frontend web de administración y rutas públicas.
- Backend API para autenticación, registro, revisión, publicación, reportes y auditoría.
- Base de datos PostgreSQL/PostGIS para entidades territoriales, direcciones, usuarios y eventos.
- Redis para soporte de ejecución y servicios auxiliares.
- Almacenamiento compatible S3 para evidencias protegidas cuando aplica.

## Módulos funcionales

- Presentación ciudadana de ubicación y seguimiento de solicitudes
- Captura y revisión de evidencia de campo
- Revisión registral y registros oficiales de dirección
- Gestión de carreteras, edificios, territorios y unidades administrativas
- Gobernanza de publicación, certificados, señalización y prueba pública
- Reportes, revisión de actividad, exportaciones, auditoría y administración de acceso

## Rutas de aplicación

- /admin/staff
- /code/[code]
- /exports
- /field
- /geotag
- /issue
- /login
- /operations-runbook
- /
- /proof/[code]
- /records
- /registry
- /reports
- /signage
- /territories
- /track
- /verify

## Principios de diseño

- Modularidad primero; microservicios solo cuando el crecimiento lo justifique.
- Autorización de servidor para funciones protegidas.
- Separación entre rutas públicas y rutas internas de operador.
- Publicación oficial bloqueada hasta aprobación institucional.
