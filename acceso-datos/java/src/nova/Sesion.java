package nova;

import java.sql.SQLException;

/**
 * Quien ha iniciado sesion y que puede hacer.
 *
 * Matriz de permisos de la aplicacion:
 *
 *                               administrador  comercial  trabajador
 *   crear pedidos                    si           si          no
 *   consultar pedidos                si           si          si
 *   confirmar o cancelar pedidos     si           si          si
 *   ver indicadores y stock          si           si          si
 *   ver auditoria (log_eventos)      si           no          no
 *   gestionar usuarios y JSON        si           no          no
 *
 * Esta comprobacion es la primera barrera. La segunda es PostgreSQL: la
 * conexion usa el rol de la base de ese usuario (SET ROLE), y aunque alguien
 * se saltara este metodo, la base rechazaria la operacion.
 */
public class Sesion {

    public static final String CREAR_PEDIDO = "crear pedidos";
    public static final String CONSULTAR = "consultar pedidos";
    public static final String CONFIRMAR_CANCELAR = "confirmar o cancelar pedidos";
    public static final String VER_INDICADORES = "ver indicadores";
    public static final String VER_AUDITORIA = "ver la auditoría";
    public static final String GESTIONAR_USUARIOS = "gestionar usuarios";

    private static int idUsuario;
    private static String usuario;
    private static String rol;

    // Hace falta para llamar a iniciar_sesion al empezar cada transaccion,
    // que es como PostgreSQL sabe quien firma la auditoria. Solo esta en
    // memoria mientras dura la sesion: no se escribe en ningun sitio.
    private static String contrasena;

    public static void iniciar(int id, String nombreUsuario, String nombreRol, String clave) {
        idUsuario = id;
        usuario = nombreUsuario;
        rol = nombreRol;
        contrasena = clave;
    }

    public static void cerrar() {
        idUsuario = 0;
        usuario = null;
        rol = null;
        contrasena = null;
    }

    public static boolean haySesion() {
        return usuario != null;
    }

    public static int getIdUsuario() {
        return idUsuario;
    }

    public static String getUsuario() {
        return usuario;
    }

    public static String getRol() {
        return rol;
    }

    public static String getContrasena() {
        return contrasena;
    }

    /** Aplica la matriz de permisos de arriba. */
    public static boolean puede(String operacion) {
        if (rol == null) {
            return false;
        }
        if (rol.equals("administrador")) {
            return true;
        }
        if (rol.equals("comercial")) {
            return operacion.equals(CREAR_PEDIDO)
                    || operacion.equals(CONSULTAR)
                    || operacion.equals(CONFIRMAR_CANCELAR)
                    || operacion.equals(VER_INDICADORES);
        }
        if (rol.equals("trabajador")) {
            return operacion.equals(CONSULTAR)
                    || operacion.equals(CONFIRMAR_CANCELAR)
                    || operacion.equals(VER_INDICADORES);
        }
        return false;
    }

    /**
     * Se llama al principio de cada operacion de los DAO. Si el rol no
     * puede, lanza el mismo codigo de error que PostgreSQL (42501).
     */
    public static void comprobarPermiso(String operacion) throws SQLException {
        if (!puede(operacion)) {
            throw new SQLException("Acceso denegado: el rol " + rol + " no puede " + operacion, "42501");
        }
    }

    /** Rol de PostgreSQL que corresponde a cada rol de la aplicacion. */
    public static String rolPostgres(String nombreRol) {
        if ("administrador".equals(nombreRol)) {
            return "nova_admin";
        }
        if ("comercial".equals(nombreRol)) {
            return "nova_comercial";
        }
        if ("trabajador".equals(nombreRol)) {
            return "nova_trabajador";
        }
        return null;
    }
}
