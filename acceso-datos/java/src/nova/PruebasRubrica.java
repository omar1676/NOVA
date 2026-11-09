package nova;

import java.io.File;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import javax.swing.table.DefaultTableModel;

/**
 * Pruebas A-J del enunciado, lanzadas desde Java con los MISMOS metodos que
 * usan los botones de la aplicacion. Cada resultado se comprueba despues con
 * una consulta SQL. Escribe PASS o FAIL por cada comprobacion.
 *
 * Pide por teclado las contrasenas de admin.demo, tienda.demo y taller.demo.
 *
 * Deja en la base, como evidencia, pedidos PRUEBA-* y un usuario prueba.*
 * desactivado. Sus nombres llevan un numero distinto cada vez, asi que se
 * puede lanzar varias veces.
 */
public class PruebasRubrica {

    private static int aciertos = 0;
    private static int fallos = 0;

    private static String claveAdmin;
    private static String claveComercial;
    private static String claveTrabajador;
    private static String sufijo;

    public static void main(String[] args) throws Exception {
        Scanner teclado = new Scanner(System.in);
        System.out.print("Contraseña de admin.demo: ");
        claveAdmin = teclado.nextLine();
        System.out.print("Contraseña de tienda.demo (comercial): ");
        claveComercial = teclado.nextLine();
        System.out.print("Contraseña de taller.demo (trabajador): ");
        claveTrabajador = teclado.nextLine();
        sufijo = String.valueOf(System.currentTimeMillis() % 1000000);

        try {
            pruebaLogin();
            int idPedidoA = pruebaA();
            pruebaB();
            pruebaC(idPedidoA);
            pruebaD();
            pruebaE();
            pruebaF();
            pruebaG();
            pruebaH();
            pruebaI();
            pruebaJ();
            pruebaPermisos();
        } catch (SQLException e) {
            fallos++;
            System.out.println("FAIL error inesperado: " + ConexionBD.mensajeError(e));
        } finally {
            UsuarioDAO.logout();
            ConexionBD.cerrar();
        }

        System.out.println();
        System.out.println("RESULTADO: " + aciertos + " PASS, " + fallos + " FAIL");
        if (fallos > 0) {
            System.exit(1);
        }
    }

    // ------------------------------------------------------------------
    // Inicio de sesion: un usuario por rol, y cada uno con su rol de base
    // ------------------------------------------------------------------
    private static void pruebaLogin() throws SQLException {
        titulo("Inicio de sesion y rol de conexion");
        String[][] cuentas = {
            {"admin.demo", claveAdmin, "administrador", "nova_admin"},
            {"tienda.demo", claveComercial, "comercial", "nova_comercial"},
            {"taller.demo", claveTrabajador, "trabajador", "nova_trabajador"}
        };
        for (String[] cuenta : cuentas) {
            UsuarioDAO.login(cuenta[0], cuenta[1]);
            String rolConexion = texto("SELECT current_user");
            comprobar("L1 login de " + cuenta[0],
                    Sesion.getRol().equals(cuenta[2]) && rolConexion.equals(cuenta[3]),
                    "rol " + Sesion.getRol() + ", conectado como " + rolConexion);
        }

        try {
            UsuarioDAO.login("admin.demo", "contrasena-equivocada");
            comprobar("L2 contrasena incorrecta", false, "ha entrado");
        } catch (SQLException e) {
            comprobar("L2 contrasena incorrecta", !Sesion.haySesion(), ConexionBD.mensajeError(e));
        }
    }

