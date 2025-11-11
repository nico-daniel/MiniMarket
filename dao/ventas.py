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