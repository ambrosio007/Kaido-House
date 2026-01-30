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
    

@user_bp.route('/login-usuer', methods=['POST'])
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
    
@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

@user_bp.route('/user/json')
def busc_user_json():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    """ if session['user_id'] != 1:
        return jsonify({"error": "Acesso negado"}), 403 """
    return jsonify(UserService.lista())

@user_bp.route('/users')
def lista_users():

    current_user_id = get_jwt_identity()

    if current_user_id is None:
        return redirect(url_for('user.login'))
    """ if session['user_id'] != 1:
        return "Acesso negado", 403 """
    usuarios = UserService.lista()
    return render_template('usuarios.html', usuarios=usuarios)

@user_bp.route('/users/<id>', methods=['DELETE'])
@jwt_required()
def delet_user(id):

    current_user_id = get_jwt_identity()

    if current_user_id != id:
        return jsonify({"error": "Não permitido deletar"}), 401
    """ if session['user_id'] != 1:
        return jsonify({"error": "Acesso negado"}), 403 """
    if UserService.deletar_usuario(id):
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    return jsonify({"error": "Falha ao deletar usuário"}), 400

@user_bp.route('/users/', methods=['PUT'])
def atualiza_user():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    """ if session['user_id'] != 1:
        return jsonify({"error": "Acesso negado"}), 403 """
    user_edit = request.get_json()
    if UserService.atualizar_usuario(user_edit):
        return jsonify({"message": "Usuário atualizado com sucesso"}), 200
    return jsonify({"error": "Falha ao atualizar usuário"}), 400

''' @user_bp.route('/api/home/vitrine')
def vitrine_home():
    try:
        # Busca todos os itens
        todas_pecas = PecaService.listar_todas() # Certifique-se que retorna uma lista de dicts
        todos_veiculos = VeiculoService.listar_todos()

        # Filtros de Peças
        pecas_novas = [p for p in todas_pecas if p.get('estado', '').lower() == 'novo']
        pecas_usadas = [p for p in todas_pecas if p.get('estado', '').lower() == 'usado']

        # Filtros de Veículos
        # Consideramos 'novo' como KM < 100 e seminovo/usado o restante
        carros_novos = [v for v in todos_veiculos if int(v.get('km', 0)) <= 100]
        carros_usados = [v for v in todos_veiculos if int(v.get('km', 0)) > 100]

        return jsonify({
            "pecas_novas": pecas_novas,
            "pecas_usadas": pecas_usadas,
            "carros_novos": carros_novos,
            "carros_usados": carros_usados
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 '''
    
'''@user_bp.route('/api/vitrine-home')
def vitrine_home():
    # Peças: limit 5, ordenado por random no banco
    pecas_novas = PecaService.buscar_custom(estado='novo', limit=5)
    pecas_usadas = PecaService.buscar_custom(estado='usado', limit=5)
    
    # Veículos: limit 5
    carros_novos = VeiculoService.buscar_custom(novo=True, limit=5)
    carros_usados = VeiculoService.buscar_custom(novo=False, limit=5)

    return jsonify({
        "pecas_novas": pecas_novas,
        "pecas_usadas": pecas_usadas,
        "carros_novos": carros_novos,
        "carros_usados": carros_usados
    })'''

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

# Adicione esta rota ao seu user_controller.py

