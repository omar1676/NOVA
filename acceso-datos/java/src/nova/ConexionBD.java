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

/**
 * La conexion con PostgreSQL y las transacciones.
 *
 * Los datos de conexion estan en conexion.properties, que NO se sube al
 * repositorio (ver conexion.properties.ejemplo). Asi la contrasena no esta
 * en el codigo.
 */
public class ConexionBD {

    private static final String ARCHIVO_CONFIGURACION = "conexion.properties";

    private static Properties configuracion;
    private static Connection conexion;

    /** Lee un valor de conexion.properties. */
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

    /** Devuelve la conexion abierta, o la abre si todavia no existe. */
    public static Connection getConexion() throws SQLException {
        if (conexion == null || conexion.isClosed()) {
            String url = getPropiedad("url", "jdbc:postgresql://localhost:5432/nova_sneakers");
            String usuario = getPropiedad("usuario", "java_nova");
            String contrasena = getPropiedad("contrasena", "");
            conexion = DriverManager.getConnection(url, usuario, contrasena);

            // Si la conexion se habia cortado con una sesion abierta, se
            // vuelve a poner el rol del usuario.
            if (Sesion.haySesion()) {
                usarRol(Sesion.rolPostgres(Sesion.getRol()));
            }
        }
        return conexion;
    }

    /**
     * Cambia el rol de PostgreSQL de la conexion (SET ROLE).
     *
     * SET ROLE no admite parametros con ?, asi que solo se aceptan estos
     * tres nombres fijos. Nunca llega aqui texto escrito por el usuario.
     */
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

    /** Vuelve al usuario de conexion, que sin rol no tiene permisos. */
    public static void quitarRol() throws SQLException {
        try (Statement sentencia = getConexion().createStatement()) {
            sentencia.execute("RESET ROLE");
        }
    }

    /**
     * Empieza una transaccion que va a escribir.
     *
     * Lo primero es iniciar_sesion: asi los triggers de auditoria saben que
     * usuario hace la operacion y lo guardan en log_eventos. Ese dato solo
     * dura hasta el COMMIT o el ROLLBACK, por eso se repite en cada una.
     */
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

    /** Deshace la transaccion en curso. Si no habia ninguna, no hace nada. */
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

    /**
     * Copia el resultado de una consulta en un modelo de JTable. Los nombres
     * de las columnas salen de los alias de la consulta (AS "Cliente").
     */
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

    /** Convierte un error de la base de datos en un mensaje que se entiende. */
    public static String mensajeError(SQLException e) {
        String codigo = e.getSQLState();
        String texto = primeraLinea(e.getMessage());

        if ("42501".equals(codigo)) {
            if (texto.startsWith("Acceso denegado")) {
                return texto;                       // lo ha denegado Java
            }
            return "Acceso denegado por PostgreSQL: " + texto;
        }
        if ("23505".equals(codigo)) {
            return "Ya existe un registro con ese valor: " + texto;
        }
        if ("28P01".equals(codigo)) {
            return "La contraseña de conexión de conexion.properties no es correcta";
        }
        if (codigo != null && codigo.startsWith("08")) {
            return "No se puede conectar con la base de datos: " + texto;
        }
        return texto;
    }

    /**
     * "rechazado" si la base o Java han dicho que no (permiso, regla de
     * negocio, restriccion), "error" si algo ha fallado de verdad.
     *
     * P0001 es el codigo de RAISE EXCEPTION en PL/pgSQL, 23xxx el de las
     * restricciones (UNIQUE, CHECK...) y 42501 el de permiso denegado.
     */
    public static String tipoResultado(SQLException e) {
        String codigo = e.getSQLState();
        if (codigo != null
                && (codigo.equals("42501") || codigo.startsWith("P0") || codigo.startsWith("23"))) {
            return "rechazado";
        }
        return "error";
    }

    /** Quita el "ERROR:" del principio y las lineas de contexto del final. */
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
