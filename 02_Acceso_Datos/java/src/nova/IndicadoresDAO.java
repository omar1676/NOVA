package nova;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import javax.swing.table.DefaultTableModel;

public class IndicadoresDAO {

    public static DefaultTableModel resumen() throws SQLException {
        return consultar("SELECT count(*) AS \"Pedidos (todos)\", "
                + "count(CASE WHEN estado <> 'cancelado' THEN 1 END) AS \"Pedidos sin cancelar\", "
                + "COALESCE(sum(CASE WHEN estado <> 'cancelado' THEN cantidad_total END), 0) AS \"Pares\", "
                + "COALESCE(sum(CASE WHEN estado <> 'cancelado' THEN importe_total END), 0) AS \"Importe ventas\" "
                + "FROM pedidos", null);
    }

    public static DefaultTableModel pedidosPorEstado() throws SQLException {
        return consultar("SELECT estado AS \"Estado\", count(*) AS \"Pedidos\", "
                + "COALESCE(sum(cantidad_total), 0) AS \"Pares\", "
                + "COALESCE(sum(importe_total), 0) AS \"Importe\" "
                + "FROM pedidos GROUP BY estado ORDER BY count(*) DESC, estado", null);
    }

    public static DefaultTableModel modelosMasSolicitados() throws SQLException {
        return consultar("SELECT COALESCE(m.nombre, 'X-NOVA') AS \"Modelo\", "
                + "sum(l.cantidad) AS \"Pares\", count(DISTINCT l.id_pedido) AS \"Pedidos\" "
                + "FROM linea_pedido l "
                + "JOIN pedidos p ON p.id_pedido = l.id_pedido "
                + "LEFT JOIN producto_sku s ON s.id_producto_sku = l.id_producto_sku "
                + "LEFT JOIN variantes v ON v.id_variante = s.id_variante "
                + "LEFT JOIN modelos m ON m.id_modelo = v.id_modelo "
                + "WHERE p.estado <> 'cancelado' "
                + "GROUP BY COALESCE(m.nombre, 'X-NOVA') "
                + "ORDER BY sum(l.cantidad) DESC, COALESCE(m.nombre, 'X-NOVA')", null);
    }

    public static DefaultTableModel paresPorTalla() throws SQLException {
        return consultar("SELECT COALESCE(s.talla, x.talla_referencia) AS \"Talla\", "
                + "sum(l.cantidad) AS \"Pares\", count(DISTINCT l.id_pedido) AS \"Pedidos\" "
                + "FROM linea_pedido l "
                + "JOIN pedidos p ON p.id_pedido = l.id_pedido "
                + "LEFT JOIN producto_sku s ON s.id_producto_sku = l.id_producto_sku "
                + "LEFT JOIN configuraciones_xnova x ON x.id_configuracion = l.id_configuracion_xnova "
                + "WHERE p.estado <> 'cancelado' "
                + "GROUP BY COALESCE(s.talla, x.talla_referencia) ORDER BY 1", null);
    }

    public static DefaultTableModel stockBajo(int umbral) throws SQLException {
        return consultar("SELECT m.nombre AS \"Modelo\", v.color AS \"Color\", s.talla AS \"Talla\", "
                + "s.sku AS \"SKU\", COALESCE(sum(e.cantidad), 0) AS \"Stock\" "
                + "FROM producto_sku s "
                + "JOIN variantes v ON v.id_variante = s.id_variante "
                + "JOIN modelos m ON m.id_modelo = v.id_modelo "
                + "LEFT JOIN existencias e ON e.id_producto_sku = s.id_producto_sku "
                + "GROUP BY m.nombre, v.color, s.talla, s.sku "
                + "HAVING COALESCE(sum(e.cantidad), 0) < ? "
                + "ORDER BY COALESCE(sum(e.cantidad), 0), m.nombre, v.color, s.talla", umbral);
    }

    private static DefaultTableModel consultar(String sql, Integer parametro) throws SQLException {
        Sesion.comprobarPermiso(Sesion.VER_INDICADORES);
        try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql)) {
            if (parametro != null) {
                sentencia.setInt(1, parametro);
            }
            try (ResultSet resultado = sentencia.executeQuery()) {
                return ConexionBD.crearModelo(resultado);
            }
        }
    }
}
