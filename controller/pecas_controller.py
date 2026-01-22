from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.peca_service import PecaService

peca_bp = Blueprint('peca', __name__)

@peca_bp.route('/cadastro-peca', methods=['POST'])
def cadastro_peca():
    """Cadastra uma nova peça"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    dados = {
        "user_id": session['user_id'],
        "nome": request.form.get('nome'),
        "categoria": request.form.get('categoria'),
        "marca": request.form.get('marca'),
        "modelo": request.form.get('modelo'),
        "estado": request.form.get('estado'),
        "preco": request.form.get('preco'),
        "descricao": request.form.get('descricao')
    }
    
    # Processar fotos se houver
    fotos = request.files.getlist('fotos')
    
    status, mensagem = PecaService.cadastrar_peca(dados, fotos)
    
    if status:
        return jsonify({"success": True, "message": "Peça cadastrada com sucesso!"}), 200
    else:
        return jsonify({"error": mensagem}), 400

@peca_bp.route('/minhas-pecas', methods=['GET'])
def minhas_pecas():
    """Lista todas as peças do usuário logado"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    pecas = PecaService.listar_por_usuario(session['user_id'])
    return jsonify(pecas), 200

@peca_bp.route('/pecas', methods=['GET'])
def listar_pecas():
    """Lista todas as peças ativas"""
    # Filtros opcionais
    categoria = request.args.get('categoria')
    estado = request.args.get('estado')
    
    pecas = PecaService.listar_todos(categoria=categoria, estado=estado)
    return jsonify(pecas), 200

@peca_bp.route('/peca/<peca_id>', methods=['GET'])
def detalhes_peca(peca_id):
    """Retorna detalhes de uma peça específica"""
    peca = PecaService.buscar_por_id(peca_id)
    if peca:
        return jsonify(peca), 200
    return jsonify({"error": "Peça não encontrada"}), 404

@peca_bp.route('/peca/<peca_id>', methods=['DELETE'])
def deletar_peca(peca_id):
    """Deleta (inativa) uma peça"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    # Verificar se a peça pertence ao usuário
    peca = PecaService.buscar_por_id(peca_id)
    if not peca or peca.get('user_id') != session['user_id']:
        return jsonify({"error": "Peça não encontrada ou não autorizada"}), 403
    
    if PecaService.deletar_peca(peca_id):
        return jsonify({"message": "Peça deletada com sucesso"}), 200
    return jsonify({"error": "Erro ao deletar peça"}), 400

@peca_bp.route('/peca/<peca_id>', methods=['PUT'])
def atualizar_peca(peca_id):
    """Atualiza informações de uma peça"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    # Verificar se a peça pertence ao usuário
    peca = PecaService.buscar_por_id(peca_id)
    if not peca or peca.get('user_id') != session['user_id']:
        return jsonify({"error": "Peça não encontrada ou não autorizada"}), 403
    
    dados = request.get_json()
    
    if PecaService.atualizar_peca(peca_id, dados):
        return jsonify({"message": "Peça atualizada com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar peça"}), 400

@peca_bp.route('/pecas/categorias', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias de peças disponíveis"""
    categorias = [
        {"value": "motor", "label": "Motor e Transmissão"},
        {"value": "suspensao", "label": "Suspensão e Freios"},
        {"value": "carroceria", "label": "Carroceria"},
        {"value": "eletrica", "label": "Parte Elétrica"},
        {"value": "interior", "label": "Interior"},
        {"value": "outros", "label": "Outros"}
    ]
    return jsonify(categorias), 200