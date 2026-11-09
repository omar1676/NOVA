package nova;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import javax.swing.table.DefaultTableModel;

/**
 * Inicio de sesion y gestion de usuarios.
 *
 * Las contrasenas las comprueba y las cifra PostgreSQL con bcrypt
 * (iniciar_sesion y establecer_password). Java nunca ve un hash.
 */
public class UsuarioDAO {

    // ------------------------------------------------------------------
    // Inicio y cierre de sesion
    // ------------------------------------------------------------------

    /**
     * 1. iniciar_sesion compara la contrasena con el hash bcrypt. Si no
     *    coincide, PostgreSQL lanza "Usuario o contrasena incorrectos".
     * 2. Se lee el rol del usuario.
     * 3. SET ROLE: desde aqui la conexion solo tiene los permisos de ese rol.
     */
    public static void login(String usuario, String contrasena) throws SQLException {
        try {
            Connection conexion = ConexionBD.getConexion();

            // Por si habia otra sesion abierta en esta misma conexion
            Sesion.cerrar();
            ConexionBD.quitarRol();

            int idUsuario;
            try (PreparedStatement sentencia = conexion.prepareStatement(
                    "SELECT iniciar_sesion(?, ?) AS id_usuario")) {
                sentencia.setString(1, usuario);
                sentencia.setString(2, contrasena);
                try (ResultSet resultado = sentencia.executeQuery()) {
                    resultado.next();
                    idUsuario = resultado.getInt("id_usuario");
                }
            }

            String rol;
            try (PreparedStatement sentencia = conexion.prepareStatement(
                    "SELECT r.nombre FROM usuarios u JOIN roles r ON r.id_rol = u.id_rol "
                    + "WHERE u.id_usuario = ?")) {
                sentencia.setInt(1, idUsuario);
                try (ResultSet resultado = sentencia.executeQuery()) {
                    resultado.next();
                    rol = resultado.getString("nombre");
                }
            }

            String rolPostgres = Sesion.rolPostgres(rol);
            if (rolPostgres == null) {
                throw new SQLException("Acceso denegado: el rol " + rol + " no usa esta aplicacion", "42501");
            }
            ConexionBD.usarRol(rolPostgres);
            Sesion.iniciar(idUsuario, usuario, rol, contrasena);
            Archivos.registrar("LOGIN", "correcto", "conectado como " + rolPostgres);
        } catch (SQLException e) {
            Archivos.registrar("LOGIN", ConexionBD.tipoResultado(e),
                    "usuario intentado " + usuario + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
    }

    public static void logout() {
        if (Sesion.haySesion()) {
            Archivos.registrar("LOGOUT", "correcto", "");
        }
        Sesion.cerrar();
        try {
            ConexionBD.quitarRol();
        } catch (SQLException e) {
            System.err.println("No se pudo quitar el rol: " + e.getMessage());
        }
    }

    // ------------------------------------------------------------------
    // Consultar usuarios (solo administrador)
    // ------------------------------------------------------------------

    /** Lista de usuarios, sin la columna password_hash. */
    public static DefaultTableModel listarUsuarios() throws SQLException {
        Sesion.comprobarPermiso(Sesion.GESTIONAR_USUARIOS);
        String sql = "SELECT u.id_usuario, u.username, r.nombre AS rol, u.activo "
                + "FROM usuarios u JOIN roles r ON r.id_rol = u.id_rol ORDER BY u.id_usuario";
        try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(sql);
             ResultSet resultado = sentencia.executeQuery()) {
            return ConexionBD.crearModelo(resultado);
        }
    }

    public static ArrayList<String> listarRoles() throws SQLException {
        Sesion.comprobarPermiso(Sesion.GESTIONAR_USUARIOS);
        ArrayList<String> roles = new ArrayList<>();
        try (PreparedStatement sentencia = ConexionBD.getConexion().prepareStatement(
                "SELECT nombre FROM roles ORDER BY nombre");
             ResultSet resultado = sentencia.executeQuery()) {
            while (resultado.next()) {
                roles.add(resultado.getString("nombre"));
            }
        }
        return roles;
    }

    // ------------------------------------------------------------------
    // Cambios (solo administrador). Despues de cada cambio confirmado se
    // vuelve a generar usuarios_sneaker.json.
    // ------------------------------------------------------------------

    /**
     * crear_usuario lo da de alta sin contrasena y establecer_password le
     * pone el hash bcrypt. Van en la misma transaccion: o las dos o ninguna.
     */
    public static void crearUsuario(String usuario, String rol, String contrasena)
            throws SQLException, IOException {
        String detalle = "usuario " + usuario + ", rol " + rol;
        try {
            Sesion.comprobarPermiso(Sesion.GESTIONAR_USUARIOS);
            Connection conexion = ConexionBD.empezarTransaccion();
            try (PreparedStatement sentencia = conexion.prepareStatement("SELECT crear_usuario(?, ?)")) {
                sentencia.setString(1, usuario);
                sentencia.setString(2, rol);
                sentencia.executeQuery();
            }
            try (PreparedStatement sentencia = conexion.prepareStatement("SELECT establecer_password(?, ?)")) {
                sentencia.setString(1, usuario);
                sentencia.setString(2, contrasena);
                sentencia.executeQuery();
            }
            ConexionBD.hacerCommit();
        } catch (SQLException e) {
            ConexionBD.hacerRollback();
            Archivos.registrar("CREAR USUARIO", ConexionBD.tipoResultado(e),
                    detalle + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
        Archivos.registrar("CREAR USUARIO", "correcto", detalle);
        exportarUsuariosJson();
    }

    public static void cambiarRol(int idUsuario, String rol) throws SQLException, IOException {
        modificarUsuario("UPDATE usuarios SET id_rol = (SELECT id_rol FROM roles WHERE nombre = ?) "
                + "WHERE id_usuario = ?", rol, idUsuario, "CAMBIAR ROL", "id_usuario " + idUsuario + " a " + rol);
    }

    public static void cambiarActivo(int idUsuario, boolean activo) throws SQLException, IOException {
        String accion = "ACTIVAR USUARIO";
        if (!activo) {
            accion = "DESACTIVAR USUARIO";
        }
        modificarUsuario("UPDATE usuarios SET activo = ? WHERE id_usuario = ?",
                activo, idUsuario, accion, "id_usuario " + idUsuario);
    }

    /** Un UPDATE sobre un usuario: un valor y el id_usuario. */
    private static void modificarUsuario(String sql, Object valor, int idUsuario,
                                         String accion, String detalle) throws SQLException, IOException {
        try {
            Sesion.comprobarPermiso(Sesion.GESTIONAR_USUARIOS);
            // Para no quedarse sin administrador por error
            if (idUsuario == Sesion.getIdUsuario()) {
                throw new SQLException("No puedes cambiar tu propio usuario mientras lo estás usando", "P0001");
            }
            Connection conexion = ConexionBD.empezarTransaccion();
            int filas;
            try (PreparedStatement sentencia = conexion.prepareStatement(sql)) {
                sentencia.setObject(1, valor);
                sentencia.setInt(2, idUsuario);
                filas = sentencia.executeUpdate();
            }
            if (filas == 0) {
                throw new SQLException("El usuario no existe", "P0001");
            }
            ConexionBD.hacerCommit();
        } catch (SQLException e) {
            ConexionBD.hacerRollback();
            Archivos.registrar(accion, ConexionBD.tipoResultado(e), detalle + "; " + ConexionBD.mensajeError(e));
            throw e;
        }
        Archivos.registrar(accion, "correcto", detalle);
        exportarUsuariosJson();
    }

    // ------------------------------------------------------------------
    // usuarios_sneaker.json
    // ------------------------------------------------------------------

    /**
     * Exporta los usuarios tal y como estan confirmados en la base. Solo se
     * llama despues de un COMMIT, asi que nunca publica un cambio deshecho.
     */
    public static File exportarUsuariosJson() throws SQLException, IOException {
        try {
            DefaultTableModel usuarios = listarUsuarios();
            File archivo = Archivos.guardarUsuariosJson(usuarios);
            Archivos.registrar("EXPORTAR USUARIOS JSON", "correcto", usuarios.getRowCount() + " usuarios");
            return archivo;
        } catch (SQLException e) {
            Archivos.registrar("EXPORTAR USUARIOS JSON", ConexionBD.tipoResultado(e), ConexionBD.mensajeError(e));
            throw e;
        } catch (IOException e) {
            Archivos.registrar("EXPORTAR USUARIOS JSON", "error", e.getMessage());
            throw e;
        }
    }
}