@user_bp.route('/diagnostico-cadastro', methods=['GET', 'POST'])
def diagnostico_cadastro():
    """Endpoint para diagnosticar problemas de cadastro"""
    
    if request.method == 'GET':
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Diagnóstico de Cadastro</title>
            <style>
                body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                .success { color: #4ec9b0; }
                .error { color: #f48771; }
                .warning { color: #dcdcaa; }
                pre { background: #252526; padding: 15px; border-radius: 5px; overflow-x: auto; }
                h2 { color: #569cd6; }
            </style>
        </head>
        <body>
            <h1>🔍 Diagnóstico de Cadastro</h1>
            <p>Este endpoint testa o processo de cadastro passo a passo.</p>
            
            <h2>Teste Automático:</h2>
            <form method="POST">
                <button type="submit" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                    Executar Diagnóstico
                </button>
            </form>
        </body>
        </html>
        """
    
    # POST - Executa o diagnóstico
    resultado = {
        "testes": [],
        "sucesso": True
    }
    
    # Dados de teste
    dados_teste = {
        'nome': 'Teste Usuario',
        'cpf': '999.999.999-99',
        'cep': '88888-888',
        'idade': '2000-01-01',
        'email': f'teste_{uuid.uuid4().hex[:8]}@teste.com',
        'senha': 'senha12345'
    }
    
    # TESTE 1: Importar UserModel
    try:
        from model.user_model import UserModel
        resultado["testes"].append({
            "nome": "Importar UserModel",
            "status": "✅ SUCESSO",
            "detalhes": "UserModel importado com sucesso"
        })
    except Exception as e:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Importar UserModel",
            "status": "❌ ERRO",
            "detalhes": str(e)
        })
        return jsonify(resultado), 500
    
    # TESTE 2: Criar instância do UserModel
    try:
        user = UserModel(**dados_teste)
        resultado["testes"].append({
            "nome": "Criar UserModel",
            "status": "✅ SUCESSO",
            "detalhes": f"ID gerado: {user.id}, Perfil: {user.perfil}"
        })
    except Exception as e:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Criar UserModel",
            "status": "❌ ERRO",
            "detalhes": str(e)
        })
        return jsonify(resultado), 500
    
    # TESTE 3: Converter para dict
    try:
        user_dict = user.__dict__
        campos = list(user_dict.keys())
        resultado["testes"].append({
            "nome": "Converter para dict",
            "status": "✅ SUCESSO",
            "detalhes": f"Campos: {campos}"
        })
    except Exception as e:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Converter para dict",
            "status": "❌ ERRO",
            "detalhes": str(e)
        })
        return jsonify(resultado), 500
    
    # TESTE 4: Verificar campos necessários
    campos_necessarios = ['id', 'nome', 'cpf', 'cep', 'email', 'idade', 'senha_hash', 'perfil']
    campos_faltando = [c for c in campos_necessarios if c not in user_dict]
    
    if campos_faltando:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Verificar campos",
            "status": "❌ ERRO",
            "detalhes": f"Campos faltando: {campos_faltando}"
        })
    else:
        resultado["testes"].append({
            "nome": "Verificar campos",
            "status": "✅ SUCESSO",
            "detalhes": "Todos os campos necessários estão presentes"
        })
    
    # TESTE 5: Testar conexão com banco
    try:
        from config.database import get_connection, release_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        release_connection(conn)
        
        resultado["testes"].append({
            "nome": "Conexão com banco",
            "status": "✅ SUCESSO",
            "detalhes": "Conexão estabelecida com sucesso"
        })
    except Exception as e:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Conexão com banco",
            "status": "❌ ERRO",
            "detalhes": str(e)
        })
        return jsonify(resultado), 500
    
    # TESTE 6: Verificar se tabela existe
    try:
        from config.database import get_connection, release_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios'
            ORDER BY ordinal_position
        """)
        colunas = cursor.fetchall()
        cursor.close()
        release_connection(conn)
        
        if colunas:
            colunas_info = [f"{col[0]} ({col[1]})" for col in colunas]
            resultado["testes"].append({
                "nome": "Verificar tabela usuarios",
                "status": "✅ SUCESSO",
                "detalhes": f"Colunas encontradas: {', '.join(colunas_info)}"
            })
        else:
            resultado["sucesso"] = False
            resultado["testes"].append({
                "nome": "Verificar tabela usuarios",
                "status": "❌ ERRO",
                "detalhes": "Tabela 'usuarios' não existe"
            })
    except Exception as e:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Verificar tabela usuarios",
            "status": "❌ ERRO",
            "detalhes": str(e)
        })
    
    # TESTE 7: Tentar inserir usuário de teste
    try:
        from repository.user_repository import UserRepository
        
        sucesso_insert = UserRepository.adicionar_user(user_dict)
        
        if sucesso_insert:
            resultado["testes"].append({
                "nome": "Inserir usuário de teste",
                "status": "✅ SUCESSO",
                "detalhes": f"Usuário inserido com ID: {user.id}"
            })
            
            # Limpar o usuário de teste
            try:
                UserRepository.delet(user.id)
                resultado["testes"].append({
                    "nome": "Limpar usuário de teste",
                    "status": "✅ SUCESSO",
                    "detalhes": "Usuário de teste removido"
                })
            except:
                pass
        else:
            resultado["sucesso"] = False
            resultado["testes"].append({
                "nome": "Inserir usuário de teste",
                "status": "❌ ERRO",
                "detalhes": "UserRepository.adicionar_user retornou False"
            })
    except Exception as e:
        resultado["sucesso"] = False
        resultado["testes"].append({
            "nome": "Inserir usuário de teste",
            "status": "❌ ERRO",
            "detalhes": str(e)
        })
    
    # Retorna resultado formatado em HTML
    html_resultado = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Resultado do Diagnóstico</title>
        <style>
            body {{ font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }}
            .success {{ color: #4ec9b0; }}
            .error {{ color: #f48771; }}
            .warning {{ color: #dcdcaa; }}
            pre {{ background: #252526; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            h2 {{ color: #569cd6; }}
            .teste {{ background: #252526; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>🔍 Resultado do Diagnóstico</h1>
        <h2 class="{'success' if resultado['sucesso'] else 'error'}">
            {'✅ TODOS OS TESTES PASSARAM!' if resultado['sucesso'] else '❌ ALGUNS TESTES FALHARAM'}
        </h2>
        
        <h2>Detalhes dos Testes:</h2>
    """
    
    for teste in resultado["testes"]:
        cor = 'success' if '✅' in teste['status'] else 'error'
        html_resultado += f"""
        <div class="teste">
            <strong class="{cor}">{teste['status']}</strong> {teste['nome']}<br>
            <span style="color: #858585;">{teste['detalhes']}</span>
        </div>
        """
    
    html_resultado += """
        <br>
        <a href="/diagnostico-cadastro" style="color: #569cd6;">← Voltar</a>
    </body>
    </html>
    """
    
    return html_resultado# Adicione no topo do arquivo se não existir