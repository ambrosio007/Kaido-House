from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.carrinho_service import CarrinhoService
import traceback

carrinho_bp = Blueprint('carrinho', __name__)

# --- ROTA PÚBLICA: Listar Itens do Carrinho ---
@carrinho_bp.route('/api/carrinho', methods=['GET'])
@jwt_required()
def listar_carrinho():
    """
    Lista todos os itens do carrinho do usuário
    """
    current_user_id = get_jwt_identity()
    
    try:
        resumo = CarrinhoService.obter_resumo_carrinho(current_user_id)
        return jsonify(resumo), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao listar carrinho: {str(e)}"}), 500

@@carrinho_bp.route('/api/carrinho/adicionar', methods=['POST'])
@jwt_required()
def adicionar_ao_carrinho():
    """
    Adiciona um item ao carrinho
    ✅ VERSÃO COM LOGS DETALHADOS
    """
    print("\n" + "="*60)
    print("🛒 REQUISIÇÃO: /api/carrinho/adicionar")
    print("="*60)
    
    try:
        # Obter ID do usuário do token JWT
        current_user_id = get_jwt_identity()
        print(f"✅ Usuário autenticado: {current_user_id}")
        
        # Obter dados da requisição
        dados = request.get_json()
        print(f"📦 Dados recebidos: {dados}")
        
        tipo_item = dados.get('tipo_item')
        item_id = dados.get('item_id')
        quantidade = dados.get('quantidade', 1)
        
        # Validação
        if not tipo_item or not item_id:
            print("❌ Dados incompletos")
            return jsonify({
                "error": "Dados incompletos",
                "message": "tipo_item e item_id são obrigatórios"
            }), 400
        
        print(f"📋 Tipo: {tipo_item}, ID: {item_id}, Qtd: {quantidade}")
        
        # Adicionar ao carrinho
        sucesso, mensagem = CarrinhoService.adicionar_item(
            user_id=current_user_id,
            tipo_item=tipo_item,
            item_id=item_id,
            quantidade=quantidade
        )
        
        if sucesso:
            print("✅ Item adicionado com sucesso!")
            
            # Obter total atualizado
            total_itens = CarrinhoService.obter_resumo_carrinho(current_user_id)['total_itens']
            
            print(f"📊 Total de itens no carrinho: {total_itens}")
            print("="*60 + "\n")
            
            return jsonify({
                "success": True,
                "message": mensagem,
                "total_itens": total_itens
            }), 200
        else:
            print(f"❌ Erro ao adicionar: {mensagem}")
            print("="*60 + "\n")
            
            return jsonify({
                "error": mensagem,
                "success": False
            }), 400
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e)
        }), 500

@carrinho_bp.route('/api/carrinho/atualizar/<item_id>', methods=['PUT'])
@jwt_required()
def atualizar_quantidade_item(item_id):
    """
    Atualiza a quantidade de um item no carrinho
    """
    current_user_id = get_jwt_identity()
    
    try:
        dados = request.get_json()
        nova_quantidade = dados.get('quantidade')
        
        if not nova_quantidade:
            return jsonify({"error": "Quantidade não informada"}), 400
        
        # Nota: O Service deve garantir que este item_id pertence a este user_id
        # Se o seu Service não valida isso, seria bom adicionar uma verificação aqui ou no Repository.
        sucesso, mensagem = CarrinhoService.atualizar_quantidade(
            item_id=item_id,
            user_id=current_user_id,
            nova_quantidade=nova_quantidade
        )
        
        if sucesso:
            return jsonify({"success": True, "message": mensagem}), 200
        else:
            return jsonify({"error": mensagem}), 400
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


@carrinho_bp.route('/api/carrinho/remover/<item_id>', methods=['DELETE'])
@jwt_required()
def remover_do_carrinho(item_id):
    """
    Remove um item do carrinho
    """
    current_user_id = get_jwt_identity()
    
    try:
        sucesso, mensagem = CarrinhoService.remover_item(
            item_id=item_id,
            user_id=current_user_id
        )
        
        if sucesso:
            total_itens = CarrinhoService.obter_resumo_carrinho(current_user_id)['total_itens']
            return jsonify({
                "success": True,
                "message": mensagem,
                "total_itens": total_itens
            }), 200
        else:
            return jsonify({"error": mensagem}), 400
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@carrinho_bp.route('/api/carrinho/limpar', methods=['DELETE'])
@jwt_required()
def limpar_carrinho():
    """
    Remove todos os itens do carrinho
    """
    current_user_id = get_jwt_identity()
    
    try:
        sucesso, mensagem = CarrinhoService.limpar_carrinho(current_user_id)
        
        if sucesso:
            return jsonify({"success": True, "message": mensagem}), 200
        else:
            return jsonify({"error": mensagem}), 400
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@carrinho_bp.route('/api/carrinho/verificar-disponibilidade', methods=['GET'])
@jwt_required()
def verificar_disponibilidade():
    """
    Verifica se todos os itens do carrinho ainda estão disponíveis
    """
    current_user_id = get_jwt_identity()
    
    try:
        todos_disponiveis, itens_indisponiveis = CarrinhoService.verificar_disponibilidade(
            current_user_id
        )
        
        return jsonify({
            "todos_disponiveis": todos_disponiveis,
            "itens_indisponiveis": itens_indisponiveis
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


@carrinho_bp.route('/api/carrinho/total', methods=['GET'])
@jwt_required(optional=True) # <--- IMPORTANTE: Aceita requisição sem token
def obter_total():
    """
    Retorna apenas o número total de itens no carrinho.
    Se não tiver token, retorna 0 (comportamento de visitante).
    """
    current_user_id = get_jwt_identity()
    
    # Se o usuário não enviou token (visitante), identity é None
    if not current_user_id:
        return jsonify({"total_itens": 0}), 200
    
    try:
        resumo = CarrinhoService.obter_resumo_carrinho(current_user_id)
        return jsonify({"total_itens": resumo['total_itens']}), 200
    except Exception as e:
        return jsonify({"error": f"Erro: {str(e)}"}), 500