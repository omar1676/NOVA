package nova;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.sql.SQLException;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

public class VentanaLogin extends JFrame {

    private final JTextField campoUsuario = new JTextField(15);
    private final JPasswordField campoContrasena = new JPasswordField(15);

    public VentanaLogin() {
        super("NOVA Sneakers - Iniciar sesión");

        JPanel formulario = new JPanel(new GridLayout(2, 2, 5, 5));
        formulario.add(new JLabel("Usuario:"));
        formulario.add(campoUsuario);
        formulario.add(new JLabel("Contraseña:"));
        formulario.add(campoContrasena);

        JButton botonEntrar = new JButton("Entrar");
        botonEntrar.addActionListener(e -> entrar());
        getRootPane().setDefaultButton(botonEntrar);

        JPanel contenido = new JPanel(new BorderLayout(10, 10));
        contenido.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        contenido.add(formulario, BorderLayout.CENTER);
        contenido.add(botonEntrar, BorderLayout.SOUTH);
        add(contenido);

        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        pack();
        setLocationRelativeTo(null);
    }

    private void entrar() {
        String usuario = campoUsuario.getText().trim();
        String contrasena = new String(campoContrasena.getPassword());
        try {
            UsuarioDAO.login(usuario, contrasena);
            new VentanaPrincipal().setVisible(true);
            dispose();
        } catch (SQLException e) {
            JOptionPane.showMessageDialog(this, ConexionBD.mensajeError(e),
                    "No se ha podido entrar", JOptionPane.ERROR_MESSAGE);
            campoContrasena.setText("");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new VentanaLogin().setVisible(true));
    }
}
