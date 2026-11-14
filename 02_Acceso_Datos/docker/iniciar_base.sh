#!/bin/bash
# Monta la base nova_sneakers dentro del contenedor "db" de compose.yaml.
#
# PostgreSQL solo lo lanza la primera vez, cuando el volumen de datos esta
# vacio. Despues los datos se quedan en el volumen y este script no se repite.
#
# Usa los scripts de 02_Acceso_Datos/sql (montados en /nova/sql, sin copiarlos)
# en el mismo orden que el apartado "Reconstruir la base de datos" del README
# principal. Las contrasenas vienen del archivo .env: se le pasan a psql por la
# entrada, que es donde las piden los \prompt de los scripts 13, 14, 17, 19 y 20.
set -e

SQL=/nova/sql
LOGS=/tmp/nova-logs   # la salida de cada script, para revisarla si algo falla
mkdir -p "$LOGS"
cd "$LOGS"            # el 15 y el 16 dejan aqui sus CSV

# instalar <script> [respuestas para los \prompt]: si falla algo, se para todo
instalar() {
  local script=$1
  shift
  if ! printf '%s\n' "$@" | psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
      -f "$SQL/$script.sql" > "$script.log" 2>&1; then
    echo "NOVA: ERROR en $script.sql"
    tail -n 20 "$script.log"
    return 1
  fi
  echo "NOVA: $script.sql correcto"
}

# probar <script>: consultas y pruebas; el 09 tiene un ERROR previsto (S4b)
probar() {
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL/$1.sql" > "$1.log" 2>&1
  echo "NOVA: $1.sql -> PASS: $(grep -c PASS "$1.log"), FAIL: $(grep -c FAIL "$1.log"), ERROR: $(grep -c ERROR "$1.log")"
}

# 1. Instalacion
for script in sneaker-factory-esquema 04_xnova 02_funciones 03_triggers 05_datos_prueba 07_seguridad 08_auditoria; do
  instalar "$script"
done

# 2. Usuarios de conexion (java_nova y los del servidor)
instalar 17_usuario_java "$CLAVE_JAVA"
instalar 19_usuario_web "$CLAVE_WEB"

# 3. Consultas y pruebas
for script in 06_consultas 09_pruebas 10_caso_custom 11_dml_ejemplos 12_consultas_panel; do
  probar "$script"
done

# 4. Cuentas de demostracion (el 13 pide admin.demo, taller.demo, tienda.demo
#    y otra vez admin.demo) y el pedido CUSTOM-40
instalar 13_activar_usuarios "$CLAVE_DEMO" "$CLAVE_DEMO" "$CLAVE_DEMO" "$CLAVE_DEMO"
instalar 14_caso_custom_persistente "$CLAVE_DEMO"

# 5. Exportaciones (los CSV se quedan en /tmp/nova-logs)
probar 15_exportar_fabricacion
probar 16_exportar_csv_dashboard

# 6. Ampliaciones: tienda, catalogo, reparto y portal del trabajador
instalar 20_tienda_web "$CLAVE_TIENDA"
instalar 21_catalogo_web
instalar 22_reparto_panel
instalar 23_portal_trabajador

# El 18 (datos de SO024) no se lanza: necesita los datos acordados.

echo "NOVA: base nova_sneakers montada. Pruebas 09 a 16 -> PASS: $(cat 09_*.log 1[0-6]_*.log | grep -c PASS), FAIL: $(cat 09_*.log 1[0-6]_*.log | grep -c FAIL), ERROR: $(cat 09_*.log 1[0-6]_*.log | grep -c ERROR)"
