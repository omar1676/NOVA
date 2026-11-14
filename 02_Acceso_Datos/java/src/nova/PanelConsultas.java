package nova;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.io.File;
import java.io.IOException;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.table.DefaultTableModel;

public class PanelConsultas extends JPanel {

    private static final String[] ESTADOS = {
        "(todos)", "pendiente", "confirmado", "en_preparacion", "enviado", "entregado", "cancelado"
    };

    private final JComboBox<Opcion> comboCliente = new JComboBox<>();
    private final JComboBox<Opcion> comboModelo = new JComboBox<>();
    private final JComboBox<String> comboEstado = new JComboBox<>(ESTADOS);
    private final JTextField campoDesde = new JTextField(8);
    private final JTextField campoHasta = new JTextField(8);
    private final JTable tabla = new JTable();
    private final JLabel etiquetaResultado = new JLabel(" ");

    public PanelConsultas() {
        setLayout(new BorderLayout(5, 5));
        setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JPanel filaUno = new JPanel(new FlowLayout(FlowLayout.LEFT));
        filaUno.add(new JLabel("Cliente:"));
        filaUno.add(comboCliente);
        filaUno.add(new JLabel("Modelo:"));
        filaUno.add(comboModelo);
        filaUno.add(new JLabel("Estado:"));
        filaUno.add(comboEstado);

        JButton botonBuscar = new JButton("Buscar / Consultar");
        JButton botonLimpiar = new JButton("Limpiar filtros");
        botonBuscar.addActionListener(e -> buscar());
        botonLimpiar.addActionListener(e -> limpiarFiltros());

        JPanel filaDos = new JPanel(new FlowLayout(FlowLayout.LEFT));
        filaDos.add(new JLabel("Desde (AAAA-MM-DD):"));
        filaDos.add(campoDesde);
        filaDos.add(new JLabel("Hasta:"));
        filaDos.add(campoHasta);
        filaDos.add(botonBuscar);
        filaDos.add(botonLimpiar);

        JPanel filtros = new JPanel(new GridLayout(2, 1));
        filtros.add(filaUno);
        filtros.add(filaDos);

        JButton botonDetalle = new JButton("Ver detalle");
        JButton botonConfirmar = new JButton("Confirmar pedido");
        JButton botonCancelar = new JButton("Cancelar pedido");
        JButton botonCsv = new JButton("Exportar a CSV");
        JButton botonAuditoria = new JButton("Ver auditoría");
        botonAuditoria.setToolTipText("Solo administrador. Los demás roles reciben 'Acceso denegado'.");
        botonDetalle.addActionListener(e -> verDetalle());
        botonConfirmar.addActionListener(e -> cambiarEstado(true));
        botonCancelar.addActionListener(e -> cambiarEstado(false));
        botonCsv.addActionListener(e -> exportarCsv());
        botonAuditoria.addActionListener(e -> verAuditoria());

        JPanel acciones = new JPanel(new FlowLayout(FlowLayout.LEFT));
        acciones.add(botonDetalle);
        acciones.add(botonConfirmar);
        acciones.add(botonCancelar);
        acciones.add(botonCsv);
        acciones.add(botonAuditoria);
        acciones.add(etiquetaResultado);

        tabla.setDefaultEditor(Object.class, null);

        add(filtros, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
        add(acciones, BorderLayout.SOUTH);

        cargarListas();
        etiquetaResultado.setText("Elige los filtros y pulsa Buscar / Consultar.");
    }

    private void cargarListas() {
        comboCliente.addItem(new Opcion(0, "(todos)"));
        comboModelo.addItem(new Opcion(0, "(todos)"));
        try {
            for (Opcion cliente : PedidoDAO.listarClientes()) {
                comboCliente.addItem(cliente);
            }
            for (Opcion modelo : PedidoDAO.listarModelos()) {
                comboModelo.addItem(modelo);
            }
        } catch (SQLException e) {
            mostrarError("No se han podido cargar los filtros", e);
        }
    }

    private void buscar() {
        Integer idCliente = idElegido(comboCliente);
        Integer idModelo = idElegido(comboModelo);
        String estado = null;
        if (comboEstado.getSelectedIndex() > 0) {
            estado = (String) comboEstado.getSelectedItem();
        }

        LocalDate desde;
        LocalDate hasta;
        try {
            desde = leerFecha(campoDesde);
            hasta = leerFecha(campoHasta);
        } catch (DateTimeParseException e) {
            Archivos.registrar("CONSULTA PEDIDOS", "error", "fecha mal escrita");
            JOptionPane.showMessageDialog(this, "Las fechas se escriben AAAA-MM-DD, por ejemplo 2026-11-09");
            return;
        }

        tabla.setModel(new DefaultTableModel());
        try {
            DefaultTableModel resultado = PedidoDAO.buscarPedidos(idCliente, idModelo, estado, desde, hasta);
            tabla.setModel(resultado);
            if (resultado.getRowCount() == 0) {
                etiquetaResultado.setText("No hay pedidos con esos filtros.");
            } else {
                etiquetaResultado.setText(resultado.getRowCount() + " pedidos.");
            }
        } catch (SQLException e) {
            etiquetaResultado.setText("La consulta no se ha podido hacer.");
            mostrarError("Error en la consulta", e);
        }
    }

    private void limpiarFiltros() {
        comboCliente.setSelectedIndex(0);
        comboModelo.setSelectedIndex(0);
        comboEstado.setSelectedIndex(0);
        campoDesde.setText("");
        campoHasta.setText("");
        Archivos.registrar("LIMPIAR FILTROS", "correcto", "");
        buscar();
    }

    private Integer idElegido(JComboBox<Opcion> combo) {
        Opcion opcion = (Opcion) combo.getSelectedItem();
        if (opcion == null || opcion.getId() == 0) {
            return null;
        }
        return opcion.getId();
    }

    private LocalDate leerFecha(JTextField campo) {
        String texto = campo.getText().trim();
        if (texto.isEmpty()) {
            return null;
        }
        return LocalDate.parse(texto);
    }

    private int pedidoSeleccionado() {
        int fila = tabla.getSelectedRow();
        if (fila < 0 || tabla.getColumnCount() == 0) {
            JOptionPane.showMessageDialog(this, "Selecciona un pedido de la tabla");
            return -1;
        }
        return Integer.parseInt(tabla.getValueAt(fila, 0).toString());
    }

    private void verDetalle() {
        int idPedido = pedidoSeleccionado();
        if (idPedido < 0) {
            return;
        }
        try {
            mostrarTabla("Líneas del pedido " + idPedido, PedidoDAO.verDetalle(idPedido));
        } catch (SQLException e) {
            mostrarError("No se puede ver el detalle", e);
        }
    }

    private void cambiarEstado(boolean confirmar) {
        int idPedido = pedidoSeleccionado();
        if (idPedido < 0) {
            return;
        }
        String accion = "cancelar";
        if (confirmar) {
            accion = "confirmar";
        }
        int respuesta = JOptionPane.showConfirmDialog(this, "¿Seguro que quieres " + accion
                + " el pedido " + idPedido + "?", "Confirmación", JOptionPane.YES_NO_OPTION);
        if (respuesta != JOptionPane.YES_OPTION) {
            return;
        }

        try {
            if (confirmar) {
                PedidoDAO.confirmarPedido(idPedido);
                JOptionPane.showMessageDialog(this, "Pedido confirmado. PostgreSQL ha descontado el stock.");
            } else {
                PedidoDAO.cancelarPedido(idPedido);
                JOptionPane.showMessageDialog(this, "Pedido cancelado. PostgreSQL ha devuelto el stock.");
            }
        } catch (SQLException e) {
            mostrarError("No se ha podido " + accion + " el pedido", e);
        }
        buscar();
    }

    private void exportarCsv() {
        try {
            File archivo = Archivos.exportarCsv(tabla.getModel(), "consulta_pedidos.csv");
            Archivos.registrar("EXPORTAR CSV", "correcto", tabla.getRowCount() + " filas");
            JOptionPane.showMessageDialog(this, tabla.getRowCount() + " filas exportadas a\n"
                    + archivo.getAbsolutePath());
        } catch (IOException e) {
            Archivos.registrar("EXPORTAR CSV", "error", e.getMessage());
            JOptionPane.showMessageDialog(this, "No se ha podido escribir el CSV: " + e.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void verAuditoria() {
        try {
            mostrarTabla("Últimos eventos de log_eventos", PedidoDAO.verAuditoria());
        } catch (SQLException e) {
            mostrarError("No se puede ver la auditoría", e);
        }
    }

    private void mostrarTabla(String titulo, DefaultTableModel modelo) {
        JTable tablaVentana = new JTable(modelo);
        tablaVentana.setDefaultEditor(Object.class, null);
        JScrollPane caja = new JScrollPane(tablaVentana);
        caja.setPreferredSize(new Dimension(900, 300));
        JOptionPane.showMessageDialog(this, caja, titulo, JOptionPane.PLAIN_MESSAGE);
    }

    private void mostrarError(String titulo, SQLException e) {
        JOptionPane.showMessageDialog(this, ConexionBD.mensajeError(e), titulo, JOptionPane.ERROR_MESSAGE);
    }
}
