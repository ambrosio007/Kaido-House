/**
 * ✅ CARD.JS CORRIGIDO - Carrega e exibe cards de peças e veículos
 */

// Função principal que carrega os dados da vitrine
async function carregarVitrine() {
    console.log('🔄 Iniciando carregamento da vitrine...');
    
    try {
        // Buscar dados do backend
        const response = await fetch('/api/vitrine-completa');
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados recebidos:', data);
        
        // Renderizar cada seção
        renderizarSecao(data.pecas_novas, 'pecas-novas', 'peca');
        renderizarSecao(data.pecas_usadas, 'pecas-usadas', 'peca');
        renderizarSecao(data.carros_novos, 'carros-novos', 'veiculo');
        renderizarSecao(data.carros_usados, 'carros-usados', 'veiculo');
        
        // Inicializar Swipers após renderizar tudo
        setTimeout(() => {
            inicializarSwipers();
        }, 100);
        
    } catch (error) {
        console.error('❌ Erro ao carregar vitrine:', error);
        
        // Exibir mensagem de erro amigável
        mostrarErroCarregamento();
    }
}

// Função que renderiza uma seção específica
function renderizarSecao(lista, idSecao, tipo) {
    console.log(`📦 Renderizando seção: ${idSecao}, Total de itens: ${lista?.length || 0}`);
    
    // IDs corretos baseados no HTML
    const container = document.getElementById(`container-${idSecao}`);
    const section = document.getElementById(idSecao);
    
    // Verificar se os elementos existem
    if (!container) {
        console.error(`❌ Container não encontrado: container-${idSecao}`);
        return;
    }
    
    if (!section) {
        console.warn(`⚠️ Section não encontrada: ${idSecao} (continuando...)`);
    }
    
    // Se não houver itens, esconder a seção
    if (!lista || lista.length === 0) {
        console.log(`ℹ️ Nenhum item na seção: ${idSecao}`);
        if (section) {
            section.classList.add('hidden');
        }
        container.innerHTML = '<p style="text-align: center; padding: 20px;">Nenhum item disponível no momento.</p>';
        return;
    }
    
    // Mostrar a seção
    if (section) {
        section.classList.remove('hidden');
    }
    
    // Renderizar os cards
    const cardsHTML = lista.map(item => criarCard(item, tipo)).join('');
    container.innerHTML = cardsHTML;
    
    console.log(`✅ Seção ${idSecao} renderizada com ${lista.length} itens`);
}

