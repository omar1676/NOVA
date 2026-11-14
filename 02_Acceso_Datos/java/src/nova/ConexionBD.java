package nova;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;
import javax.swing.table.DefaultTableModel;

public class ConexionBD {

    private static final String ARCHIVO_CONFIGURACION = "conexion.properties";

    private static Properties configuracion;
    private static Connection conexion;

    public static String getPropiedad(String nombre, String valorPorDefecto) {
        if (configuracion == null) {
            configuracion = new Properties();
            try (InputStreamReader lector = new InputStreamReader(
                    new FileInputStream(ARCHIVO_CONFIGURACION), StandardCharsets.UTF_8)) {
                configuracion.load(lector);
            } catch (IOException e) {
                System.err.println("No se encuentra " + ARCHIVO_CONFIGURACION
                        + ". Copia conexion.properties.ejemplo y rellenalo.");
            }
        }
        return configuracion.getProperty(nombre, valorPorDefecto);
    }

    public static Connection getConexion() throws SQLException {
        if (conexion == null || conexion.isClosed()) {
            String url = getPropiedad("url", "jdbc:postgresql://localhost:5432/nova_sneakers");
            String usuario = getPropiedad("usuario", "java_nova");
            String contrasena = getPropiedad("contrasena", "");
            conexion = DriverManager.getConnection(url, usuario, contrasena);

            if (Sesion.haySesion()) {
                usarRol(Sesion.rolPostgres(Sesion.getRol()));
            }
        }
        return conexion;
    }

    public static void usarRol(String rolPostgres) throws SQLException {
        if (!"nova_admin".equals(rolPostgres)
                && !"nova_comercial".equals(rolPostgres)
                && !"nova_trabajador".equals(rolPostgres)) {
            throw new SQLException("Rol de base de datos no valido: " + rolPostgres, "42501");
        }
        try (Statement sentencia = getConexion().createStatement()) {
            sentencia.execute("SET ROLE " + rolPostgres);
        }
    }

    public static void quitarRol() throws SQLException {
        try (Statement sentencia = getConexion().createStatement()) {
            sentencia.execute("RESET ROLE");
        }
    }

    public static Connection empezarTransaccion() throws SQLException {
        Connection con = getConexion();
        con.setAutoCommit(false);
        try (PreparedStatement sentencia = con.prepareStatement("SELECT iniciar_sesion(?, ?)")) {
            sentencia.setString(1, Sesion.getUsuario());
            sentencia.setString(2, Sesion.getContrasena());
            sentencia.executeQuery();
        } catch (SQLException e) {
            hacerRollback();
            throw e;
        }
        return con;
    }

    public static void hacerCommit() throws SQLException {
        conexion.commit();
        conexion.setAutoCommit(true);
    }

    public static void hacerRollback() {
        try {
            if (conexion != null && !conexion.isClosed() && !conexion.getAutoCommit()) {
                conexion.rollback();
                conexion.setAutoCommit(true);
            }
        } catch (SQLException e) {
            System.err.println("No se pudo deshacer la transaccion: " + e.getMessage());
        }
    }

    public static void cerrar() {
        try {
            if (conexion != null) {
                conexion.close();
            }
        } catch (SQLException e) {
            System.err.println("Error al cerrar la conexion: " + e.getMessage());
        }
        conexion = null;
    }

    public static DefaultTableModel crearModelo(ResultSet resultado) throws SQLException {
        ResultSetMetaData columnas = resultado.getMetaData();
        int numeroColumnas = columnas.getColumnCount();

        DefaultTableModel modelo = new DefaultTableModel();
        for (int i = 1; i <= numeroColumnas; i++) {
            modelo.addColumn(columnas.getColumnLabel(i));
        }

        while (resultado.next()) {
            Object[] fila = new Object[numeroColumnas];
            for (int i = 1; i <= numeroColumnas; i++) {
                fila[i - 1] = resultado.getObject(i);
            }
            modelo.addRow(fila);
        }
        return modelo;
    }

    public static String mensajeError(SQLException e) {
        String codigo = e.getSQLState();
        String texto = primeraLinea(e.getMessage());

        if ("42501".equals(codigo)) {
            if (texto.startsWith("Acceso denegado")) {
                return texto;
            }
            return "Acceso denegado: la base de datos no permite esta operación a tu rol (" + texto + ")";
        }
        if ("23505".equals(codigo)) {
            return "Ese dato ya existe y no se puede repetir, por ejemplo la referencia "
                    + "del pedido o el nombre de usuario (" + texto + ")";
        }
        if ("23503".equals(codigo)) {
            return "El registro elegido no existe o está relacionado con otros datos (" + texto + ")";
        }
        if (codigo != null && (codigo.startsWith("22") || codigo.startsWith("23"))) {
            return "Algún dato no es válido para la base de datos (" + texto + ")";
        }
        if ("28P01".equals(codigo)) {
            return "La contraseña de conexión de conexion.properties no es correcta";
        }
        if (codigo != null && codigo.startsWith("08")) {
            return "No se puede conectar con la base de datos.\n"
                    + "Comprueba que PostgreSQL está arrancado y la url de conexion.properties.\n"
                    + "Detalle: " + texto;
        }
        return texto;
    }

    public static String tipoResultado(SQLException e) {
        String codigo = e.getSQLState();
        if (codigo != null
                && (codigo.equals("42501") || codigo.startsWith("P0") || codigo.startsWith("23"))) {
            return "rechazado";
        }
        return "error";
    }

    private static String primeraLinea(String mensaje) {
        if (mensaje == null) {
            return "Error desconocido";
        }
        int salto = mensaje.indexOf('\n');
        if (salto >= 0) {
            mensaje = mensaje.substring(0, salto);
        }
        if (mensaje.startsWith("ERROR:")) {
            mensaje = mensaje.substring("ERROR:".length());
        }
        return mensaje.trim();
    }
}
