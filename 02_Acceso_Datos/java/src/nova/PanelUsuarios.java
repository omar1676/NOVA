package nova;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.io.File;
import java.io.IOException;
import java.sql.SQLException;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;

/**
 * Pestaña "Usuarios" (solo administrador): alta, cambio de rol,
 * activar/desactivar y exportación a usuarios_sneaker.json.
 */
public class PanelUsuarios extends JPanel {

    private final JTable tabla = new JTable();
    private final JTextField campoUsuario = new JTextField(12);
    private final JPasswordField campoContrasena = new JPasswordField(12);
    private final JComboBox<String> comboRol = new JComboBox<>();

    public PanelUsuarios() {
        setLayout(new BorderLayout(5, 5));
        setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JButton botonCrear = new JButton("Crear usuario");
        botonCrear.addActionListener(e -> crearUsuario());

        JPanel alta = new JPanel(new FlowLayout(FlowLayout.LEFT));
        alta.add(new JLabel("Usuario:"));
        alta.add(campoUsuario);
        alta.add(new JLabel("Contraseña (mínimo 8):"));
        alta.add(campoContrasena);
        alta.add(new JLabel("Rol:"));
        alta.add(comboRol);
        alta.add(botonCrear);

        JButton botonRol = new JButton("Poner el rol elegido al seleccionado");
        JButton botonActivo = new JButton("Activar / desactivar seleccionado");
        JButton botonJson = new JButton("Exportar usuarios a JSON");
        JButton botonActualizar = new JButton("Actualizar lista");
        botonRol.addActionListener(e -> cambiarRol());
        botonActivo.addActionListener(e -> cambiarActivo());
        botonJson.addActionListener(e -> exportarJson());
        botonActualizar.addActionListener(e -> actualizarLista());

        JPanel acciones = new JPanel(new FlowLayout(FlowLayout.LEFT));
        acciones.add(botonRol);
        acciones.add(botonActivo);
        acciones.add(botonJson);
        acciones.add(botonActualizar);

        tabla.setDefaultEditor(Object.class, null);

        add(alta, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
        add(acciones, BorderLayout.SOUTH);

        try {
            for (String rol : UsuarioDAO.listarRoles()) {
                comboRol.addItem(rol);
            }
        } catch (SQLException e) {
            mostrarError("No se han podido cargar los roles", e);
        }
        actualizarLista();
    }

    private void actualizarLista() {
        try {
            tabla.setModel(UsuarioDAO.listarUsuarios());
        } catch (SQLException e) {
            mostrarError("No se han podido cargar los usuarios", e);
        }
    }

    private void crearUsuario() {
        String usuario = campoUsuario.getText().trim();
        String contrasena = new String(campoContrasena.getPassword());
        String rol = (String) comboRol.getSelectedItem();
        if (usuario.isEmpty() || rol == null) {
            JOptionPane.showMessageDialog(this, "Escribe el nombre de usuario y elige un rol");
            return;
        }
        try {
            UsuarioDAO.crearUsuario(usuario, rol, contrasena);
            JOptionPane.showMessageDialog(this, "Usuario " + usuario + " creado. El JSON está actualizado.");
            campoUsuario.setText("");
            campoContrasena.setText("");
        } catch (SQLException e) {
            mostrarError("No se ha creado el usuario", e);
        } catch (IOException e) {
            avisarJson(e);
        }
        actualizarLista();
    }

    private void cambiarRol() {
        int idUsuario = usuarioSeleccionado();
        String rol = (String) comboRol.getSelectedItem();
        if (idUsuario < 0 || rol == null) {
            return;
        }
        try {
            UsuarioDAO.cambiarRol(idUsuario, rol);
        } catch (SQLException e) {
            mostrarError("No se ha cambiado el rol", e);
        } catch (IOException e) {
            avisarJson(e);
        }
        actualizarLista();
    }

    private void cambiarActivo() {
        int idUsuario = usuarioSeleccionado();
        if (idUsuario < 0) {
            return;
        }
        // Columna 3 = activo. Se pone el valor contrario.
        boolean activo = Boolean.parseBoolean(tabla.getValueAt(tabla.getSelectedRow(), 3).toString());
        try {
            UsuarioDAO.cambiarActivo(idUsuario, !activo);
        } catch (SQLException e) {
            mostrarError("No se ha cambiado el usuario", e);
        } catch (IOException e) {
            avisarJson(e);
        }
        actualizarLista();
    }

    private void exportarJson() {
        try {
            File archivo = UsuarioDAO.exportarUsuariosJson();
            JOptionPane.showMessageDialog(this, "Usuarios exportados a\n" + archivo.getAbsolutePath());
        } catch (SQLException e) {
            mostrarError("No se ha exportado el JSON", e);
        } catch (IOException e) {
            avisarJson(e);
        }
    }

    /** El id de la fila seleccionada (columna 0 = id_usuario), o -1. */
    private int usuarioSeleccionado() {
        int fila = tabla.getSelectedRow();
        if (fila < 0) {
            JOptionPane.showMessageDialog(this, "Selecciona un usuario de la tabla");
            return -1;
        }
        return Integer.parseInt(tabla.getValueAt(fila, 0).toString());
    }

    private void avisarJson(IOException e) {
        JOptionPane.showMessageDialog(this, "El cambio se ha guardado en la base, pero no se ha podido "
                + "escribir usuarios_sneaker.json: " + e.getMessage(), "Aviso", JOptionPane.WARNING_MESSAGE);
    }

    private void mostrarError(String titulo, SQLException e) {
        JOptionPane.showMessageDialog(this, ConexionBD.mensajeError(e), titulo, JOptionPane.ERROR_MESSAGE);
    }
}
