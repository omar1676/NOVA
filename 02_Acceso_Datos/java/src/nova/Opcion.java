package nova;

/**
 * Un elemento de un JComboBox: el id de la base de datos y el texto que se
 * ve. El JComboBox muestra lo que devuelve toString().
 */
public class Opcion {

    private final int id;
    private final String texto;

    public Opcion(int id, String texto) {
        this.id = id;
        this.texto = texto;
    }

    public int getId() {
        return id;
    }

    @Override
    public String toString() {
        return texto;
    }
}
