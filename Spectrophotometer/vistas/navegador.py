from vistas.frame_medicion import *
from tkinter import ttk


class App(ttk.Frame):
    def __init__(self, ventana):
        super().__init__(ventana)

        self.miVentana = ventana
        self.miVentana.title("Espectrofotómetro")
        self.miVentana.geometry("720x600")
        self.miVentana.resizable(True, True)  

        # Contenedor
        self.navegador = ttk.Notebook(self)
        self.navegador.pack(
            fill="both", expand=True, padx=20, pady=20)  

        # Pestaña de Mediciones
        self.Mediciones = Graficas(self.navegador)
        self.navegador.add(
            self.Mediciones, text="Mediciones", padding=20)  

        self.pack(
            fill="both", expand=True)  



