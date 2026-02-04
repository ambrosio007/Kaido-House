/**
 * DETALHES DO PRODUTO - JavaScript
 */

// ==========================================
// TROCA DE IMAGENS NA GALERIA
// ==========================================

function trocarImagem(urlImagem) {
    const imagemDestaque = document.getElementById('imagem-destaque');
    const miniaturas = document.querySelectorAll('.miniatura');
    
    // Atualizar imagem principal
    imagemDestaque.src = urlImagem;
    
    // Atualizar classe ativa das miniaturas
    miniaturas.forEach(mini => {
        if (mini.src === urlImagem) {
            mini.classList.add('ativa');
        } else {
            mini.classList.remove('ativa');
        }
    });
}

// ==========================================
// SISTEMA DE ABAS
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remover classe active de todos
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Adicionar classe active ao clicado
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});

// ==========================================
// ADICIONAR AO CARRINHO
// ==========================================

async function adicionarAoCarrinho(itemId, tipo) {
    console.log(`🛒 Adicionando ao carrinho: ${tipo} ${itemId}`);
    
    // Verificar se está logado
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        mostrarNotificacao('Você precisa estar logado para adicionar itens ao carrinho!', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1000);
        return;
    }
    
    // Desabilitar botão temporariamente
    const btnAdicionar = document.querySelector('.btn-adicionar-carrinho');
    const textoOriginal = btnAdicionar.innerHTML;
    btnAdicionar.disabled = true;
    btnAdicionar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adicionando...';
    
    try {
        const response = await fetch('/api/carrinho/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                tipo_item: tipo,
                item_id: itemId,
                quantidade: 1
            })
        });
        
        const contentType = response.headers.get('content-type');
        let result;
        
        if (contentType && contentType.includes('application/json')) {
            result = await response.json();
        } else {
            if (response.status === 401) {
                mostrarNotificacao('Sessão expirada. Faça login novamente.', 'error');
                setTimeout(() => {
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                }, 1500);
                return;
            }
            throw new Error('Resposta inválida do servidor');
        }
        
        if (response.ok) {
            // Atualizar badge do carrinho
            if (result.total_itens !== undefined) {
                const badge = document.querySelector('.cart-badge');
                if (badge) {
                    badge.textContent = result.total_itens;
                    badge.style.transform = 'scale(1.3)';
                    setTimeout(() => {
                        badge.style.transform = 'scale(1)';
                    }, 300);
                }
            }
            
            // Mudar texto do botão temporariamente
            btnAdicionar.innerHTML = '<i class="fas fa-check"></i> Adicionado!';
            btnAdicionar.style.background = '#27ae60';
            
            mostrarNotificacao('✅ Item adicionado ao carrinho!', 'success');
            
            // Voltar ao normal após 2 segundos
            setTimeout(() => {
                btnAdicionar.innerHTML = textoOriginal;
                btnAdicionar.style.background = '';
                btnAdicionar.disabled = false;
            }, 2000);
            
        } else {
            btnAdicionar.innerHTML = textoOriginal;
            btnAdicionar.disabled = false;
            
            if (response.status === 401) {
                mostrarNotificacao('Sessão expirada. Redirecionando...', 'error');
                setTimeout(() => {
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                }, 1500);
            } else {
                mostrarNotificacao(result.error || 'Erro ao adicionar item', 'error');
            }
        }
        
    } catch (error) {
        console.error('❌ Erro:', error);
        btnAdicionar.innerHTML = textoOriginal;
        btnAdicionar.disabled = false;
        mostrarNotificacao('Erro ao adicionar item ao carrinho', 'error');
    }
}

// ==========================================
// COMPRAR AGORA
// ==========================================

async function comprarAgora(itemId, tipo) {
    console.log(`⚡ Comprar agora: ${tipo} ${itemId}`);
    
    // Verificar se está logado
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        mostrarNotificacao('Você precisa estar logado!', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1000);
        return;
    }
    
    try {
        // Adicionar ao carrinho
        const response = await fetch('/api/carrinho/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                tipo_item: tipo,
                item_id: itemId,
                quantidade: 1
            })
        });
        
        if (response.ok) {
            // Redirecionar para o carrinho
            mostrarNotificacao('Redirecionando para o carrinho...', 'success');
            setTimeout(() => {
                window.location.href = '/carrinho';
            }, 500);
        } else {
            const result = await response.json();
            mostrarNotificacao(result.error || 'Erro ao processar compra', 'error');
        }
        
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('Erro ao processar compra', 'error');
    }
}

// ==========================================
// FAVORITAR PRODUTO
// ==========================================

function toggleFavorito(itemId, tipo) {
    const btnFavorito = document.querySelector('.btn-favorito');
    const icon = btnFavorito.querySelector('i');
    
    // Verificar se está logado
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        mostrarNotificacao('Você precisa estar logado para favoritar!', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1000);
        return;
    }
    
    // Toggle visual imediato
    btnFavorito.classList.toggle('ativo');
    
    if (btnFavorito.classList.contains('ativo')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        mostrarNotificacao('❤️ Adicionado aos favoritos!', 'success');
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        mostrarNotificacao('Removido dos favoritos', 'info');
    }
    
    // TODO: Implementar API de favoritos
    // fetch('/api/favoritos/toggle', { ... })
}

