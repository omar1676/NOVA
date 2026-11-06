package nova;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.sql.SQLException;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;

/**
 * Pestaña "Indicadores": seis tablas pequeñas calculadas en PostgreSQL.
 * El umbral de stock bajo se puede cambiar.
 */
public class PanelIndicadores extends JPanel {

    private final JTextField campoUmbral = new JTextField("10", 4);
    private final JTable tablaResumen = new JTable();
    private final JTable tablaEstados = new JTable();
    private final JTable tablaModelos = new JTable();
    private final JTable tablaTallas = new JTable();
    private final JTable tablaStock = new JTable();

    public PanelIndicadores() {
        setLayout(new BorderLayout(5, 5));
        setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JButton botonCalcular = new JButton("Calcular indicadores");
        botonCalcular.addActionListener(e -> calcular());

        JPanel arriba = new JPanel(new FlowLayout(FlowLayout.LEFT));
        arriba.add(new JLabel("Umbral de stock bajo (pares):"));
        arriba.add(campoUmbral);
        arriba.add(botonCalcular);

        JPanel tablas = new JPanel(new GridLayout(0, 2, 10, 10));
        tablas.add(caja("Resumen de ventas", tablaResumen));
        tablas.add(caja("Pedidos por estado", tablaEstados));
        tablas.add(caja("Modelos más solicitados", tablaModelos));
        tablas.add(caja("Pares por talla", tablaTallas));
        tablas.add(caja("Stock por debajo del umbral", tablaStock));

        JLabel nota = new JLabel("Las ventas no cuentan los pedidos cancelados. "
                + "Un pedido con varias líneas cuenta como un solo pedido.");

        add(arriba, BorderLayout.NORTH);
        add(tablas, BorderLayout.CENTER);
        add(nota, BorderLayout.SOUTH);
    }

    private JScrollPane caja(String titulo, JTable tabla) {
        tabla.setDefaultEditor(Object.class, null);
        JScrollPane caja = new JScrollPane(tabla);
        caja.setBorder(BorderFactory.createTitledBorder(titulo));
        return caja;
    }

    private void calcular() {
        int umbral;
        try {
            umbral = Integer.parseInt(campoUmbral.getText().trim());
        } catch (NumberFormatException e) {
            JOptionPane.showMessageDialog(this, "El umbral tiene que ser un número entero");
            return;
        }

        try {
            tablaResumen.setModel(IndicadoresDAO.resumen());
            tablaEstados.setModel(IndicadoresDAO.pedidosPorEstado());
            tablaModelos.setModel(IndicadoresDAO.modelosMasSolicitados());
            tablaTallas.setModel(IndicadoresDAO.paresPorTalla());
            tablaStock.setModel(IndicadoresDAO.stockBajo(umbral));
            Archivos.registrar("INDICADORES", "correcto", "umbral de stock " + umbral);
        } catch (SQLException e) {
            Archivos.registrar("INDICADORES", ConexionBD.tipoResultado(e), ConexionBD.mensajeError(e));
            JOptionPane.showMessageDialog(this, ConexionBD.mensajeError(e),
                    "No se han podido calcular", JOptionPane.ERROR_MESSAGE);
        }
    }
}
