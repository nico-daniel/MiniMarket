from db.connection import get_connection

class Ventas:
    def __init__(self):
        self.conexion = get_connection()
        if self.conexion is None:
            raise ConnectionError("Error al conectar con la Base de Datos")

    def registrar_venta(self, saldo_inicial, total_venta, id_medio_pago, items):
        try:
            self.conexion.autocommit = False
            with self.conexion.cursor() as cursor:
                for item in items:
                    cursor.execute("SELECT stock FROM productos WHERE id = %s FOR UPDATE;", (item['id_producto'],))
                    stock_actual = cursor.fetchone()[0]
                    if stock_actual < item['cantidad']:
                        raise Exception(f"Stock insuficiente para producto ID {item['id_producto']}")

                cursor.execute("INSERT INTO caja (fecha_apertura, saldo_inicial, estado) VALUES (CURDATE(), %s, 'ABIERTA') RETURNING id;", (saldo_inicial,))
                id_caja = cursor.fetchone()[0]

                cursor.execute("INSERT INTO ventas (fecha, total, id_medio_pago, id_caja) VALUES (CURDATE(), %s, %s, %s) RETURNING id;", (total_venta, id_medio_pago, id_caja))
                id_venta = cursor.fetchone()[0]

                for item in items:
                    cursor.execute("INSERT INTO detalle_ventas (precio_unitario, cantidad, subtotal, iva, id_venta, id_producto) VALUES (%s, %s, %s, %s, %s, %s);", (item['precio_unitario'], item['cantidad'], item['subtotal'], item['iva'], id_venta, item['id_producto']))
                    cursor.execute("UPDATE productos SET stock = stock - %s WHERE id = %s;", (item['cantidad'], item['id_producto']))
                    cursor.execute("INSERT INTO movimientos_stock (tipo_movimiento, cantidad, fecha, id_producto) VALUES ('SALIDA_VENTA', %s, CURDATE(), %s);", (item['cantidad'], item['id_producto']))

                self.conexion.commit()
                return {"id_venta": id_venta}
        except Exception as e:
            print(f"Error al registrar venta: {e}")
            self.conexion.rollback()
            return {"error": str(e)}
        
    def obtener_carrito_actual(self):
        query = "SELECT * FROM vista_carrito_actual;"
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener carrito actual: {e}")
            return []
        
    def obtener_caja_del_dia(self):
        query = "SELECT * FROM vista_caja_del_dia;"
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener caja del día: {e}")
            return {}
        
    def calcular_totales_venta(self, id_venta):
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT calcular_totales_venta(%s) AS totales;", (id_venta,))
                resultado = cursor.fetchone()
                return resultado["totales"]
        except Exception as e:
            print(f"Error al calcular totales de venta: {e}")
            return {"error": str(e)}      
        
    def calcular_cambio(self, total, pago):
        try:
            cambio = pago - total
            billetes = [10000, 5000, 2000, 1000, 500, 200, 100]
            desglose = {}
            for b in billetes:
                cantidad = cambio // b
                if cantidad:
                    desglose[f"${b}"] = int(cantidad)
                    cambio -= b * cantidad
            return {
                "cambio": round(pago - total, 2),
                "billetes": desglose
            }
        except Exception as e:
            print(f"Error al calcular cambio: {e}")
            return {"error": str(e)}
        
    def obtener_historial_cajas_completo(self):
        query = "SELECT * FROM vista_historial_cajas_completo;"
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener historial completo de cajas: {e}")
            return []
    
    def cerrar_caja(self, id_caja, saldo_final):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE caja 
                    SET fecha_cierre = NOW(), saldo_final = %s, estado = 'CERRADA' 
                    WHERE id = %s;
                """, (saldo_final, id_caja))
                self.conexion.commit()
                return {"status": "ok"}
        except Exception as e:
            print(f"Error al cerrar caja: {e}")
            self.conexion.rollback()
            return {"error": str(e)}
        
    def obtener_detalle_venta(self, id_venta):
        query = """
            SELECT dv.*, p.nombre AS producto 
            FROM detalle_ventas dv
            JOIN productos p ON dv.id_producto = p.id
            WHERE dv.id_venta = %s;
        """
        return self._ejecutar_consulta(query, (id_venta,))
    
    def anular_venta(self, id_venta):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute("SELECT id_producto, cantidad FROM detalle_ventas WHERE id_venta = %s;", (id_venta,))
                items = cursor.fetchall()
                for item in items:
                    cursor.execute("UPDATE productos SET stock = stock + %s WHERE id = %s;", (item[1], item[0]))
                    cursor.execute("INSERT INTO movimientos_stock (tipo_movimiento, cantidad, fecha, id_producto) VALUES ('ANULACION_VENTA', %s, CURDATE(), %s);", (item[1], item[0]))
                cursor.execute("DELETE FROM detalle_ventas WHERE id_venta = %s;", (id_venta,))
                cursor.execute("DELETE FROM ventas WHERE id = %s;", (id_venta,))
                self.conexion.commit()
                return {"status": "venta anulada"}
        except Exception as e:
            print(f"Error al anular venta: {e}")
            self.conexion.rollback()
            return {"error": str(e)}