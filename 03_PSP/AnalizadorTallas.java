import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

// Version anterior del hijo 2 (8 de noviembre): suma los pares de cada talla del CSV.
// La lanza LanzadorValidacion; el coordinador usa Psp.AnalizadorTallas, el de Alvaro
public class AnalizadorTallas {

    // Lee el CSV por stdin y escribe los pares de cada talla y el total
    public static void main(String[] args) throws Exception {

        // Listas paralelas: la talla tallas.get(i) tiene cantidades.get(i) pares
        ArrayList<Integer> tallas = new ArrayList<>();
        ArrayList<Integer> cantidades = new ArrayList<>();

        String contenido = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);

        ArrayList<ArrayList<String>> registros;

        // Si el CSV esta mal formado: ERROR por stderr y codigo 2
        try {
            registros = LectorCsv.partirTodo(contenido);

        } catch (IllegalArgumentException e) {
            System.err.println("ERROR;El CSV esta mal formado: " + e.getMessage());
            System.exit(2);
            // El return hace falta porque el compilador no sabe que System.exit acaba el programa
            return;
        }

        // Se empieza en 1 para saltar la cabecera
        for (int i = 1; i < registros.size(); i++) {

            ArrayList<String> campos = registros.get(i);

            if (campos.size() != 8) {
                System.err.println("ERROR;El registro " + i
                        + " no tiene 8 campos");
                System.exit(2);
            }

            int talla;
            int cantidad;

            // Los campos 6 y 7 son la talla y la cantidad
            try {
                talla = Integer.parseInt(campos.get(6).trim());
                cantidad = Integer.parseInt(campos.get(7).trim());

            } catch (NumberFormatException e) {
                System.err.println("ERROR;El registro " + i
                        + " tiene una talla o una cantidad que no son numeros");
                System.exit(2);
                return;
            }

            // Si la talla ya esta en la lista se suman los pares; si no, se anade
            int posicion = buscarTalla(tallas, talla);

            if (posicion == -1) {
                tallas.add(talla);
                cantidades.add(cantidad);
            } else {
                cantidades.set(posicion, cantidades.get(posicion) + cantidad);
            }
        }

        if (tallas.isEmpty()) {
            System.err.println("ERROR;No hay ninguna linea de pedido que resumir");
            System.exit(2);
        }

        // Resultado ordenado por talla, con el total al final
        ordenarPorTalla(tallas, cantidades);

        int totalPares = 0;

        for (int i = 0; i < tallas.size(); i++) {
            System.out.println("Talla " + tallas.get(i) + ": "
                    + cantidades.get(i) + " pares");

            totalPares = totalPares + cantidades.get(i);
        }

        System.out.println("Total: " + totalPares + " pares");
    }

    // Devuelve la posicion de la talla en la lista, o -1 si no esta
    private static int buscarTalla(ArrayList<Integer> tallas, int talla) {

        for (int i = 0; i < tallas.size(); i++) {

            if (tallas.get(i) == talla) {
                return i;
            }
        }

        return -1;
    }

    // Ordena las tallas de menor a mayor (metodo de la burbuja) y mueve con ellas sus cantidades
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
