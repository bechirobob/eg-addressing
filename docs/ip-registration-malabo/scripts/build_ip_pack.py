#!/usr/bin/env python3
"""Build bilingual Malabo IP registration documentation PDFs."""
from __future__ import annotations

import base64
import html
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/ip-registration-malabo"
SRC = OUT / "sources"
HTML = OUT / "html"
PDF = OUT / "pdf"
BUNDLE = ROOT / "artifacts/ip-registration-malabo/EG-Addressing-Malabo-IP-Documentation-Pack.zip"
CHROME = "/usr/bin/google-chrome"
COAT = ROOT / "apps/admin-portal/public/eg-coat-of-arms.svg"

FOUNDER_EN = "Benjamin Bob Bechiro"
FOUNDER_ES = "Benjamin Bob Bechiro"
COMPANY = "BeCoreOps"
PRODUCT_EN = "National Digital Addressing System"
PRODUCT_ES = "Sistema Nacional de Direccionamiento Digital"


def clean_svg() -> str:
    raw = COAT.read_text(encoding="utf-8")
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    raw = re.sub(r"<metadata.*?</metadata>", "", raw, flags=re.S)
    raw = re.sub(r"\s(?:sodipodi|inkscape|dc|cc|rdf):[\w-]+=(['\"]).*?\1", "", raw)
    raw = re.sub(r"\s+xmlns:(?:sodipodi|inkscape|dc|cc|rdf)=(['\"]).*?\1", "", raw)
    return "data:image/svg+xml;base64," + base64.b64encode(raw.strip().encode("utf-8")).decode("ascii")


def project_inventory() -> dict[str, list[str]]:
    routes = []
    app_root = ROOT / "apps/admin-portal/app"
    for p in sorted(app_root.glob("**/page.tsx")):
        rel = p.relative_to(app_root)
        route = "/" + str(rel.parent).replace("\\", "/")
        route = route.replace("/.", "/").rstrip("/") or "/"
        routes.append(route)
    api_text = (ROOT / "services/api/app/main.py").read_text(encoding="utf-8")
    endpoints = [f"{m.group(1).upper()} {m.group(2)}" for m in re.finditer(r"@app\.(get|post|patch|delete)\('([^']+)'", api_text)]
    db_text = (ROOT / "services/api/app/db.py").read_text(encoding="utf-8")
    tables = sorted(set(re.findall(r"CREATE TABLE IF NOT EXISTS ([a-z_]+)", db_text)))
    modules = [
        "Citizen location submission and address tracking",
        "Field evidence capture and review",
        "Registry review and official address records",
        "Road, building, territory, and administrative-unit management",
        "Publication governance, certificates, signage, and public proof",
        "Reports, activity review, exports, audit logging, and access administration",
    ]
    return {"routes": routes, "endpoints": endpoints, "tables": tables, "modules": modules}


INV = project_inventory()

CSS = """
@page { size: A4; margin: 17mm 18mm 18mm 18mm; }
:root { --navy:#0d2f4f; --blue:#174f82; --ink:#14202b; --muted:#51616f; --paper:#ffffff; }
* { box-sizing: border-box; }
html, body { margin:0; padding:0; }
body { background: var(--paper); color: var(--ink); font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 10.4pt; line-height: 1.58; }
.sheet { width:100%; min-height:260mm; background: transparent; }
.cover { min-height:246mm; display:flex; flex-direction:column; page-break-after: always; }
.cover-main { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:20mm 9mm 18mm; }
.crest { width:32mm; margin:0 auto 8px; }
.crest img { display:block; width:100%; height:auto; }
.republic { margin:0; text-transform:uppercase; letter-spacing:.12em; font-weight:850; font-size:9pt; color:var(--blue); }
.platform { margin:2mm 0 21mm; color:var(--muted); font-weight:650; }
.eyebrow { margin:0 0 8mm; text-transform:uppercase; letter-spacing:.12em; color:var(--navy); font-weight:850; font-size:8.5pt; }
h1.cover-title { max-width:155mm; margin:0; color:var(--navy); font-size:28pt; line-height:1.06; font-weight:850; letter-spacing:-.035em; }
.subtitle { max-width:145mm; margin:8mm auto 0; color:var(--muted); font-size:11.2pt; line-height:1.65; }
.cover-footer { padding:7mm 8mm 0; display:flex; justify-content:space-between; color:var(--muted); font-size:9pt; gap:9mm; }
.content { padding:0 1mm 4mm; }
section { break-inside: avoid-page; page-break-inside: avoid; margin-bottom:8mm; }
section + section { margin-top:6mm; }
h1,h2,h3 { color:var(--navy); font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; break-after:avoid; page-break-after:avoid; line-height:1.2; }
h1 { font-size:21pt; margin:0 0 7mm; }
h2 { font-size:15pt; margin:0 0 4.5mm; padding-bottom:1mm; }
h3 { font-size:11.8pt; margin:5mm 0 2mm; color:var(--blue); }
p { margin:0 0 3.2mm; }
ul,ol { margin:0 0 4mm 7mm; padding-left:6mm; }
li { margin-bottom:1.35mm; padding-left:1mm; }
strong { color:var(--navy); }
.meta p { display:grid; grid-template-columns:42mm minmax(0,1fr); column-gap:5mm; margin-bottom:2.4mm; }
.meta strong,.meta span { display:block; min-width:0; }
.small { color:var(--muted); font-size:9pt; }
.footer-note { margin-top:9mm; padding-top:4mm; color:var(--muted); font-size:8.8pt; }
"""


