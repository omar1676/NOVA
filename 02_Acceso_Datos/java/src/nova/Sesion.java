package nova;

import java.sql.SQLException;

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

    public static void comprobarPermiso(String operacion) throws SQLException {
        if (!puede(operacion)) {
            if (rol == null) {
                throw new SQLException("Acceso denegado: no hay ninguna sesión iniciada", "42501");
            }
            throw new SQLException("Acceso denegado: el rol " + rol + " no puede " + operacion, "42501");
        }
    }

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
