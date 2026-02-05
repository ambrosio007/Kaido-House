/**
 * ✅ CARRINHO.JS - Gerenciamento completo do carrinho de compras
 * 🔧 VERSÃO CORRIGIDA - Com proteção contra undefined
 */

// ==========================================
// CARREGAR ITENS DO CARRINHO
// ==========================================

async function carregarCarrinho() {
    console.log('🛒 Carregando itens do carrinho...');
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token) {
        console.warn('⚠️ Usuário não autenticado');
        mostrarCarrinhoVazio();
        return;
    }
    
    console.log('🔑 Token encontrado');
    
    try {
        const response = await fetch('/api/carrinho', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📊 Status da resposta:', response.status);
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('❌ Token inválido ou expirado');
                localStorage.removeItem('access_token');
                localStorage.removeItem('token');
                mostrarNotificacao('Sua sessão expirou. Faça login novamente.', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=/carrinho';
                }, 1500);
                return;
            }
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados do carrinho recebidos:', data);
        
        // Renderizar os itens
        renderizarItens(data.itens);
        
        // Atualizar resumo
        atualizarResumo(data);
        
    } catch (error) {
        console.error('❌ Erro ao carregar carrinho:', error);
        mostrarErroCarregamento();
    }
}

// ==========================================
// RENDERIZAR ITENS DO CARRINHO
// ==========================================

function renderizarItens(itens) {
    const container = document.querySelector('.cart-items');
    
    if (!container) {
        console.error('❌ Container .cart-items não encontrado');
        return;
    }
    
    // Se não houver itens
    if (!itens || itens.length === 0) {
        mostrarCarrinhoVazio();
        return;
    }
    
    // Gerar HTML dos itens
    const itensHTML = itens.map(item => criarItemHTML(item)).join('');
    container.innerHTML = itensHTML;
    
    // Adicionar event listeners
    adicionarEventListeners();
    
    console.log(`✅ ${itens.length} itens renderizados`);
}

// ==========================================
// CRIAR HTML DE UM ITEM - VERSÃO CORRIGIDA
// ==========================================

