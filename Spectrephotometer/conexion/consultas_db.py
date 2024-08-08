import sqlite3


class Conectar:
    nombre_db = "bdd/Espectrofotómetro.db"

    def run_db(self, query, parametros=()):
        with sqlite3.connect(self.nombre_db) as conexion:
            cursor = conexion.cursor()
            datos = cursor.execute(query, parametros)

            conexion.commit()
        return datos