def e(s: str) -> str:
    return html.escape(s, quote=True)


def md_escape(s: str) -> str:
    return s


def doc_control(lang: str, title: str, doc_type: str) -> list[tuple[str, str]]:
    if lang == "es":
        return [
            ("Título", title),
            ("Producto", PRODUCT_ES),
            ("Fundador responsable", FOUNDER_ES),
            ("Empresa", COMPANY),
            ("Tipo de documento", doc_type),
            ("Estado", "Documento de soporte para preparación de registro de propiedad intelectual en Malabo."),
        ]
    return [
        ("Title", title),
        ("Product", PRODUCT_EN),
        ("Responsible founder", FOUNDER_EN),
        ("Company", COMPANY),
        ("Document type", doc_type),
        ("Status", "Supporting document for intellectual-property registration preparation in Malabo."),
    ]


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {x}" for x in items)


def numbered(items: list[str]) -> str:
    return "\n".join(f"{i}. {x}" for i, x in enumerate(items, 1))


def common_sections(lang: str, title: str, doc_type: str, purpose: str, sections: list[tuple[str, list[str] | str]]) -> str:
    lines = [f"# {title}", "", "## Document Control" if lang == "en" else "## Control del documento", ""]
    for k, v in doc_control(lang, title, doc_type):
        lines.append(f"{k}: {v}")
    lines += ["", "## Purpose" if lang == "en" else "## Finalidad", "", purpose, ""]
    for heading, body in sections:
        lines += [f"## {heading}", ""]
        if isinstance(body, str):
            lines += [body, ""]
        else:
            lines += [bullets(body), ""]
    return "\n".join(lines).strip() + "\n"


ENDPOINT_SAMPLE = INV["endpoints"][:38]
ROUTE_SAMPLE = INV["routes"]
TABLES = INV["tables"]
MODULES = INV["modules"]
MODULES_ES = [
    "Presentación ciudadana de ubicación y seguimiento de solicitudes",
    "Captura y revisión de evidencia de campo",
    "Revisión registral y registros oficiales de dirección",
    "Gestión de carreteras, edificios, territorios y unidades administrativas",
    "Gobernanza de publicación, certificados, señalización y prueba pública",
    "Reportes, revisión de actividad, exportaciones, auditoría y administración de acceso",
]

DOCS: list[dict[str, str]] = []

def add(slug: str, es_title: str, en_title: str, es_type: str, en_type: str, es_purpose: str, en_purpose: str, es_sections, en_sections):
    DOCS.append({"slug": slug, "lang": "es", "title": es_title, "doc_type": es_type, "purpose": es_purpose, "body": common_sections("es", es_title, es_type, es_purpose, es_sections)})
    DOCS.append({"slug": slug, "lang": "en", "title": en_title, "doc_type": en_type, "purpose": en_purpose, "body": common_sections("en", en_title, en_type, en_purpose, en_sections)})

add(
"00-corporate-readiness",
"Paquete de preparación corporativa y anexos", "Corporate Readiness and Attachment Pack",
"Lista de preparación", "Readiness checklist",
"Este documento organiza los anexos corporativos que deben acompañar el expediente de propiedad intelectual. No sustituye certificados oficiales emitidos por autoridades; identifica qué evidencia debe adjuntarse cuando esté disponible.",
"This document organizes the corporate attachments that should accompany the intellectual-property filing packet. It does not replace official certificates issued by authorities; it identifies the evidence to attach when available.",
[
("Identidad de presentación", [f"Fundador responsable: {FOUNDER_ES}.", f"Empresa presentada: {COMPANY}.", f"Producto tecnológico: {PRODUCT_ES}.", "Lugar de preparación del expediente: Malabo, República de Guinea Ecuatorial."]),
("Anexos corporativos requeridos", ["Certificado de registro de empresa, cuando esté emitido por la autoridad competente.", "Documento de identidad del fundador o representante autorizado.", "Domicilio o dirección de contacto de la empresa.", "Documento de objeto social o actividad empresarial donde consten software, datos, geolocalización, infraestructura digital y automatización.", "Cualquier poder, mandato o autorización si un tercero presenta el expediente."]),
("Declaración de responsabilidad", [f"{FOUNDER_ES} declara responsabilidad sobre la concepción, diseño, implementación, arquitectura, dirección de producto y coordinación documental del sistema.", "Las evidencias técnicas se adjuntan como soporte de autoría, originalidad, alcance funcional y control de versiones."])
],
[
("Presentation identity", [f"Responsible founder: {FOUNDER_EN}.", f"Presented company: {COMPANY}.", f"Technology product: {PRODUCT_EN}.", "Filing packet location: Malabo, Republic of Equatorial Guinea."]),
("Corporate attachments required", ["Company registration certificate, once issued by the competent authority.", "Identity document of the founder or authorized representative.", "Company address or contact address.", "Business activity/object document covering software, data, geolocation, digital infrastructure, and automation.", "Any mandate or authorization if a third party files the packet."]),
("Responsibility statement", [f"{FOUNDER_EN} states responsibility for conception, design, implementation, architecture, product direction, and documentation coordination of the system.", "Technical evidence is attached as support for authorship, originality, functional scope, and version control."])
])

