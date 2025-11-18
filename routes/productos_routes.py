from flask import Blueprint, request, jsonify
from dao.productos import Productos

productos_bp = Blueprint('productos_bp', __name__)
productos = Productos()

# ✅ Obtener todos los productos con detalle
@productos_bp.route('/', methods=['GET'])
def obtener_todos():
    return jsonify(productos.obtener_todos_con_detalle())

# ✅ Buscar producto por código de barra
@productos_bp.route('/buscar', methods=['GET'])
def buscar_por_codigo():
    codigo = request.args.get('codigo_barra')
    if not codigo:
        return jsonify({"error": "Falta el parámetro 'codigo_barra'"}), 400
    return jsonify(productos.busqueda_por_lector(codigo))

# ✅ Agregar nuevo producto
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

# ✅ Actualizar producto existente
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

# ✅ Registrar entrada de stock
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

# ✅ Obtener historial de movimientos de un producto
@productos_bp.route('/movimientos/<int:id_producto>', methods=['GET'])
def historial_movimientos(id_producto):
    resultado = productos.obtener_historial_movimientos(id_producto)
    return jsonify(resultado)

# ✅ Obtener resumen diario de ventas y stock bajo
@productos_bp.route('/resumen-diario', methods=['GET'])
def resumen_diario():
    resultado = productos.obtener_resumen_diario()
    return jsonify(resultado)

# ✅ Obtener Historial de caja
@productos_bp.route('/historial-cajas', methods=['GET'])
def historial_cajas():
    resultado = productos.obtener_historial_cajas()
    return jsonify(resultado)

# ✅ Obtener productos mas vendidos hoy
@productos_bp.route('/mas-vendidos-hoy', methods=['GET'])
def mas_vendidos_hoy():
    resultado = productos.obtener_mas_vendidos_hoy()
    return jsonify(resultado)

# ✅ Elimnar producto
@productos_bp.route('/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    resultado = productos.eliminar_producto(id_producto)
    return jsonify(resultado)

# ✅ Obtener productos ordenados con filtros
@productos_bp.route('/ordenados', methods=['GET'])
def productos_ordenados():
    orden = request.args.get('orden', 'stock_asc')
    tipo = request.args.get('tipo')
    busqueda = request.args.get('busqueda')
    resultado = productos.obtener_productos_ordenados(orden, tipo, busqueda)
    return jsonify(resultado)