    // ------------------------------------------------------------------
    // A: pedido Custom valido desde Java, confirmado por un comercial
    // ------------------------------------------------------------------
    private static int pruebaA() throws SQLException {
        titulo("Prueba A: pedido Custom valido");
        UsuarioDAO.login("tienda.demo", claveComercial);
        int idVariante = variante("NOVA Velocity", "Azul");
        int idCliente = cliente("club.atletico@example.com");
        int stock41 = stock(idVariante, 41);
        int stock42 = stock(idVariante, 42);

        ArrayList<int[]> lineas = new ArrayList<>();
        lineas.add(new int[] {idVariante, 41, 2});
        lineas.add(new int[] {idVariante, 42, 3});
        String referencia = "PRUEBA-A-" + sufijo;
        int idPedido = PedidoDAO.crearPedido(referencia, idCliente, lineas, true, "Escudo del club en el lateral");
        PedidoDAO.confirmarPedido(idPedido);

        comprobar("A1 cabecera", texto("SELECT estado || ' ' || personalizado FROM pedidos WHERE id_pedido = ?",
                idPedido).equals("confirmado true"), referencia + " confirmado y personalizado");
        comprobar("A2 lineas", numero("SELECT count(*) FROM linea_pedido WHERE id_pedido = ?", idPedido) == 2,
                "2 lineas, tallas 41 y 42");

        BigDecimal total = decimal("SELECT importe_total FROM pedidos WHERE id_pedido = ?", idPedido);
        BigDecimal suma = decimal("SELECT sum(cantidad * precio_unitario) FROM linea_pedido WHERE id_pedido = ?",
                idPedido);
        int pares = numero("SELECT cantidad_total FROM pedidos WHERE id_pedido = ?", idPedido);
        comprobar("A3 total calculado por PostgreSQL", total.compareTo(suma) == 0 && pares == 5,
                "importe_total " + total + " = suma de lineas " + suma + ", " + pares + " pares");

        int stock41Despues = stock(idVariante, 41);
        int stock42Despues = stock(idVariante, 42);
        comprobar("A4 stock tras confirmar", stock41Despues == stock41 - 2 && stock42Despues == stock42 - 3,
                "talla 41: " + stock41 + " -> " + stock41Despues + ", talla 42: " + stock42 + " -> " + stock42Despues);

        // log_eventos solo lo puede leer el administrador
        UsuarioDAO.login("admin.demo", claveAdmin);
        int idComercial = numero("SELECT id_usuario FROM usuarios WHERE username = 'tienda.demo'");
        int eventos = numero("SELECT count(*) FROM log_eventos WHERE tabla_afectada = 'pedidos' "
                + "AND id_registro = ? AND id_usuario = ? AND fecha_hora IS NOT NULL", idPedido, idComercial);
        String acciones = texto("SELECT string_agg(accion || ' ' || to_char(fecha_hora, 'HH24:MI:SS'), ', ' "
                + "ORDER BY id_evento) FROM log_eventos WHERE tabla_afectada = 'pedidos' AND id_registro = ?", idPedido);
        comprobar("A5 auditoria con usuario y hora", eventos == 2, "tienda.demo: " + acciones);
        int eventosStock = numero("SELECT count(*) FROM log_eventos WHERE tabla_afectada = 'existencias' "
                + "AND id_usuario = ? AND detalle LIKE 'SKU %' AND fecha_hora >= "
                + "(SELECT fecha_pedido FROM pedidos WHERE id_pedido = ?)", idComercial, idPedido);
        comprobar("A6 auditoria del stock", eventosStock >= 2, eventosStock + " cambios de stock firmados por tienda.demo");
        return idPedido;
    }

    // ------------------------------------------------------------------
    // B: confirmar sin stock suficiente
    // ------------------------------------------------------------------
    private static void pruebaB() throws SQLException {
        titulo("Prueba B: stock insuficiente");
        UsuarioDAO.login("tienda.demo", claveComercial);
        int idVariante = variante("NOVA Pulse", "Verde");
        int stockAntes = stock(idVariante, 43);

        ArrayList<int[]> lineas = new ArrayList<>();
        lineas.add(new int[] {idVariante, 43, stockAntes + 100});
        int idPedido = PedidoDAO.crearPedido("PRUEBA-B-" + sufijo, cliente("daniel.jan@example.com"),
                lineas, false, "");

        try {
            PedidoDAO.confirmarPedido(idPedido);
            comprobar("B1 confirmacion rechazada", false, "se ha confirmado");
        } catch (SQLException e) {
            comprobar("B1 confirmacion rechazada", ConexionBD.mensajeError(e).contains("Stock insuficiente"),
                    ConexionBD.mensajeError(e));
        }
        String estado = texto("SELECT estado FROM pedidos WHERE id_pedido = ?", idPedido);
        int marcadas = numero("SELECT count(*) FROM linea_pedido WHERE id_pedido = ? AND stock_descontado", idPedido);
        int stockDespues = stock(idVariante, 43);
        comprobar("B2 sin cambios parciales", estado.equals("pendiente") && marcadas == 0 && stockDespues == stockAntes,
                "estado " + estado + ", stock " + stockAntes + " -> " + stockDespues);

        // Se cancela para que este pedido imposible no cuente como venta
        PedidoDAO.cancelarPedido(idPedido);
    }

