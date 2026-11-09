package nova;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.sql.SQLException;
import java.util.ArrayList;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.table.DefaultTableModel;

/**
 * Pestana "Nuevo pedido": cliente, modelo, talla y cantidad.
 *
 * Se pueden anadir varias lineas (por ejemplo, un pedido Custom de 40 pares
 * en cuatro tallas) y despues se crea todo de una vez con "Crear pedido".
 */
public class PanelNuevoPedido extends JPanel {

    private final JTextField campoReferencia = new JTextField(12);
    private final JComboBox<Opcion> comboCliente = new JComboBox<>();
    private final JComboBox<Opcion> comboModelo = new JComboBox<>();
    private final JTextField campoTalla = new JTextField(4);
    private final JTextField campoCantidad = new JTextField(4);
    private final JCheckBox casillaCustom = new JCheckBox("Pedido Custom. Personalización:");
    private final JTextField campoPersonalizacion = new JTextField(30);

    // Las lineas que se van anadiendo: lo que se ve en la tabla y lo que se envia
    private final DefaultTableModel modeloLineas =
            new DefaultTableModel(new Object[] {"Modelo y color", "Talla", "Cantidad"}, 0);
    private final ArrayList<int[]> lineas = new ArrayList<>();

    public PanelNuevoPedido() {
        setLayout(new BorderLayout(10, 10));
        setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JPanel formulario = new JPanel(new GridLayout(0, 2, 5, 5));
        formulario.add(new JLabel("Referencia del pedido (por ejemplo SO024):"));
        formulario.add(campoReferencia);
        formulario.add(new JLabel("Cliente:"));
        formulario.add(comboCliente);
        formulario.add(new JLabel("Modelo y color:"));
        formulario.add(comboModelo);
        formulario.add(new JLabel("Talla:"));
        formulario.add(campoTalla);
        formulario.add(new JLabel("Cantidad (pares):"));
        formulario.add(campoCantidad);
        formulario.add(casillaCustom);
        formulario.add(campoPersonalizacion);

        JButton botonAnadir = new JButton("Añadir línea");
        JButton botonVaciar = new JButton("Vaciar líneas");
        JButton botonCrear = new JButton("Crear pedido");
        botonAnadir.addActionListener(e -> anadirLinea());
        botonVaciar.addActionListener(e -> vaciarLineas());
        botonCrear.addActionListener(e -> crearPedido());

        JPanel botones = new JPanel(new FlowLayout(FlowLayout.LEFT));
        botones.add(botonAnadir);
        botones.add(botonVaciar);
        botones.add(botonCrear);

        JPanel arriba = new JPanel(new BorderLayout());
        arriba.add(formulario, BorderLayout.CENTER);
        arriba.add(botones, BorderLayout.SOUTH);

        JTable tablaLineas = new JTable(modeloLineas);
        tablaLineas.setDefaultEditor(Object.class, null);   // no se edita a mano
        JScrollPane cajaLineas = new JScrollPane(tablaLineas);
        cajaLineas.setBorder(BorderFactory.createTitledBorder("Líneas del pedido"));

        add(arriba, BorderLayout.NORTH);
        add(cajaLineas, BorderLayout.CENTER);

        cargarListas();
    }

    private void cargarListas() {
        try {
            for (Opcion cliente : PedidoDAO.listarClientes()) {
                comboCliente.addItem(cliente);
            }
            for (Opcion variante : PedidoDAO.listarVariantes()) {
                comboModelo.addItem(variante);
            }
        } catch (SQLException e) {
            mostrarError("No se han podido cargar los clientes y modelos", e);
        }
    }

    /** Anade una linea a la lista. Todavia no se guarda nada en la base. */
    private void anadirLinea() {
        Opcion variante = (Opcion) comboModelo.getSelectedItem();
        if (variante == null) {
            JOptionPane.showMessageDialog(this, "Elige un modelo");
            return;
        }

        int talla;
        int cantidad;
        try {
            talla = Integer.parseInt(campoTalla.getText().trim());
            cantidad = Integer.parseInt(campoCantidad.getText().trim());
        } catch (NumberFormatException e) {
            JOptionPane.showMessageDialog(this, "La talla y la cantidad tienen que ser números enteros");
            return;
        }

        lineas.add(new int[] {variante.getId(), talla, cantidad});
        modeloLineas.addRow(new Object[] {variante.toString(), talla, cantidad});
        campoTalla.setText("");
        campoCantidad.setText("");
    }

    private void vaciarLineas() {
        lineas.clear();
        modeloLineas.setRowCount(0);
    }

    /** Envia el pedido a la base. Si PostgreSQL lo rechaza, se ensena el motivo. */
    private void crearPedido() {
        String referencia = campoReferencia.getText().trim();
        Opcion cliente = (Opcion) comboCliente.getSelectedItem();
        boolean custom = casillaCustom.isSelected();
        String personalizacion = campoPersonalizacion.getText().trim();

        if (referencia.isEmpty() || cliente == null) {
            JOptionPane.showMessageDialog(this, "Escribe la referencia y elige un cliente");
            return;
        }
        if (lineas.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Añade al menos una línea al pedido");
            return;
        }
        if (custom && personalizacion.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Un pedido Custom necesita la descripción de la personalización");
            return;
        }

        try {
            int idPedido = PedidoDAO.crearPedido(referencia, cliente.getId(), lineas, custom, personalizacion);
            JOptionPane.showMessageDialog(this, "Pedido " + referencia + " creado (id " + idPedido + ").\n"
                    + "Esta pendiente: PostgreSQL ha calculado el importe, y el stock se descontara\n"
                    + "cuando se confirme en la pestaña Consultas.");
            campoReferencia.setText("");
            campoPersonalizacion.setText("");
            casillaCustom.setSelected(false);
            vaciarLineas();
        } catch (SQLException e) {
            mostrarError("No se ha creado el pedido", e);
        }
    }

    private void mostrarError(String titulo, SQLException e) {
        JOptionPane.showMessageDialog(this, ConexionBD.mensajeError(e), titulo, JOptionPane.ERROR_MESSAGE);
    }
}
