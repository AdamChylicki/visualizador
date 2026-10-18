import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mi primera ventana")
        self.resize(400, 200)

        # Crear el diseño vertical
        layout = QVBoxLayout(self)

        # Crear el texto
        self.label = QLabel("Pulsa el botón")
        layout.addWidget(self.label)

        # Crear el botón
        self.button = QPushButton("Haz clic aquí")
        layout.addWidget(self.button)

        # Conectar el botón con la función
        self.button.clicked.connect(self.say_hello)

    def say_hello(self):
        self.label.setText("hello bitches")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())