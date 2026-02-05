/**
 * ✅ PECAS.JS - Carregamento dinâmico de peças da API
 * 🔧 VERSÃO CORRIGIDA - Carrega peças do banco de dados
 */

// ==========================================
// VARIÁVEIS GLOBAIS
// ==========================================

let todasPecas = []; // Armazena todas as peças carregadas
let filtroAtual = 'all'; // 'all', 'new', 'used'
let categoriaAtual = 'all'; // Categoria selecionada

// ==========================================
// CARREGAR PEÇAS DA API
// ==========================================

async function carregarPecas() {
    console.log('🔧 Carregando peças da API...');
    
    const container = document.querySelector('.parts-grid');
    
    if (!container) {
        console.error('❌ Container .parts-grid não encontrado');
        return;
    }
    
    // Mostrar loading
    container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
            <div class="loading-spinner" style="margin: 0 auto 20px; border: 4px solid #f3f3f3; border-top: 4px solid #e74c3c; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite;"></div>
            <p style="color: #999;">Carregando peças...</p>
        </div>
    `;
    
    try {
        // ✅ Endpoint correto
        const response = await fetch('/pecas');
        
        // ✅ Verificar Content-Type antes de parsear
        const contentType = response.headers.get('content-type');
        
        if (!response.ok) {
            console.error(`❌ Erro HTTP ${response.status}`);
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        // ✅ Verificar se é JSON
        if (!contentType || !contentType.includes('application/json')) {
            console.error('❌ Resposta não é JSON:', contentType);
            const htmlText = await response.text();
            console.error('Conteúdo recebido (primeiros 200 chars):', htmlText.substring(0, 200));
            throw new Error('Resposta do servidor não é JSON - verifique se o endpoint /pecas está retornando JSON');
        }
        
        const pecas = await response.json();
        console.log('✅ Peças carregadas:', pecas);
        
        if (!pecas || pecas.length === 0) {
            mostrarMensagemVazia();
            return;
        }
        
        // Armazenar peças globalmente
        todasPecas = pecas;
        
        // Renderizar peças
        renderizarPecas(pecas);
        
    } catch (error) {
        console.error('❌ Erro ao carregar peças:', error);
        mostrarErroCarregamento();
    }
}

// ==========================================
// RENDERIZAR PEÇAS
// ==========================================

function renderizarPecas(pecas) {
    const container = document.querySelector('.parts-grid');
    
    if (!container) return;
    
    if (!pecas || pecas.length === 0) {
        mostrarMensagemVazia();
        return;
    }
    
    const pecasHTML = pecas.map(peca => criarPecaCard(peca)).join('');
    container.innerHTML = pecasHTML;
    
    // Adicionar event listeners para os botões "Adicionar ao Carrinho"
    adicionarEventListenersCarrinho();
    
    console.log(`✅ ${pecas.length} peças renderizadas`);
}

// ==========================================
// CRIAR CARD DE PEÇA
// ==========================================

function criarPecaCard(peca) {
    // Processar imagem
    let imagemSrc = '/static/images/default-part.jpg';
    
    if (peca.fotos) {
        const fotos = peca.fotos.split(',').map(f => f.trim()).filter(f => f);
        if (fotos.length > 0) {
            imagemSrc = fotos[0];
        }
    }
    
    // ✅ Validar preço antes de formatar
    const precoNumerico = parseFloat(peca.preco) || 0;
    const preco = precoNumerico.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Determinar se é nova ou usada
    const condicao = peca.estado && peca.estado.toLowerCase() === 'usado' ? 'used' : 'new';
    const tagTexto = condicao === 'new' ? 'Novo' : 'Usado';
    const tagClass = condicao === 'new' ? 'new-tag' : 'used-tag';
    
    // Marca/Fabricante
    const marca = peca.marca || peca.fabricante || 'Genérico';
    
    // ✅ Adicionar data-categoria ao card
    const categoria = peca.categoria || 'outros';
    
    return `
        <div class="part-card" 
             data-condition="${condicao}" 
             data-id="${peca.id}"
             data-categoria="${categoria}">
            <div class="part-image">
                <img src="${imagemSrc}" 
                     alt="${peca.nome}"
                     onerror="this.src='/static/images/default-part.jpg'">
                <span class="tag ${tagClass}">${tagTexto}</span>
            </div>
            <div class="part-info">
                <span class="brand">${marca}</span>
                <h3>${peca.nome}</h3>
                <p class="part-price">R$ ${preco}</p>
                <button class="add-to-cart" data-id="${peca.id}" data-nome="${peca.nome}" data-preco="${peca.preco}">
                    <i class="fas fa-cart-plus"></i> Adicionar
                </button>
            </div>
        </div>
    `;
}

// ==========================================
// ADICIONAR AO CARRINHO
// ==========================================

function adicionarEventListenersCarrinho() {
    const botoes = document.querySelectorAll('.add-to-cart');
    
    botoes.forEach(botao => {
        botao.addEventListener('click', async function() {
            const pecaId = this.getAttribute('data-id');
            const pecaNome = this.getAttribute('data-nome');
            
            // ✅ CORREÇÃO: Verificar autenticação antes de adicionar
            // Tentar ambos os nomes de token para compatibilidade
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            
            if (!token) {
                mostrarNotificacao('Você precisa estar logado para adicionar ao carrinho', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=/pecas_pg';
                }, 1500);
                return;
            }
            
            await adicionarAoCarrinho(pecaId, pecaNome);
        });
    });
}

async function adicionarAoCarrinho(pecaId, pecaNome) {
    console.log(`🛒 Adicionando peça ${pecaId} ao carrinho`);
    
    // ✅ CORREÇÃO: Buscar token com ambos os nomes
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token) {
        console.error('❌ Token não encontrado');
        mostrarNotificacao('Você precisa estar logado', 'warning');
        setTimeout(() => {
            window.location.href = '/login?redirect=/pecas_pg';
        }, 1500);
        return;
    }
    
    console.log('🔑 Token encontrado:', token.substring(0, 20) + '...');
    
    try {
        const response = await fetch('/api/carrinho/adicionar', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tipo_item: 'peca',
                item_id: parseInt(pecaId),
                quantidade: 1
            })
        });
        
        console.log('📊 Status da resposta:', response.status);
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('❌ Token inválido ou expirado');
                localStorage.removeItem('access_token');
                localStorage.removeItem('token');
                mostrarNotificacao('Sua sessão expirou. Faça login novamente.', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=/pecas_pg';
                }, 1500);
                return;
            }
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Peça adicionada ao carrinho:', result);
        
        // Atualizar badge do carrinho
        if (result.total_itens !== undefined) {
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.textContent = result.total_itens;
                // Animar badge
                badge.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    badge.style.transform = 'scale(1)';
                }, 300);
            }
        }
        
        mostrarNotificacao(`${pecaNome} adicionado ao carrinho!`, 'success');
        
    } catch (error) {
        console.error('❌ Erro ao adicionar ao carrinho:', error);
        mostrarNotificacao('Erro ao adicionar ao carrinho', 'error');
    }
}

// ==========================================
// FILTROS DE CONDIÇÃO (NOVO/USADO)
// ==========================================

// ✅ CORREÇÃO: Adicionar parâmetro event
function filterCondition(tipo, event) {
    console.log('🔎 Filtro aplicado:', tipo);
    filtroAtual = tipo;
    
    // Atualizar botões ativos
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // ✅ CORREÇÃO: event agora é um parâmetro
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // ✅ Usar todasPecas para filtrar
    aplicarFiltros();
}

// Tornar função global
window.filterCondition = filterCondition;

// ==========================================
// FILTRO POR CATEGORIA
// ==========================================

// ✅ CORREÇÃO: Implementação completa do filtro de categoria
function filtrarPorCategoria(event) {
    const categoriaElement = event.target.closest('[data-categoria]');
    const categoria = categoriaElement ? categoriaElement.getAttribute('data-categoria') : 'all';
    
    console.log('📂 Filtro de categoria:', categoria);
    categoriaAtual = categoria;
    
    // Atualizar botões ativos
    document.querySelectorAll('.cat-link').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // ✅ CORREÇÃO: event agora é um parâmetro
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // ✅ Aplicar filtros combinados
    aplicarFiltros();
}

// ==========================================
// APLICAR FILTROS COMBINADOS
// ==========================================

// ✅ NOVA FUNÇÃO: Aplica filtros de condição e categoria juntos
function aplicarFiltros() {
    let pecasFiltradas = todasPecas;
    
    // Filtrar por condição (novo/usado)
    if (filtroAtual === 'new') {
        pecasFiltradas = pecasFiltradas.filter(p => 
            !p.estado || p.estado.toLowerCase() !== 'usado'
        );
    } else if (filtroAtual === 'used') {
        pecasFiltradas = pecasFiltradas.filter(p => 
            p.estado && p.estado.toLowerCase() === 'usado'
        );
    }
    
    // Filtrar por categoria
    if (categoriaAtual && categoriaAtual !== 'all') {
        pecasFiltradas = pecasFiltradas.filter(p => 
            p.categoria === categoriaAtual
        );
    }
    
    // Renderizar peças filtradas
    renderizarPecas(pecasFiltradas);
    
    console.log(`🔍 Filtros aplicados: ${pecasFiltradas.length} peças encontradas`);
}

// ==========================================
// MOSTRAR MENSAGEM QUANDO NÃO HÁ PEÇAS
// ==========================================

function mostrarMensagemVazia() {
    const container = document.querySelector('.parts-grid');
    
    if (container) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-tools" style="font-size: 80px; color: #ddd; margin-bottom: 20px;"></i>
                <h3 style="color: #666; margin-bottom: 10px;">Nenhuma peça disponível</h3>
                <p style="color: #999;">Novos produtos em breve!</p>
            </div>
        `;
    }
}