add(
"01-ip-ownership-declaration",
"Declaración de titularidad de propiedad intelectual", "Intellectual Property Ownership Declaration",
"Declaración", "Declaration",
"Esta declaración establece la autoría responsable y la titularidad presentada para el sistema, sus módulos, documentación y materiales técnicos.",
"This declaration states the responsible authorship and presented ownership for the system, its modules, documentation, and technical materials.",
[
("Declaración principal", [f"{FOUNDER_ES}, fundador de {COMPANY}, declara que es responsable de la concepción, diseño, implementación y dirección técnica del {PRODUCT_ES}.", f"{COMPANY} se presenta como vehículo empresarial responsable de la explotación, mantenimiento, soporte y presentación administrativa del sistema.", "La titularidad presentada comprende software, interfaces, lógica funcional, documentación técnica, arquitectura, procesos operativos, estándares de datos y materiales de capacitación asociados."]),
("Alcance protegido", MODULES_ES + ["Documentación técnica, documentación operativa, manuales, registros de versión, especificaciones de API, modelo de datos y estándares GIS." ]),
("Exclusiones", ["No se declara titularidad sobre símbolos oficiales del Estado, nombres de instituciones públicas, mapas base de terceros o datos oficiales que pertenezcan al Gobierno.", "La presente declaración se limita al sistema desarrollado, su documentación, su diseño de implementación y sus componentes propios."])
],
[
("Main declaration", [f"{FOUNDER_EN}, founder of {COMPANY}, declares responsibility for the conception, design, implementation, and technical direction of the {PRODUCT_EN}.", f"{COMPANY} is presented as the business vehicle responsible for operation, maintenance, support, and administrative presentation of the system.", "The presented ownership covers software, interfaces, functional logic, technical documentation, architecture, operating processes, data standards, and associated training materials."]),
("Protected scope", MODULES + ["Technical documentation, operational documentation, manuals, version registers, API specifications, data model, and GIS standards." ]),
("Exclusions", ["No ownership is claimed over official State symbols, public institution names, third-party basemaps, or official data belonging to the Government.", "This declaration is limited to the developed system, its documentation, implementation design, and proprietary components."])
])

add(
"02-software-ownership-certificate",
"Certificado interno de titularidad del software", "Internal Software Ownership Certificate",
"Certificado interno", "Internal certificate",
"Este certificado interno identifica los componentes del software y la persona responsable de su diseño e implementación para el expediente de registro.",
"This internal certificate identifies the software components and the person responsible for their design and implementation for the registration packet.",
[
("Certificación", [f"Se certifica internamente que el {PRODUCT_ES} ha sido diseñado e implementado bajo responsabilidad de {FOUNDER_ES}, fundador de {COMPANY}.", "El sistema está compuesto por una aplicación web de administración, una API de servicios, base de datos relacional, almacenamiento de evidencias, automatización operativa y documentación técnica asociada."]),
("Componentes de software", ["Portal ciudadano y rutas públicas de consulta.", "Portal de administración y operadores.", "Servicio API para autenticación, registro, revisión, publicación y reportes.", "Motor de generación y validación de códigos de dirección.", "Módulos GIS, registro de carreteras, edificios, territorios y direcciones.", "Sistema de auditoría, actividad, publicación, exportación y evidencia de campo."]),
("Registro de soporte", ["El código fuente, la estructura de datos, las rutas de aplicación, los endpoints y los manuales técnicos sirven como evidencia de alcance y control del software."])
],
[
("Certification", [f"It is internally certified that the {PRODUCT_EN} has been designed and implemented under the responsibility of {FOUNDER_EN}, founder of {COMPANY}.", "The system consists of an administration web application, service API, relational database, evidence storage, operational automation, and associated technical documentation."]),
("Software components", ["Citizen portal and public lookup routes.", "Administration and operator portal.", "API service for authentication, registry, review, publication, and reporting.", "Address-code generation and validation engine.", "GIS, road, building, territory, and address registry modules.", "Audit, activity, publication, export, and field-evidence system."]),
("Supporting record", ["Source code, data structure, application routes, endpoints, and technical manuals serve as evidence of software scope and control."])
])

