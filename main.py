from flask import Flask
from flask_cors import CORS
from routes.productos_routes import productos_bp
from routes.ventas_routes import ventas_bp

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor Flask funcionando"

# Habilitar CORS para permitir peticiones desde el frontend en localhost:3000
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})


# Registrar los blueprints con prefijos
app.register_blueprint(productos_bp, url_prefix='/api/productos')
app.register_blueprint(ventas_bp, url_prefix='/api/ventas')

# Ejecutar la app en el puerto 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)