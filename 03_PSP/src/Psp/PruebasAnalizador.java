package Psp;

public class PruebasAnalizador {

    private static int superadas = 0;
    private static int fallidas = 0;

    public static void main(String[] args) throws Exception {

        System.out.println("PRUEBA POSITIVA: pedido correcto, debe aceptarse");

        ResultadoProceso r = LanzadorAnalizador.analizar(
                "PEDIDO;NOVA-0001\n"
                        + "LINEA;ADI-ZA-NE-42;Adidos Zamba;Negro;42;2\n"
                        + "LINEA;NOK-AM-BL-42;Nokia Air Maximo;Blanco;42;1\n"
                        + "LINEA;ADI-ZA-NE-43;Adidos Zamba;Negro;43;1\n"
                        + "LINEA;ADI-ZA-NE-42;Adidos Zamba;Negro;42;1\n"
                        + "FIN\n");
        boolean aceptado = r.esCorrecto()
                && r.getSalida().contains("VARIANTE_TALLA;Adidos Zamba;Negro;42;3")
                && r.getSalida().contains("TALLA;42;4")
                && r.getSalida().contains("TOTAL;5");
        if (aceptado) {
            superadas++;
            System.out.println("[SUPERADA] Pedido correcto -> aceptado. Resultado del análisis:");
            System.out.println(r.getSalida());
        } else {
            fallidas++;
            System.out.println("[FALLIDA]  Pedido correcto -> " + r);
        }

        System.out.println("=== PRUEBAS NEGATIVAS: datos incorrectos a propósito, deben rechazarse ===");

        r = LanzadorAnalizador.analizar(
                "PEDIDO;NOVA-0002\n"
                        + "LINEA;ADI-ZA-NE-42;Adidos Zamba;Negro;42\n"
                        + "FIN\n");
        comprobarRechazo("Datos incompletos", r, AnalizadorTallas.DATOS_INCORRECTOS);

        r = LanzadorAnalizador.analizar(
                "PEDIDO;NOVA-0003\n"
                        + "LINEA;ADI-ZA-NE-42;Adidos Zamba;Negro;42;0\n"
                        + "FIN\n");
        comprobarRechazo("Cantidad cero", r, AnalizadorTallas.DATOS_INCORRECTOS);

        r = LanzadorAnalizador.analizar(
                "PEDIDO;NOVA-0004\n"
                        + "LINEA;ADI-ZA-NE-42;Adidos Zamba;Negro;42;dos\n"
                        + "FIN\n");
        comprobarRechazo("Cantidad no numérica", r, AnalizadorTallas.DATOS_INCORRECTOS);

        r = LanzadorAnalizador.analizar("hola\nFIN\n");
        comprobarRechazo("Entrada incorrecta", r, AnalizadorTallas.DATOS_INCORRECTOS);

        r = LanzadorAnalizador.analizar(
                "PEDIDO;NOVA-0005\n"
                        + "LINEA;ADI-ZA-NE-42;Adidos Zamba;Negro;42;1\n");
        comprobarRechazo("Falta FIN", r, AnalizadorTallas.DATOS_INCORRECTOS);

        r = LanzadorAnalizador.analizar(
                "PEDIDO;NOVA-0006\n"
                        + "LINEA;ADI-ZA-NE-99;Adidos Zamba;Negro;99;1\n"
                        + "FIN\n");
        comprobarRechazo("Talla fuera de rango", r, AnalizadorTallas.DATOS_INCORRECTOS);

        System.out.println(" PRUEBA DE FALLO DEL PROCESO HIJO: el hijo no arranca, debe detectarse ");

        r = LanzadorAnalizador.lanzar("Psp.ClaseQueNoExiste", "PEDIDO;NOVA-0007\nFIN\n");
        if (!r.esCorrecto() && r.getCodigoSalida() != AnalizadorTallas.OK) {
            superadas++;
            System.out.println("[SUPERADA] Error en el proceso hijo -> fallo detectado (código " + r.getCodigoSalida() + ")");
        } else {
            fallidas++;
            System.out.println("[FALLIDA]  Error en el proceso hijo -> " + r);
        }

        System.out.println();
        System.out.println("Pruebas superadas: " + superadas + " de " + (superadas + fallidas));
    }

    private static void comprobarRechazo(String nombre, ResultadoProceso r, int codigoEsperado) {
        if (r.getCodigoSalida() == codigoEsperado) {
            superadas++;
            String motivo = r.getErrores().trim().replace("ERROR;", "");
            System.out.println("[SUPERADA] " + nombre + " -> rechazado: " + motivo);
        } else {
            fallidas++;
            System.out.println("[FALLIDA]  " + nombre + " -> " + r);
        }
    }
}