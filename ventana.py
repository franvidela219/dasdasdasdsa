import sys, webbrowser, requests
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QBrush, QLinearGradient
from api_juego import buscar_juego, obtener_url_cover, obtener_url_screenshot


# --- Señales e hilos para cargar imágenes ---
class Señales(QObject):
    terminado = pyqtSignal(QPixmap, object)


class HiloImagen(QRunnable):
    cache = {}

    def __init__(self, url, etiqueta):
        super().__init__()
        self.url = url
        self.etiqueta = etiqueta
        self.senales = Señales()

    def run(self):
        pixmap = QPixmap()
        try:
            if self.url in HiloImagen.cache:
                pixmap = HiloImagen.cache[self.url]
            else:
                r = requests.get(self.url, timeout=8)
                if r.status_code == 200:
                    pixmap.loadFromData(r.content)
                    HiloImagen.cache[self.url] = pixmap
                else:
                    pixmap.load("placeholder.jpg")
        except:
            pixmap.load("placeholder.jpg")
        self.senales.terminado.emit(pixmap, self.etiqueta)


# --- Ventana principal ---
class VentanaJuegos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biblioteca de Juegos")
        self.setStyleSheet("background-color:#0B1D2F; color:white;")
        self.showMaximized()
        self.hilos = QThreadPool()

        layout_principal = QVBoxLayout(self)

        # --- Título ---
        titulo = QLabel("Biblioteca de Juegos")
        titulo.setFont(QFont("Arial", 36, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)

        grad = QLinearGradient(0, 0, 400, 0)
        grad.setColorAt(0, QColor("#66C0F4"))
        grad.setColorAt(1, QColor("#FFFFFF"))
        paleta = QPalette()
        paleta.setBrush(QPalette.WindowText, QBrush(grad))
        titulo.setPalette(paleta)
        layout_principal.addWidget(titulo)

        # --- Barra de búsqueda ---
        barra_busqueda = QHBoxLayout()
        self.caja = QLineEdit()
        self.caja.setPlaceholderText("Buscar juegos...")
        self.caja.setStyleSheet("background:#1B2838; color:white; padding:8px; border-radius:6px;")
        boton_buscar = QPushButton("Buscar")
        boton_buscar.setStyleSheet("background-color:#66C0F4; color:black; padding:8px 16px; border-radius:6px;")
        boton_buscar.clicked.connect(self.buscar)
        barra_busqueda.addWidget(self.caja)
        barra_busqueda.addWidget(boton_buscar)
        layout_principal.addLayout(barra_busqueda)

        # --- Área de resultados ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.widget_resultados = QWidget()
        self.layout_resultados = QVBoxLayout(self.widget_resultados)
        self.scroll.setWidget(self.widget_resultados)
        layout_principal.addWidget(self.scroll)

    # --- Buscar juegos ---
    def buscar(self):
        texto = self.caja.text().strip()
        if not texto:
            return

        # Limpiar resultados anteriores
        while self.layout_resultados.count():
            item = self.layout_resultados.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            juegos = buscar_juego(texto, limit=8)
        except Exception as e:
            self.layout_resultados.addWidget(QLabel(f"Error al buscar: {e}"))
            return

        if not juegos:
            self.layout_resultados.addWidget(QLabel("No se encontraron resultados."))
            return

        for juego in juegos:
            self.layout_resultados.addWidget(self.crear_tarjeta(juego))

    # --- Crear tarjeta de juego ---
    def crear_tarjeta(self, juego):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color:#1B2838;
                border-radius:10px;
                padding:10px;
            }
        """)
        layout = QVBoxLayout(frame)

        # --- Parte superior ---
        hbox = QHBoxLayout()

        # Portada
        lbl_portada = QLabel()
        lbl_portada.setFixedSize(200, 250)
        hbox.addWidget(lbl_portada)

        if "cover" in juego and "image_id" in juego["cover"]:
            url = obtener_url_cover(juego["cover"]["image_id"])
            hilo = HiloImagen(url, lbl_portada)
            hilo.senales.terminado.connect(lambda pix, l=lbl_portada: l.setPixmap(
                pix.scaled(200, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            self.hilos.start(hilo)

        # Datos del juego
        vinfo = QVBoxLayout()
        nombre = QLabel(juego.get("name", "Sin nombre"))
        nombre.setFont(QFont("Arial", 20, QFont.Bold))
        vinfo.addWidget(nombre)

        rating = juego.get("rating")
        vinfo.addWidget(QLabel(f"Puntuación: {rating:.2f}" if rating else "Puntuación: N/A"))

        plataformas = ", ".join(p['name'] for p in juego.get("platforms", [])) if juego.get("platforms") else "N/A"
        vinfo.addWidget(QLabel(f"Plataformas: {plataformas}"))

        generos = ", ".join(g['name'] for g in juego.get("genres", [])) if juego.get("genres") else "N/A"
        vinfo.addWidget(QLabel(f"Géneros: {generos}"))

        resumen = QLabel(juego.get("summary", "Sin resumen disponible."))
        resumen.setWordWrap(True)
        vinfo.addWidget(resumen)

        # --- Botón con marco ---
        boton = QPushButton("Ver Trailer")
        boton.setStyleSheet("""
            QPushButton {
                border: 2px solid #66C0F4;
                color: white;
                padding: 6px 12px;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #66C0F4;
                color: black;
            }
        """)
        boton.clicked.connect(lambda _, n=juego.get("name", ""): webbrowser.open(
            f"https://www.youtube.com/results?search_query={n.replace(' ', '+')}+trailer"))
        vinfo.addWidget(boton)

        hbox.addLayout(vinfo)
        layout.addLayout(hbox)

        # --- Capturas ---
        capturas = juego.get("screenshots", [])[:3]
        if capturas:
            hcapt = QHBoxLayout()
            for cap in capturas:
                lbl = QLabel()
                lbl.setFixedSize(300, 180)
                lbl.setStyleSheet("border-radius:6px;")
                hcapt.addWidget(lbl)
                url = obtener_url_screenshot(cap["image_id"])
                hilo = HiloImagen(url, lbl)
                hilo.senales.terminado.connect(lambda pix, l=lbl: l.setPixmap(
                    pix.scaled(300, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                self.hilos.start(hilo)
            layout.addLayout(hcapt)

        return frame


# --- Inicio ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaJuegos()
    ventana.show()
    sys.exit(app.exec_())


