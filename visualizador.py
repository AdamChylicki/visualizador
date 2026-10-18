"""
Módulo: visualizador

Descripción:
    Este módulo permite cargar archivos CSV, 
    y generar gráficas para su visualización y análisis.

Autor:
    Adam

Fecha:
    13-10-2026

Versión:
    1.0
"""

from tkinter import Tk, filedialog
from pathlib import Path
import pandas as pd

import matplotlib.pyplot as plt
import pyqtgraph as pg

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout


def comprobar_datos_numericos(datos):
    for columna in datos.columns:
        valores = pd.to_numeric(datos[columna], errors="coerce")

        valores_invalidos = datos[columna].notna() & valores.isna()

        if valores_invalidos.any():
            filas = datos.index[valores_invalidos].tolist()
            raise ValueError(
                f"La columna '{columna}' contiene datos no numéricos "
                f"en las filas: {filas}"
            )

    return True



def visualizar_csv2(archivo):
    """
    Carga un archivo CSV y representa sus variables mediante PyQtGraph.

    Args:
        archivo: Ruta del archivo CSV seleccionado.
    """
    try:
        # Leer el archivo CSV
        datos = pd.read_csv(archivo, sep=",", comment="#")

        # Limpiar los nombres de las columnas
        datos.columns = datos.columns.str.strip()

        # Comprobar que existe la columna de frecuencia
        if "freq_Hz" not in datos.columns:
            print("El CSV no contiene la columna freq_Hz.")
            return

        # Convertir las columnas a valores numéricos
        for columna in datos.columns:
            datos[columna] = pd.to_numeric(datos[columna], errors="coerce")

        # Eliminar filas sin frecuencia válida
        datos = datos.dropna(subset=["freq_Hz"])

        if datos.empty:
            print("El archivo no contiene datos válidos.")
            return

        # Seleccionar las variables que se representarán
        columnas_graficar = [
            columna for columna in datos.select_dtypes(include="number").columns
            if columna != "freq_Hz" and datos[columna].notna().any()
        ]

        if not columnas_graficar:
            print("No hay variables numéricas para representar.")
            return

        # Crear la aplicación Qt si todavía no existe
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Crear la ventana principal
        ventana = QMainWindow()
        ventana.setWindowTitle(f"Visualizador CSV - {Path(archivo).name}")
        ventana.resize(1100, 800)

        # Crear el contenedor de las gráficas
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)

        # Crear una gráfica independiente para cada variable
        for columna in columnas_graficar:
            grafica = pg.PlotWidget()
            grafica.setBackground("w")
            grafica.showGrid(x=True, y=True, alpha=0.3)
            grafica.setTitle(columna)
            grafica.setLabel("bottom", "Frecuencia", units="Hz")
            grafica.setLabel("left", columna)

            # Obtener los puntos válidos de la variable
            datos_validos = datos[["freq_Hz", columna]].dropna()

            grafica.plot(
                datos_validos["freq_Hz"].to_numpy(),
                datos_validos[columna].to_numpy(),
                pen=pg.mkPen(color=(0, 100, 220), width=2)
            )

            layout.addWidget(grafica)

        ventana.setCentralWidget(contenedor)
        ventana.show()

        # Mantener referencias para evitar que se cierre la ventana
        visualizar_csv2.ventana = ventana
        visualizar_csv2.app = app

        # Ejecutar el bucle de eventos si la aplicación no está iniciada
        if not getattr(app, "_bucle_iniciado", False):
            app._bucle_iniciado = True
            app.exec()

    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        print(f"Error al leer el archivo CSV: {error}")

