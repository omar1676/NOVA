package Jdbc;

import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public class Conexion {

    private static final Properties config = new Properties();

    static {
        try (InputStream in = Conexion.class.getClassLoader().getResourceAsStream("db.properties")) {
            if (in == null) {
                throw new IllegalStateException("No se encuentra el archivo db.properties");
            }
            config.load(in);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public static Connection obtener() throws SQLException {
        return DriverManager.getConnection(
                config.getProperty("url"),
                config.getProperty("usuario"),
                config.getProperty("password"));
    }
}