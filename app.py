from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from controller.user_controller import user_bp
from controller.pecas_controller import peca_bp      # 🔥 ADICIONAR
from controller.veiculo_controller import veiculo_bp  # 🔥 ADICIONAR
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
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Tamanho máximo de upload (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configurar JWT
jwt = JWTManager(app)

# Handler para token expirado
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    Chamado quando o token JWT expirou
    """
    print(f"⏰ Token expirado para usuário: {jwt_payload.get('sub')}")
    return jsonify({
        'error': 'Token expirado',
        'message': 'Sua sessão expirou. Faça login novamente',
        'code': 'EXPIRED_TOKEN'
    }), 401

# Handler para token inválido
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    """
    Chamado quando o token JWT é inválido
    """
    print(f"❌ Token inválido: {error_string}")
    return jsonify({
        'error': 'Token inválido',
        'message': 'Por favor, faça login novamente',
        'code': 'INVALID_TOKEN'
    }), 401

# Handler para token ausente
@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    """
    Chamado quando nenhum token foi enviado
    """
    print(f"🚫 Acesso não autorizado: {error_string}")
    return jsonify({
        'error': 'Autenticação necessária',
        'message': 'Você precisa estar logado para acessar este recurso',
        'code': 'NO_TOKEN'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """
    Chamado quando o token foi revogado
    """
    print(f"🔒 Token revogado para usuário: {jwt_payload.get('sub')}")
    return jsonify({
        'error': 'Token revogado',
        'message': 'Este token foi revogado. Faça login novamente',
        'code': 'REVOKED_TOKEN'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    """
    Chamado quando uma operação precisa de um token "fresco"
    """
    return jsonify({
        'error': 'Token não é fresco',
        'message': 'Esta operação requer um login recente',
        'code': 'FRESH_TOKEN_REQUIRED'
    }), 401

# ==================== REGISTRAR BLUEPRINTS ====================

# Registrar User Blueprint
app.register_blueprint(user_bp)

# 🔥 ADICIONAR - Registrar Peças Blueprint
app.register_blueprint(peca_bp)

# 🔥 ADICIONAR - Registrar Veículos Blueprint
app.register_blueprint(veiculo_bp)

print("\n" + "="*60)
print("✅ Blueprints registrados:")
print("   - user_bp")
print("   - peca_bp")
print("   - veiculo_bp")
print("="*60 + "\n")

# ==================== ROTAS DE SISTEMA ====================

# Rota de health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'}), 200

# Rota para listar todas as rotas (útil para debug)
@app.route('/routes', methods=['GET'])
def list_routes():
    """Lista todas as rotas disponíveis"""
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]),
                'path': str(rule)
            })
    routes.sort(key=lambda x: x['path'])
    return jsonify({'total': len(routes), 'routes': routes}), 200

# ==================== TRATAMENTO DE ERROS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Rota não encontrada',
        'message': f'A rota {request.path} não existe',
        'dica': 'Acesse /routes para ver todas as rotas'
    }), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'error': 'Arquivo muito grande',
        'message': 'O arquivo excede o tamanho máximo de 16MB'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# ==================== MIDDLEWARE DE LOG ====================

@app.before_request
def log_request():
    """Log de requisições (útil para debug)"""
    if not request.path.startswith('/static'):
        print(f"\n{'='*60}")
        print(f"📥 {request.method} {request.path}")
        if request.headers.get('Authorization'):
            print(f"   Auth: Bearer ***")
        if request.content_type:
            print(f"   Content-Type: {request.content_type}")
        print(f"{'='*60}")

@app.after_request
def after_request(response):
    """Log de respostas"""
    if not request.path.startswith('/static'):
        emoji = "✅" if response.status_code < 400 else "❌"
        print(f"{emoji} Response: {response.status}\n")
    return response

# ==================== EXECUTAR APLICAÇÃO ====================

if __name__ == '__main__':
    # Criar pastas necessárias
    folders = ['static/uploads', 'static/uploads/profile_photos', 
               'static/uploads/veiculos', 'static/uploads/pecas']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)