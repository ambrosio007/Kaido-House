from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.user_service import UserService
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from service.pecas_service import PecaService
from service.veiculos_service import VeiculoService
from werkzeug.utils import secure_filename
import os
import uuid
import traceback


user_bp = Blueprint('user', __name__, template_folder='templates')

# Configurações de upload
UPLOAD_FOLDER = 'static/uploads/profile_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/') 
def home():
    return render_template('home.html')

@user_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@user_bp.route('/login')
def login():
    return render_template('login.html')

@user_bp.route('/perfil')
def perfil():
    return render_template('perfil.html')

@user_bp.route('/carrinho')
def ver_carrinho():
    return render_template('carrinho.html') 

@user_bp.route('/pecas')
def pag_pecas():
    return render_template('pecas_pg.html')

@user_bp.route('/veiculos')
def pag_veiculos():
    return render_template('carros_pg.html')

@user_bp.route('/recuperar_senha')
def recuperar_senha():
    """Renderiza a página de solicitação de recuperação de senha"""
    return render_template('recupera_senha.html')

@user_bp.route('/redefinir_senha')
def redefinir_senha_page():
    """Renderiza a página de redefinição de senha com o token"""
    token = request.args.get('token')
    if not token:
        return redirect(url_for('user.recuperar_senha'))
    return render_template('redefinir_senha.html', token=token)


# ============= ROTAS DE AUTENTICAÇÃO =============

@user_bp.route('/cadastro-user', methods=['POST'])
def cadastro_usuario():
    dados = request.form.to_dict() 

    try:
        status, mensagem = UserService.cadastrar_user(dados)

        if status:
            return jsonify({
                "success": True,
                "message": f"Usuário {dados.get('nome')} cadastrado com sucesso!"
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": mensagem
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro inesperado no servidor: {str(e)}"
        }), 500
    

@user_bp.route('/login-user', methods=['POST'])
def login_usuario():
    """
    Rota de login com logs detalhados e validação do token
    ✅ VERSÃO CORRIGIDA
    """
    try:
        data = request.get_json() or request.form
        email = data.get('email')
        senha = data.get('senha')

        print(f"\n{'='*60}")
        print(f"🔐 LOGIN REQUEST")
        print(f"{'='*60}")
        print(f"Email: {email}")
        
        # Autenticar usuário
        user = UserService.autenticar_usuario(email, senha)

        if not user:
            print(f"❌ Autenticação falhou para: {email}")
            print(f"{'='*60}\n")
            return jsonify({"error": "Email ou senha incorretos"}), 401
        
        # Usuário autenticado com sucesso
        print(f"✅ Usuário autenticado: {user.get('nome')}")
        print(f"\n📋 Dados do usuário para o token:")
        print(f"   ID: {user.get('id')}")
        print(f"   Tipo ID: {type(user.get('id'))}")
        print(f"   Nome: {user.get('nome')}")
        print(f"   Email: {user.get('email')}")
        
        # Garantir que o ID é string
        user_id = str(user['id']) if user.get('id') else None
        
        if not user_id:
            print(f"❌ ERRO: ID do usuário está vazio!")
            print(f"{'='*60}\n")
            return jsonify({"error": "Erro ao processar dados do usuário"}), 500
        
        # Criar identity para o token (APENAS O ID COMO STRING)
        print(f"\n🔑 Identity que será usado no token: {user_id}")
        
        # Gerar token JWT
        try:
            access_token = create_access_token(identity=user_id)
            
            print(f"\n✅ Token JWT gerado com sucesso!")
            print(f"   Comprimento: {len(access_token)} caracteres")
            print(f"   Partes (deve ser 3): {len(access_token.split('.'))}")
            print(f"   Preview: {access_token[:50]}...")
            
            # Validar que o token tem 3 partes
            if len(access_token.split('.')) != 3:
                print(f"❌ ERRO: Token malformado! Não tem 3 partes!")
                print(f"{'='*60}\n")
                return jsonify({"error": "Erro ao gerar token de autenticação"}), 500
                
        except Exception as e:
            print(f"❌ ERRO ao gerar token JWT: {str(e)}")
            traceback.print_exc()
            print(f"{'='*60}\n")
            return jsonify({"error": "Erro ao gerar token de autenticação"}), 500
        
        # Salvar na sessão
        session['user_id'] = user_id
        session['user_nome'] = user.get('nome', '')
        session['user_email'] = user.get('email', '')
        
        print(f"\n✅ Login concluído com sucesso!")
        print(f"{'='*60}\n")
        
        return jsonify({
            "message": "Login realizado com sucesso", 
            "access_token": access_token,
            "user": {
                "id": user_id,
                "nome": user.get('nome'),
                "email": user.get('email')
            }
        }), 200
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO no login:")
        print(f"   {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({"error": "Erro interno do servidor"}), 500

    
@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


# ============= ROTAS DE RECUPERAÇÃO DE SENHA =============

@user_bp.route('/solicitar-recuperacao-senha', methods=['POST'])
def solicitar_recuperacao():
    """
    Endpoint para solicitar recuperação de senha
    Recebe o e-mail e envia link de recuperação
    """
    try:
        data = request.get_json() or request.form
        email = data.get('email')
        
        if not email:
            return jsonify({
                "success": False,
                "error": "E-mail é obrigatório"
            }), 400
        
        # Processar recuperação
        sucesso, mensagem = UserService.solicitar_recuperacao_senha(email)
        
        if sucesso:
            return jsonify({
                "success": True,
                "message": mensagem
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": mensagem
            }), 400
            
    except Exception as e:
        print(f"Erro ao solicitar recuperação: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Erro ao processar solicitação"
        }), 500


