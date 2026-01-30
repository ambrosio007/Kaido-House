from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from controller.user_controller import user_bp
import os

app = Flask(__name__)

# Habilitar CORS para todas as rotas
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurações de segurança
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ddfbbfb184d7143c012eee95a50b05b34aa722887368574a0db514622eb2c8cd')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', '09fbf119994172d829e9e927cb6e9f27dc9b7940df04b2c5f07660aee423b432')

# Configurar JWT
jwt = JWTManager(app)

# Registrar Blueprint
app.register_blueprint(user_bp)

# Rota de health check
@app.route('/health', methods=['GET'])
def health():
    return {'status': 'OK'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)