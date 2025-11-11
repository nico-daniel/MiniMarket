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