from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.user_service import UserService

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

@user_bp.route('/cadastro-user', methods=['POST'])
def cadastro_usuario():
    # 1. Corrigido: to_dict() sem argumentos
    dados = request.form.to_dict() 

    try:
        # 2. Certifique-se que o UserService retorna (bool, str)
        status, mensagem = UserService.cadastrar_user(dados)

        if status:
            # 3. Corrigido: url_for usa o nome da FUNÇÃO (ex: login_page)
            # Supondo que sua função de login se chama 'login' no blueprint 'auth'
            return f"Usuário {dados.get('nome')} cadastrado com sucesso! <a href='{url_for('user_bp.login')}'>Faça login aqui</a>"
        else:
            return f"Erro no cadastro: {mensagem} <a href='{url_for('user_bp.cadastro_usuario')}'>Tente novamente</a>"
            
    except Exception as e:
        return f"Erro inesperado no servidor: {str(e)}", 500
    

@user_bp.route('/login-usuer', methods=['POST'])
def login_usuario():
    email = request.form.get('email')
    senha = request.form.get('senha')

    user = UserService.autenticar_usuario(email, senha)

    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['nome']
        return f"Login bem-sucedido! <a href='{url_for('user.dashboard')}'>Ir para o dashboard</a>"
    return f"Falha no login. <a href='{url_for('user.login')}'>Tente novamente</a>"

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
    if "user_id" not in session:
        return redirect(url_for('user.login'))
    """ if session['user_id'] != 1:
        return "Acesso negado", 403 """
    usuarios = UserService.lista()
    return render_template('usuarios.html', usuarios=usuarios)

@user_bp.route('/users/<id>', methods=['DELETE'])
def delet_user(id):
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
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