add(
"03-product-ownership-statement",
"Declaración de propiedad del producto", "Product Ownership Statement",
"Declaración de producto", "Product statement",
"Este documento resume el producto como obra tecnológica integral, su finalidad pública y el control responsable de su diseño.",
"This document summarizes the product as an integrated technology work, its public-service purpose, and responsible control of its design.",
[
("Descripción del producto", [f"El {PRODUCT_ES} es una plataforma digital para capturar, revisar, administrar, publicar y verificar direcciones oficiales y evidencia territorial.", "El producto integra flujos públicos, operaciones de campo, revisión institucional, registro oficial, publicación controlada, reportes, auditoría y soporte técnico."]),
("Responsable", [f"{FOUNDER_ES}, fundador de {COMPANY}, asume responsabilidad sobre diseño, implementación, arquitectura, evolución funcional y coordinación documental."]),
("Valor público", ["Mejora la localización de personas, propiedades, servicios, instituciones y actividad económica.", "Apoya administración territorial, servicios públicos, logística, emergencia, planificación, registro y transparencia operativa."])
],
[
("Product description", [f"The {PRODUCT_EN} is a digital platform for capturing, reviewing, administering, publishing, and verifying official addresses and territorial evidence.", "The product integrates public workflows, field operations, institutional review, official registry, controlled publication, reporting, audit, and technical support."]),
("Responsible person", [f"{FOUNDER_EN}, founder of {COMPANY}, assumes responsibility for design, implementation, architecture, functional evolution, and documentation coordination."]),
("Public value", ["Improves location of people, properties, services, institutions, and economic activity.", "Supports territorial administration, public services, logistics, emergency response, planning, registry work, and operational transparency."])
])

add(
"04-version-release-register",
"Registro de versiones y entregas", "Version and Release Register",
"Registro", "Register",
"Este registro establece una línea de control de versiones para demostrar evolución, trazabilidad y preparación documental del sistema.",
"This register establishes version-control evidence to demonstrate evolution, traceability, and documentation readiness of the system.",
[
("Versión base documentada", ["Versión de expediente: 0.1.0.", "Estado: piloto controlado y preparación de registro de propiedad intelectual.", "Alcance: rutas públicas, operación administrativa, API, base de datos, GIS, reportes, auditoría, publicaciones controladas y manuales de capacitación."]),
("Componentes incluidos", ["Código fuente de frontend y backend.", "Esquema de base de datos y migraciones internas.", "Documentación técnica y operativa.", "Manuales de capacitación bilingües.", "Propuesta gubernamental y documentos de soporte."]),
("Regla de futuras versiones", ["Toda versión debe conservar número, descripción, módulos afectados, responsable, evidencias de prueba y fecha administrativa de aprobación cuando exista."])
],
[
("Documented base version", ["Packet version: 0.1.0.", "Status: controlled pilot and intellectual-property registration preparation.", "Scope: public routes, administrative operation, API, database, GIS, reports, audit, controlled publication, and training manuals."]),
("Included components", ["Frontend and backend source code.", "Database schema and internal migrations.", "Technical and operational documentation.", "Bilingual training manuals.", "Government proposal and supporting documents."]),
("Future-version rule", ["Each future version should preserve number, description, affected modules, responsible person, test evidence, and administrative approval date where available."])
])

add(
"05-trademark-oapi-portfolio",
"Portafolio de marcas y signos distintivos para OAPI", "Trademark and Distinctive Signs Portfolio for OAPI",
"Portafolio", "Portfolio",
"Este portafolio organiza los nombres y signos que pueden prepararse para búsqueda, reserva o registro ante la vía competente de OAPI.",
"This portfolio organizes names and signs that may be prepared for search, reservation, or registration through the competent OAPI channel.",
[
("Signos a revisar", [COMPANY, PRODUCT_ES, PRODUCT_EN, "Logotipo empresarial cuando esté aprobado.", "Logotipo o marca del producto cuando esté aprobado.", "Nombres de servicios públicos asociados, si se decide registrarlos."]),
("Clases y alcance a confirmar", ["Software descargable o registrado como programa informático.", "Servicios de software, datos, geolocalización, cartografía digital e infraestructura tecnológica.", "Consultoría, implementación, soporte, capacitación y mantenimiento técnico."]),
("Acciones recomendadas", ["Realizar búsqueda de anterioridad antes de presentar.", "Preparar representación gráfica limpia de cada signo.", "Confirmar clases con asesor o autoridad competente.", "Separar marcas empresariales de nombres descriptivos del sistema cuando convenga."])
],
[
("Signs to review", [COMPANY, PRODUCT_ES, PRODUCT_EN, "Company logo once approved.", "Product logo or mark once approved.", "Associated public-service names if registration is later chosen."]),
("Classes and scope to confirm", ["Software recorded or protected as a computer program.", "Software, data, geolocation, digital mapping, and technology infrastructure services.", "Consulting, implementation, support, training, and technical maintenance."]),
("Recommended actions", ["Perform availability search before filing.", "Prepare a clean graphical representation of each sign.", "Confirm classes with an advisor or competent authority.", "Separate company marks from descriptive system names where appropriate."])
])