// ==========================================
// COMPARTILHAR PRODUTO
// ==========================================

function compartilhar() {
    const url = window.location.href;
    const titulo = document.querySelector('.titulo-produto').textContent;
    
    // Verificar se o navegador suporta Web Share API
    if (navigator.share) {
        navigator.share({
            title: titulo,
            text: `Confira este produto: ${titulo}`,
            url: url
        })
        .then(() => {
            mostrarNotificacao('✅ Compartilhado com sucesso!', 'success');
        })
        .catch((error) => {
            console.log('Erro ao compartilhar:', error);
        });
    } else {
        // Fallback: copiar para área de transferência
        copiarParaClipboard(url);
        mostrarNotificacao('🔗 Link copiado para a área de transferência!', 'success');
    }
}

function copiarParaClipboard(texto) {
    const textarea = document.createElement('textarea');
    textarea.value = texto;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

// ==========================================
// SISTEMA DE NOTIFICAÇÕES
// ==========================================

function mostrarNotificacao(mensagem, tipo = 'info') {
    // Remover notificação anterior se existir
    const notifAnterior = document.querySelector('.notificacao-toast');
    if (notifAnterior) {
        notifAnterior.remove();
    }
    
    // Criar nova notificação
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao-toast notificacao-${tipo}`;
    
    // Ícone baseado no tipo
    let icone = 'fa-info-circle';
    if (tipo === 'success') icone = 'fa-check-circle';
    if (tipo === 'error') icone = 'fa-exclamation-circle';
    if (tipo === 'warning') icone = 'fa-exclamation-triangle';
    
    notificacao.innerHTML = `
        <i class="fas ${icone}"></i>
        <span>${mensagem}</span>
    `;
    
    // Estilos da notificação
    notificacao.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        padding: 18px 25px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 15px;
        font-weight: 600;
        z-index: 9999;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s;
    `;
    
    // Cores baseadas no tipo
    const cores = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };
    
    const cor = cores[tipo] || cores.info;
    notificacao.style.borderLeft = `5px solid ${cor}`;
    notificacao.querySelector('i').style.color = cor;
    
    document.body.appendChild(notificacao);
    
    // Animar entrada
    setTimeout(() => {
        notificacao.style.opacity = '1';
        notificacao.style.transform = 'translateY(0)';
    }, 10);
    
    // Remover após 3 segundos
    setTimeout(() => {
        notificacao.style.opacity = '0';
        notificacao.style.transform = 'translateY(20px)';
        setTimeout(() => notificacao.remove(), 300);
    }, 3000);
}

// ==========================================
// CARREGAR PRODUTOS RELACIONADOS
// ==========================================

async function carregarProdutosRelacionados() {
    // Verificar se existe o container
    const container = document.getElementById('produtos-relacionados');
    if (!container) return;
    
    try {
        // Buscar produtos similares (você pode implementar uma API específica)
        const tipo = produtoAtual.tipo;
        const response = await fetch(`/api/${tipo}s?limit=4&aleatorio=true`);
        
        if (!response.ok) throw new Error('Erro ao carregar relacionados');
        
        const produtos = await response.json();
        
        if (produtos.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">Nenhum produto relacionado encontrado.</p>';
            return;
        }
        
        // Renderizar produtos
        container.innerHTML = produtos.map(produto => criarCardRelacionado(produto, tipo)).join('');
        
    } catch (error) {
        console.error('Erro ao carregar produtos relacionados:', error);
        container.innerHTML = '<p style="text-align: center; color: #999;">Erro ao carregar produtos relacionados.</p>';
    }
}

function criarCardRelacionado(produto, tipo) {
    const nome = tipo === 'veiculo' 
        ? `${produto.marca} ${produto.modelo}` 
        : produto.nome;
    
    const preco = parseFloat(produto.preco).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    const foto = produto.fotos ? produto.fotos.split(',')[0].trim() : '/static/img/default-placeholder.jpg';
    
    return `
        <div class="product-card" style="cursor: pointer;" onclick="window.location.href='/${tipo}/${produto.id}'">
            <div class="card-image" style="aspect-ratio: 4/3; overflow: hidden; border-radius: 10px;">
                <img src="${foto}" alt="${nome}" 
                     style="width: 100%; height: 100%; object-fit: cover;"
                     onerror="this.src='/static/img/default-placeholder.jpg'">
            </div>
            <div style="padding: 15px;">
                <h4 style="font-size: 16px; margin: 10px 0; color: #222;">${nome}</h4>
                <p style="font-size: 20px; font-weight: 700; color: #27ae60; margin: 0;">R$ ${preco}</p>
            </div>
        </div>
    `;
}

// Carregar produtos relacionados quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    carregarProdutosRelacionados();
});

// ==========================================
// ATUALIZAR BADGE DO CARRINHO
// ==========================================

async function atualizarBadgeCarrinho() {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        const badge = document.querySelector('.cart-badge');
        if (badge) badge.textContent = '0';
        return;
    }
    
    try {
        const response = await fetch('/api/carrinho/total', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.textContent = data.total_itens || '0';
            }
        }
    } catch (error) {
        console.error('Erro ao atualizar badge do carrinho:', error);
    }
}

// Atualizar badge ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    atualizarBadgeCarrinho();
});

console.log('✅ detalhes_produto.js carregado com sucesso!');