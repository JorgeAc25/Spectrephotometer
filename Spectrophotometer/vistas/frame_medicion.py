from tkinter import ttk
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import serial.tools.list_ports
import time
from conexion.consultas_db import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import serial
from time import sleep
from export.export_data import *


class Graficas(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def graph_values():
            try:
                self.nombre = self.tabla.item(self.tabla.selection())["text"]
                self.v400 = self.tabla.item(self.tabla.selection())["values"][0]
                self.v460 = self.tabla.item(self.tabla.selection())["values"][1]
                self.v515 = self.tabla.item(self.tabla.selection())["values"][2]
                self.v603 = self.tabla.item(self.tabla.selection())["values"][3]
                self.v625 = self.tabla.item(self.tabla.selection())["values"][4]

                self.values = [
                    self.v400,
                    self.v460,
                    self.v515,
                    self.v603,
                    self.v625
                ]
                plot_graph(self.nombre, 0, 0,self.values)

            except:
                tk.messagebox.showinfo("Error", "Debes elegir datos válidos")

        def detect_serial_port():
            excluded_ports = ["COM1"]  # Agrega aquí los puertos que deseas excluir
            ports = [port for port in serial.tools.list_ports.comports() if port.device not in excluded_ports and hasattr(port, 'device')]
            
            if len(ports) > 0:
                return ports[0].device
            else:
                return None

        def show_error_message():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", "Conecta correctamente el cable USB")

        def start_measurement(nombre):
            if nombre is None or nombre == "":
                tk.messagebox.showinfo("Advertencia", "Agrega un nombre válido a tu solución")
                return

            port = detect_serial_port()
            
            if port is not None:
                try:
                    self.nombre = nombre
                    self.datos = []
                    self.ser = serial.Serial(port, 9600)
                    self.flag = "3"
                    self.ser.write(self.flag.encode())
                    time.sleep(9)
                    
                    for i in range(0, 5):
                        self.output = self.ser.readline().decode().strip()
                        self.datos.append(self.output)

                    self.res = [eval(i) for i in self.datos]
                    
                    self.flag = 0
                    print(self.flag)
                    
                    if (self.ser.isOpen() == True) and (self.flag == 0):
                        self.flag = 1
                        print(self.flag)
                        self.ser.close()
                        
                        if (self.ser.isOpen() == False) and (self.flag == 1):
                            self.flag = 0
                            print(self.flag)
                            print(self.res)
                            save_values(self.nombre, 0, self.res)
                except Exception as e:
                    show_error_message()
                    print(f"Error: {e}")


        def calibracion():
            port = detect_serial_port()
            print("puerto: ", port)
            if port is not None:

                nombre = "Calibración"
                datos = []
                ser = serial.Serial(port, 9600)
                flag = "4"
                ser.write(flag.encode())
                time.sleep(9)

                for _ in range(5):
                    output = ser.readline().decode().strip()
                    datos.append(output)

                # Usar try-except para manejar posibles errores de conversión a número
                res = []
                for item in datos:
                    try:
                        valor = float(item)
                        res.append(valor)
                        
                        # Verificar si el valor no es igual a 205
                        if valor != 205:
                            tk.messagebox.showinfo("Error", "Datos de calibración incorrectos, inténtalo de nuevo")
                            return  # Salir de la función si hay un error
                            
                    except ValueError:
                        tk.messagebox.showinfo("Error", "Error al realizar la calibración")
                        return  # Salir de la función si hay un error
                        
                save_values(nombre, 1, res)
                
        def save_values(nombre, flag,values=[] ):
            self.flag = flag
            self.compuesto = nombre
            self.lista = values
            print(self.lista)
            query = "INSERT INTO MEDICIONES (SOLUCION, '-400','-460','-515','-603','-625') VALUES (?,?,?,?,?,?)"
            parametros = (
                self.compuesto,
                self.lista[0],
                self.lista[1],
                self.lista[2],
                self.lista[3],
                self.lista[4],
            )

            conexion = Conectar()
            conexion.run_db(query, parametros)
            listar_datos()
            plot_graph(self.compuesto,0, self.flag,self.lista)
            
       

        def plot_graph(nombre, flag_export, flag, value=[]):
            plt.close()
            compuesto1 = nombre
            lista1 = value

            # Convertir los valores de lista1 a números decimales
            lista1 = [float(val) for val in lista1]

            valores = {
                "Longitud de onda": ["400", "460", "515", "603", "625"],
                "Valores": lista1,
            }
            df = pd.DataFrame(valores)

            # Crear la figura y los ejes del gráfico
            fig, ax = plt.subplots(num="Medición", figsize=(8, 6))

            # Graficar los valores en el eje y
            ax.plot(df.index, df["Valores"], marker="o")

            # Agregar etiquetas a cada punto
            for i, txt in enumerate(df["Valores"]):
                ax.text(df.index[i], txt, f"{txt:.4f}", ha='center', va='bottom')

            # Configurar el título y las etiquetas de los ejes
            ax.set_title(compuesto1, fontsize=14)
            ax.set_xlabel("Longitud de Onda (nm)", fontsize=12)
            ax.set_ylabel("Absorbancia", fontsize=12)

            # Configurar las etiquetas del eje x
            ax.set_xticks(df.index)
            ax.set_xticklabels(df["Longitud de onda"])

            # Configurar los límites del eje y según la bandera
            if flag == 1:
                ax.set_ylim(195, 215)
            else:
                # Configurar los límites del eje y y las etiquetas con incrementos de 0.05
                min_y = min(lista1)
                max_y = max(lista1)
                step = 0.05
                ax.set_yticks(np.arange(0-0.05, max_y + step, step))
                export_data(compuesto1, lista1)

            # Mostrar el gráfico
            print(type(plt.show()))
            print("Valor de la bandera:", flag_export)
            if flag_export == 1:
                export_data(compuesto1, lista1)
                plt.show()
            else:
                plt.show()

                            
        def delete_values():
            try:
                selected_item = self.tabla.selection()
                if selected_item:
                    selected_id = self.tabla.item(selected_item, "text")  # Suponiendo que el ID está en la primera columna
                    query = f"DELETE FROM MEDICIONES WHERE ID = ?"
                    parametros = (selected_id,)

                    conexion = Conectar() 
                    conexion.run_db(query, parametros)
                    print(f"Dato con ID {selected_id} eliminado correctamente")
                    listar_datos()
                else:
                    tk.messagebox.showinfo("Advertencia", "Selecciona un dato para borrar.")
            except Exception as e:
                tk.messagebox.showinfo("Error", f"Error al borrar el dato: {str(e)}")
                        
        # Labels
        self.label = Label(self, text="").grid(
            column=1, columnspan=10, row=1, rowspan=10, padx=1000, pady=1000
        )
        self.labelReg = Label(self, text="").place(x=447, y=1)
        self.labelNombre = Label(self, text="Solución").place(x=140, y=30)

        # Entradas
        self.entryCompuesto = Entry(self, width=25)
        self.entryCompuesto.place(x=215, y=30)

        # Botones
        self.botonMedicion = Button(
            self,
            text="Nueva Medición",
            command=lambda: start_measurement(self.entryCompuesto.get()),
        )
        self.botonMedicion.place(x=215, y=65)
        self.botonGraficar = Button(self, text="Graficar", command=graph_values)
        self.botonGraficar.place(x=215, y=100)
        self.botonBorrar = Button(self, text = "Borrar", command = delete_values)
        self.botonBorrar.place(x= 215, y= 135)
        self.botonCalibrar = Button(self, text = "Calibrar Dispositivo", command = calibracion)
        self.botonCalibrar.place(x= 215, y= 170)

        # Tabla
        self.tabla = ttk.Treeview(self, columns=("", "", "", "", "",""))
        self.tabla.place(x=70, y=230)
        self.vector = {"#0":"ID","#1":"SOLUCIÓN","#2":"400nm","#3":"460nm","#4":"515nm","#5":"603nm","#6":"625nm"}
        
        for i in self.vector:
            self.texto = self.vector[i]
            self.tabla.heading(i,text = self.texto)
            if i != "#1":
                self.tabla.column(i, width=50)
                
        
        def listar_datos():
            recorrer_tabla = self.tabla.get_children()

            for elementos in recorrer_tabla:
                self.tabla.delete(elementos)

            query = "SELECT * FROM MEDICIONES"
            conexion = Conectar()
            datos = conexion.run_db(query)

            for valor in datos:
                self.tabla.insert(
                    "",
                    "end",
                    text=valor[0],
                    values=(
                        valor[1],
                        valor[2],
                        valor[3],
                        valor[4],
                        valor[5]
                    ),
                )

        listar_datos()
        
        