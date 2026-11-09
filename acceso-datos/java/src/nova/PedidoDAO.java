package nova;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.util.ArrayList;
import javax.swing.table.DefaultTableModel;

/**
 * Todo lo que tiene que ver con pedidos: crearlos, confirmarlos,
 * cancelarlos y consultarlos.
 *
 * Java NO calcula importes ni toca el stock ni escribe la auditoria: eso lo
 * hacen los triggers de PostgreSQL. Java llama a las funciones de la base y
 * cambia el estado del pedido.
 */
public class PedidoDAO {

    // ------------------------------------------------------------------
    // Listas para los JComboBox
    // ------------------------------------------------------------------

    public static ArrayList<Opcion> listarClientes() throws SQLException {
        return listarOpciones("SELECT id_cliente AS id, nombre AS texto FROM clientes "
                + "WHERE activo ORDER BY nombre");
    }

    public static ArrayList<Opcion> listarModelos() throws SQLException {
        return listarOpciones("SELECT id_modelo AS id, nombre AS texto FROM modelos ORDER BY nombre");
    }

    /** Modelo y color juntos, porque el color es lo que distingue una variante. */
    public static ArrayList<Opcion> listarVariantes() throws SQLException {
        return listarOpciones("SELECT v.id_variante AS id, m.nombre || ' - ' || v.color AS texto "
                + "FROM variantes v JOIN modelos m ON m.id_modelo = v.id_modelo "
                + "WHERE m.activo ORDER BY m.nombre, v.color");
    }

