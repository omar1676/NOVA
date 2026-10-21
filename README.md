# NOVA Sneakers

Proyecto intermodular de 2.º DAM: catálogo de zapatillas, gestión de pedidos,
base de datos PostgreSQL y procesos Java de fabricación.

## Componentes

| Carpeta | Contenido |
| --- | --- |
| `acceso-datos/` | Modelos, esquema, funciones, permisos y pruebas SQL |
| `interfaces/cliente/` | Catálogo visual y probador conceptual |
| `interfaces/admin/` | Panel de administración y páginas de ejemplo |
| `psp/` | Validación del CSV de fabricación y análisis de tallas |
| `psp/src/Psp/` | Analizador independiente con protocolo de líneas |
| `integracion/` | Formatos y límites de integración documentados |
| `odoo/` | Espacio reservado para el ERP |

## Abrir las interfaces

Desde la raíz del repositorio:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Abrir `http://127.0.0.1:8000/interfaces/cliente/` o
`http://127.0.0.1:8000/interfaces/admin/admin.html`.
El servidor estático no implementa `/api/admin/dashboard` ni autenticación.
El catálogo todavía no permite comprar y el probador no recomienda tallas.

## Comprobaciones

```sh
python3 scripts/comprobar_web.py
python3 scripts/comprobar_psp.py
```

Las comprobaciones PSP requieren un JDK 17 o posterior y compilan en un
directorio temporal. No escriben clases dentro del repositorio.
La comprobación web valida recursos locales; no evalúa el diseño ni una API.

La instalación SQL está en `acceso-datos/documentacion/README.md`.
El formato de fabricación está en `integracion/contrato-fabricacion.md`.
Las comprobaciones manuales están en `docs/PRUEBAS_MANUALES.md`.

La rama integrada reúne archivos de los distintos módulos. La integración
funcional con Odoo, el backend y el pago sigue pendiente.