    // ------------------------------------------------------------------
    // C: cancelar un pedido confirmado (lo hace el trabajador)
    // ------------------------------------------------------------------
    private static void pruebaC(int idPedido) throws SQLException {
        titulo("Prueba C: cancelacion");
        UsuarioDAO.login("taller.demo", claveTrabajador);
        int idVariante = variante("NOVA Velocity", "Azul");
        int stock41 = stock(idVariante, 41);
        int stock42 = stock(idVariante, 42);

        PedidoDAO.cancelarPedido(idPedido);

        String estado = texto("SELECT estado FROM pedidos WHERE id_pedido = ?", idPedido);
        int marcadas = numero("SELECT count(*) FROM linea_pedido WHERE id_pedido = ? AND stock_descontado", idPedido);
        comprobar("C1 estado cancelado", estado.equals("cancelado") && marcadas == 0, "estado " + estado);
        comprobar("C2 stock devuelto", stock(idVariante, 41) == stock41 + 2 && stock(idVariante, 42) == stock42 + 3,
                "talla 41: " + stock41 + " -> " + stock(idVariante, 41) + ", talla 42: " + stock42 + " -> "
                + stock(idVariante, 42));

        UsuarioDAO.login("admin.demo", claveAdmin);
        String detalle = texto("SELECT u.username || ' ' || e.accion || ': ' || e.detalle FROM log_eventos e "
                + "JOIN usuarios u ON u.id_usuario = e.id_usuario WHERE e.tabla_afectada = 'pedidos' "
                + "AND e.id_registro = ? AND e.accion = 'BAJA_LOGICA'", idPedido);
        comprobar("C3 cancelacion auditada", detalle != null && detalle.startsWith("taller.demo"), detalle);
    }

    // ------------------------------------------------------------------
    // D: ROLLBACK deliberado
    // ------------------------------------------------------------------
    private static void pruebaD() throws SQLException {
        titulo("Prueba D: ROLLBACK deliberado");
        UsuarioDAO.login("tienda.demo", claveComercial);
        int idVariante = variante("NOVA Origin", "Blanco");
        ArrayList<int[]> lineas = new ArrayList<>();
        lineas.add(new int[] {idVariante, 40, 1});
        int idPedido = PedidoDAO.crearPedido("PRUEBA-D-" + sufijo, cliente("santi.cruz@example.com"),
                lineas, false, "");
        int stockAntes = stock(idVariante, 40);

        UsuarioDAO.login("admin.demo", claveAdmin);
        int eventosAntes = numero("SELECT count(*) FROM log_eventos WHERE tabla_afectada = 'pedidos' "
                + "AND id_registro = ?", idPedido);

        // Se confirma dentro de una transaccion y se deshace a proposito
        UsuarioDAO.login("tienda.demo", claveComercial);
        ConexionBD.empezarTransaccion();
        try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(
                "UPDATE pedidos SET estado = 'confirmado' WHERE id_pedido = ?")) {
            sentencia.setInt(1, idPedido);
            sentencia.executeUpdate();
        }
        int stockDentro = stock(idVariante, 40);
        ConexionBD.hacerRollback();

        String estado = texto("SELECT estado FROM pedidos WHERE id_pedido = ?", idPedido);
        int stockDespues = stock(idVariante, 40);
        comprobar("D1 dentro de la transaccion si habia cambiado", stockDentro == stockAntes - 1,
                "stock " + stockAntes + " -> " + stockDentro + " antes del ROLLBACK");
        comprobar("D2 el ROLLBACK lo deshace todo", estado.equals("pendiente") && stockDespues == stockAntes,
                "estado " + estado + ", stock " + stockDespues);

        UsuarioDAO.login("admin.demo", claveAdmin);
        int eventosDespues = numero("SELECT count(*) FROM log_eventos WHERE tabla_afectada = 'pedidos' "
                + "AND id_registro = ?", idPedido);
        comprobar("D3 la auditoria tambien se deshace", eventosDespues == eventosAntes,
                eventosAntes + " eventos antes y " + eventosDespues + " despues");