asset_items = ["Citizen Portal", "Government Administration Portal", "Field Evidence Workflow", "Address Generation Engine", "GIS and Mapping Engine", "Property and Building Registry Modules", "Administrative Boundary Module", "Public Search and Proof Portal", "API Platform", "Authentication and Access System", "Notification and Support Services", "Analytics, Reports, Exports, and Audit Logging"]
asset_items_es = ["Portal ciudadano", "Portal de administración gubernamental", "Flujo de evidencia de campo", "Motor de generación de direcciones", "Motor GIS y cartográfico", "Módulos de registro de propiedades y edificios", "Módulo de límites administrativos", "Portal público de búsqueda y prueba", "Plataforma API", "Sistema de autenticación y acceso", "Servicios de notificación y soporte", "Analítica, reportes, exportaciones y auditoría"]

add(
"06-software-copyright-portfolio",
"Portafolio de derechos de autor del software", "Software Copyright Portfolio",
"Portafolio", "Portfolio",
"Este portafolio identifica los módulos de software protegibles como expresión técnica del sistema.",
"This portfolio identifies software modules protectable as technical expression of the system.",
[
("Módulos protegibles", asset_items_es),
("Evidencia asociada", ["Código fuente y estructura de carpetas.", "Especificaciones técnicas y operativas.", "Capturas, manuales y rutas funcionales.", "Registros de versión y pruebas.", "Esquemas de base de datos y documentación API."]),
("Titularidad presentada", [f"Responsable de diseño e implementación: {FOUNDER_ES}.", f"Empresa de presentación y explotación: {COMPANY}."])
],
[
("Protectable modules", asset_items),
("Associated evidence", ["Source code and folder structure.", "Technical and operational specifications.", "Screens, manuals, and functional routes.", "Version and testing records.", "Database schemas and API documentation."]),
("Presented ownership", [f"Responsible for design and implementation: {FOUNDER_EN}.", f"Presentation and operation company: {COMPANY}."])
])

add(
"07-master-ip-asset-register",
"Registro maestro de activos de propiedad intelectual", "Master Intellectual Property Asset Register",
"Registro maestro", "Master register",
"Este registro concentra los activos principales, su tipo, responsable, estado y evidencia documental disponible.",
"This register consolidates principal assets, type, responsible person, status, and available documentary evidence.",
[
("Activos principales", [f"{PRODUCT_ES}: plataforma completa, estado preparado para expediente."] + [f"{x}: componente funcional documentado." for x in asset_items_es]),
("Evidencia técnica", [f"Rutas de aplicación documentadas: {len(ROUTE_SAMPLE)}.", f"Endpoints API identificados: {len(ENDPOINT_SAMPLE)} de {len(INV['endpoints'])} listados para referencia de alcance.", f"Tablas principales de base de datos identificadas: {len(TABLES)}.", "Manuales de capacitación, arquitectura, operación y seguridad preparados como anexos."]),
("Responsabilidad", [f"Diseño, implementación y dirección técnica: {FOUNDER_ES}.", f"Vehículo empresarial: {COMPANY}."])
],
[
("Principal assets", [f"{PRODUCT_EN}: complete platform, prepared for filing packet."] + [f"{x}: documented functional component." for x in asset_items]),
("Technical evidence", [f"Documented application routes: {len(ROUTE_SAMPLE)}.", f"Identified API endpoints: {len(ENDPOINT_SAMPLE)} of {len(INV['endpoints'])} listed as scope reference.", f"Principal database tables identified: {len(TABLES)}.", "Training, architecture, operations, and security manuals prepared as attachments."]),
("Responsibility", [f"Design, implementation, and technical direction: {FOUNDER_EN}.", f"Business vehicle: {COMPANY}."])
])

add(
"08-technical-architecture-manual",
"Manual de arquitectura técnica", "Technical Architecture Manual",
"Manual técnico", "Technical manual",
"Este manual describe la arquitectura base del sistema para demostrar estructura, alcance técnico y operación coordinada de sus componentes.",
"This manual describes the base architecture of the system to demonstrate structure, technical scope, and coordinated operation of its components.",
[
("Arquitectura general", ["Frontend web de administración y rutas públicas.", "Backend API para autenticación, registro, revisión, publicación, reportes y auditoría.", "Base de datos PostgreSQL/PostGIS para entidades territoriales, direcciones, usuarios y eventos.", "Redis para soporte de ejecución y servicios auxiliares.", "Almacenamiento compatible S3 para evidencias protegidas cuando aplica."]),
("Módulos funcionales", MODULES_ES),
("Rutas de aplicación", ROUTE_SAMPLE),
("Principios de diseño", ["Modularidad primero; microservicios solo cuando el crecimiento lo justifique.", "Autorización de servidor para funciones protegidas.", "Separación entre rutas públicas y rutas internas de operador.", "Publicación oficial bloqueada hasta aprobación institucional."])
],
[
("Overall architecture", ["Administration web frontend and public routes.", "Backend API for authentication, registry, review, publication, reporting, and audit.", "PostgreSQL/PostGIS database for territorial entities, addresses, users, and events.", "Redis for runtime support and auxiliary services.", "S3-compatible storage for protected evidence where applicable."]),
("Functional modules", MODULES),
("Application routes", ROUTE_SAMPLE),
("Design principles", ["Modular-first architecture; microservices only when growth justifies them.", "Server-side authorization for protected functions.", "Separation between public routes and internal operator routes.", "Official publication remains locked until institutional approval."])
])

