from db.connection import get_connection

class Productos:
    def __init__(self):
        self.conexion = get_connection()
        if self.conexion is None:
            raise ConnectionError("Error al conectar con la Base de Datos")

    def _ejecutar_consulta(self, query, params=None):
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return []


# Realizar las consultas aqui

    # Obtener Lista de productos completa
    def obtener_todos_con_detalle(self):
        query = """
            SELECT 
                p.id,
                p.nombre,
                p.codigo_barra,
                p.unidad_medida,
                p.precio_venta,
                p.stock,
                tp.detalle AS tipo_producto,
                d.nombre AS distribuidora
            FROM productos p
            LEFT JOIN tipos_productos tp ON p.id_tipo_producto = tp.id
            LEFT JOIN distribuidores d ON p.id_distribuidora = d.id
            ORDER BY p.nombre;
        """
        return self._ejecutar_consulta(query)
    
    # Busqueda con Lector 
    def busqueda_por_lector(self, codigo_barra):
        query = """
        SELECT 
            id, nombre, precio_venta, stock, unidad_medida
        FROM productos 
        WHERE codigo_barra = %s;
    """
        return self._ejecutar_consulta(query, (codigo_barra,))

    # Ingresar un producto Nuevo
    def agregar_producto(self, nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora):
        query = """
            INSERT INTO productos
            (nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(query, (
                    nombre,
                    codigo_barra,
                    unidad_medida,
                    precio_venta,
                    stock,
                    id_tipo_producto,
                    id_distribuidora
                ))
                self.conexion.commit() #Esto guarda los cambios
                return cursor.lastrowid # Devuelve el ID del nuevo producto
        except Exception as e:
            print(f"Error al insertar producto: {e}")
            self.conexion.rollback()
            return None
    
    #Editar o Actualizar productos
    def actualizar_producto(self, id_producto, nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora):
        query = """
            UPDATE productos
            SET
                nombre = %s,
                codigo_barra = %s,
                unidad_medida = %s,
                precio_venta = %s,
                stock = %s,
                id_tipo_producto = %s,
                id_distribuidora = %s,
            WHERE id = %s;
        """
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(query,(
                    nombre,
                    codigo_barra,
                    unidad_medida,
                    precio_venta,
                    stock,
                    id_tipo_producto,
                    id_distribuidora,
                    id_producto
                ))
                self.conexion.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            self.conexion.rollback()
            return None
        
     #Registrar una Venta
     