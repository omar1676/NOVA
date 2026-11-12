package nova;

import java.awt.BorderLayout;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTabbedPane;

/**
 * Ventana principal, con una pestana por seccion.
 *
 * Solo se anaden las pestanas que el rol puede usar. Aun asi, cada operacion
 * se vuelve a comprobar al ejecutarse (Java y PostgreSQL).
 */
public class VentanaPrincipal extends JFrame {

    public VentanaPrincipal() {
        super("NOVA Sneakers - Gestión de pedidos");

        JLabel etiquetaUsuario = new JLabel("Usuario: " + Sesion.getUsuario() + "    Rol: " + Sesion.getRol());
        JButton botonCerrarSesion = new JButton("Cerrar sesión");
        botonCerrarSesion.addActionListener(e -> cerrarSesion());

        JPanel cabecera = new JPanel(new BorderLayout());
        cabecera.setBorder(BorderFactory.createEmptyBorder(5, 10, 5, 10));
        cabecera.add(etiquetaUsuario, BorderLayout.WEST);
        cabecera.add(botonCerrarSesion, BorderLayout.EAST);

        JTabbedPane pestanas = new JTabbedPane();
        if (Sesion.puede(Sesion.CREAR_PEDIDO)) {
            pestanas.addTab("Nuevo pedido", new PanelNuevoPedido());
        }
        pestanas.addTab("Consultas", new PanelConsultas());
        pestanas.addTab("Indicadores", new PanelIndicadores());
        if (Sesion.puede(Sesion.GESTIONAR_USUARIOS)) {
            pestanas.addTab("Usuarios", new PanelUsuarios());
        }

        add(cabecera, BorderLayout.NORTH);
        add(pestanas, BorderLayout.CENTER);

        // Al cerrar la ventana se registra el logout y se cierra la conexion
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent evento) {
                UsuarioDAO.logout();
                ConexionBD.cerrar();
            }
        });

        setSize(1100, 650);
        setLocationRelativeTo(null);
    }

    private void cerrarSesion() {
        UsuarioDAO.logout();
        dispose();
        new VentanaLogin().setVisible(true);
    }
}
