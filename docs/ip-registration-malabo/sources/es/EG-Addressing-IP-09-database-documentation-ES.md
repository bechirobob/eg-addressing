# Documentación de base de datos

## Control del documento

Título: Documentación de base de datos
Producto: Sistema Nacional de Direccionamiento Digital
Fundador responsable: Benjamin Bob Bechiro
Empresa: BeCoreOps
Tipo de documento: Manual técnico
Estado: Documento de soporte para preparación de registro de propiedad intelectual en Malabo.

## Finalidad

Este documento resume las entidades persistentes, relaciones operativas y reglas de conservación que sostienen el sistema.

## Tablas identificadas

- address_corrections
- address_points
- address_record_events
- address_records
- addresses
- admin_units
- audit_logs
- auth_tokens
- buildings
- citizen_geotag_submissions
- field_assignments
- field_submissions
- import_jobs
- import_rows
- provinces
- publication_pack_addresses
- publication_packs
- roads
- territories
- users

## Dominios de datos

- Usuarios, sesiones y roles internos.
- Provincias, unidades administrativas, territorios, carreteras y edificios.
- Direcciones candidatas y registros oficiales.
- Correcciones ciudadanas y evidencias de campo.
- Paquetes de publicación, certificados, señalización, reportes y auditoría.

## Reglas de datos

- Los datos sensibles no se exponen en rutas públicas.
- Los identificadores internos se mantienen separados de la presentación ciudadana cuando sea necesario.
- La publicación oficial requiere revisión y bloqueo de aprobación.
- La auditoría conserva eventos de acción, actor, entidad y detalle operativo.
