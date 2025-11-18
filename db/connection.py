import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='minimarket'
        )

        if conexion.is_connected():
            print("Conexion Exitosa a la Base de Datos")
            db_info = conexion.get_server_info()
            print("Version del Servidor MySQL", db_info)
            return conexion

    except Error as e:
        print("Error al Conectarse a MySQL", e)
        return None

# 👇 Este bloque debe estar FUERA de la función
if __name__ == "__main__":
    print("--- Iniciando Prueba de conexion ---")
    conexion_prueba = get_connection()

    if conexion_prueba:
        print("Resultado de la prueba de conexion: La conexion se establecio y funciona")
        conexion_prueba.close()
    else:
        print("Resultado de la prueba: Conexion fallida. Revisa los errores o tu servidor MySQL.")