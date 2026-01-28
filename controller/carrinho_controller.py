from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from service.carrinho_service import CarrinhoService

carrinho_bp = Blueprint('carrinho', __name__)

@carrinho_bp.route('/carrinho')
def ver_carrinho():
    """Página do carrinho de compras"""
    if "user_id" not in session:
        return redirect(url_for('user.login'))
    
    return render_template('carrinho.html')

@carrinho_bp.route('/api/carrinho', methods=['GET'])
def listar_carrinho():
    """
    Lista todos os itens do carrinho do usuário
    
    Returns:
        JSON com itens do carrinho e resumo
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        resumo = CarrinhoService.obter_resumo_carrinho(session['user_id'])
        return jsonify(resumo), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao listar carrinho: {str(e)}"}), 500

@carrinho_bp.route('/api/carrinho/adicionar', methods=['POST'])
def adicionar_ao_carrinho():
    """
    Adiciona um item ao carrinho
    
    Body JSON:
        {
            "tipo_item": "veiculo" ou "peca",
            "item_id": "id-do-item",
            "quantidade": 1 (opcional, padrão 1)
        }
    
    Returns:
        JSON com mensagem de sucesso ou erro
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        dados = request.get_json()
        
        tipo_item = dados.get('tipo_item')
        item_id = dados.get('item_id')
        quantidade = dados.get('quantidade', 1)
        
        if not tipo_item or not item_id:
            return jsonify({"error": "Dados incompletos"}), 400
        
        sucesso, mensagem = CarrinhoService.adicionar_item(
            user_id=session['user_id'],
            tipo_item=tipo_item,
            item_id=item_id,
            quantidade=quantidade
        )
        
        if sucesso:
            # Retornar também o total de itens atualizado
            total_itens = CarrinhoService.obter_resumo_carrinho(session['user_id'])['total_itens']
            return jsonify({
                "success": True,
                "message": mensagem,
                "total_itens": total_itens
            }), 200
        else:
            return jsonify({"error": mensagem}), 400
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@carrinho_bp.route('/api/carrinho/atualizar/<item_id>', methods=['PUT'])
def atualizar_quantidade_item(item_id):
    """
    Atualiza a quantidade de um item no carrinho
    
    Args:
        item_id (str): ID do item no carrinho
    
    Body JSON:
        {
            "quantidade": 2
        }
    
    Returns:
        JSON com mensagem de sucesso ou erro
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        dados = request.get_json()
        nova_quantidade = dados.get('quantidade')
        
        if not nova_quantidade:
            return jsonify({"error": "Quantidade não informada"}), 400
        
        sucesso, mensagem = CarrinhoService.atualizar_quantidade(
            item_id=item_id,
            user_id=session['user_id'],
            nova_quantidade=nova_quantidade
        )
        
        if sucesso:
            return jsonify({"success": True, "message": mensagem}), 200
        else:
            return jsonify({"error": mensagem}), 400
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@carrinho_bp.route('/api/carrinho/remover/<item_id>', methods=['DELETE'])
def remover_do_carrinho(item_id):
    """
    Remove um item do carrinho
    
    Args:
        item_id (str): ID do item no carrinho
    
    Returns:
        JSON com mensagem de sucesso ou erro
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        sucesso, mensagem = CarrinhoService.remover_item(
            item_id=item_id,
            user_id=session['user_id']
        )
        
        if sucesso:
            # Retornar também o total de itens atualizado
            total_itens = CarrinhoService.obter_resumo_carrinho(session['user_id'])['total_itens']
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
def limpar_carrinho():
    """
    Remove todos os itens do carrinho
    
    Returns:
        JSON com mensagem de sucesso ou erro
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        sucesso, mensagem = CarrinhoService.limpar_carrinho(session['user_id'])
        
        if sucesso:
            return jsonify({"success": True, "message": mensagem}), 200
        else:
            return jsonify({"error": mensagem}), 400
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@carrinho_bp.route('/api/carrinho/verificar-disponibilidade', methods=['GET'])
def verificar_disponibilidade():
    """
    Verifica se todos os itens do carrinho ainda estão disponíveis
    
    Returns:
        JSON com status e lista de itens indisponíveis
    """
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401
    
    try:
        todos_disponiveis, itens_indisponiveis = CarrinhoService.verificar_disponibilidade(
            session['user_id']
        )
        
        return jsonify({
            "todos_disponiveis": todos_disponiveis,
            "itens_indisponiveis": itens_indisponiveis
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@carrinho_bp.route('/api/carrinho/total', methods=['GET'])
def obter_total():
    """
    Retorna apenas o número total de itens no carrinho
    Útil para atualizar o badge do ícone de carrinho
    
    Returns:
        JSON com total de itens
    """
    if "user_id" not in session:
        return jsonify({"total_itens": 0}), 200
    
    try:
        resumo = CarrinhoService.obter_resumo_carrinho(session['user_id'])
        return jsonify({"total_itens": resumo['total_itens']}), 200
    except Exception as e:
        return jsonify({"error": f"Erro: {str(e)}"}), 500