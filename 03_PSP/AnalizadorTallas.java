import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class AnalizadorTallas {

    public static void main(String[] args) throws Exception {

        ArrayList<Integer> tallas = new ArrayList<>();
        ArrayList<Integer> cantidades = new ArrayList<>();

        String contenido = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);

        ArrayList<ArrayList<String>> registros;

        try {
            registros = LectorCsv.partirTodo(contenido);

        } catch (IllegalArgumentException e) {
            System.err.println("ERROR;El CSV esta mal formado: " + e.getMessage());
            System.exit(2);
            return;
        }

        for (int i = 1; i < registros.size(); i++) {

            ArrayList<String> campos = registros.get(i);

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
                return;
            }

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

        ordenarPorTalla(tallas, cantidades);

        int totalPares = 0;

        for (int i = 0; i < tallas.size(); i++) {
            System.out.println("Talla " + tallas.get(i) + ": "
                    + cantidades.get(i) + " pares");

            totalPares = totalPares + cantidades.get(i);
        }

        System.out.println("Total: " + totalPares + " pares");
    }

    private static int buscarTalla(ArrayList<Integer> tallas, int talla) {

        for (int i = 0; i < tallas.size(); i++) {

            if (tallas.get(i) == talla) {
                return i;
            }
        }

        return -1;
    }

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