add(
"09-database-documentation",
"Documentación de base de datos", "Database Documentation",
"Manual técnico", "Technical manual",
"Este documento resume las entidades persistentes, relaciones operativas y reglas de conservación que sostienen el sistema.",
"This document summarizes persistent entities, operational relationships, and retention rules supporting the system.",
[
("Tablas identificadas", TABLES),
("Dominios de datos", ["Usuarios, sesiones y roles internos.", "Provincias, unidades administrativas, territorios, carreteras y edificios.", "Direcciones candidatas y registros oficiales.", "Correcciones ciudadanas y evidencias de campo.", "Paquetes de publicación, certificados, señalización, reportes y auditoría."]),
("Reglas de datos", ["Los datos sensibles no se exponen en rutas públicas.", "Los identificadores internos se mantienen separados de la presentación ciudadana cuando sea necesario.", "La publicación oficial requiere revisión y bloqueo de aprobación.", "La auditoría conserva eventos de acción, actor, entidad y detalle operativo."])
],
[
("Identified tables", TABLES),
("Data domains", ["Internal users, sessions, and roles.", "Provinces, administrative units, territories, roads, and buildings.", "Candidate addresses and official records.", "Citizen corrections and field evidence.", "Publication packs, certificates, signage, reports, and audit."]),
("Data rules", ["Sensitive data is not exposed on public routes.", "Internal identifiers remain separate from citizen-facing presentation where necessary.", "Official publication requires review and approval lock.", "Audit preserves action, actor, entity, and operational detail events."])
])

add(
"10-gis-addressing-standards",
"Manual de estándares GIS y direccionamiento", "GIS and Addressing Standards Manual",
"Manual de estándares", "Standards manual",
"Este manual define las reglas técnicas para ubicación, jerarquía administrativa, generación de códigos y ciclo de vida de direcciones.",
"This manual defines technical rules for location, administrative hierarchy, code generation, and address lifecycle.",
[
("Jerarquía administrativa", ["Provincia.", "Distrito, municipio o unidad administrativa aplicable.", "Área local, territorio, carretera, edificio o punto de dirección.", "Código oficial de dirección cuando el registro esté aprobado."]),
("Reglas de ubicación", ["Captura GPS o punto de mapa como evidencia de ubicación.", "Sistema de referencia WGS84 para coordenadas de latitud y longitud.", "Separación entre evidencia de campo y publicación pública.", "Corrección manual bajo revisión de operador cuando la evidencia lo requiera."]),
("Ciclo de vida", ["Solicitud ciudadana o captura de campo.", "Revisión de evidencia.", "Promoción a registro oficial.", "Retención en espera de publicación.", "Publicación, certificado o señalización solo tras aprobación."])
],
[
("Administrative hierarchy", ["Province.", "District, municipality, or applicable administrative unit.", "Local area, territory, road, building, or address point.", "Official address code once the record is approved."]),
("Location rules", ["GPS capture or map point as location evidence.", "WGS84 reference system for latitude and longitude coordinates.", "Separation between field evidence and public publication.", "Manual correction under operator review where evidence requires it."]),
("Lifecycle", ["Citizen request or field capture.", "Evidence review.", "Promotion to official registry.", "Hold before publication.", "Publication, certificate, or signage only after approval."])
])

add(
"11-api-documentation",
"Documentación de API", "API Documentation",
"Manual técnico", "Technical manual",
"Este documento resume la superficie API como evidencia de integración, control de acceso y alcance funcional.",
"This document summarizes the API surface as evidence of integration, access control, and functional scope.",
[
("Familias de API", ["Autenticación y sesión.", "Usuarios y administración de personal.", "Provincias, unidades administrativas y territorios.", "Carreteras, edificios, direcciones y registros oficiales.", "Geotagging ciudadano, correcciones y seguimiento.", "Evidencia de campo, revisión, publicación, reportes, exportaciones y auditoría."]),
("Endpoints representativos", ENDPOINT_SAMPLE),
("Controles", ["Autenticación para rutas internas.", "Roles de administración, edición, visualización y revisión institucional.", "Validación de entrada y separación de datos públicos/protegidos.", "Límites de publicación controlados por aprobación."])
],
[
("API families", ["Authentication and session.", "Users and staff administration.", "Provinces, administrative units, and territories.", "Roads, buildings, addresses, and official records.", "Citizen geotagging, corrections, and tracking.", "Field evidence, review, publication, reports, exports, and audit."]),
("Representative endpoints", ENDPOINT_SAMPLE),
("Controls", ["Authentication for internal routes.", "Administration, editing, viewing, and institutional-review roles.", "Input validation and separation of public/protected data.", "Publication limits controlled by approval."])
])