    private static ArrayList<Opcion> listarOpciones(String sql) throws SQLException {
        ArrayList<Opcion> opciones = new ArrayList<>();
        try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql);
             ResultSet resultado = sentencia.executeQuery()) {
            while (resultado.next()) {
                opciones.add(new Opcion(resultado.getInt("id"), resultado.getString("texto")));
            }
        }
        return opciones;
    }

    // ------------------------------------------------------------------
    // Crear un pedido
    // ------------------------------------------------------------------

    /**
     * Crea un pedido con todas sus lineas en UNA sola transaccion: o se
     * guarda entero o no se guarda nada.
     *
     * Cada linea es un int[] con {idVariante, talla, cantidad}.
     *
     * El pedido queda pendiente. El stock no se toca hasta confirmarlo.
     */
    public static int crearPedido(String referencia, int idCliente, ArrayList<int[]> lineas,
                                  boolean custom, String personalizacion) throws SQLException {
        String detalle = "referencia " + referencia + ", " + lineas.size() + " lineas";
        int idPedido = 0;
        try {
            Sesion.comprobarPermiso(Sesion.CREAR_PEDIDO);
            if (lineas.isEmpty()) {
                throw new SQLException("El pedido necesita al menos una línea", "P0001");
            }

            Connection conexion = ConexionBD.empezarTransaccion();
            int idNave = buscarNave(conexion);

            for (int i = 0; i < lineas.size(); i++) {
                int[] linea = lineas.get(i);
                int idSku = buscarSku(conexion, linea[0], linea[1]);
                if (i == 0) {
                    // La primera linea crea la cabecera del pedido
                    idPedido = realizarCompra(conexion, referencia, idCliente, idSku, idNave, linea[2]);
                } else {
                    anadirLinea(conexion, idPedido, idSku, idNave, linea[2]);
                }
            }

            if (custom) {
                marcarCustom(conexion, idPedido, personalizacion);
            }
            ConexionBD.hacerCommit();
        } catch (SQLException e) {
            ConexionBD.hacerRollback();
            Archivos.registrar("CREAR PEDIDO", ConexionBD.tipoResultado(e),
                    detalle + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
        Archivos.registrar("CREAR PEDIDO", "correcto", "id_pedido " + idPedido + ", " + detalle);
        return idPedido;
    }

    /** Solo hay una nave (NOVA Central): se usa la primera. */
    private static int buscarNave(Connection conexion) throws SQLException {
        String sql = "SELECT id_nave FROM nave ORDER BY id_nave LIMIT 1";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql);
             ResultSet resultado = sentencia.executeQuery()) {
            if (!resultado.next()) {
                throw new SQLException("No hay ninguna nave dada de alta", "P0001");
            }
            return resultado.getInt("id_nave");
        }
    }

    /** El SKU es la combinacion de variante (modelo + color) y talla. */
    private static int buscarSku(Connection conexion, int idVariante, int talla) throws SQLException {
        String sql = "SELECT id_producto_sku FROM producto_sku "
                + "WHERE id_variante = ? AND talla = ? AND activo";
        try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setInt(1, idVariante);
            sentencia.setInt(2, talla);
            try (ResultSet resultado = sentencia.executeQuery()) {
                if (!resultado.next()) {
                    throw new SQLException("No existe la talla " + talla + " para ese modelo y color", "P0001");
                }
                return resultado.getInt("id_producto_sku");
            }
        }
    }

    /** realizar_compra crea la cabecera y su primera linea. Devuelve el id. */
    private static int realizarCompra(Connection conexion, String referencia, int idCliente,
                                      int idSku, int idNave, int cantidad) throws SQLException {
        try (PreparedStatement sentencia = conexion.prepareStatement(
                "SELECT realizar_compra(?, ?, ?, ?, ?, ?) AS id_pedido")) {
            sentencia.setString(1, referencia);
            sentencia.setInt(2, idCliente);
            sentencia.setInt(3, idSku);
            sentencia.setInt(4, idNave);
            sentencia.setInt(5, cantidad);
            sentencia.setInt(6, Sesion.getIdUsuario());
            try (ResultSet resultado = sentencia.executeQuery()) {
                resultado.next();
                return resultado.getInt("id_pedido");
            }
        }
    }

    private static void anadirLinea(Connection conexion, int idPedido, int idSku,
                                    int idNave, int cantidad) throws SQLException {
        try (PreparedStatement sentencia = conexion.prepareStatement(
                "SELECT anadir_linea_pedido(?, ?, ?, ?)")) {
            sentencia.setInt(1, idPedido);
            sentencia.setInt(2, idSku);
            sentencia.setInt(3, idNave);
            sentencia.setInt(4, cantidad);
            sentencia.executeQuery();
        }
    }

    private static void marcarCustom(Connection conexion, int idPedido, String personalizacion)
            throws SQLException {
        try (PreparedStatement sentencia = conexion.prepareStatement(
                "UPDATE pedidos SET personalizado = true, personalizacion = ? WHERE id_pedido = ?")) {
            sentencia.setString(1, personalizacion);
            sentencia.setInt(2, idPedido);
            sentencia.executeUpdate();
        }
    }

    // ------------------------------------------------------------------
    // Confirmar y cancelar
    // ------------------------------------------------------------------

    /**
     * Al confirmar, un trigger descuenta el stock de cada linea. Si no hay
     * bastante, PostgreSQL lanza un error y se deshace todo.
     */
    public static void confirmarPedido(int idPedido) throws SQLException {
        String sql = "UPDATE pedidos SET estado = 'confirmado' "
                + "WHERE id_pedido = ? AND estado = 'pendiente'";
        cambiarEstado(idPedido, sql, "CONFIRMAR PEDIDO", "Solo se puede confirmar un pedido pendiente");
    }

    /** Al cancelar, un trigger devuelve al almacen el stock descontado. */
    public static void cancelarPedido(int idPedido) throws SQLException {
        String sql = "UPDATE pedidos SET estado = 'cancelado' "
                + "WHERE id_pedido = ? AND estado IN ('pendiente', 'confirmado')";
        cambiarEstado(idPedido, sql, "CANCELAR PEDIDO",
                "Solo se puede cancelar un pedido pendiente o confirmado");
    }

    private static void cambiarEstado(int idPedido, String sql, String accion,
                                      String mensajeSiNoCambia) throws SQLException {
        try {
            Sesion.comprobarPermiso(Sesion.CONFIRMAR_CANCELAR);
            Connection conexion = ConexionBD.empezarTransaccion();
            int filas;
            try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
                sentencia.setInt(1, idPedido);
                filas = sentencia.executeUpdate();
            }
            if (filas == 0) {
                throw new SQLException(mensajeSiNoCambia, "P0001");
            }
            ConexionBD.hacerCommit();
        } catch (SQLException e) {
            ConexionBD.hacerRollback();
            Archivos.registrar(accion, ConexionBD.tipoResultado(e),
                    "id_pedido " + idPedido + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
        Archivos.registrar(accion, "correcto", "id_pedido " + idPedido);
    }

    // ------------------------------------------------------------------
    // Consultas
    // ------------------------------------------------------------------

    /**
     * Busca pedidos. Un filtro que vale null no se aplica, asi que con todo
     * a null salen todos los pedidos.
     *
     * Solo se anade al WHERE el trozo de cada filtro que se usa, y su valor
     * va siempre como parametro (?), nunca pegado al texto del SQL.
     */
    public static DefaultTableModel buscarPedidos(Integer idCliente, Integer idModelo, String estado,
                                                  LocalDate desde, LocalDate hasta) throws SQLException {
        String filtros = "cliente=" + idCliente + ", modelo=" + idModelo + ", estado=" + estado
                + ", desde=" + desde + ", hasta=" + hasta;
        try {
            Sesion.comprobarPermiso(Sesion.CONSULTAR);

            String sql = "SELECT p.id_pedido AS \"Id\", p.referencia AS \"Referencia\", "
                    + "c.nombre AS \"Cliente\", to_char(p.fecha_pedido, 'YYYY-MM-DD HH24:MI') AS \"Fecha\", "
                    + "p.estado AS \"Estado\", "
                    + "CASE WHEN p.personalizado THEN 'Custom' ELSE 'Normal' END AS \"Tipo\", "
                    + "p.cantidad_total AS \"Pares\", p.importe_total AS \"Importe\", "
                    + "p.personalizacion AS \"Personalizacion\" "
                    + "FROM pedidos p JOIN clientes c ON c.id_cliente = p.id_cliente "
                    + "WHERE 1 = 1";
            ArrayList<Object> parametros = new ArrayList<>();

            if (idCliente != null) {
                sql += " AND p.id_cliente = ?";
                parametros.add(idCliente);
            }
            if (idModelo != null) {
                // El modelo esta en las lineas: basta con que una sea de ese modelo
                sql += " AND EXISTS (SELECT 1 FROM linea_pedido l"
                        + " JOIN producto_sku s ON s.id_producto_sku = l.id_producto_sku"
                        + " JOIN variantes v ON v.id_variante = s.id_variante"
                        + " WHERE l.id_pedido = p.id_pedido AND v.id_modelo = ?)";
                parametros.add(idModelo);
            }
            if (estado != null) {
                sql += " AND p.estado = ?";
                parametros.add(estado);
            }
            if (desde != null) {
                sql += " AND p.fecha_pedido::date >= ?";
                parametros.add(java.sql.Date.valueOf(desde));
            }
            if (hasta != null) {
                sql += " AND p.fecha_pedido::date <= ?";
                parametros.add(java.sql.Date.valueOf(hasta));
            }
            sql += " ORDER BY p.id_pedido DESC";

            try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql)) {
                for (int i = 0; i < parametros.size(); i++) {
                    sentencia.setObject(i + 1, parametros.get(i));
                }
                try (ResultSet resultado = sentencia.executeQuery()) {
                    DefaultTableModel modelo = ConexionBD.crearModelo(resultado);
                    Archivos.registrar("CONSULTA PEDIDOS", "correcto",
                            modelo.getRowCount() + " filas; " + filtros);
                    return modelo;
                }
            }
        } catch (SQLException e) {
            Archivos.registrar("CONSULTA PEDIDOS", ConexionBD.tipoResultado(e),
                    filtros + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
    }

    /** Las lineas de un pedido. */
    public static DefaultTableModel verDetalle(int idPedido) throws SQLException {
        try {
            Sesion.comprobarPermiso(Sesion.CONSULTAR);
            String sql = "SELECT COALESCE(m.nombre, 'X-NOVA') AS \"Modelo\", v.color AS \"Color\", "
                    + "s.talla AS \"Talla\", l.cantidad AS \"Cantidad\", "
                    + "l.precio_unitario AS \"Precio\", l.subtotal AS \"Subtotal\", "
                    + "l.stock_descontado AS \"Stock descontado\" "
                    + "FROM linea_pedido l "
                    + "LEFT JOIN producto_sku s ON s.id_producto_sku = l.id_producto_sku "
                    + "LEFT JOIN variantes v ON v.id_variante = s.id_variante "
                    + "LEFT JOIN modelos m ON m.id_modelo = v.id_modelo "
                    + "WHERE l.id_pedido = ? ORDER BY l.id_linea";
            try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql)) {
                sentencia.setInt(1, idPedido);
                try (ResultSet resultado = sentencia.executeQuery()) {
                    DefaultTableModel modelo = ConexionBD.crearModelo(resultado);
                    Archivos.registrar("DETALLE PEDIDO", "correcto",
                            "id_pedido " + idPedido + ", " + modelo.getRowCount() + " lineas");
                    return modelo;
                }
            }
        } catch (SQLException e) {
            Archivos.registrar("DETALLE PEDIDO", ConexionBD.tipoResultado(e),
                    "id_pedido " + idPedido + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
    }

    /** Los ultimos eventos de log_eventos. Solo el administrador. */
    public static DefaultTableModel verAuditoria() throws SQLException {
        try {
            Sesion.comprobarPermiso(Sesion.VER_AUDITORIA);
            String sql = "SELECT to_char(e.fecha_hora, 'YYYY-MM-DD HH24:MI:SS') AS \"Fecha y hora\", "
                    + "COALESCE(u.username, '(sin sesion)') AS \"Usuario\", e.accion AS \"Accion\", "
                    + "e.tabla_afectada AS \"Tabla\", e.id_registro AS \"Registro\", e.detalle AS \"Detalle\" "
                    + "FROM log_eventos e LEFT JOIN usuarios u ON u.id_usuario = e.id_usuario "
                    + "ORDER BY e.id_evento DESC LIMIT 100";
            try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql);
                 ResultSet resultado = sentencia.executeQuery()) {
                DefaultTableModel modelo = ConexionBD.crearModelo(resultado);
                Archivos.registrar("VER AUDITORIA", "correcto", modelo.getRowCount() + " eventos");
                return modelo;
            }
        } catch (SQLException e) {
            Archivos.registrar("VER AUDITORIA", ConexionBD.tipoResultado(e), ConexionBD.mensajeError(e));
            throw e;
        }
    }
}