        // Era solo para la prueba: se cancela para que no cuente como venta
        UsuarioDAO.login("tienda.demo", claveComercial);
        PedidoDAO.cancelarPedido(idPedido);
    }

    // ------------------------------------------------------------------
    // E: consulta sin filtros, con filtros combinados y "Limpiar filtros"
    // ------------------------------------------------------------------
    private static void pruebaE() throws SQLException {
        titulo("Prueba E: consultas y filtros");
        UsuarioDAO.login("taller.demo", claveTrabajador);
        int total = numero("SELECT count(*) FROM pedidos");
        DefaultTableModel todos = PedidoDAO.buscarPedidos(null, null, null, null, null);
        comprobar("E1 sin filtros", todos.getRowCount() == total, todos.getRowCount() + " filas, SQL " + total);

        int idClub = cliente("club.atletico@example.com");
        DefaultTableModel dos = PedidoDAO.buscarPedidos(idClub, null, "pendiente", null, null);
        int dosSql = numero("SELECT count(*) FROM pedidos WHERE id_cliente = ? AND estado = 'pendiente'", idClub);
        boolean filasCorrectas = true;
        for (int fila = 0; fila < dos.getRowCount(); fila++) {
            if (!dos.getValueAt(fila, 4).equals("pendiente") || !dos.getValueAt(fila, 2).equals("Club Atletico NOVA")) {
                filasCorrectas = false;
            }
        }
        comprobar("E2 dos filtros (cliente y estado)", dos.getRowCount() == dosSql && dosSql > 0 && filasCorrectas,
                dos.getRowCount() + " filas, SQL " + dosSql);

        int idVelocity = numero("SELECT id_modelo FROM modelos WHERE nombre = 'NOVA Velocity'");
        LocalDate hoy = LocalDate.now();
        DefaultTableModel tres = PedidoDAO.buscarPedidos(idClub, idVelocity, null, hoy.minusDays(30), hoy);
        int tresSql = numero("SELECT count(*) FROM pedidos p WHERE p.id_cliente = ? "
                + "AND p.fecha_pedido::date BETWEEN ? AND ? AND EXISTS (SELECT 1 FROM linea_pedido l "
                + "JOIN producto_sku s ON s.id_producto_sku = l.id_producto_sku "
                + "JOIN variantes v ON v.id_variante = s.id_variante "
                + "WHERE l.id_pedido = p.id_pedido AND v.id_modelo = ?)",
                idClub, java.sql.Date.valueOf(hoy.minusDays(30)), java.sql.Date.valueOf(hoy), idVelocity);
        comprobar("E3 tres filtros (cliente, modelo y fechas)", tres.getRowCount() == tresSql,
                tres.getRowCount() + " filas, SQL " + tresSql);

        DefaultTableModel limpio = PedidoDAO.buscarPedidos(null, null, null, null, null);
        comprobar("E4 limpiar filtros vuelve a todo", limpio.getRowCount() == total, limpio.getRowCount() + " filas");
    }

    // ------------------------------------------------------------------
    // F: busqueda sin resultados y perfil sin permiso
    // ------------------------------------------------------------------
    private static void pruebaF() throws SQLException {
        titulo("Prueba F: sin coincidencias y sin permiso");
        UsuarioDAO.login("tienda.demo", claveComercial);
        DefaultTableModel vacio = PedidoDAO.buscarPedidos(null, null, "entregado",
                LocalDate.of(2000, 1, 1), LocalDate.of(2000, 1, 2));
        comprobar("F1 busqueda sin coincidencias", vacio.getRowCount() == 0, "0 filas");

        try {
            PedidoDAO.verAuditoria();
            comprobar("F2 el comercial no ve la auditoria (Java)", false, "la ha visto");
        } catch (SQLException e) {
            comprobar("F2 el comercial no ve la auditoria (Java)", "42501".equals(e.getSQLState()),
                    ConexionBD.mensajeError(e));
        }

        // Interfaz manipulada: Java cree que es administrador, pero la
        // conexion sigue siendo nova_comercial. Lo para PostgreSQL.
        Sesion.iniciar(Sesion.getIdUsuario(), "tienda.demo", "administrador", claveComercial);
        try {
            PedidoDAO.verAuditoria();
            comprobar("F3 PostgreSQL lo deniega aunque se salte Java", false, "la ha visto");
        } catch (SQLException e) {
            comprobar("F3 PostgreSQL lo deniega aunque se salte Java",
                    "42501".equals(e.getSQLState()) && e.getMessage().contains("log_eventos"),
                    ConexionBD.mensajeError(e));
        }
        UsuarioDAO.login("tienda.demo", claveComercial);
    }

    // ------------------------------------------------------------------
    // G: tres consultas = tres lineas nuevas en el TXT
    // ------------------------------------------------------------------
    private static void pruebaG() throws Exception {
        titulo("Prueba G: registro TXT");
        UsuarioDAO.login("taller.demo", claveTrabajador);
        File txt = Archivos.archivo("actividad_sneaker.txt");
        int lineasAntes = Files.readAllLines(txt.toPath(), StandardCharsets.UTF_8).size();

        PedidoDAO.buscarPedidos(null, null, null, null, null);
        PedidoDAO.buscarPedidos(cliente("club.atletico@example.com"), null, "pendiente", null, null);
        PedidoDAO.buscarPedidos(null, null, "entregado", LocalDate.of(2000, 1, 1), LocalDate.of(2000, 1, 2));

        List<String> lineas = Files.readAllLines(txt.toPath(), StandardCharsets.UTF_8);
        boolean correctas = lineas.size() - lineasAntes == 3;
        for (int i = lineasAntes; i < lineas.size(); i++) {
            String linea = lineas.get(i);
            System.out.println("     " + linea);
            if (!linea.contains("| taller.demo | trabajador | CONSULTA PEDIDOS | correcto | ")) {
                correctas = false;
            }
        }
        comprobar("G1 tres consultas, tres lineas nuevas", correctas
                && lineas.get(lineas.size() - 1).contains("| 0 filas;"), (lineas.size() - lineasAntes) + " lineas");
    }

    // ------------------------------------------------------------------
    // H: pedido desde Java + error forzado
    // ------------------------------------------------------------------
    private static void pruebaH() throws Exception {
        titulo("Prueba H: pedido completo y error forzado");
        UsuarioDAO.login("tienda.demo", claveComercial);
        int idVariante = variante("NOVA Eclipse", "Negro");
        int idCliente = cliente("nuria.soto@example.com");
        String referencia = "PRUEBA-H-" + sufijo;
        ArrayList<int[]> lineas = new ArrayList<>();
        lineas.add(new int[] {idVariante, 44, 2});
        int idPedido = PedidoDAO.crearPedido(referencia, idCliente, lineas, false, "");
        PedidoDAO.confirmarPedido(idPedido);

        comprobar("H1 tablas actualizadas",
                texto("SELECT estado || ' ' || importe_total FROM pedidos WHERE id_pedido = ?", idPedido)
                        .equals("confirmado 259.98"), "confirmado, 2 x 129.99");

        DefaultTableModel visual = PedidoDAO.buscarPedidos(idCliente, null, "confirmado", null, null);
        boolean aparece = false;
        for (int fila = 0; fila < visual.getRowCount(); fila++) {
            if (visual.getValueAt(fila, 1).equals(referencia)) {
                aparece = true;
            }
        }
        comprobar("H2 aparece en la consulta visual", aparece, referencia);

        String txt = Files.readString(Archivos.archivo("actividad_sneaker.txt").toPath(), StandardCharsets.UTF_8);
        comprobar("H3 TXT de la creacion y la confirmacion",
                txt.contains("| CREAR PEDIDO | correcto | id_pedido " + idPedido)
                        && txt.contains("| CONFIRMAR PEDIDO | correcto | id_pedido " + idPedido), "las dos lineas estan");

        // Error forzado: la misma referencia otra vez
        try {
            PedidoDAO.crearPedido(referencia, idCliente, lineas, false, "");
            comprobar("H4 error forzado", false, "se ha creado un duplicado");
        } catch (SQLException e) {
            List<String> lineasTxt = Files.readAllLines(Archivos.archivo("actividad_sneaker.txt").toPath(),
                    StandardCharsets.UTF_8);
            String ultima = lineasTxt.get(lineasTxt.size() - 1);
            int iguales = numero("SELECT count(*) FROM pedidos WHERE referencia = ?", referencia);
            comprobar("H4 error forzado: TXT rechazado y ningun pedido nuevo",
                    ultima.contains("| CREAR PEDIDO | rechazado |") && iguales == 1, ConexionBD.mensajeError(e));
        }

        UsuarioDAO.login("admin.demo", claveAdmin);
        int altas = numero("SELECT count(*) FROM log_eventos WHERE accion = 'ALTA' AND detalle LIKE ?",
                "Pedido " + referencia + " %");
        comprobar("H5 en log_eventos solo queda el alta buena", altas == 1, altas + " alta");
    }

    // ------------------------------------------------------------------
    // I: crear, cambiar y desactivar un usuario; JSON y permisos
    // ------------------------------------------------------------------
    private static void pruebaI() throws Exception {
        titulo("Prueba I: usuarios y JSON");
        UsuarioDAO.login("admin.demo", claveAdmin);
        File json = Archivos.archivo("usuarios_sneaker.json");
        String nuevo = "prueba." + sufijo;
        String claveNueva = "Prueba-" + sufijo + "x";

        UsuarioDAO.crearUsuario(nuevo, "comercial", claveNueva);
        int usuariosSql = numero("SELECT count(*) FROM usuarios");
        String contenido = Files.readString(json.toPath(), StandardCharsets.UTF_8);
        comprobar("I1 el usuario nuevo aparece en el JSON",
                contenido.contains("\"username\": \"" + nuevo + "\", \"rol\": \"comercial\", \"activo\": true")
                        && contar(contenido, "\"id_usuario\"") == usuariosSql,
                usuariosSql + " usuarios en el JSON");
        comprobar("I2 el JSON no lleva contrasenas ni hashes",
                !contenido.contains("password") && !contenido.contains("$2a$"), "sin password ni $2a$");

        UsuarioDAO.login(nuevo, claveNueva);
        comprobar("I3 el usuario nuevo puede entrar", Sesion.getRol().equals("comercial"), "rol " + Sesion.getRol());

        UsuarioDAO.login("admin.demo", claveAdmin);
        int idNuevo = numero("SELECT id_usuario FROM usuarios WHERE username = ?", nuevo);
        UsuarioDAO.cambiarRol(idNuevo, "trabajador");
        UsuarioDAO.cambiarActivo(idNuevo, false);
        contenido = Files.readString(json.toPath(), StandardCharsets.UTF_8);
        comprobar("I4 cambio de rol y desactivacion en el JSON, sin perder a nadie",
                contenido.contains("\"username\": \"" + nuevo + "\", \"rol\": \"trabajador\", \"activo\": false")
                        && contar(contenido, "\"id_usuario\"") == usuariosSql,
                usuariosSql + " usuarios en el JSON");

        UsuarioDAO.login("tienda.demo", claveComercial);
        String antes = Files.readString(json.toPath(), StandardCharsets.UTF_8);
        try {
            UsuarioDAO.exportarUsuariosJson();
            comprobar("I5 el comercial no puede exportar", false, "ha exportado");
        } catch (SQLException e) {
            String despues = Files.readString(json.toPath(), StandardCharsets.UTF_8);
            comprobar("I5 el comercial no puede exportar", "42501".equals(e.getSQLState()) && antes.equals(despues),
                    ConexionBD.mensajeError(e));
        }
    }

    // ------------------------------------------------------------------
    // J: indicadores frente a SQL y CSV filtrado frente a la tabla
    // ------------------------------------------------------------------
    private static void pruebaJ() throws Exception {
        titulo("Prueba J: indicadores y CSV filtrado");
        UsuarioDAO.login("admin.demo", claveAdmin);

        DefaultTableModel resumen = IndicadoresDAO.resumen();
        int pedidosSql = numero("SELECT count(*) FROM pedidos WHERE estado <> 'cancelado'");
        int paresSql = numero("SELECT COALESCE(sum(cantidad_total), 0) FROM pedidos WHERE estado <> 'cancelado'");
        BigDecimal importeSql = decimal("SELECT COALESCE(sum(importe_total), 0) FROM pedidos WHERE estado <> 'cancelado'");
        int pedidosPanel = Integer.parseInt(resumen.getValueAt(0, 1).toString());
        int paresPanel = Integer.parseInt(resumen.getValueAt(0, 2).toString());
        BigDecimal importePanel = new BigDecimal(resumen.getValueAt(0, 3).toString());
        comprobar("J1 resumen = SQL (P-A)", pedidosPanel == pedidosSql && paresPanel == paresSql
                && importePanel.compareTo(importeSql) == 0,
                pedidosPanel + " pedidos, " + paresPanel + " pares, " + importePanel + " EUR");

        DefaultTableModel estados = IndicadoresDAO.pedidosPorEstado();
        int sumaEstados = 0;
        for (int fila = 0; fila < estados.getRowCount(); fila++) {
            sumaEstados += Integer.parseInt(estados.getValueAt(fila, 1).toString());
        }
        int totalSql = numero("SELECT count(*) FROM pedidos");
        comprobar("J2 pedidos por estado suman el total", sumaEstados == totalSql, sumaEstados + " = " + totalSql);

        DefaultTableModel tallas = IndicadoresDAO.paresPorTalla();
        int sumaTallas = 0;
        for (int fila = 0; fila < tallas.getRowCount(); fila++) {
            sumaTallas += Integer.parseInt(tallas.getValueAt(fila, 1).toString());
        }
        comprobar("J3 pares por talla suman los pares vendidos", sumaTallas == paresSql, sumaTallas + " = " + paresSql);

        DefaultTableModel modelos = IndicadoresDAO.modelosMasSolicitados();
        int sumaModelos = 0;
        for (int fila = 0; fila < modelos.getRowCount(); fila++) {
            sumaModelos += Integer.parseInt(modelos.getValueAt(fila, 1).toString());
        }
        comprobar("J4 pares por modelo suman los pares vendidos", sumaModelos == paresSql,
                "primero: " + modelos.getValueAt(0, 0) + " con " + modelos.getValueAt(0, 1) + " pares");

        DefaultTableModel stockBajo = IndicadoresDAO.stockBajo(19);
        int stockBajoSql = numero("SELECT count(*) FROM (SELECT s.id_producto_sku FROM producto_sku s "
                + "LEFT JOIN existencias e ON e.id_producto_sku = s.id_producto_sku "
                + "GROUP BY s.id_producto_sku HAVING COALESCE(sum(e.cantidad), 0) < 19) bajo");
        comprobar("J5 stock bajo con umbral 19", stockBajo.getRowCount() == stockBajoSql,
                stockBajo.getRowCount() + " referencias, SQL " + stockBajoSql);

        DefaultTableModel consulta = PedidoDAO.buscarPedidos(null, null, "pendiente", null, null);
        File csv = Archivos.exportarCsv(consulta, "consulta_pedidos.csv");
        List<String> lineasCsv = Files.readAllLines(csv.toPath(), StandardCharsets.UTF_8);
        boolean mismasFilas = lineasCsv.size() == consulta.getRowCount() + 1
                && lineasCsv.get(0).split(",").length == consulta.getColumnCount();
        for (int fila = 0; mismasFilas && fila < consulta.getRowCount(); fila++) {
            if (!lineasCsv.get(fila + 1).startsWith(consulta.getValueAt(fila, 0) + ",")) {
                mismasFilas = false;
            }
        }
        comprobar("J6 CSV = tabla filtrada", mismasFilas, consulta.getRowCount() + " filas y "
                + consulta.getColumnCount() + " columnas en " + csv.getName());
    }

    // ------------------------------------------------------------------
    // Permisos: operacion denegada sin cambiar datos, por Java y por la base
    // ------------------------------------------------------------------
    private static void pruebaPermisos() throws SQLException {
        titulo("Permisos: el trabajador no crea pedidos y el comercial no crea usuarios");
        UsuarioDAO.login("taller.demo", claveTrabajador);
        int pedidosAntes = numero("SELECT count(*) FROM pedidos");
        ArrayList<int[]> lineas = new ArrayList<>();
        lineas.add(new int[] {variante("NOVA Aura", "Rosa"), 40, 1});
        int idCliente = cliente("aitor.parras@example.com");

        try {
            PedidoDAO.crearPedido("PRUEBA-P1-" + sufijo, idCliente, lineas, false, "");
            comprobar("P1 trabajador crea pedido (Java)", false, "lo ha creado");
        } catch (SQLException e) {
            comprobar("P1 trabajador crea pedido (Java)", "42501".equals(e.getSQLState()), ConexionBD.mensajeError(e));
        }

        Sesion.iniciar(Sesion.getIdUsuario(), "taller.demo", "comercial", claveTrabajador);   // interfaz manipulada
        try {
            PedidoDAO.crearPedido("PRUEBA-P2-" + sufijo, idCliente, lineas, false, "");
            comprobar("P2 trabajador crea pedido saltandose Java", false, "lo ha creado");
        } catch (SQLException e) {
            comprobar("P2 trabajador crea pedido saltandose Java", "42501".equals(e.getSQLState()),
                    ConexionBD.mensajeError(e));
        }
        UsuarioDAO.login("taller.demo", claveTrabajador);
        int pedidosDespues = numero("SELECT count(*) FROM pedidos");
        comprobar("P3 ningun pedido nuevo", pedidosDespues == pedidosAntes, pedidosAntes + " -> " + pedidosDespues);

        UsuarioDAO.login("admin.demo", claveAdmin);
        int usuariosAntes = numero("SELECT count(*) FROM usuarios");
        UsuarioDAO.login("tienda.demo", claveComercial);
        Sesion.iniciar(Sesion.getIdUsuario(), "tienda.demo", "administrador", claveComercial);   // manipulada
        try {
            UsuarioDAO.crearUsuario("intruso." + sufijo, "administrador", "Intruso-12345");
            comprobar("P4 comercial crea usuario saltandose Java", false, "lo ha creado");
        } catch (Exception e) {
            String mensaje = e.getMessage();
            if (e instanceof SQLException) {
                mensaje = ConexionBD.mensajeError((SQLException) e);
            }
            comprobar("P4 comercial crea usuario saltandose Java", mensaje.contains("crear_usuario"), mensaje);
        }
        UsuarioDAO.login("admin.demo", claveAdmin);
        int usuariosDespues = numero("SELECT count(*) FROM usuarios");
        comprobar("P5 ningun usuario nuevo", usuariosDespues == usuariosAntes, usuariosAntes + " -> " + usuariosDespues);
    }

    // ------------------------------------------------------------------
    // Ayudas
    // ------------------------------------------------------------------

    private static void titulo(String texto) {
        System.out.println();
        System.out.println("--- " + texto);
    }

    private static void comprobar(String nombre, boolean correcto, String detalle) {
        if (correcto) {
            aciertos++;
            System.out.println("PASS " + nombre + " -> " + detalle);
        } else {
            fallos++;
            System.out.println("FAIL " + nombre + " -> " + detalle);
        }
    }

    /** Primer valor de una consulta, como texto (con el rol de la sesion actual). */
    private static String texto(String sql, Object... parametros) throws SQLException {
        try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql)) {
            for (int i = 0; i < parametros.length; i++) {
                sentencia.setObject(i + 1, parametros[i]);
            }
            try (ResultSet resultado = sentencia.executeQuery()) {
                if (!resultado.next()) {
                    return null;
                }
                return resultado.getString(1);
            }
        }
    }

    private static int numero(String sql, Object... parametros) throws SQLException {
        return Integer.parseInt(texto(sql, parametros));
    }

    private static BigDecimal decimal(String sql, Object... parametros) throws SQLException {
        return new BigDecimal(texto(sql, parametros));
    }

    private static int variante(String modelo, String color) throws SQLException {
        return numero("SELECT v.id_variante FROM variantes v JOIN modelos m ON m.id_modelo = v.id_modelo "
                + "WHERE m.nombre = ? AND v.color = ?", modelo, color);
    }

    private static int cliente(String email) throws SQLException {
        return numero("SELECT id_cliente FROM clientes WHERE email = ?", email);
    }

    private static int stock(int idVariante, int talla) throws SQLException {
        return numero("SELECT COALESCE(sum(e.cantidad), 0) FROM existencias e "
                + "JOIN producto_sku s ON s.id_producto_sku = e.id_producto_sku "
                + "WHERE s.id_variante = ? AND s.talla = ?", idVariante, talla);
    }

    private static int contar(String texto, String buscado) {
        int veces = 0;
        int posicion = texto.indexOf(buscado);
        while (posicion >= 0) {
            veces++;
            posicion = texto.indexOf(buscado, posicion + 1);
        }
        return veces;
    }
}
