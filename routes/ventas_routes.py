from flask import Blueprint, request, jsonify
from dao.ventas import Ventas

ventas_bp = Blueprint('ventas_bp', __name__)
ventas = Ventas()

# ✅ Registrar una venta con validación de stock
@ventas_bp.route('/', methods=['POST'])
def registrar_venta():
    data = request.json
    try:
        resultado = ventas.registrar_venta(
            data['saldo_inicial'],
            data['total_venta'],
            data['id_medio_pago'],
            data['items']
        )
        return jsonify(resultado)
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400
    
# ✅ Obtener carrito actual
@ventas_bp.route('/carrito-actual', methods=['GET'])
def carrito_actual():
    resultado = ventas.obtener_carrito_actual()
    return jsonify(resultado)
    
# ✅ Obtener caja del dia
@ventas_bp.route('/caja-del-dia', methods=['GET'])
def caja_del_dia():
    resultado = ventas.obtener_caja_del_dia()
    return jsonify(resultado)

# ✅  Calcular totales de una venta
@ventas_bp.route('/totales/<int:id_venta>', methods=['GET'])
def calcular_totales(id_venta):
    resultado = ventas.calcular_totales_venta(id_venta)
    return jsonify(resultado)

# ✅ Calcular cambio y desglose
@ventas_bp.route('/calcular-cambio', methods=['POST'])
def calcular_cambio():
    data = request.json
    resultado = ventas.calcular_cambio(data['total'], data['pago'])
    return jsonify(resultado)

# ✅  Obtener historial completo de cajas
@ventas_bp.route('/historial-cajas-completo', methods=['GET'])
def historial_cajas_completo():
    resultado = ventas.obtener_historial_cajas_completo()
    return jsonify(resultado)

# ✅ Anular venta
@ventas_bp.route('/anular-venta/<int:id_venta>', methods=['DELETE'])
def anular_venta(id_venta):
    resultado = ventas.anular_venta(id_venta)
    return jsonify(resultado)

# ✅Cerrar caja
@ventas_bp.route('/cerrar-caja', methods=['POST'])
def cerrar_caja():
    data = request.json
    resultado = ventas.cerrar_caja(data['id_caja'], data['saldo_final'])
    return jsonify(resultado)

# ✅Detalle de venta
@ventas_bp.route('/detalle-venta/<int:id_venta>', methods=['GET'])
def detalle_venta(id_venta):
    resultado = ventas.obtener_detalle_venta(id_venta)
    return jsonify(resultado)
