from flask import Blueprint, request, jsonify
from dao.ventas import Ventas

ventas_bp = Blueprint('ventas_bp', __name__)
ventas = Ventas()

# =============================
# ✅ Registrar una venta con validación de stock
# =============================
@ventas_bp.route('/', methods=['POST'])
def registrar_venta():
    data = request.json
    try:
        # --------------------- CORREGIDO ---------------------
        # Eliminé 'saldo_inicial' porque la clase Ventas maneja la caja automáticamente
        resultado = ventas.registrar_venta(
            total_venta=data['total_venta'],
            id_medio_pago=data['id_medio_pago'],
            items=data['items']
        )
        # ------------------------------------------------------
        return jsonify(resultado)
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400

# =============================
# GET carrito actual
# =============================
@ventas_bp.route('/carrito-actual', methods=['GET'])
def carrito_actual():
    # --------------------- CORREGIDO ---------------------
    # Antes dependía de vista 'vista_carrito_actual', ahora se hace consulta directa a la última venta
    query = """
        SELECT dv.*, p.nombre AS producto
        FROM detalle_ventas dv
        LEFT JOIN productos p ON dv.id_producto = p.id
        WHERE dv.id_venta = (
            SELECT id FROM ventas ORDER BY id DESC LIMIT 1
        );
    """
    resultado = ventas._ejecutar_consulta(query)
    # ------------------------------------------------------
    return jsonify(resultado)

# =============================
# GET caja del dia
# =============================
@ventas_bp.route('/caja-del-dia', methods=['GET'])
def caja_del_dia():
    resultado = ventas.obtener_caja_del_dia()
    return jsonify(resultado)

# =============================
# GET totales de una venta
# =============================
@ventas_bp.route('/totales/<int:id_venta>', methods=['GET'])
def calcular_totales(id_venta):
    # --------------------- CORREGIDO ---------------------
    # Antes usaba función MySQL 'calcular_totales_venta', ahora sumamos desde detalle_ventas
    query = """
        SELECT
            COALESCE(SUM(subtotal),0) AS total_subtotal,
            COALESCE(SUM(iva),0) AS total_iva,
            COALESCE(SUM(subtotal + iva),0) AS total_general
        FROM detalle_ventas
        WHERE id_venta = %s;
    """
    resultado = ventas._ejecutar_consulta(query, (id_venta,), fetchone=True)
    # ------------------------------------------------------
    return jsonify(resultado)

# =============================
# POST calcular cambio y desglose
# =============================
@ventas_bp.route('/calcular-cambio', methods=['POST'])
def calcular_cambio():
    data = request.json
    resultado = ventas.calcular_cambio(data['total'], data['pago'])
    return jsonify(resultado)

# =============================
# GET historial completo de cajas
# =============================
@ventas_bp.route('/historial-cajas-completo', methods=['GET'])
def historial_cajas_completo():
    resultado = ventas.obtener_historial_cajas_completo()
    return jsonify(resultado)

# =============================
# DELETE anular venta
# =============================
@ventas_bp.route('/anular-venta/<int:id_venta>', methods=['DELETE'])
def anular_venta(id_venta):
    resultado = ventas.anular_venta(id_venta)
    return jsonify(resultado)

# =============================
# POST cerrar caja
# =============================
@ventas_bp.route('/cerrar-caja', methods=['POST'])
def cerrar_caja():
    data = request.json
    resultado = ventas.cerrar_caja(data['id_caja'], data['saldo_final'])
    return jsonify(resultado)

# =============================
# GET detalle de venta
# =============================
@ventas_bp.route('/detalle-venta/<int:id_venta>', methods=['GET'])
def detalle_venta(id_venta):
    resultado = ventas.obtener_detalle_venta(id_venta)
    return jsonify(resultado)