function criarItemHTML(item) {
    console.log('🔍 Processando item:', item);
    
    // Processar imagem
    let imagemSrc = '/static/img/default-placeholder.jpg';
    
    if (item.fotos) {
        const fotos = item.fotos.split(',').map(f => f.trim()).filter(f => f);
        if (fotos.length > 0) {
            imagemSrc = fotos[0];
        }
    }
    
    // ✅ CORREÇÃO: Nome do item com proteção contra undefined
    let nome = 'Produto';
    if (item.tipo_item === 'peca') {
        nome = item.nome || 'Peça sem nome';
    } else if (item.tipo_item === 'veiculo') {
        const marca = item.marca || '';
        const modelo = item.modelo || '';
        const ano = item.ano || '';
        nome = `${marca} ${modelo} ${ano}`.trim() || 'Veículo';
    }
    
    console.log('✅ Nome processado:', nome);
    
    // Categoria/Estado
    const categoria = item.tipo_item === 'peca'
        ? item.categoria || 'Novo'
        : `${item.estado || 'Novo'} - ${item.km ? item.km.toLocaleString('pt-BR') : '0'} km`;
    
    // ✅ CORREÇÃO: Preço formatado com proteção
    const precoUnitario = parseFloat(item.preco_unitario || 0).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    const subtotal = parseFloat(item.subtotal || 0).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Controle de quantidade (desabilitado para veículos)
    const controlesQtd = item.tipo_item === 'veiculo' 
        ? `<div class="item-quantity">
               <button class="qty-btn minus" disabled style="opacity: 0.5; cursor: not-allowed;">-</button>
               <input type="number" value="1" min="1" max="1" disabled style="background: #f5f5f5;">
               <button class="qty-btn plus" disabled style="opacity: 0.5; cursor: not-allowed;">+</button>
           </div>`
        : `<div class="item-quantity">
               <button class="qty-btn minus" data-id="${item.id}">-</button>
               <input type="number" value="${item.quantidade}" min="1" data-id="${item.id}">
               <button class="qty-btn plus" data-id="${item.id}">+</button>
           </div>`;
    
    return `
        <div class="cart-item" data-id="${item.id}" data-price="${item.preco_unitario || 0}">
            <div class="item-img">
                <img src="${imagemSrc}" 
                     alt="${nome}"
                     onerror="this.onerror=null; this.src='/static/img/default-placeholder.jpg';">
            </div>
            <div class="item-details">
                <span class="item-category">${categoria}</span>
                <h3>${nome}</h3>
                <p class="unit-price">Preço unitário: R$ ${precoUnitario}</p>
            </div>
            ${controlesQtd}
            <div class="item-subtotal">
                R$ ${subtotal}
            </div>
            <button class="remove-item" data-id="${item.id}">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
}

// ==========================================
// ADICIONAR EVENT LISTENERS
// ==========================================

function adicionarEventListeners() {
    // Botões de aumentar quantidade
    document.querySelectorAll('.qty-btn.plus').forEach(btn => {
        btn.addEventListener('click', async function() {
            if (this.disabled) return;
            
            const itemId = this.getAttribute('data-id');
            const input = document.querySelector(`input[data-id="${itemId}"]`);
            const novaQuantidade = parseInt(input.value) + 1;
            
            await atualizarQuantidade(itemId, novaQuantidade);
        });
    });
    
    // Botões de diminuir quantidade
    document.querySelectorAll('.qty-btn.minus').forEach(btn => {
        btn.addEventListener('click', async function() {
            if (this.disabled) return;
            
            const itemId = this.getAttribute('data-id');
            const input = document.querySelector(`input[data-id="${itemId}"]`);
            const novaQuantidade = parseInt(input.value) - 1;
            
            if (novaQuantidade < 1) {
                if (confirm('Deseja remover este item do carrinho?')) {
                    await removerItem(itemId);
                }
            } else {
                await atualizarQuantidade(itemId, novaQuantidade);
            }
        });
    });
    
    // Inputs de quantidade
    document.querySelectorAll('.item-quantity input[type="number"]').forEach(input => {
        input.addEventListener('change', async function() {
            if (this.disabled) return;
            
            const itemId = this.getAttribute('data-id');
            let novaQuantidade = parseInt(this.value);
            
            if (novaQuantidade < 1) {
                this.value = 1;
                novaQuantidade = 1;
            }
            
            await atualizarQuantidade(itemId, novaQuantidade);
        });
    });
    
    // Botões de remover item
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', async function() {
            const itemId = this.getAttribute('data-id');
            
            if (confirm('Deseja remover este item do carrinho?')) {
                await removerItem(itemId);
            }
        });
    });
    
    // Botão de finalizar compra
    const btnCheckout = document.querySelector('.btn-checkout');
    if (btnCheckout) {
        btnCheckout.addEventListener('click', function() {
            window.location.href = '/checkout';
        });
    }
    
    // Botão de aplicar cupom
    const btnAplicarCupom = document.querySelector('.coupon button');
    if (btnAplicarCupom) {
        btnAplicarCupom.addEventListener('click', function() {
            const cupomInput = document.getElementById('cupom-input');
            const cupom = cupomInput ? cupomInput.value.trim() : '';
            
            if (cupom) {
                aplicarCupom(cupom);
            } else {
                mostrarNotificacao('Digite um cupom válido', 'warning');
            }
        });
    }
}

// ==========================================
// ATUALIZAR QUANTIDADE DE UM ITEM
// ==========================================

async function atualizarQuantidade(itemId, novaQuantidade) {
    console.log(`🔄 Atualizando quantidade do item ${itemId} para ${novaQuantidade}`);
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token) {
        mostrarNotificacao('Você precisa estar logado', 'warning');
        setTimeout(() => {
            window.location.href = '/login?redirect=/carrinho';
        }, 1500);
        return;
    }
    
    try {
        const response = await fetch(`/api/carrinho/atualizar/${itemId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantidade: novaQuantidade })
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('token');
                mostrarNotificacao('Sua sessão expirou', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=/carrinho';
                }, 1500);
                return;
            }
            throw new Error('Erro ao atualizar quantidade');
        }
        
        const result = await response.json();
        console.log('✅ Quantidade atualizada:', result);
        
        // Recarregar carrinho
        await carregarCarrinho();
        
        mostrarNotificacao('Quantidade atualizada!', 'success');
        
    } catch (error) {
        console.error('❌ Erro ao atualizar quantidade:', error);
        mostrarNotificacao('Erro ao atualizar quantidade', 'error');
    }
}

// ==========================================
// REMOVER ITEM DO CARRINHO
// ==========================================