@user_bp.route('/validar-token-recuperacao', methods=['GET'])
def validar_token():
    """
    Valida se o token de recuperação é válido
    """
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({
                "valid": False,
                "error": "Token não fornecido"
            }), 400
        
        token_data = UserService.validar_token_recuperacao(token)
        
        if token_data:
            return jsonify({
                "valid": True,
                "email": token_data.get('email')
            }), 200
        else:
            return jsonify({
                "valid": False,
                "error": "Token inválido ou expirado"
            }), 400
            
    except Exception as e:
        print(f"Erro ao validar token: {str(e)}")
        return jsonify({
            "valid": False,
            "error": "Erro ao validar token"
        }), 500


@user_bp.route('/redefinir-senha', methods=['POST'])
def redefinir_senha():
    """
    Redefine a senha do usuário usando o token
    """
    try:
        data = request.get_json() or request.form
        token = data.get('token')
        nova_senha = data.get('nova_senha')
        confirmar_senha = data.get('confirmar_senha')
        
        # Validações
        if not token or not nova_senha or not confirmar_senha:
            return jsonify({
                "success": False,
                "error": "Todos os campos são obrigatórios"
            }), 400
        
        if nova_senha != confirmar_senha:
            return jsonify({
                "success": False,
                "error": "As senhas não coincidem"
            }), 400
        
        if len(nova_senha) < 6:
            return jsonify({
                "success": False,
                "error": "A senha deve ter no mínimo 6 caracteres"
            }), 400
        
        # Redefinir senha
        sucesso, mensagem = UserService.redefinir_senha(token, nova_senha)
        
        if sucesso:
            return jsonify({
                "success": True,
                "message": mensagem
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": mensagem
            }), 400
            
    except Exception as e:
        print(f"Erro ao redefinir senha: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Erro ao redefinir senha"
        }), 500


# ============= ROTAS DE USUÁRIO =============

@user_bp.route('/user/json')
def busc_user_json():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    return jsonify(UserService.lista())

@user_bp.route('/users')
def lista_users():
    current_user_id = get_jwt_identity()

    if current_user_id is None:
        return redirect(url_for('user.login'))
    
    usuarios = UserService.lista()
    return render_template('usuarios.html', usuarios=usuarios)

@user_bp.route('/users/<id>', methods=['DELETE'])
@jwt_required()
def delet_user(id):
    current_user_id = get_jwt_identity()

    if current_user_id != id:
        return jsonify({"error": "Não permitido deletar"}), 401
    
    if UserService.deletar_usuario(id):
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    return jsonify({"error": "Falha ao deletar usuário"}), 400

@user_bp.route('/users/', methods=['PUT'])
def atualiza_user():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_edit = request.get_json()
    user_id = user_edit.get('id') or session.get('user_id')
    
    if UserService.atualizar_usuario(user_id, user_edit):
        return jsonify({"message": "Usuário atualizado com sucesso"}), 200
    return jsonify({"error": "Falha ao atualizar usuário"}), 400


# ============= ROTAS DE PERFIL =============