// ==========================================
// MOSTRAR ERRO DE CARREGAMENTO
// ==========================================

function mostrarErroCarregamento() {
    const container = document.querySelector('.parts-grid');
    
    if (container) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 80px; color: #ff6b6b; margin-bottom: 20px;"></i>
                <h3 style="color: #666; margin-bottom: 10px;">Erro ao carregar peças</h3>
                <p style="color: #999; margin-bottom: 30px;">Tente novamente mais tarde</p>
                <button onclick="carregarPecas()" class="btn" style="padding: 12px 30px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; border: none; border-radius: 8px; cursor: pointer;">
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
    // Remover notificação anterior se existir
    const notifAnterior = document.querySelector('.notificacao-toast');
    if (notifAnterior) {
        notifAnterior.remove();
    }
    
    // Criar nova notificação
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao-toast notificacao-${tipo}`;
    
    const icone = tipo === 'success' ? 'check-circle' : 
                  tipo === 'error' ? 'times-circle' :
                  tipo === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    notificacao.innerHTML = `
        <i class="fas fa-${icone}"></i>
        <span>${mensagem}</span>
    `;
    
    // Estilos inline
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
    
    // Animar entrada
    setTimeout(() => {
        notificacao.style.opacity = '1';
        notificacao.style.transform = 'translateX(0)';
    }, 10);
    
    // Remover após 3 segundos
    setTimeout(() => {
        notificacao.style.opacity = '0';
        notificacao.style.transform = 'translateX(100%)';
        setTimeout(() => notificacao.remove(), 300);
    }, 3000);
}

// ==========================================
// ✅ INICIALIZAÇÃO - CONSOLIDADO EM UM ÚNICO LISTENER
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Página de peças carregada');
    
    // Inicializar event listeners de categoria
    const catLinks = document.querySelectorAll('.cat-link');
    catLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            filtrarPorCategoria(e);
        });
    });
    
    // Carregar peças da API
    carregarPecas();
});

// ==========================================
// ADICIONAR CSS PARA SPINNER
// ==========================================

const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log('✅ pecas.js carregado com sucesso!');