// Função que cria o HTML de um card
function criarCard(item, tipo) {
    // Processar fotos
    let imagemSrc = '/static/img/default-placeholder.jpg';
    
    if (item.fotos) {
        const fotos = item.fotos.split(',').map(f => f.trim()).filter(f => f);
        if (fotos.length > 0) {
            imagemSrc = fotos[0];
        }
    }
    
    // Nome do item
    const nome = tipo === 'peca' 
        ? item.nome 
        : `${item.marca} ${item.modelo}`;
    
    // Preço formatado
    const preco = parseFloat(item.preco).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Badge de estado (novo/usado)
    const badgeEstado = item.estado === 'novo' || (item.km && item.km < 100)
        ? '<span class="badge-novo">NOVO</span>'
        : '';
    
    // Informações extras
    let infoExtra = '';
    if (tipo === 'veiculo') {
        infoExtra = `
            <p class="card-info">
                <i class="fas fa-calendar"></i> ${item.ano || 'N/A'}
                <i class="fas fa-tachometer-alt"></i> ${item.km ? item.km.toLocaleString('pt-BR') : 'N/A'} km
            </p>
        `;
    } else {
        infoExtra = `
            <p class="card-info">
                <i class="fas fa-tag"></i> ${item.categoria || 'N/A'}
                <i class="fas fa-box"></i> ${item.estado || 'N/A'}
            </p>
        `;
    }
    
    return `
        <div class="swiper-slide">
            <div class="product-card" data-id="${item.id}" data-tipo="${tipo}">
                <div class="card-image">
                    <img src="${imagemSrc}" 
                         alt="${nome}"
                         onerror="this.src='/static/img/default-placeholder.jpg'">
                    ${badgeEstado}
                </div>
                <div class="card-content">
                    <h3 class="card-title">${nome}</h3>
                    ${infoExtra}
                    <p class="card-price">R$ ${preco}</p>
                    <div class="card-actions">
                        <a href="/${tipo}/${item.id}" class="btn-ver-detalhes">
                            <i class="fas fa-eye"></i> Ver Detalhes
                        </a>
                        <button class="btn-add-carrinho" onclick="adicionarAoCarrinho('${item.id}', '${tipo}')">
                            <i class="fas fa-shopping-cart"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Função para inicializar os Swipers
function inicializarSwipers() {
    console.log('🎠 Inicializando carrosséis Swiper...');
    
    const swiperConfig = {
        slidesPerView: 1,
        spaceBetween: 20,
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            640: {
                slidesPerView: 2,
                spaceBetween: 20,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 30,
            },
            1024: {
                slidesPerView: 4,
                spaceBetween: 30,
            },
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    };
    
    // Inicializar cada carrossel
    const carrosseis = document.querySelectorAll('.card-slider');
    
    carrosseis.forEach((carrossel, index) => {
        try {
            new Swiper(carrossel, swiperConfig);
            console.log(`✅ Carrossel ${index + 1} inicializado`);
        } catch (error) {
            console.error(`❌ Erro ao inicializar carrossel ${index + 1}:`, error);
        }
    });
}

// Função para adicionar item ao carrinho
// ==========================================
// ADICIONAR AO CARRINHO - VERSÃO CORRIGIDA
// ==========================================

async function adicionarAoCarrinho(itemId, tipo) {
    console.log(`🛒 Tentando adicionar ao carrinho: ${tipo} ${itemId}`);
    
    // ✅ PASSO 1: Verificar se tem token
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        console.warn('⚠️ Token não encontrado no localStorage');
        mostrarNotificacao('Você precisa estar logado para adicionar itens ao carrinho!', 'warning');
        setTimeout(() => {
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        }, 1500);
        return;
    }
    
    console.log('✅ Token encontrado:', token.substring(0, 20) + '...');
    
    // ✅ PASSO 2: Verificar se token está expirado (opcional mas recomendado)
    if (isTokenExpired(token)) {
        console.warn('⚠️ Token expirado');
        localStorage.removeItem('access_token');
        mostrarNotificacao('Sua sessão expirou. Faça login novamente.', 'error');
        setTimeout(() => {
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        }, 1500);
        return;
    }
    
    try {
        console.log('📤 Enviando requisição para /api/carrinho/adicionar...');
        
        const response = await fetch('/api/carrinho/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`  // ✅ Formato correto
            },
            body: JSON.stringify({
                tipo_item: tipo,
                item_id: itemId,
                quantidade: 1
            })
        });
        
        console.log(`📥 Resposta recebida: Status ${response.status} ${response.statusText}`);
        
        // ✅ PASSO 3: Verificar o Content-Type ANTES de fazer parse
        const contentType = response.headers.get('content-type');
        console.log('📋 Content-Type:', contentType);
        
        let result;
        
        if (contentType && contentType.includes('application/json')) {
            result = await response.json();
            console.log('📦 Dados da resposta:', result);
        } else {
            // Se não for JSON, pode ser HTML de redirect
            const text = await response.text();
            console.error('❌ Resposta não é JSON. Recebido:', text.substring(0, 200));
            
            if (response.status === 401) {
                console.error('❌ Erro 401: Não autorizado');
                localStorage.removeItem('access_token');
                mostrarNotificacao('Sessão inválida. Redirecionando para o login...', 'error');
                setTimeout(() => {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                }, 1500);
                return;
            }
            
            throw new Error('Resposta inválida do servidor');
        }
        
        // ✅ PASSO 4: Processar resposta de sucesso
        if (response.ok) {
            console.log('✅ Item adicionado com sucesso!');
            
            // Atualizar badge do carrinho
            if (result.total_itens !== undefined) {
                const badge = document.querySelector('.cart-badge');
                if (badge) {
                    badge.textContent = result.total_itens;
                    
                    // Animação de destaque
                    badge.style.transform = 'scale(1.3)';
                    badge.style.transition = 'transform 0.3s';
                    setTimeout(() => {
                        badge.style.transform = 'scale(1)';
                    }, 300);
                }
            }
            
            // Feedback visual
            mostrarNotificacao('✅ Item adicionado ao carrinho!', 'success');
            
        } else {
            // ✅ PASSO 5: Tratar erros específicos
            console.error('❌ Erro na requisição:', result);
            
            // Tratamento por código de erro
            if (result.code === 'EXPIRED_TOKEN' || result.code === 'INVALID_TOKEN') {
                console.error('❌ Token expirado ou inválido');
                localStorage.removeItem('access_token');
                mostrarNotificacao('Sessão expirada. Redirecionando...', 'error');
                setTimeout(() => {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                }, 1500);
            } else if (result.code === 'NO_TOKEN') {
                console.error('❌ Token não enviado');
                mostrarNotificacao('Você precisa estar logado!', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                }, 1500);
            } else {
                // Outros erros
                mostrarNotificacao(result.error || result.message || 'Erro ao adicionar item', 'error');
            }
        }
        
    } catch (error) {
        console.error('❌ Erro na requisição:', error);
        mostrarNotificacao('Erro ao adicionar item ao carrinho. Tente novamente.', 'error');
    }
}

