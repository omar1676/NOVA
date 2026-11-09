package Psp;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

public class AnalizadorTallas {

    public static final int OK = 0;
    public static final int DATOS_INCORRECTOS = 2;
    public static final int ERROR_INESPERADO = 3;

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));
        try {
            BufferedReader entrada = new BufferedReader(
                    new InputStreamReader(System.in, StandardCharsets.UTF_8));
            String resultado = analizar(entrada);
            System.out.print(resultado);
            System.exit(OK);
        } catch (DatosIncorrectosException e) {
            System.err.println("ERROR;" + e.getMessage());
            System.exit(DATOS_INCORRECTOS);
        } catch (Exception e) {
            System.err.println("ERROR;Error inesperado: " + e.getMessage());
            System.exit(ERROR_INESPERADO);
        }
    }

    public static String analizar(BufferedReader entrada)
            throws IOException, DatosIncorrectosException {

        String primera = entrada.readLine();
        if (primera == null || primera.isBlank()) {
            throw new DatosIncorrectosException("Entrada vacía");
        }
        String[] cabecera = primera.trim().split(";", -1);
        if (cabecera.length != 2 || !cabecera[0].equals("PEDIDO") || cabecera[1].isBlank()) {
            throw new DatosIncorrectosException("La primera línea debe ser PEDIDO;referencia");
        }
        String referencia = cabecera[1].trim();

        Map<String, Integer> porVarianteYTalla = new LinkedHashMap<>();
        Map<Integer, Integer> porTalla = new TreeMap<>();
        int total = 0;
        int numeroLinea = 1;
        boolean hayFin = false;
        String linea;

        while ((linea = entrada.readLine()) != null) {
            numeroLinea++;
            linea = linea.trim();
            if (linea.isEmpty()) {
                continue;
            }
            if (linea.equals("FIN")) {
                hayFin = true;
                break;
            }

            String[] partes = linea.split(";", -1);
            if (!partes[0].equals("LINEA")) {
                throw new DatosIncorrectosException("Línea " + numeroLinea + ": tipo desconocido");
            }
            if (partes.length != 6) {
                throw new DatosIncorrectosException("Línea " + numeroLinea
                        + ": faltan datos (formato LINEA;sku;modelo;color;talla;cantidad)");
            }

            String sku = partes[1].trim();
            String modelo = partes[2].trim();
            String color = partes[3].trim();
            if (sku.isEmpty() || modelo.isEmpty() || color.isEmpty()) {
                throw new DatosIncorrectosException("Línea " + numeroLinea + ": sku, modelo o color vacíos");
            }

            int talla = leerEntero(partes[4], "talla", numeroLinea);
            int cantidad = leerEntero(partes[5], "cantidad", numeroLinea);
            if (talla < 20 || talla > 55) {
                throw new DatosIncorrectosException("Línea " + numeroLinea + ": talla fuera de rango (20-55)");
            }
            if (cantidad <= 0) {
                throw new DatosIncorrectosException("Línea " + numeroLinea + ": la cantidad debe ser mayor que cero");
            }

            String clave = modelo + ";" + color + ";" + talla;
            porVarianteYTalla.merge(clave, cantidad, Integer::sum);
            porTalla.merge(talla, cantidad, Integer::sum);
            total += cantidad;
        }

        if (!hayFin) {
            throw new DatosIncorrectosException("Pedido incompleto: falta la línea FIN");
        }
        if (total == 0) {
            throw new DatosIncorrectosException("El pedido no tiene líneas");
        }

        StringBuilder sb = new StringBuilder();
        sb.append("OK;").append(referencia).append("\n");
        for (Map.Entry<String, Integer> e : porVarianteYTalla.entrySet()) {
            sb.append("VARIANTE_TALLA;").append(e.getKey()).append(";").append(e.getValue()).append("\n");
        }
        for (Map.Entry<Integer, Integer> e : porTalla.entrySet()) {
            sb.append("TALLA;").append(e.getKey()).append(";").append(e.getValue()).append("\n");
        }
        sb.append("TOTAL;").append(total).append("\n");
        return sb.toString();
    }

    private static int leerEntero(String texto, String campo, int numeroLinea)
            throws DatosIncorrectosException {
        try {
            return Integer.parseInt(texto.trim());
        } catch (NumberFormatException e) {
            throw new DatosIncorrectosException("Línea " + numeroLinea + ": " + campo + " no es un número");
        }
    }
}