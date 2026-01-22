from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.veiculo_service import VeiculoService

veiculo_bp = Blueprint('veiculo', __name__)

@veiculo_bp.route('/cadastro-veiculo', methods=['POST'])
def cadastro_veiculo():
    """Cadastra um novo veículo"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    dados = {
        "user_id": session['user_id'],
        "marca": request.form.get('marca'),
        "modelo": request.form.get('modelo'),
        "ano": request.form.get('ano'),
        "km": request.form.get('km'),
        "cor": request.form.get('cor'),
        "preco": request.form.get('preco'),
        "descricao": request.form.get('descricao')
    }
    
    # Processar fotos se houver
    fotos = request.files.getlist('fotos')
    
    status, mensagem = VeiculoService.cadastrar_veiculo(dados, fotos)
    
    if status:
        return jsonify({"success": True, "message": "Veículo cadastrado com sucesso!"}), 200
    else:
        return jsonify({"error": mensagem}), 400

@veiculo_bp.route('/meus-veiculos', methods=['GET'])
def meus_veiculos():
    """Lista todos os veículos do usuário logado"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    veiculos = VeiculoService.listar_por_usuario(session['user_id'])
    return jsonify(veiculos), 200

@veiculo_bp.route('/veiculos', methods=['GET'])
def listar_veiculos():
    """Lista todos os veículos ativos"""
    veiculos = VeiculoService.listar_todos()
    return jsonify(veiculos), 200

@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['GET'])
def detalhes_veiculo(veiculo_id):
    """Retorna detalhes de um veículo específico"""
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    if veiculo:
        return jsonify(veiculo), 200
    return jsonify({"error": "Veículo não encontrado"}), 404

@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['DELETE'])
def deletar_veiculo(veiculo_id):
    """Deleta (inativa) um veículo"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    # Verificar se o veículo pertence ao usuário
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    if not veiculo or veiculo.get('user_id') != session['user_id']:
        return jsonify({"error": "Veículo não encontrado ou não autorizado"}), 403
    
    if VeiculoService.deletar_veiculo(veiculo_id):
        return jsonify({"message": "Veículo deletado com sucesso"}), 200
    return jsonify({"error": "Erro ao deletar veículo"}), 400

@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['PUT'])
def atualizar_veiculo(veiculo_id):
    """Atualiza informações de um veículo"""
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    # Verificar se o veículo pertence ao usuário
    veiculo = VeiculoService.buscar_por_id(veiculo_id)
    if not veiculo or veiculo.get('user_id') != session['user_id']:
        return jsonify({"error": "Veículo não encontrado ou não autorizado"}), 403
    
    dados = request.get_json()
    
    if VeiculoService.atualizar_veiculo(veiculo_id, dados):
        return jsonify({"message": "Veículo atualizado com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar veículo"}), 400