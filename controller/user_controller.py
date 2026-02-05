from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.user_service import UserService
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from service.pecas_service import PecaService
from service.veiculos_service import VeiculoService
from repository.pecas_repository import PecaRepository
from repository.veiculo_repository import VeiculoRepository
from werkzeug.utils import secure_filename
import os
import uuid
import traceback
from datetime import datetime


user_bp = Blueprint('user', __name__, template_folder='templates')

# Configurações de upload
UPLOAD_FOLDER = 'static/uploads/profile_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============= ROTAS DE PÁGINAS =============

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

@user_bp.route('/pecas_pag')
def pag_pecas():
    return render_template('pecas_pg.html')

@user_bp.route('/veiculos_pag')
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
    """
    Cadastra um novo usuário
    ✅ VERSÃO CORRIGIDA - Converte data de nascimento em idade
    """
    try:
        # Captura os dados do formulário
        dados = {
            'nome': request.form.get('nome'),
            'cpf': request.form.get('cpf'),
            'cep': request.form.get('cep'),
            'email': request.form.get('email'),
            'senha': request.form.get('senha')
        }
        
        # ✅ CORREÇÃO: Converte data de nascimento em idade
        data_nascimento_str = request.form.get('idade')  # Vem como "2004-01-17"
        
        if data_nascimento_str:
            try:
                # Converte string para objeto date
                data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                
                # Calcula a idade
                hoje = datetime.now().date()
                idade = hoje.year - data_nascimento.year
                
                # Ajusta se ainda não fez aniversário este ano
                if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
                    idade -= 1
                
                # Adiciona a idade calculada aos dados
                dados['idade'] = idade
                
                print(f"📅 Data de nascimento: {data_nascimento_str}")
                print(f"🎂 Idade calculada: {idade} anos")
                
            except ValueError as e:
                print(f"❌ Erro ao converter data: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Data de nascimento inválida'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'Data de nascimento é obrigatória'
            }), 400
        
        # Validação básica
        if not all([dados['nome'], dados['cpf'], dados['email'], dados['senha']]):
            return jsonify({
                'success': False,
                'error': 'Todos os campos são obrigatórios'
            }), 400
        
        # Chama o serviço para cadastrar
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
        print(f"❌ Erro no controller: {str(e)}")
        traceback.print_exc()
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
    Valida se um token de recuperação é válido
    """
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({
                "success": False,
                "error": "Token não fornecido"
            }), 400
        
        token_data = UserService.validar_token_recuperacao(token)
        
        if token_data:
            return jsonify({
                "success": True,
                "message": "Token válido"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Token inválido ou expirado"
            }), 400
            
    except Exception as e:
        print(f"Erro ao validar token: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Erro ao validar token"
        }), 500


@user_bp.route('/redefinir-senha', methods=['POST'])
def redefinir_senha():
    """
    Redefine a senha do usuário
    """
    try:
        data = request.get_json() or request.form
        token = data.get('token')
        nova_senha = data.get('nova_senha')
        
        if not token or not nova_senha:
            return jsonify({
                "success": False,
                "error": "Token e nova senha são obrigatórios"
            }), 400
        
        if len(nova_senha) < 8:
            return jsonify({
                "success": False,
                "error": "A senha deve ter no mínimo 8 caracteres"
            }), 400
        
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


# ============= ROTAS DE USUÁRIOS (CRUD) =============

@user_bp.route('/lista-users')
def lista_users():
    users = UserService.lista()
    return jsonify(users), 200


@user_bp.route('/buscar-user/<string:user_id>')
def buscar_user(user_id):
    user = UserService.buscar_por_id(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Usuário não encontrado"}), 404


@user_bp.route('/deletar-user', methods=['DELETE'])
def deletar_user():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    user_id = request.args.get('id') or session.get('user_id')
    
    if UserService.deletar_usuario(user_id):
        session.clear()
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    return jsonify({"error": "Falha ao deletar usuário"}), 400


@user_bp.route('/atualizar-user', methods=['PUT'])
def atualizar_user():
    """
    Atualiza dados do usuário
    ✅ COM SUPORTE PARA CONVERSÃO DE DATA DE NASCIMENTO
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        user_edit = request.get_json()
        user_id = user_edit.get('id') or session.get('user_id')
        
        # ✅ Se vier data de nascimento, converte para idade
        if 'idade' in user_edit and isinstance(user_edit['idade'], str) and '-' in user_edit['idade']:
            data_nascimento_str = user_edit['idade']
            data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            idade = hoje.year - data_nascimento.year
            if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
                idade -= 1
            user_edit['idade'] = idade
        
        if UserService.atualizar_usuario(user_id, user_edit):
            return jsonify({"message": "Usuário atualizado com sucesso"}), 200
        return jsonify({"error": "Falha ao atualizar usuário"}), 400
        
    except Exception as e:
        print(f"Erro ao atualizar usuário: {str(e)}")
        return jsonify({"error": "Erro ao atualizar usuário"}), 500


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


