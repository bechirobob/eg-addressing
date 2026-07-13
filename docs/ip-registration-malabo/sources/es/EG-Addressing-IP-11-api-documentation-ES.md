# Documentación de API

## Control del documento

Título: Documentación de API
Producto: Sistema Nacional de Direccionamiento Digital
Fundador responsable: Benjamin Bob Bechiro
Empresa: BeCorps
Tipo de documento: Manual técnico
Estado: Documento de soporte para preparación de registro de propiedad intelectual en Malabo.

## Finalidad

Este documento resume la superficie API como evidencia de integración, control de acceso y alcance funcional.

## Familias de API

- Autenticación y sesión.
- Usuarios y administración de personal.
- Provincias, unidades administrativas y territorios.
- Carreteras, edificios, direcciones y registros oficiales.
- Geotagging ciudadano, correcciones y seguimiento.
- Evidencia de campo, revisión, publicación, reportes, exportaciones y auditoría.

## Endpoints representativos

- GET /
- GET /api/v1/health
- GET /api/v1/meta
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- POST /api/v1/auth/logout
- GET /api/v1/admin/users
- POST /api/v1/admin/users
- PATCH /api/v1/admin/users/{user_id}
- POST /api/v1/admin/users/{user_id}/disable
- POST /api/v1/admin/users/{user_id}/revoke-sessions
- GET /api/v1/territories/provinces
- GET /api/v1/provinces
- GET /api/v1/admin-units
- GET /api/v1/public/territory-options
- GET /api/v1/territories
- GET /api/v1/territories/{territory_id}
- POST /api/v1/territories
- PATCH /api/v1/territories/{territory_id}
- DELETE /api/v1/territories/{territory_id}
- GET /api/v1/audit-logs
- GET /api/v1/roads
- GET /api/v1/roads/{road_id}
- POST /api/v1/roads
- PATCH /api/v1/roads/{road_id}
- DELETE /api/v1/roads/{road_id}
- GET /api/v1/buildings
- GET /api/v1/buildings/{building_id}
- POST /api/v1/buildings
- PATCH /api/v1/buildings/{building_id}
- DELETE /api/v1/buildings/{building_id}
- GET /api/v1/addresses
- GET /api/v1/addresses/{address_id}
- POST /api/v1/addresses
- PATCH /api/v1/addresses/{address_id}
- DELETE /api/v1/addresses/{address_id}
- GET /api/v1/field/assignments
- GET /api/v1/field/geotag-tasks

## Controles

- Autenticación para rutas internas.
- Roles de administración, edición, visualización y revisión institucional.
- Validación de entrada y separación de datos públicos/protegidos.
- Límites de publicación controlados por aprobación.
