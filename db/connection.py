import mysql.connector
from mysql.connector import Error

def get_connection():

    try:
        conexion = mysql.connector.connet(
            host = 'localhost',         # o la IP del servivor MySQL
            user = 'root',              # el ususario de MySQL
            password = '',              # tu contraseña , si no se tiene una contraseña se deja vacio
            database = 'minimarket'     # el nombre de la base de datos que se usara , tiene que estar escrito de la misma forma que en la base de datos creada
        )

        if conexion.is_connected():
            print("Conexion Exitosa a la Base de Datos")
            db_info = conexion.get_server_info()
            print("Version del Servidor MySQL" , db_info)
            return conexion
        
    except Error as e:
        print ("Error al Conectarse a MySQL", e)
        return None
    
    
    if __name__ == "__main":
        print("--- Iniciando Prueba de conexion ---")
        conexion_prueba = get_connection()

        if conexion_prueba:
            print("Resultado de la prueba de conexion: La conexion se establecio y funciona")
            conexion_prueba.close()
        else:
            print("Resultado de la prueba: Conexion fallida. Revisa los errores o tu servidor MySQL.")

# Para conectar escribir (python -m db.connection)