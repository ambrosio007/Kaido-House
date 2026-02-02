from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.veiculos_service import VeiculoService

veiculo_bp = Blueprint('veiculo', __name__)

@veiculo_bp.route('/cadastro-veiculo', methods=['POST'])
@jwt_required()
def cadastro_veiculo():
    """Cadastra um novo veículo COM SUPORTE A UPLOAD DE IMAGENS"""
    
    # Pega o ID do usuário que está dentro do Token
    current_user_id = get_jwt_identity()
    
    # ✅ CORREÇÃO: Aceitar tanto FormData (com fotos) quanto JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Requisição com arquivos (FormData)
        dados = {
            "user_id": current_user_id,
            "marca": request.form.get('marca'),
            "modelo": request.form.get('modelo'),
            "ano": request.form.get('ano'),
            "km": request.form.get('km'),
            "cor": request.form.get('cor'),
            "estado": request.form.get('estado'),
            "preco": request.form.get('preco'),
            "descricao": request.form.get('descricao')
        }
        
        # Processar fotos
        fotos = request.files.getlist('fotos')
    else:
        # Requisição JSON (sem fotos)
        dados_json = request.get_json()
        dados = {
            "user_id": current_user_id,
            "marca": dados_json.get('marca'),
            "modelo": dados_json.get('modelo'),
            "ano": dados_json.get('ano'),
            "km": dados_json.get('km'),
            "cor": dados_json.get('cor'),
            "estado": dados_json.get('estado'),
            "preco": dados_json.get('preco'),
            "descricao": dados_json.get('descricao')
        }
        fotos = None
    
    status, mensagem = VeiculoService.cadastrar_veiculo(dados, fotos)
    
    if status:
        return jsonify({"success": True, "message": "Veículo cadastrado com sucesso!"}), 201
    else:
        return jsonify({"error": mensagem}), 400

# --- ROTA PROTEGIDA: Usuário vê apenas SEUS veículos ---
@veiculo_bp.route('/meus-veiculos', methods=['GET'])
@jwt_required()
def meus_veiculos():
    """Lista todos os veículos do usuário logado"""
    
    current_user_id = get_jwt_identity()
    
    veiculos = VeiculoService.listar_por_usuario(current_user_id)
    return jsonify(veiculos), 200

# --- ROTA PÚBLICA: Qualquer pessoa pode ver a lista de vendas ---
@veiculo_bp.route('/veiculos', methods=['GET'])
def listar_veiculos():
    """Lista todos os veículos ativos"""
    veiculos = VeiculoService.listar_todos()
    return jsonify(veiculos), 200

# --- ROTA PÚBLICA: Página HTML de Detalhes ---
@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['GET'])
def detalhes_veiculo_pagina(veiculo_id):
    """Renderiza a página HTML de detalhes do veículo"""
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    if veiculo:
        return render_template('detalhes_veiculo.html', veiculo=veiculo)
    return render_template('erro_404.html'), 404

# --- ROTA PÚBLICA API: Detalhes (JSON) ---
@veiculo_bp.route('/api/veiculo/<veiculo_id>', methods=['GET'])
def detalhes_veiculo_api(veiculo_id):
    """Retorna detalhes de um veículo específico em JSON"""
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    if veiculo:
        return jsonify(veiculo), 200
    return jsonify({"error": "Veículo não encontrado"}), 404

# --- ROTA PROTEGIDA: Deletar ---
@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['DELETE'])
@jwt_required()
def deletar_veiculo(veiculo_id):
    """Deleta (inativa) um veículo"""
    
    current_user_id = get_jwt_identity()
    
    # Busca o veículo para garantir que ele existe
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    
    # VERIFICAÇÃO DE PROPRIEDADE:
    if not veiculo or veiculo.get('user_id') != current_user_id:
        return jsonify({"error": "Veículo não encontrado ou você não tem permissão para deletá-lo"}), 403
    
    if VeiculoService.deletar_veiculo(veiculo_id):
        return jsonify({"message": "Veículo deletado com sucesso"}), 200
    return jsonify({"error": "Erro ao deletar veículo"}), 400

@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['PUT'])
@jwt_required()
def atualizar_veiculo(veiculo_id):
    """Atualiza informações de um veículo"""
    
    current_user_id = get_jwt_identity()
    
    # Verificar se o veículo pertence ao usuário do token
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    
    if not veiculo or veiculo.get('user_id') != current_user_id:
        return jsonify({"error": "Veículo não encontrado ou você não tem permissão para editá-lo"}), 403
    
    dados = request.get_json()
    
    if VeiculoService.atualizar_veiculo(veiculo_id, dados):
        return jsonify({"message": "Veículo atualizado com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar veículo"}), 400