# ============= ROTAS DE VEÍCULOS E PEÇAS =============

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

# ====================================================================
# ROTAS PARA DETALHES DE PRODUTOS (TEMPLATE ÚNICO)
# ====================================================================

@user_bp.route('/veiculo/<veiculo_id>')
def detalhes_veiculo(veiculo_id):
    """
    Exibe os detalhes de um veículo específico
    Usa o template unificado detalhes_produto.html
    """
    try:
        # Buscar veículo no banco
        veiculo = VeiculoRepository.buscar_por_id(veiculo_id)
        
        if not veiculo:
            # Você pode criar um template 404.html customizado
            return render_template('404.html', mensagem="Veículo não encontrado"), 404
        
        # Renderizar template unificado passando tipo='veiculo'
        return render_template('detalhes_produto.html', 
                             produto=veiculo, 
                             tipo='veiculo')
        
    except Exception as e:
        print(f"❌ Erro ao buscar veículo: {e}")
        traceback.print_exc()
        # Você pode criar um template 500.html customizado
        return render_template('500.html', erro=str(e)), 500


@user_bp.route('/peca/<peca_id>')
def detalhes_peca(peca_id):
    """
    Exibe os detalhes de uma peça específica
    Usa o template unificado detalhes_produto.html
    """
    try:
        # Buscar peça no banco
        peca = PecaRepository.buscar_por_id(peca_id)
        
        if not peca:
            return render_template('404.html', mensagem="Peça não encontrada"), 404
        
        # Renderizar template unificado passando tipo='peca'
        return render_template('detalhes_produto.html', 
                            produto=peca, 
                            tipo='peca')
        
    except Exception as e:
        print(f"❌ Erro ao buscar peça: {e}")
        traceback.print_exc()
        return render_template('500.html', erro=str(e)), 500
    
# ============= ROTAS DE RECUPERAÇÃO DE SENHA =============

@user_bp.route('/solicitar-recuperacao-senha', methods=['POST'])
def solicitar_recuperacao_senha_api():  # ✅ Nome único
    """
    Endpoint API para solicitar recuperação de senha
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        print(f"\n{'='*60}")
        print(f"📧 SOLICITAÇÃO DE RECUPERAÇÃO DE SENHA")
        print(f"{'='*60}")
        print(f"Email: {email}")
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'E-mail é obrigatório'
            }), 400
        
        # Chamar o serviço
        sucesso, mensagem = UserService.solicitar_recuperacao_senha(email)
        
        if sucesso:
            print(f"✅ Recuperação iniciada com sucesso")
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'message': mensagem
            }), 200
        else:
            print(f"❌ Erro ao solicitar recuperação")
            print(f"{'='*60}\n")
            return jsonify({
                'success': False,
                'error': mensagem
            }), 400
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500


@user_bp.route('/redefinir-senha', methods=['POST'])
def redefinir_senha_api():  # ✅ Nome diferente de redefinir_senha_page
    """
    Endpoint API para redefinir a senha usando o token
    """
    try:
        data = request.get_json()
        token = data.get('token')
        nova_senha = data.get('nova_senha')
        
        print(f"\n{'='*60}")
        print(f"🔑 REDEFINIÇÃO DE SENHA")
        print(f"{'='*60}")
        print(f"Token: {token[:20]}..." if token else "Token: None")
        
        if not token or not nova_senha:
            return jsonify({
                'success': False,
                'error': 'Token e nova senha são obrigatórios'
            }), 400
        
        # Validar tamanho mínimo da senha
        if len(nova_senha) < 6:
            return jsonify({
                'success': False,
                'error': 'A senha deve ter no mínimo 6 caracteres'
            }), 400
        
        # Chamar o serviço
        sucesso, mensagem = UserService.redefinir_senha(token, nova_senha)
        
        if sucesso:
            print(f"✅ Senha redefinida com sucesso")
            print(f"{'='*60}\n")
            return jsonify({
                'success': True,
                'message': mensagem
            }), 200
        else:
            print(f"❌ Erro ao redefinir senha")
            print(f"{'='*60}\n")
            return jsonify({
                'success': False,
                'error': mensagem
            }), 400
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500


@user_bp.route('/validar-token-recuperacao', methods=['POST'])
def validar_token_recuperacao_api():  # ✅ Nome único
    """
    Valida se um token de recuperação é válido
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'valido': False,
                'mensagem': 'Token não fornecido'
            }), 400
        
        token_data = UserService.validar_token_recuperacao(token)
        
        if token_data:
            return jsonify({
                'valido': True,
                'mensagem': 'Token válido'
            }), 200
        else:
            return jsonify({
                'valido': False,
                'mensagem': 'Token inválido ou expirado'
            }), 400
            
    except Exception as e:
        print(f"Erro ao validar token: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'valido': False,
            'mensagem': 'Erro ao validar token'
        }), 500

# ============= ROTAS DE GERENCIAMENTO DE USUÁRIO =============