def visualizar_csv_matplot(archivo):
    """
    Lee un archivo CSV y representa sus columnas numéricas en una gráfica.
    """
    try:
        # Leer el CSV, detectando posibles separadores
        datos = pd.read_csv(archivo, sep=",", comment="#")

        # Eliminar espacios de los nombres de las columnas
        datos.columns = datos.columns.str.strip()

        # Convertir las columnas a valores numéricos cuando sea posible
        comprobar_datos_numericos(datos)

        # Seleccionar las columnas numéricas
        columnas_numericas = datos.select_dtypes(include="number").columns

        if len(columnas_numericas) == 0:
            print("El archivo no contiene columnas numéricas.")
            return

        # Utilizar la frecuencia como eje X si existe
        eje_x = "freq_Hz" if "freq_Hz" in columnas_numericas else None

        if eje_x:
            columnas_y = [
                columna for columna in columnas_numericas
                if columna != eje_x
            ]
            datos = datos.set_index(eje_x)
        else:
            columnas_y = list(columnas_numericas)

        if not columnas_y:
            print("No hay columnas disponibles para representar.")
            return

        # Crear una única gráfica con dos escalas verticales
        plt.style.use("dark_background")

        # --------------------------------------------------------------------

        fig, ax1 = plt.subplots(figsize=(7, 5))

        # Eje izquierdo: módulo de impedancia
        ax1.plot(
            datos.index,
            datos["absZ_Ohm"],
            color="deepskyblue",
            linewidth=1.5,
            label="Módulo de impedancia (|Z|)"
        )

        ax1.set_xlabel("Frecuencia (Hz)")
        ax1.set_ylabel("Módulo de impedancia (Ω)", color="deepskyblue")
        ax1.tick_params(axis="y", labelcolor="deepskyblue")
        ax1.set_facecolor("black")
        ax1.grid(True, color="gray", alpha=0.3)

        # Eje derecho: módulo de admitancia
        ax2 = ax1.twinx()

        ax2.plot(
            datos.index,
            datos["absY_S"],
            color="orange",
            linewidth=1.5,
            label="Módulo de admitancia (|Y|)"
        )

        ax2.set_ylabel("Módulo de admitancia (S)", color="orange")
        ax2.tick_params(axis="y", labelcolor="orange")

        # Unificar las leyendas
        lineas1, etiquetas1 = ax1.get_legend_handles_labels()
        lineas2, etiquetas2 = ax2.get_legend_handles_labels()

        ax1.legend(
            lineas1 + lineas2,
            etiquetas1 + etiquetas2,
            loc="best"
        )

        ax1.set_title("Módulos de impedancia y admitancia")
        fig.patch.set_facecolor("black")

        # --------------------------------------------------------------------
        
        fig2, ax3 = plt.subplots(figsize=(7, 5))

        # Eje izquierdo: módulo de impedancia
        ax3.plot(
            datos.index,
            datos["realZ_Ohm"],
            color="deepskyblue",
            linewidth=1.5,
            label="realZ_Ohm"
        )

        ax3.set_xlabel("Frecuencia (Hz)")
        ax3.set_ylabel("realZ_Ohm", color="deepskyblue")
        ax3.tick_params(axis="y", labelcolor="deepskyblue")
        ax3.set_facecolor("black")
        ax3.grid(True, color="gray", alpha=0.3)

        # Eje derecho: módulo de admitancia
        ax4 = ax3.twinx()

        ax4.plot(
            datos.index,
            datos["imagZ_Ohm"],
            color="orange",
            linewidth=1.5,
            label="imagZ_Ohm"
        )

        ax4.set_ylabel("imagZ_Ohm", color="orange")
        ax4.tick_params(axis="y", labelcolor="orange")

        # Unificar las leyendas
        lineas3, etiquetas3 = ax3.get_legend_handles_labels()
        lineas4, etiquetas4 = ax4.get_legend_handles_labels()

        ax3.legend(
            lineas3 + lineas4,
            etiquetas3 + etiquetas4,
            loc="best"
        )

        ax1.set_title("abs Z, abs Y")
        ax3.set_title("Re Z, Im Z")
        fig.patch.set_facecolor("black")

        fig.canvas.manager.window.move(0, 0)
        fig2.canvas.manager.window.move(750, 0)

        plt.tight_layout()
        plt.show()

    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        print(f"No se ha podido leer el archivo CSV: {error}")

def seleccionar_archivo_csv():
    """
    Abre una ventana para seleccionar un archivo CSV.

    Returns:
        Path | None: Ruta del archivo seleccionado o None si se cancela.
    """
    ventana = Tk()
    ventana.withdraw()

    archivo = filedialog.askopenfilename(
        parent=ventana,
        title="Seleccionar archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    ventana.destroy()

    if not archivo:
        return None

    return Path(archivo)

def seleccionar_carpeta():
    """
    Abre una ventana para seleccionar la carpeta que contiene los archivos.

    Returns:
        Path | None: Ruta de la carpeta seleccionada o None si se cancela.
    """
    ventana = Tk()
    ventana.withdraw()

    carpeta = filedialog.askdirectory(
        title="Seleccionar carpeta con archivos"
    )

    ventana.destroy()

    if not carpeta:
        return None

    return Path(carpeta)


# --------------------------- main -------------------------------


print("Iniciando visualizador...")

# Ejemplo de uso
archivo = seleccionar_archivo_csv()

if archivo:
    visualizar_csv_matplot(archivo)






