from db.connection import get_connection

class Ventas:
    def __init__(self):
        self.conexion = get_connection()
        if self.conexion is None:
            raise ConnectionError("Error al conectar con la Base de Datos")

    # =========================
    # MÉTODO AUXILIAR
    # =========================
    def _ejecutar_consulta(self, query, params=None, fetchone=False):
        try:
            with self.conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                if fetchone:
                    return cursor.fetchone()
                return cursor.fetchall()
        except Exception as e:
            print(f"Error de consulta: {e}")
            return [] if not fetchone else None

    # =========================
    # REGISTRAR VENTA
    # =========================
    def registrar_venta(self, total_venta, id_medio_pago, items):
        """
        items = [
            {
                'id_producto': int,
                'precio_unitario': float,
                'cantidad': int,
                'subtotal': float,
                'iva': float
            },
            ...
        ]
        """
        try:
            self.conexion.autocommit = False
            with self.conexion.cursor() as cursor:
                # 1️⃣ Crear caja si no hay abierta
                cursor.execute(
                    "SELECT id FROM caja WHERE estado='ABIERTA' ORDER BY fecha_apertura DESC LIMIT 1;"
                )
                caja = cursor.fetchone()
                if caja:
                    id_caja = caja[0]
                else:
                    cursor.execute(
                        "INSERT INTO caja (fecha_apertura, saldo_inicial, estado) VALUES (CURDATE(), 0, 'ABIERTA');"
                    )
                    id_caja = cursor.lastrowid

                # 2️⃣ Verificar stock
                for item in items:
                    cursor.execute(
                        "SELECT stock FROM productos WHERE id = %s FOR UPDATE;",
                        (item['id_producto'],)
                    )
                    stock_actual = cursor.fetchone()[0]
                    if stock_actual < item['cantidad']:
                        raise Exception(f"Stock insuficiente para producto ID {item['id_producto']}")

                # 3️⃣ Registrar venta
                cursor.execute(
                    "INSERT INTO ventas (fecha, total, id_medio_pago, id_caja) VALUES (CURDATE(), %s, %s, %s);",
                    (total_venta, id_medio_pago, id_caja)
                )
                id_venta = cursor.lastrowid

                # 4️⃣ Registrar detalle de venta y movimientos de stock
                for item in items:
                    cursor.execute(
                        """
                        INSERT INTO detalle_ventas
                        (precio_unitario, cantidad, subtotal, iva, id_venta, id_producto)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (
                            item['precio_unitario'],
                            item['cantidad'],
                            item['subtotal'],
                            item['iva'],
                            id_venta,
                            item['id_producto']
                        )
                    )

                    cursor.execute(
                        "UPDATE productos SET stock = stock - %s WHERE id = %s;",
                        (item['cantidad'], item['id_producto'])
                    )

                    cursor.execute(
                        "INSERT INTO movimientos_stock (tipo_movimiento, cantidad, fecha, id_producto) "
                        "VALUES ('SALIDA_VENTA', %s, CURDATE(), %s);",
                        (item['cantidad'], item['id_producto'])
                    )

                self.conexion.commit()
                return {"id_venta": id_venta}

        except Exception as e:
            print(f"Error al registrar venta: {e}")
            self.conexion.rollback()
            return {"error": str(e)}

    # =========================
    # OBTENER VENTA POR ID
    # =========================
    def obtener_detalle_venta(self, id_venta):
        query = """
            SELECT dv.id, dv.precio_unitario, dv.cantidad, dv.subtotal, dv.iva,
                   p.nombre AS producto
            FROM detalle_ventas dv
            LEFT JOIN productos p ON dv.id_producto = p.id
            WHERE dv.id_venta = %s;
        """
        return self._ejecutar_consulta(query, (id_venta,))

    # =========================
    # ANULAR VENTA
    # =========================
    def anular_venta(self, id_venta):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id_producto, cantidad FROM detalle_ventas WHERE id_venta = %s;",
                    (id_venta,)
                )
                items = cursor.fetchall()

                for item in items:
                    cursor.execute(
                        "UPDATE productos SET stock = stock + %s WHERE id = %s;",
                        (item[1], item[0])
                    )
                    cursor.execute(
                        "INSERT INTO movimientos_stock (tipo_movimiento, cantidad, fecha, id_producto) "
                        "VALUES ('ANULACION_VENTA', %s, CURDATE(), %s);",
                        (item[1], item[0])
                    )

                cursor.execute("DELETE FROM detalle_ventas WHERE id_venta = %s;", (id_venta,))
                cursor.execute("DELETE FROM ventas WHERE id = %s;", (id_venta,))
                self.conexion.commit()
                return {"status": "venta anulada"}

        except Exception as e:
            print(f"Error al anular venta: {e}")
            self.conexion.rollback()
            return {"error": str(e)}

    # =========================
    # OBTENER CAJA DEL DÍA
    # =========================
    def obtener_caja_del_dia(self):
        query = """
            SELECT c.id, c.fecha_apertura, c.fecha_cierre, c.saldo_inicial, c.saldo_final, c.estado,
                   COALESCE(SUM(v.total),0) AS total_ventas
            FROM caja c
            LEFT JOIN ventas v ON v.id_caja = c.id
            WHERE DATE(c.fecha_apertura) = CURDATE()
            GROUP BY c.id;
        """
        return self._ejecutar_consulta(query, fetchone=True)

    # =========================
    # CALCULAR CAMBIO
    # =========================
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
            return {"cambio": round(pago - total, 2), "billetes": desglose}
        except Exception as e:
            print(f"Error al calcular cambio: {e}")
            return {"error": str(e)}

    # =========================
    # CERRAR CAJA
    # =========================
    def cerrar_caja(self, id_caja, saldo_final):
        try:
            with self.conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE caja SET fecha_cierre = NOW(), saldo_final = %s, estado = 'CERRADA' WHERE id = %s;",
                    (saldo_final, id_caja)
                )
                self.conexion.commit()
                return {"status": "ok"}
        except Exception as e:
            print(f"Error al cerrar caja: {e}")
            self.conexion.rollback()
            return {"error": str(e)}

    # =========================
    # HISTORIAL DE CAJAS COMPLETO
    # =========================
    def obtener_historial_cajas_completo(self):
        query = """
            SELECT c.id, c.fecha_apertura, c.fecha_cierre, c.saldo_inicial, c.saldo_final, c.estado,
                   COALESCE(SUM(v.total),0) AS total_ventas
            FROM caja c
            LEFT JOIN ventas v ON v.id_caja = c.id
            GROUP BY c.id
            ORDER BY c.fecha_apertura DESC;
        """
        return self._ejecutar_consulta(query)