@user_bp.route('/atualizar-user', methods=['PUT'])
@jwt_required()
def atualizar_usuario():
    """
    Atualiza dados do usuário autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        
        print(f"\n{'='*60}")
        print(f"📝 ATUALIZAÇÃO DE USUÁRIO")
        print(f"{'='*60}")
        print(f"User ID: {user_id}")
        print(f"Dados recebidos: {data}")
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['nome', 'email', 'cpf', 'idade', 'cep']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
        
        # Atualizar usuário
        sucesso = UserService.atualizar_usuario(user_id, data)
        
        if sucesso:
            print(f"✅ Usuário atualizado com sucesso!")
            print(f"{'='*60}\n")
            return jsonify({'message': 'Usuário atualizado com sucesso'}), 200
        else:
            print(f"❌ Erro ao atualizar usuário")
            print(f"{'='*60}\n")
            return jsonify({'error': 'Erro ao atualizar usuário'}), 400
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@user_bp.route('/alterar-senha', methods=['POST'])
@jwt_required()
def alterar_senha_usuario():
    """
    Altera a senha do usuário autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        senha_atual = data.get('senha_atual')
        nova_senha = data.get('nova_senha')
        
        print(f"\n{'='*60}")
        print(f"🔑 ALTERAÇÃO DE SENHA")
        print(f"{'='*60}")
        print(f"User ID: {user_id}")
        
        if not senha_atual or not nova_senha:
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        
        if len(nova_senha) < 6:
            return jsonify({'error': 'A nova senha deve ter no mínimo 6 caracteres'}), 400
        
        # Buscar usuário
        user = UserService.buscar_por_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar senha atual
        import bcrypt
        senha_hash_banco = user.get('senha')
        
        if not senha_hash_banco:
            return jsonify({'error': 'Erro ao verificar senha'}), 500
        
        if not bcrypt.checkpw(senha_atual.encode('utf-8'), senha_hash_banco.encode('utf-8')):
            print(f"❌ Senha atual incorreta")
            print(f"{'='*60}\n")
            return jsonify({'error': 'Senha atual incorreta'}), 401
        
        # Gerar hash da nova senha
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Atualizar senha
        from repository.user_repository import UserRepository
        sucesso = UserRepository.atualizar_senha(user_id, nova_senha_hash)
        
        if sucesso:
            print(f"✅ Senha alterada com sucesso!")
            print(f"{'='*60}\n")
            return jsonify({'message': 'Senha alterada com sucesso'}), 200
        else:
            print(f"❌ Erro ao atualizar senha")
            print(f"{'='*60}\n")
            return jsonify({'error': 'Erro ao atualizar senha'}), 400
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@user_bp.route('/deletar-user', methods=['DELETE'])
@jwt_required()
def deletar_usuario():
    """
    Deleta a conta do usuário autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        print(f"\n{'='*60}")
        print(f"🗑️ DELEÇÃO DE CONTA")
        print(f"{'='*60}")
        print(f"User ID: {user_id}")
        
        # Deletar usuário
        sucesso = UserService.deletar_usuario(user_id)
        
        if sucesso:
            print(f"✅ Conta deletada com sucesso!")
            print(f"{'='*60}\n")
            return jsonify({'message': 'Conta deletada com sucesso'}), 200
        else:
            print(f"❌ Erro ao deletar conta")
            print(f"{'='*60}\n")
            return jsonify({'error': 'Erro ao deletar conta'}), 400
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@user_bp.route('/meus-veiculos')
@jwt_required()
def meus_veiculos():
    """
    Renderiza página com os veículos do usuário
    """
    return render_template('meus_veiculos.html')


@user_bp.route('/meus-veiculos', methods=['GET'])
@jwt_required()
def listar_meus_veiculos():
    """
    Retorna lista de veículos do usuário autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        veiculos = VeiculoService.buscar_por_usuario(user_id)
        
        return jsonify({
            'veiculos': veiculos
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar veículos: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Erro ao listar veículos'}), 500


@user_bp.route('/api/deletar-veiculo/<veiculo_id>', methods=['DELETE'])
@jwt_required()
def deletar_veiculo(veiculo_id):
    """
    Deleta um veículo do usuário autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Verificar se o veículo pertence ao usuário
        veiculo = VeiculoRepository.buscar_por_id(veiculo_id)
        
        if not veiculo:
            return jsonify({'error': 'Veículo não encontrado'}), 404
        
        if veiculo.get('user_id') != user_id:
            return jsonify({'error': 'Você não tem permissão para deletar este veículo'}), 403
        
        # Deletar veículo
        sucesso = VeiculoRepository.deletar(veiculo_id)
        
        if sucesso:
            return jsonify({'message': 'Veículo deletado com sucesso'}), 200
        else:
            return jsonify({'error': 'Erro ao deletar veículo'}), 400
            
    except Exception as e:
        print(f"Erro ao deletar veículo: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Erro ao deletar veículo'}), 500