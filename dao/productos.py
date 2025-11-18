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

    def obtener_todos_con_detalle(self):
        query = """
            SELECT p.id, p.nombre, p.codigo_barra, p.unidad_medida, p.precio_venta, p.stock,
                   tp.detalle AS tipo_producto, d.nombre AS distribuidora
            FROM productos p
            LEFT JOIN tipos_productos tp ON p.id_tipo_producto = tp.id
            LEFT JOIN distribuidores d ON p.id_distribuidora = d.id
            ORDER BY p.nombre;
        """
        return self._ejecutar_consulta(query)

    def busqueda_por_lector(self, codigo_barra):
        query = """
            SELECT id, nombre, precio_venta, stock, unidad_medida
            FROM productos
            WHERE codigo_barra = %s;
        """
        return self._ejecutar_consulta(query, (codigo_barra,))

    def agregar_producto(self, nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora):
        query = """
            INSERT INTO productos (nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(query, (nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora))
                self.conexion.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al insertar producto: {e}")
            self.conexion.rollback()
            return None

    def actualizar_producto(self, id_producto, nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora):
        query = """
            UPDATE productos
            SET nombre = %s, codigo_barra = %s, unidad_medida = %s, precio_venta = %s,
                stock = %s, id_tipo_producto = %s, id_distribuidora = %s
            WHERE id = %s;
        """
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(query, (nombre, codigo_barra, unidad_medida, precio_venta, stock, id_tipo_producto, id_distribuidora, id_producto))
                self.conexion.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            self.conexion.rollback()
            return None

    def registrar_entrada_stock(self, id_producto, cantidad):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute("UPDATE productos SET stock = stock + %s WHERE id = %s;", (cantidad, id_producto))
                cursor.execute("INSERT INTO movimientos_stock (tipo_movimiento, cantidad, fecha, id_producto) VALUES ('ENTRADA_COMPRA', %s, CURDATE(), %s);", (cantidad, id_producto))
                self.conexion.commit()
                return {"status": "ok"}
        except Exception as e:
            print(f"Error al registrar entrada de stock: {e}")
            self.conexion.rollback()
            return {"error": str(e)}

    def obtener_historial_movimientos(self, id_producto):
        query = """
            SELECT ms.id, ms.tipo_movimiento, ms.cantidad, ms.fecha,
                   CASE WHEN ms.tipo_movimiento LIKE 'ENTRADA%' THEN 'success'
                        WHEN ms.tipo_movimiento LIKE 'SALIDA%' THEN 'danger'
                        ELSE 'info' END AS tipo_color
            FROM movimientos_stock ms
            WHERE ms.id_producto = %s
            ORDER BY ms.fecha DESC;
        """
        return self._ejecutar_consulta(query, (id_producto,))

    def obtener_resumen_diario(self):
        try:
            with self.conexion.cursor(dictionary=True) as cursor:

                # ------------------------- CAMBIO 1 -------------------------
                # Quitado "AND activo = 1" porque la columna NO existe
                cursor.execute("""
                    SELECT COALESCE(SUM(v.total), 0) AS total_ventas, 
                           COUNT(v.id) AS cantidad_ventas
                    FROM ventas v 
                    WHERE v.fecha = CURDATE();
                """)

                resumen_ventas = cursor.fetchone()

                cursor.execute("""
                    SELECT COUNT(*) AS productos_bajo_stock
                    FROM productos
                    WHERE stock <= 5;  -- ← CAMBIO (se quitó activo = 1)
                """)
                # -------------------------------------------------------------

                resumen_stock = cursor.fetchone()

                return {
                    "total_ventas": resumen_ventas['total_ventas'],
                    "cantidad_ventas": resumen_ventas['cantidad_ventas'],
                    "productos_bajo_stock": resumen_stock['productos_bajo_stock']
                }

        except Exception as e:
            print(f"Error al obtener resumen diario: {e}")
            return {"error": str(e)}

    def obtener_historial_cajas(self):
        query = "SELECT * FROM vista_historial_cajas;"
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener historial de cajas: {e}")
            return []

    def obtener_mas_vendidos_hoy(self):
        query = "SELECT * FROM vista_mas_vendidos_hoy;"
        return self._ejecutar_consulta(query)

    def obtener_productos_ordenados(self, orden="stock_asc", tipo=None, busqueda=None):
        query = """
            SELECT 
                p.*, 
                tp.detalle AS tipo_producto,
                d.nombre AS distribuidor,
                CASE WHEN p.stock <= 5 THEN 1 ELSE 0 END AS alerta_critica
            FROM productos p
            LEFT JOIN tipos_productos tp ON p.id_tipo_producto = tp.id

            -- ------------------------- CAMBIO 2 -------------------------
            -- Estaba "id_distribuidor" pero tu columna real es id_distribuidora
            LEFT JOIN distribuidores d ON p.id_distribuidora = d.id
            -- ------------------------------------------------------------

            WHERE 1=1
        """

        params = {}

        if tipo:
            query += " AND p.id_tipo_producto = %(tipo)s"
            params["tipo"] = tipo

        if busqueda:
            query += " AND (p.nombre LIKE %(busqueda)s OR p.codigo_barra LIKE %(busqueda)s)"
            params["busqueda"] = f"%{busqueda}%"

        orden_map = {
            "stock_asc": "p.stock ASC",
            "stock_desc": "p.stock DESC",
            "nombre_asc": "p.nombre ASC",
            "precio_asc": "p.precio_venta ASC",
            "precio_desc": "p.precio_venta DESC",
            "nuevo": "p.id DESC"
        }

        orden_sql = orden_map.get(orden, "p.stock ASC")
        query += f" ORDER BY {orden_sql}, p.nombre ASC"

        return self._ejecutar_consulta(query, params)

    def eliminar_producto(self, id_producto):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute("DELETE FROM productos WHERE id = %s;", (id_producto,))
                self.conexion.commit()
                return {"status": "ok"}
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            self.conexion.rollback()
            return {"error": str(e)}
