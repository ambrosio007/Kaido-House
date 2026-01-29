from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.veiculo_service import VeiculoService

veiculo_bp = Blueprint('veiculo', __name__)

@veiculo_bp.route('/cadastro-veiculo', methods=['POST'])
@jwt_required() # <--- O "porteiro" verifica o token aqui
def cadastro_veiculo():
    """Cadastra um novo veículo"""
    
    # Pega o ID do usuário que está dentro do Token
    current_user_id = get_jwt_identity()
    
    dados = {
        "user_id": current_user_id, # Usamos o ID do token, não da sessão
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
    # Não tem @jwt_required, pois é público
    veiculos = VeiculoService.listar_todos()
    return jsonify(veiculos), 200

# --- ROTA PÚBLICA: Ver detalhes do carro ---
@veiculo_bp.route('/veiculo/<veiculo_id>', methods=['GET'])
def detalhes_veiculo(veiculo_id):
    """Retorna detalhes de um veículo específico"""
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
    # Compara o dono do veículo com o dono do token
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