// ==========================================
// FUNÇÃO AUXILIAR: Verificar se token está expirado
// ==========================================

function isTokenExpired(token) {
    try {
        // Decodificar o payload do JWT (parte do meio)
        const payload = JSON.parse(atob(token.split('.')[1]));
        
        // Verificar se tem campo 'exp' (expiration)
        if (!payload.exp) {
            console.warn('⚠️ Token não tem campo de expiração');
            return false;
        }
        
        // Comparar com o tempo atual
        const expirationTime = payload.exp * 1000; // Converter para milissegundos
        const now = Date.now();
        
        const isExpired = now >= expirationTime;
        
        if (isExpired) {
            console.warn('⏰ Token expirado!');
            console.warn(`   Expirou em: ${new Date(expirationTime).toLocaleString()}`);
            console.warn(`   Agora: ${new Date(now).toLocaleString()}`);
        }
        
        return isExpired;
        
    } catch (error) {
        console.error('❌ Erro ao validar token:', error);
        return true; // Se não conseguir validar, considerar expirado
    }
}

// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo = 'info') {
    // Remover notificação anterior se existir
    const notifAnterior = document.querySelector('.notificacao-toast');
    if (notifAnterior) {
        notifAnterior.remove();
    }
    
    // Criar nova notificação
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao-toast notificacao-${tipo}`;
    notificacao.innerHTML = `
        <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${mensagem}</span>
    `;
    
    document.body.appendChild(notificacao);
    
    // Animar entrada
    setTimeout(() => notificacao.classList.add('show'), 10);
    
    // Remover após 3 segundos
    setTimeout(() => {
        notificacao.classList.remove('show');
        setTimeout(() => notificacao.remove(), 300);
    }, 3000);
}

// Função para mostrar erro de carregamento
function mostrarErroCarregamento() {
    const secoes = ['pecas-novas', 'pecas-usadas', 'carros-novos', 'carros-usados'];
    
    secoes.forEach(secaoId => {
        const container = document.getElementById(`container-${secaoId}`);
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #ff6b6b; margin-bottom: 20px;"></i>
                    <p style="color: #666;">Erro ao carregar itens. Tente novamente mais tarde.</p>
                    <button onclick="carregarVitrine()" style="margin-top: 20px; padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        <i class="fas fa-redo"></i> Tentar Novamente
                    </button>
                </div>
            `;
        }
    });
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM carregado, iniciando aplicação...');
    carregarVitrine();
});

// Log para debug
console.log('✅ card.js carregado com sucesso!');

// ==========================================
// VERIFICAR TOKEN AO CARREGAR A PÁGINA
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Verificando autenticação...');
    
    const token = localStorage.getItem('access_token');
    
    if (token) {
        console.log('✅ Token encontrado');
        
        // Verificar se está expirado
        if (isTokenExpired(token)) {
            console.warn('⚠️ Token expirado - removendo');
            localStorage.removeItem('access_token');
            
            // Atualizar UI para estado deslogado
            const loginState = document.querySelector('.login-state');
            const profileState = document.querySelector('.profile-state');
            
            if (loginState) loginState.classList.remove('hidden');
            if (profileState) profileState.classList.add('hidden');
            
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.textContent = '0';
        } else {
            console.log('✅ Token válido');
            
            // Atualizar badge do carrinho
            atualizarBadgeCarrinho();
        }
    } else {
        console.log('ℹ️ Usuário não autenticado');
    }
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
        } else if (response.status === 401) {
            // Token inválido
            console.warn('⚠️ Token inválido ao buscar total do carrinho');
            localStorage.removeItem('access_token');
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.textContent = '0';
        }
    } catch (error) {
        console.error('❌ Erro ao atualizar badge:', error);
    }
}