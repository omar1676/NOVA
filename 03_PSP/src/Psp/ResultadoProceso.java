package Psp;

public class ResultadoProceso {

    public static final int SIN_RESPUESTA = -1;

    private final int codigoSalida;
    private final String salida;
    private final String errores;

    public ResultadoProceso(int codigoSalida, String salida, String errores) {
        this.codigoSalida = codigoSalida;
        this.salida = salida;
        this.errores = errores;
    }

    public int getCodigoSalida() {
        return codigoSalida;
    }

    public String getSalida() {
        return salida;
    }

    public String getErrores() {
        return errores;
    }

    public boolean esCorrecto() {
        return codigoSalida == AnalizadorTallas.OK && salida.startsWith("OK;");
    }

    public String descripcion() {
        switch (codigoSalida) {
            case AnalizadorTallas.OK:
                return "Correcto";
            case AnalizadorTallas.DATOS_INCORRECTOS:
                return "Datos del pedido incorrectos: " + errores.trim();
            case AnalizadorTallas.ERROR_INESPERADO:
                return "Error inesperado en el proceso hijo: " + errores.trim();
            case SIN_RESPUESTA:
                return "El proceso hijo no respondió a tiempo y se detuvo";
            default:
                return "El proceso hijo falló (código " + codigoSalida + "): " + errores.trim();
        }
    }

    @Override
    public String toString() {
        return "ResultadoProceso{codigo=" + codigoSalida + ", " + descripcion() + "}";
    }
}