add(
"12-operations-manual",
"Manual de operaciones", "Operations Manual",
"Manual operativo", "Operations manual",
"Este manual define cómo operar, mantener, respaldar y atender el sistema durante piloto controlado y preparación institucional.",
"This manual defines how to operate, maintain, back up, and support the system during controlled pilot and institutional preparation.",
[
("Operación diaria", ["Verificar salud de API, portal administrativo, base de datos, almacenamiento y caché.", "Revisar solicitudes, evidencias, reportes y cola de publicación.", "Mantener usuarios activos con el menor privilegio necesario.", "Registrar incidencias y acciones de mantenimiento."]),
("Mantenimiento", ["Respaldar base de datos y evidencias antes de cambios importantes.", "Probar restauración de respaldo en entorno controlado.", "Actualizar documentación cuando cambien módulos, endpoints o reglas.", "Separar datos de prueba de datos institucionales."]),
("Soporte", ["Canalizar errores operativos por responsable de sistema.", "Documentar pasos de reproducción, impacto y resolución.", "No publicar datos sensibles en reportes de soporte."])
],
[
("Daily operation", ["Check health of API, administration portal, database, storage, and cache.", "Review requests, evidence, reports, and publication queue.", "Maintain active users with least privilege required.", "Record incidents and maintenance actions."]),
("Maintenance", ["Back up database and evidence before major changes.", "Test backup restoration in a controlled environment.", "Update documentation when modules, endpoints, or rules change.", "Separate test data from institutional data."]),
("Support", ["Route operational errors through the system responsible person.", "Document reproduction steps, impact, and resolution.", "Do not publish sensitive data in support reports."])
])

add(
"13-cybersecurity-manual",
"Manual de ciberseguridad", "Cybersecurity Manual",
"Manual de seguridad", "Security manual",
"Este manual resume controles mínimos de seguridad para proteger usuarios, sesiones, datos de ubicación, evidencias y publicación oficial.",
"This manual summarizes minimum security controls for protecting users, sessions, location data, evidence, and official publication.",
[
("Controles de acceso", ["Autenticación obligatoria para áreas internas.", "Roles separados para administración, edición, visualización y revisión.", "Revocación de sesiones al desactivar usuarios o rotar contraseñas.", "Bloqueo de acciones críticas cuando falte aprobación institucional."]),
("Protección de datos", ["Minimización de datos ciudadanos y documentos de identidad.", "Separación entre datos públicos y datos protegidos de operador.", "Enmascaramiento de identificadores sensibles en reportes y exportaciones.", "Auditoría de acciones relevantes."]),
("Operación segura", ["No almacenar secretos en código fuente o documentos públicos.", "Respaldos controlados y restauración probada.", "Registro de incidentes, correcciones y seguimiento.", "Actualización de dependencias y revisión de cambios críticos."])
],
[
("Access controls", ["Mandatory authentication for internal areas.", "Separate roles for administration, editing, viewing, and review.", "Session revocation when users are disabled or passwords rotated.", "Critical actions locked when institutional approval is missing."]),
("Data protection", ["Minimization of citizen data and identity documents.", "Separation between public data and protected operator data.", "Masking sensitive identifiers in reports and exports.", "Audit of relevant actions."]),
("Secure operation", ["Do not store secrets in source code or public documents.", "Controlled backups and tested restoration.", "Incident, correction, and follow-up records.", "Dependency updates and review of critical changes."])
])

add(
"14-national-addressing-system-specification",
"Especificación del Sistema Nacional de Direccionamiento Digital", "National Digital Addressing System Specification",
"Especificación", "Specification",
"Esta especificación resume los requisitos funcionales, reglas de datos, interoperabilidad y expansión del sistema.",
"This specification summarizes functional requirements, data rules, interoperability, and expansion of the system.",
[
("Objetivo", ["Crear una capa nacional de direcciones digitales verificables.", "Permitir captura pública controlada, revisión técnica e institucional, publicación oficial y verificación ciudadana.", "Sostener integración futura con instituciones, servicios públicos, logística y planificación territorial."]),
("Requisitos funcionales", ["Registro de ubicación y seguimiento de solicitud.", "Revisión de evidencia de campo.", "Gestión de carreteras, edificios, territorios y unidades administrativas.", "Generación y validación de códigos de dirección.", "Publicación controlada, prueba pública, certificados y señalización.", "Reportes, auditoría, exportación y administración de usuarios."]),
("Interoperabilidad y expansión", ["API versionada para futuras integraciones.", "Jerarquía administrativa extensible.", "Modelo GIS compatible con coordenadas estándar.", "Controles de privacidad y publicación antes de exponer información."])
],
[
("Objective", ["Create a national layer of verifiable digital addresses.", "Enable controlled public capture, technical and institutional review, official publication, and citizen verification.", "Support future integration with institutions, public services, logistics, and territorial planning."]),
("Functional requirements", ["Location registration and request tracking.", "Field-evidence review.", "Management of roads, buildings, territories, and administrative units.", "Address-code generation and validation.", "Controlled publication, public proof, certificates, and signage.", "Reports, audit, export, and user administration."]),
("Interoperability and expansion", ["Versioned API for future integrations.", "Extensible administrative hierarchy.", "GIS model compatible with standard coordinates.", "Privacy and publication controls before exposing information."])
])


