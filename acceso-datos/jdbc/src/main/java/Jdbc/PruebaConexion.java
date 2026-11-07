package Jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class PruebaConexion {

    public static void main(String[] args) {
        String sql = "SELECT COUNT(*) FROM pedidos";
        try (Connection con = Conexion.obtener();
             PreparedStatement ps = con.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            rs.next();
            System.out.println("Conexión correcta con la base de datos " + con.getCatalog());
            System.out.println("Pedidos en la base de datos: " + rs.getInt(1));
        } catch (SQLException e) {
            System.out.println("No se ha podido conectar: " + e.getMessage());
        }
    }
}