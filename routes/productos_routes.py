from flask import Blueprint, request, jsonify
from dao.productos import Productos
from db.connection import get_connection   # ← CAMBIO (para consultas directas sin vistas)

productos_bp = Blueprint('productos_bp', __name__)
productos = Productos()

# ======================
# ENDPOINTS NORMALES
# ======================

@productos_bp.route('/', methods=['GET'])
def obtener_todos():
    return jsonify(productos.obtener_todos_con_detalle())

@productos_bp.route('/buscar', methods=['GET'])
def buscar_por_codigo():
    codigo = request.args.get('codigo_barra')
    if not codigo:
        return jsonify({"error": "Falta el parámetro 'codigo_barra'"}), 400
    return jsonify(productos.busqueda_por_lector(codigo))

@productos_bp.route('/', methods=['POST'])
def agregar_producto():
    data = request.json
    try:
        nuevo_id = productos.agregar_producto(
            data['nombre'],
            data['codigo_barra'],
            data['unidad_medida'],
            data['precio_venta'],
            data['stock'],
            data['id_tipo_producto'],
            data['id_distribuidora']
        )
        return jsonify({"id": nuevo_id})
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400

@productos_bp.route('/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    data = request.json
    try:
        filas_afectadas = productos.actualizar_producto(
            id_producto,
            data['nombre'],
            data['codigo_barra'],
            data['unidad_medida'],
            data['precio_venta'],
            data['stock'],
            data['id_tipo_producto'],
            data['id_distribuidora']
        )
        return jsonify({"actualizados": filas_afectadas})
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400

@productos_bp.route('/entrada-stock', methods=['POST'])
def entrada_stock():
    data = request.json
    try:
        resultado = productos.registrar_entrada_stock(
            data['id_producto'],
            data['cantidad']
        )
        return jsonify(resultado)
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400

@productos_bp.route('/movimientos/<int:id_producto>', methods=['GET'])
def historial_movimientos(id_producto):
    return jsonify(productos.obtener_historial_movimientos(id_producto))

@productos_bp.route('/resumen-diario', methods=['GET'])
def resumen_diario():
    return jsonify(productos.obtener_resumen_diario())

# ======================================================
# 🔥 ENDPOINT MODIFICADO 1 – historial-cajas SIN VISTA
# ======================================================

@productos_bp.route('/historial-cajas', methods=['GET'])
def historial_cajas():

    # ← CAMBIO: consulta directa sin vista
    query = """
        SELECT 
            c.id,
            c.fecha_apertura,
            c.fecha_cierre,
            c.saldo_inicial,
            c.saldo_final,
            c.estado,
            (
                SELECT COALESCE(SUM(v.total), 0)
                FROM ventas v
                WHERE v.id_caja = c.id
            ) AS total_ventas
        FROM caja c
        ORDER BY c.fecha_apertura DESC;
    """

    try:
        conn = get_connection()   # ← CAMBIO
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            datos = cursor.fetchall()
        return jsonify(datos)

    except Exception as e:
        print("Error historial cajas:", e)
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🔥 ENDPOINT MODIFICADO 2 – mas-vendidos-hoy SIN VISTA
# ======================================================

@productos_bp.route('/mas-vendidos-hoy', methods=['GET'])
def mas_vendidos_hoy():

    # ← CAMBIO: consulta directa sin vista
    query = """
        SELECT 
            p.id AS id_producto,
            p.nombre,
            SUM(dv.cantidad) AS total_vendido
        FROM detalle_ventas dv
        JOIN ventas v ON dv.id_venta = v.id
        JOIN productos p ON dv.id_producto = p.id
        WHERE v.fecha = CURDATE()
        GROUP BY p.id, p.nombre
        ORDER BY total_vendido DESC;
    """

    try:
        conn = get_connection()   # ← CAMBIO
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            datos = cursor.fetchall()
        return jsonify(datos)

    except Exception as e:
        print("Error mas vendidos:", e)
        return jsonify({"error": str(e)}), 500


# ======================
# ELIMINAR PRODUCTO
# ======================

@productos_bp.route('/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    return jsonify(productos.eliminar_producto(id_producto))

# ===========================
# ORDENADOS (FUNCIONA OK)
# ===========================

@productos_bp.route('/ordenados', methods=['GET'])
def productos_ordenados():
    orden = request.args.get('orden', 'stock_asc')
    tipo = request.args.get('tipo')
    busqueda = request.args.get('busqueda')
    return jsonify(productos.obtener_productos_ordenados(orden, tipo, busqueda))
