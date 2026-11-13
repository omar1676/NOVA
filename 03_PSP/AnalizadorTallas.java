import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

/**
 * Analizador CSV que usa LanzadorValidacion en sus comprobaciones independientes.
 * Agrupa pares por talla tras validar los registros; conserva el formato de salida.
 * El coordinador del equipo utiliza Psp.AnalizadorTallas, de Alvaro.
 */
public class AnalizadorTallas {

    public static void main(String[] args) throws Exception {

        // Las dos listas que van en paralelo.
        ArrayList<Integer> tallas = new ArrayList<>();
        ArrayList<Integer> cantidades = new ArrayList<>();

        /*
         * Leemos TODA la entrada de golpe, igual que el validador, porque un
         * registro del CSV puede ocupar varias lineas del archivo cuando un
         * campo entrecomillado lleva un salto de linea dentro.
         */
        String contenido = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);

        // LectorCsv nos da los registros ya separados en campos.
        ArrayList<ArrayList<String>> registros;

        try {
            registros = LectorCsv.partirTodo(contenido);

        } catch (IllegalArgumentException e) {
            System.err.println("ERROR;El CSV esta mal formado: " + e.getMessage());
            System.exit(2);
            return;   // no se llega: exit termina el programa
        }

        // Recorremos los registros saltando la cabecera, que es el primero.
        for (int i = 1; i < registros.size(); i++) {

            ArrayList<String> campos = registros.get(i);

            // Si un registro viene mal, avisamos y no seguimos.
            if (campos.size() != 8) {
                System.err.println("ERROR;El registro " + i
                        + " no tiene 8 campos");
                System.exit(2);
            }

            int talla;
            int cantidad;

            try {
                talla = Integer.parseInt(campos.get(6).trim());
                cantidad = Integer.parseInt(campos.get(7).trim());

            } catch (NumberFormatException e) {
                System.err.println("ERROR;El registro " + i
                        + " tiene una talla o una cantidad que no son numeros");
                System.exit(2);
                return;   // no se llega: exit termina el programa
            }

            /*
             * Buscamos si esa talla ya la habiamos visto antes.
             * Si la encontramos, le sumamos los pares.
             * Si no, la anadimos al final de las dos listas.
             */
            int posicion = buscarTalla(tallas, talla);

            if (posicion == -1) {
                tallas.add(talla);
                cantidades.add(cantidad);
            } else {
                cantidades.set(posicion, cantidades.get(posicion) + cantidad);
            }
        }

        // Si no habia ninguna linea de pedido, no hay nada que resumir.
        if (tallas.isEmpty()) {
            System.err.println("ERROR;No hay ninguna linea de pedido que resumir");
            System.exit(2);
        }

        // Ordenamos de talla menor a mayor, para que el resumen salga igual
        // aunque el archivo venga desordenado.
        ordenarPorTalla(tallas, cantidades);

        // Escribimos el resumen y vamos sumando el total.
        int totalPares = 0;

        for (int i = 0; i < tallas.size(); i++) {
            System.out.println("Talla " + tallas.get(i) + ": "
                    + cantidades.get(i) + " pares");

            totalPares = totalPares + cantidades.get(i);
        }

        System.out.println("Total: " + totalPares + " pares");
    }

    /**
     * Devuelve la posicion de una talla dentro de la lista,
     * o -1 si todavia no esta.
     */
    private static int buscarTalla(ArrayList<Integer> tallas, int talla) {

        for (int i = 0; i < tallas.size(); i++) {

            if (tallas.get(i) == talla) {
                return i;
            }
        }

        return -1;
    }

    /**
     * Ordena las dos listas de menor a mayor talla.
     *
     * Cada vez que intercambia dos tallas, intercambia tambien sus
     * cantidades, para que sigan estando en la misma posicion.
     */
    private static void ordenarPorTalla(ArrayList<Integer> tallas,
                                        ArrayList<Integer> cantidades) {

        for (int i = 0; i < tallas.size() - 1; i++) {

            for (int j = 0; j < tallas.size() - 1 - i; j++) {

                if (tallas.get(j) > tallas.get(j + 1)) {

                    int tallaGuardada = tallas.get(j);
                    tallas.set(j, tallas.get(j + 1));
                    tallas.set(j + 1, tallaGuardada);

                    int cantidadGuardada = cantidades.get(j);
                    cantidades.set(j, cantidades.get(j + 1));
                    cantidades.set(j + 1, cantidadGuardada);
                }
            }
        }
    }
}