def markdown_to_html(md: str) -> str:
    out=[]
    in_ul=False
    in_ol=False
    section_open=False
    for raw in md.splitlines():
        line=raw.rstrip()
        if not line:
            if in_ul: out.append("</ul>"); in_ul=False
            if in_ol: out.append("</ol>"); in_ol=False
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            if in_ul: out.append("</ul>"); in_ul=False
            if in_ol: out.append("</ol>"); in_ol=False
            if section_open:
                out.append("</section>")
            cls = " class='meta'" if "control" in line.lower() else ""
            out.append(f"<section{cls}><h2>{e(line[3:])}</h2>")
            section_open=True
            continue
        if re.match(r"^\d+\.\s+", line):
            if not in_ol:
                if in_ul: out.append("</ul>"); in_ul=False
                out.append("<ol>"); in_ol=True
            item_text = re.sub(r"^\d+\.\s+", "", line)
            out.append(f"<li>{e(item_text)}</li>")
            continue
        if line.startswith("- "):
            if not in_ul:
                if in_ol: out.append("</ol>"); in_ol=False
                out.append("<ul>"); in_ul=True
            out.append(f"<li>{e(line[2:])}</li>")
            continue
        if ":" in line and len(line.split(":",1)[0]) < 42:
            left,right=line.split(":",1)
            out.append(f"<p><strong>{e(left)}:</strong><span>{e(right.strip())}</span></p>")
        else:
            out.append(f"<p>{e(line)}</p>")
    if in_ul: out.append("</ul>")
    if in_ol: out.append("</ol>")
    if section_open:
        out.append("</section>")
    return "\n".join(out)


def render_doc(doc: dict[str, str], crest: str) -> None:
    lang=doc["lang"]
    title=doc["title"]
    stem=f"EG-Addressing-IP-{doc['slug']}-{lang.upper()}"
    (SRC/lang).mkdir(parents=True, exist_ok=True)
    (HTML/lang).mkdir(parents=True, exist_ok=True)
    (PDF/lang).mkdir(parents=True, exist_ok=True)
    md_path=SRC/lang/f"{stem}.md"
    html_path=HTML/lang/f"{stem}.html"
    pdf_path=PDF/lang/f"{stem}.pdf"
    md_path.write_text(doc["body"], encoding="utf-8")
    republic = "República de Guinea Ecuatorial" if lang=="es" else "Republic of Equatorial Guinea"
    platform = PRODUCT_ES if lang=="es" else PRODUCT_EN
    eyebrow = "Expediente de propiedad intelectual" if lang=="es" else "Intellectual property filing packet"
    subtitle = (f"Documentación preparada para registro de propiedad intelectual en Malabo. Fundador responsable: {FOUNDER_ES}. Empresa: {COMPANY}." if lang=="es" else f"Documentation prepared for intellectual-property registration in Malabo. Responsible founder: {FOUNDER_EN}. Company: {COMPANY}.")
    status_left = "Documento de soporte para presentación administrativa" if lang=="es" else "Supporting document for administrative presentation"
    status_right = "Versión española" if lang=="es" else "English version"
    body=markdown_to_html(doc["body"])
    html_doc=f"""<!doctype html><html lang='{lang}'><head><meta charset='utf-8'><title>{e(title)}</title><style>{CSS}</style></head><body>
<main class='sheet'>
<section class='cover' aria-label='cover'>
<div class='cover-main'>
<div class='crest'><img src='{crest}' alt=''/></div>
<p class='republic'>{e(republic)}</p><p class='platform'>{e(platform)}</p>
<p class='eyebrow'>{e(eyebrow)}</p><h1 class='cover-title'>{e(title)}</h1><p class='subtitle'>{e(subtitle)}</p>
</div><div class='cover-footer'><span>{e(status_left)}</span><span>{e(status_right)} · {e(COMPANY)}</span></div>
</section><section class='content'>{body}<p class='footer-note'>{e(republic)} · {e(platform)} · {e(COMPANY)}</p></section></main></body></html>"""
    html_path.write_text(html_doc, encoding="utf-8")
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox","--no-pdf-header-footer",f"--print-to-pdf={pdf_path}",html_path.as_uri()], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main() -> None:
    crest=clean_svg()
    for d in (SRC, HTML, PDF, BUNDLE.parent):
        d.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        render_doc(doc, crest)
    if BUNDLE.exists():
        BUNDLE.unlink()
    with ZipFile(BUNDLE, "w", ZIP_DEFLATED) as z:
        for p in sorted(PDF.glob("*/*.pdf")):
            z.write(p, f"{p.parent.name}/{p.name}")
    print(f"sources={len(list(SRC.glob('*/*.md')))}")
    print(f"pdfs={len(list(PDF.glob('*/*.pdf')))}")
    print(BUNDLE)

if __name__ == "__main__":
    main()