async function removerItem(itemId) {
    console.log(`🗑️ Removendo item ${itemId}...`);
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token) {
        mostrarNotificacao('Você precisa estar logado', 'warning');
        setTimeout(() => {
            window.location.href = '/login?redirect=/carrinho';
        }, 1500);
        return;
    }
    
    try {
        const response = await fetch(`/api/carrinho/remover/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('token');
                mostrarNotificacao('Sua sessão expirou', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=/carrinho';
                }, 1500);
                return;
            }
            throw new Error('Erro ao remover item');
        }
        
        const result = await response.json();
        console.log('✅ Item removido:', result);
        
        // Atualizar badge do carrinho
        if (result.total_itens !== undefined) {
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.textContent = result.total_itens;
            }
        }
        
        // Recarregar carrinho
        await carregarCarrinho();
        
        mostrarNotificacao('Item removido do carrinho!', 'success');
        
    } catch (error) {
        console.error('❌ Erro ao remover item:', error);
        mostrarNotificacao('Erro ao remover item', 'error');
    }
}

// ==========================================
// ATUALIZAR RESUMO DO PEDIDO
// ==========================================

function atualizarResumo(data) {
    const subtotalEl = document.getElementById('subtotal-val');
    const totalEl = document.getElementById('total-val');
    
    if (subtotalEl) {
        const subtotal = parseFloat(data.total_valor || 0).toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        subtotalEl.textContent = `R$ ${subtotal}`;
    }
    
    if (totalEl) {
        const total = parseFloat(data.total_valor || 0).toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        totalEl.textContent = `R$ ${total}`;
    }
    
    // Atualizar badge do carrinho
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = data.total_itens || 0;
    }
}

// ==========================================
// APLICAR CUPOM DE DESCONTO
// ==========================================

async function aplicarCupom(cupom) {
    console.log(`🎟️ Aplicando cupom: ${cupom}`);
    mostrarNotificacao('Funcionalidade de cupom em desenvolvimento', 'info');
}

// ==========================================
// MOSTRAR CARRINHO VAZIO
// ==========================================

function mostrarCarrinhoVazio() {
    const container = document.querySelector('.cart-items');
    
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; grid-column: 1 / -1;">
                <i class="fas fa-shopping-cart" style="font-size: 80px; color: #ddd; margin-bottom: 20px;"></i>
                <h3 style="color: #666; margin-bottom: 10px;">Seu carrinho está vazio</h3>
                <p style="color: #999; margin-bottom: 30px;">Adicione produtos para começar suas compras!</p>
                <a href="/pecas_pag" class="btn" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; text-decoration: none; border-radius: 8px;">
                    <i class="fas fa-shopping-bag"></i> Ver Produtos
                </a>
            </div>
        `;
    }
    
    atualizarResumo({ total_valor: 0, total_itens: 0 });
}

// ==========================================
// MOSTRAR ERRO DE CARREGAMENTO
// ==========================================

function mostrarErroCarregamento() {
    const container = document.querySelector('.cart-items');
    
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; grid-column: 1 / -1;">
                <i class="fas fa-exclamation-triangle" style="font-size: 80px; color: #ff6b6b; margin-bottom: 20px;"></i>
                <h3 style="color: #666; margin-bottom: 10px;">Erro ao carregar carrinho</h3>
                <p style="color: #999; margin-bottom: 30px;">Tente novamente mais tarde</p>
                <button onclick="carregarCarrinho()" class="btn" style="padding: 12px 30px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; border: none; border-radius: 8px; cursor: pointer;">
                    <i class="fas fa-redo"></i> Tentar Novamente
                </button>
            </div>
        `;
    }
}

// ==========================================
// FUNÇÃO PARA MOSTRAR NOTIFICAÇÕES
// ==========================================

function mostrarNotificacao(mensagem, tipo = 'info') {
    const notifAnterior = document.querySelector('.notificacao-toast');
    if (notifAnterior) {
        notifAnterior.remove();
    }
    
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao-toast notificacao-${tipo}`;
    
    const icone = tipo === 'success' ? 'check-circle' : 
                  tipo === 'error' ? 'times-circle' :
                  tipo === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    notificacao.innerHTML = `
        <i class="fas fa-${icone}"></i>
        <span>${mensagem}</span>
    `;
    
    notificacao.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${tipo === 'success' ? '#4CAF50' : 
                     tipo === 'error' ? '#f44336' :
                     tipo === 'warning' ? '#ff9800' : '#2196F3'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(notificacao);
    
    setTimeout(() => {
        notificacao.style.opacity = '1';
        notificacao.style.transform = 'translateX(0)';
    }, 10);
    
    setTimeout(() => {
        notificacao.style.opacity = '0';
        notificacao.style.transform = 'translateX(100%)';
        setTimeout(() => notificacao.remove(), 300);
    }, 3000);
}

// ==========================================
// INICIALIZAR QUANDO A PÁGINA CARREGAR
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Página do carrinho carregada');
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token) {
        console.warn('⚠️ Usuário não autenticado - redirecionando...');
        mostrarNotificacao('Você precisa estar logado para acessar o carrinho', 'warning');
        setTimeout(() => {
            window.location.href = '/login?redirect=/carrinho';
        }, 1500);
        return;
    }
    
    carregarCarrinho();
});

console.log('✅ carrinho.js carregado com sucesso!');