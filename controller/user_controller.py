from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.user_service import UserService
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from service.pecas_service import PecaService
from service.veiculos_service import VeiculoService


user_bp = Blueprint('user', __name__, template_folder='templates')

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

# --- ROTA DE PÁGINA (HTML) ---
@user_bp.route('/carrinho')
def ver_carrinho():
    return render_template('carrinho.html') 

@user_bp.route('/pecas')
def pag_pecas():
    return render_template('pecas_pg.html')

@user_bp.route('/veiculos')
def pag_veiculos():
    return render_template('carros_pg.html')

@user_bp.route('/receuperar-senha')
def recuperar_senha():
    return render_template('recupera_senha.html')



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
    data = request.get_json() or request.form
    email = data.get('email')
    senha = data.get('senha')

    user = UserService.autenticar_usuario(email, senha)

    if user:
        acces_token = create_access_token(identity={'id': user['id'], 'nome': user['nome'], 'email': user['email']})
        session['user_id'] = user['id']
        session['user_nome'] = user['nome']
        session['user_email'] = user['email']
        return jsonify({
            "message": "Login realizado com sucesso", 
            "access_token": acces_token
            }), 200
    else:
        return jsonify({
            "error": "Email ou senha incorretos"
        }), 401
    
@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

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


# ============= NOVAS ROTAS ADICIONADAS =============

@user_bp.route('/user-profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    Retorna os dados do perfil do usuário logado
    Requer token JWT válido
    """
    try:
        # Pega a identidade do usuário do token JWT
        current_user = get_jwt_identity()
        user_id = current_user.get('id')
        
        # Busca os dados completos do usuário
        user_data = UserService.buscar_por_id(user_id)
        
        if not user_data:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Retorna os dados do usuário
        return jsonify({
            'id': user_data.get('id'),
            'nome': user_data.get('nome'),
            'email': user_data.get('email'),
            'cpf': user_data.get('cpf'),
            'data_nascimento': user_data.get('data_nascimento'),
            'cep': user_data.get('cep'),
            'data_cadastro': user_data.get('data_cadastro') or user_data.get('created_at'),
            # Estatísticas (pode ajustar conforme seu banco)
            'total_pedidos': user_data.get('total_pedidos', 0),
            'avaliacao': user_data.get('avaliacao', 0.0),
            'total_favoritos': user_data.get('total_favoritos', 0)
        }), 200
        
    except Exception as e:
        print(f'Erro ao buscar perfil: {str(e)}')
        return jsonify({'error': 'Erro ao buscar dados do usuário'}), 500


@user_bp.route('/cadastrar-veiculo', methods=['POST'])
@jwt_required()
def cadastrar_veiculo():
    """
    Rota para cadastrar um veículo para venda
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('id')
        data = request.get_json()
        
        # Validação básica
        campos_obrigatorios = ['marca', 'modelo', 'ano', 'km', 'cor', 'preco', 'descricao']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
        
        # Adiciona o ID do usuário aos dados
        data['user_id'] = user_id
        
        # Cadastra o veículo usando o service
        sucesso = VeiculoService.cadastrar_veiculo(data)
        
        if sucesso:
            return jsonify({'message': 'Veículo cadastrado com sucesso'}), 201
        else:
            return jsonify({'error': 'Erro ao cadastrar veículo'}), 400
        
    except Exception as e:
        print(f'Erro ao cadastrar veículo: {str(e)}')
        return jsonify({'error': 'Erro ao cadastrar veículo'}), 500


@user_bp.route('/cadastrar-peca', methods=['POST'])
@jwt_required()
def cadastrar_peca():
    """
    Rota para cadastrar uma peça para venda
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('id')
        data = request.get_json()
        
        # Validação básica
        campos_obrigatorios = ['nome', 'categoria', 'marca', 'estado', 'preco', 'descricao']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
        
        # Adiciona o ID do usuário aos dados
        data['user_id'] = user_id
        
        # Cadastra a peça usando o service
        sucesso = PecaService.cadastrar_peca(data)
        
        if sucesso:
            return jsonify({'message': 'Peça cadastrada com sucesso'}), 201
        else:
            return jsonify({'error': 'Erro ao cadastrar peça'}), 400
        
    except Exception as e:
        print(f'Erro ao cadastrar peça: {str(e)}')
        return jsonify({'error': 'Erro ao cadastrar peça'}), 500


@user_bp.route('/api/vitrine-completa')
def vitrine_completa():
    # Peças
    p_novas = PecaService.buscar_vitrine(estado='novo', limit=5)
    p_usadas = PecaService.buscar_vitrine(estado='usado', limit=5)
    
    # Veículos
    v_novos = VeiculoService.buscar_vitrine(apenas_novos=True, limit=5)
    v_usados = VeiculoService.buscar_vitrine(apenas_novos=False, limit=5)
    
    return jsonify({
        "pecas_novas": p_novas,
        "pecas_usadas": p_usadas,
        "carros_novos": v_novos,
        "carros_usados": v_usados
    })