@user_bp.route('/user-profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    Retorna os dados do perfil do usuário logado
    ✅ VERSÃO FINAL COM LOGS DETALHADOS
    """
    try:
        print("\n" + "="*60)
        print("🔐 REQUISIÇÃO: /user-profile")
        print("="*60)
        
        # Obter identidade do JWT
        current_user = get_jwt_identity()
        print(f"✅ Token JWT processado")
        print(f"📋 Identity extraída do token:")
        print(f"   Tipo: {type(current_user)}")
        print(f"   Conteúdo: {current_user}")
        
        if not current_user:
            print("❌ Identity do token está vazia!")
            return jsonify({'error': 'Token inválido'}), 401
        
        # Extrair user_id (pode ser string ou dict)
        if isinstance(current_user, dict):
            user_id = current_user.get('id')
        else:
            user_id = current_user
            
        print(f"🆔 User ID extraído: {user_id} (tipo: {type(user_id)})")
        
        if not user_id:
            print("❌ ID de usuário não encontrado no token")
            return jsonify({'error': 'ID de usuário não encontrado no token'}), 401
        
        # Buscar dados do usuário
        print(f"\n🔍 Buscando usuário no banco...")
        user_data = UserService.buscar_por_id(user_id)
        
        if not user_data:
            print(f"❌ Usuário não encontrado no banco: {user_id}")
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        print(f"✅ Usuário encontrado!")
        
        # Construir resposta
        print(f"\n📦 Montando resposta...")
        response = {
            'id': user_data.get('id'),
            'nome': user_data.get('nome'),
            'email': user_data.get('email'),
            'cpf': user_data.get('cpf', ''),
            'idade': user_data.get('idade', 0),
            'cep': user_data.get('cep', ''),
            'foto_perfil': user_data.get('foto_perfil'),
            'data_cadastro': user_data.get('created_at'),
            'total_pedidos': user_data.get('total_pedidos', 0),
            'avaliacao': user_data.get('avaliacao', 0.0),
            'total_favoritos': user_data.get('total_favoritos', 0)
        }
        
        print(f"✅ Resposta montada!")
        print(f"📤 Retornando 200 OK")
        print("="*60 + "\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({'error': 'Erro interno do servidor'}), 500


@user_bp.route('/upload-foto-perfil', methods=['POST'])
@jwt_required()
def upload_foto_perfil():
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        
        if 'foto' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['foto']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
            
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            foto_url = f"/static/uploads/profile_photos/{unique_filename}"
            
            if UserService.atualizar_foto_perfil(user_id, foto_url):
                return jsonify({
                    'message': 'Foto de perfil atualizada com sucesso',
                    'foto_url': foto_url
                }), 200
            else:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({'error': 'Erro ao atualizar foto no banco de dados'}), 500
        else:
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
            
    except Exception as e:
        print(f'Erro ao fazer upload: {str(e)}')
        traceback.print_exc()
        return jsonify({'error': 'Erro ao fazer upload da foto'}), 500


@user_bp.route('/remover-foto-perfil', methods=['DELETE'])
@jwt_required()
def remover_foto_perfil():
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        
        user_data = UserService.buscar_por_id(user_id)
        
        if user_data and user_data.get('foto_perfil'):
            foto_path = user_data['foto_perfil'].replace('/static/', 'static/')
            if os.path.exists(foto_path):
                os.remove(foto_path)
        
        if UserService.atualizar_foto_perfil(user_id, None):
            return jsonify({'message': 'Foto de perfil removida com sucesso'}), 200
        else:
            return jsonify({'error': 'Erro ao remover foto'}), 500
            
    except Exception as e:
        print(f'Erro ao remover foto: {str(e)}')
        traceback.print_exc()
        return jsonify({'error': 'Erro ao remover foto'}), 500


@user_bp.route('/cadastrar-veiculo', methods=['POST'])
@jwt_required()
def cadastrar_veiculo():
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        data = request.get_json()
        
        campos_obrigatorios = ['marca', 'modelo', 'ano', 'km', 'cor', 'preco', 'descricao']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
        
        data['user_id'] = user_id
        sucesso = VeiculoService.cadastrar_veiculo(data)
        
        if sucesso:
            return jsonify({'message': 'Veículo cadastrado com sucesso'}), 201
        else:
            return jsonify({'error': 'Erro ao cadastrar veículo'}), 400
        
    except Exception as e:
        print(f'Erro ao cadastrar veículo: {str(e)}')
        traceback.print_exc()
        return jsonify({'error': 'Erro ao cadastrar veículo'}), 500


@user_bp.route('/cadastrar-peca', methods=['POST'])
@jwt_required()
def cadastrar_peca():
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        data = request.get_json()
        
        campos_obrigatorios = ['nome', 'categoria', 'marca', 'estado', 'preco', 'descricao']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
        
        data['user_id'] = user_id
        sucesso = PecaService.cadastrar_peca(data)
        
        if sucesso:
            return jsonify({'message': 'Peça cadastrada com sucesso'}), 201
        else:
            return jsonify({'error': 'Erro ao cadastrar peça'}), 400
        
    except Exception as e:
        print(f'Erro ao cadastrar peça: {str(e)}')
        traceback.print_exc()
        return jsonify({'error': 'Erro ao cadastrar peça'}), 500


@user_bp.route('/api/vitrine-completa')
def vitrine_completa():
    p_novas = PecaService.buscar_vitrine(estado='novo', limit=5)
    p_usadas = PecaService.buscar_vitrine(estado='usado', limit=5)
    v_novos = VeiculoService.buscar_vitrine(apenas_novos=True, limit=5)
    v_usados = VeiculoService.buscar_vitrine(apenas_novos=False, limit=5)
    
    return jsonify({
        "pecas_novas": p_novas,
        "pecas_usadas": p_usadas,
        "carros_novos": v_novos,
        "carros_usados": v_usados
    })