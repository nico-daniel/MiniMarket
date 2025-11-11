from flask import Flask
from flask_cors import CORS
from routes.productos_routes import productos_bp
from routes.ventas_routes import ventas_bp

app = Flask(__name__)
CORS(app)

# Registrar los blueprints
app.register_blueprint(productos_bp, url_prefix='/api/productos')
app.register_blueprint(ventas_bp, url_prefix='/api/ventas')

if __name__ == '__main__':
    app.run(debug=True)
