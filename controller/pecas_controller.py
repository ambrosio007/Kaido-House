from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.pecas_service import PecaService

peca_bp = Blueprint('peca', __name__)

# --- ROTA PROTEGIDA: Cadastro ---
@peca_bp.route('/cadastro-peca', methods=['POST'])
@jwt_required()
def cadastro_peca():
    """Cadastra uma nova peça COM SUPORTE A UPLOAD DE IMAGENS"""
    
    # Obtém o ID do usuário através do Token
    current_user_id = get_jwt_identity()
    
    # ✅ CORREÇÃO: Aceitar tanto FormData (com fotos) quanto JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Requisição com arquivos (FormData)
        dados = {
            "user_id": current_user_id,
            "nome": request.form.get('nome'),
            "categoria": request.form.get('categoria'),
            "marca": request.form.get('marca'),
            "modelo": request.form.get('modelo', ''),
            "estado": request.form.get('estado'),
            "preco": request.form.get('preco'),
            "descricao": request.form.get('descricao')
        }
        
        # Processar fotos se houver
        fotos = request.files.getlist('fotos')
    else:
        # Requisição JSON (sem fotos)
        dados_json = request.get_json()
        dados = {
            "user_id": current_user_id,
            "nome": dados_json.get('nome'),
            "categoria": dados_json.get('categoria'),
            "marca": dados_json.get('marca'),
            "modelo": dados_json.get('modelo', ''),
            "estado": dados_json.get('estado'),
            "preco": dados_json.get('preco'),
            "descricao": dados_json.get('descricao')
        }
        fotos = None
    
    status, mensagem = PecaService.cadastrar_peca(dados, fotos)
    
    if status:
        return jsonify({"success": True, "message": "Peça cadastrada com sucesso!"}), 201
    else:
        return jsonify({"error": mensagem}), 400


# --- ROTA PROTEGIDA: Minhas Peças ---
@peca_bp.route('/minhas-pecas', methods=['GET'])
@jwt_required()
def minhas_pecas():
    """Lista todas as peças do usuário logado"""
    
    current_user_id = get_jwt_identity()
    
    pecas = PecaService.listar_por_usuario(current_user_id)
    return jsonify(pecas), 200


# --- ROTA PÚBLICA: Listagem Geral ---
@peca_bp.route('/pecas', methods=['GET'])
def listar_pecas():
    """Lista todas as peças ativas"""
    
    # Filtros opcionais
    categoria = request.args.get('categoria')
    estado = request.args.get('estado')
    
    pecas = PecaService.listar_todos(categoria=categoria, estado=estado)
    return jsonify(pecas), 200

# --- ROTA PÚBLICA: Detalhes ---
@peca_bp.route('/peca/<peca_id>', methods=['GET'])
def detalhes_peca(peca_id):
    """Retorna detalhes de uma peça específica"""
    peca = PecaService.buscar_por_id(peca_id)
    if peca:
        return jsonify(peca), 200
    return jsonify({"error": "Peça não encontrada"}), 404


# --- ROTA PROTEGIDA: Deletar ---
@peca_bp.route('/peca/<peca_id>', methods=['DELETE'])
@jwt_required()
def deletar_peca(peca_id):
    """Deleta (inativa) uma peça"""
    
    current_user_id = get_jwt_identity()
    
    # Verificar se a peça existe
    peca = PecaService.buscar_por_id(peca_id)
    
    # VERIFICAÇÃO DE PROPRIEDADE:
    if not peca or peca.get('user_id') != current_user_id:
        return jsonify({"error": "Peça não encontrada ou você não tem permissão para apagá-la"}), 403
    
    if PecaService.deletar_peca(peca_id):
        return jsonify({"message": "Peça deletada com sucesso"}), 200
    return jsonify({"error": "Erro ao deletar peça"}), 400

# --- ROTA PROTEGIDA: Atualizar ---
@peca_bp.route('/peca/<peca_id>', methods=['PUT'])
@jwt_required()
def atualizar_peca(peca_id):
    """Atualiza informações de uma peça"""
    
    current_user_id = get_jwt_identity()
    
    # Verificar se a peça pertence ao usuário
    peca = PecaService.buscar_por_id(peca_id)
    if not peca or peca.get('user_id') != current_user_id:
        return jsonify({"error": "Peça não encontrada ou você não tem permissão para editá-la"}), 403
    
    dados = request.get_json()
    
    if PecaService.atualizar_peca(peca_id, dados):
        return jsonify({"message": "Peça atualizada com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar peça"}), 400

# --- ROTA PÚBLICA: Listas Auxiliares ---
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

# --- ROTA PÚBLICA: Listas Auxiliares ---
@peca_bp.route('/pecas/categorias', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias de peças disponíveis"""
    # Dados estáticos não precisam de proteção
    categorias = [
        {"value": "motor", "label": "Motor e Transmissão"},
        {"value": "suspensao", "label": "Suspensão e Freios"},
        {"value": "carroceria", "label": "Carroceria"},
        {"value": "eletrica", "label": "Parte Elétrica"},
        {"value": "interior", "label": "Interior"},
        {"value": "outros", "label": "Outros"}
    ]
    return jsonify(categorias), 200