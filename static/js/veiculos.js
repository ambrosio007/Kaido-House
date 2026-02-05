/**
 * ✅ VEICULOS.JS - Carregamento dinâmico de veículos da API
 * 🔧 VERSÃO CORRIGIDA - Carrega veículos do banco de dados
 */

// ==========================================
// VARIÁVEIS GLOBAIS
// ==========================================

let todosVeiculos = []; // Armazena todos os veículos carregados

// ==========================================
// CARREGAR VEÍCULOS DA API
// ==========================================

async function carregarVeiculos() {
    console.log('🚗 Carregando veículos da API...');
    
    const container = document.querySelector('.vehicles-grid');
    
    if (!container) {
        console.error('❌ Container .vehicles-grid não encontrado');
        return;
    }
    
    // Mostrar loading
    container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
            <div class="loading-spinner" style="margin: 0 auto 20px; border: 4px solid #f3f3f3; border-top: 4px solid #e74c3c; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite;"></div>
            <p style="color: #999;">Carregando veículos...</p>
        </div>
    `;
    
    try {
        // ✅ Endpoint correto
        const response = await fetch('/veiculos');
        
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
            throw new Error('Resposta do servidor não é JSON - verifique se o endpoint /veiculos está retornando JSON');
        }
        
        const veiculos = await response.json();
        console.log('✅ Veículos carregados:', veiculos);
        
        if (!veiculos || veiculos.length === 0) {
            mostrarMensagemVazia();
            return;
        }
        
        // Armazenar veículos globalmente
        todosVeiculos = veiculos;
        
        // Renderizar veículos
        renderizarVeiculos(veiculos);
        
    } catch (error) {
        console.error('❌ Erro ao carregar veículos:', error);
        mostrarErroCarregamento();
    }
}

// ==========================================
// RENDERIZAR VEÍCULOS
// ==========================================

function renderizarVeiculos(veiculos) {
    const container = document.querySelector('.vehicles-grid');
    
    if (!container) return;
    
    if (!veiculos || veiculos.length === 0) {
        mostrarMensagemVazia();
        return;
    }
    
    const veiculosHTML = veiculos.map(veiculo => criarVeiculoCard(veiculo)).join('');
    container.innerHTML = veiculosHTML;
    
    // ✅ ADICIONADO: Event listeners para adicionar ao carrinho
    adicionarEventListenersCarrinho();
    
    console.log(`✅ ${veiculos.length} veículos renderizados`);
}

// ==========================================
// CRIAR CARD DE VEÍCULO
// ==========================================

function criarVeiculoCard(veiculo) {
    // Processar imagem
    let imagemSrc = '/static/images/default-vehicle.jpg';
    
    if (veiculo.fotos) {
        const fotos = veiculo.fotos.split(',').map(f => f.trim()).filter(f => f);
        if (fotos.length > 0) {
            imagemSrc = fotos[0];
        }
    }
    
    // ✅ Validar preço antes de formatar
    const precoNumerico = parseFloat(veiculo.preco) || 0;
    const preco = precoNumerico.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Determinar status
    let statusTag = '';
    let statusStyle = '';
    let botoesAcao = '';
    
    if (veiculo.disponivel === false || veiculo.status === 'vendido') {
        statusTag = 'Vendido';
        statusStyle = 'background: #95a5a6; color: #fff;';
        botoesAcao = `<a href="/veiculo/${veiculo.id}" class="btn-view">Ver Detalhes</a>`;
    } else if (veiculo.status === 'reservado') {
        statusTag = 'Reservado';
        statusStyle = 'background: #ffcc00; color: #000;';
        botoesAcao = `<a href="/veiculo/${veiculo.id}" class="btn-view">Ver Detalhes</a>`;
    } else {
        statusTag = 'Disponível';
        statusStyle = 'background: #27ae60; color: #fff;';
        // ✅ ADICIONADO: Botões para veículos disponíveis
        botoesAcao = `
            <div style="display: flex; gap: 8px; width: 100%;">
                <button class="add-to-cart-vehicle" 
                        data-id="${veiculo.id}" 
                        data-nome="${veiculo.marca} ${veiculo.modelo}"
                        data-preco="${veiculo.preco}"
                        style="flex: 1; padding: 12px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: transform 0.2s;">
                    <i class="fas fa-cart-plus"></i> Adicionar
                </button>
                <a href="/veiculo/${veiculo.id}" 
                   class="btn-view" 
                   style="flex: 1; text-align: center;">
                    Ver Detalhes
                </a>
            </div>
        `;
    }
    
    // Nome completo do veículo
    const nomeCompleto = `${veiculo.marca || ''} ${veiculo.modelo || ''} ${veiculo.versao || ''}`.trim();
    
    // Categoria (ex: "Coupe / Turbo")
    const categoria = veiculo.tipo || 'Esportivo';
    
    // Quilometragem formatada
    const km = veiculo.km ? parseInt(veiculo.km).toLocaleString('pt-BR') : '0';
    
    return `
        <div class="vehicle-card" data-id="${veiculo.id}">
            <div class="card-image">
                <img src="${imagemSrc}" 
                     alt="${nomeCompleto}"
                     onerror="this.src='/static/images/default-vehicle.jpg'">
                <span class="status-tag" style="${statusStyle}">${statusTag}</span>
            </div>
            <div class="card-content">
                <span class="category">${categoria}</span>
                <h3>${nomeCompleto}</h3>
                <div class="specs">
                    <span><i class="fas fa-calendar-alt"></i> ${veiculo.ano || 'N/A'}</span>
                    <span><i class="fas fa-tachometer-alt"></i> ${km}km</span>
                </div>
                <p class="price">R$ ${preco}</p>
                ${botoesAcao}
            </div>
        </div>
    `;
}

// ==========================================
// MOSTRAR MENSAGEM QUANDO NÃO HÁ VEÍCULOS
// ==========================================

function mostrarMensagemVazia() {
    const container = document.querySelector('.vehicles-grid');
    
    if (container) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-car" style="font-size: 80px; color: #ddd; margin-bottom: 20px;"></i>
                <h3 style="color: #666; margin-bottom: 10px;">Nenhum veículo disponível</h3>
                <p style="color: #999;">Novos veículos em breve!</p>
            </div>
        `;
    }
}

// ==========================================
// MOSTRAR ERRO DE CARREGAMENTO
// ==========================================

function mostrarErroCarregamento() {
    const container = document.querySelector('.vehicles-grid');
    
    if (container) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 80px; color: #ff6b6b; margin-bottom: 20px;"></i>
                <h3 style="color: #666; margin-bottom: 10px;">Erro ao carregar veículos</h3>
                <p style="color: #999; margin-bottom: 30px;">Tente novamente mais tarde</p>
                <button onclick="carregarVeiculos()" class="btn-view" style="padding: 12px 30px; cursor: pointer;">
                    <i class="fas fa-redo"></i> Tentar Novamente
                </button>
            </div>
        `;
    }
}

// ==========================================
// ADICIONAR AO CARRINHO
// ==========================================

function adicionarEventListenersCarrinho() {
    const botoes = document.querySelectorAll('.add-to-cart-vehicle');
    
    botoes.forEach(botao => {
        // Adicionar efeito hover
        botao.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        botao.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Click para adicionar
        botao.addEventListener('click', async function() {
            const veiculoId = this.getAttribute('data-id');
            const veiculoNome = this.getAttribute('data-nome');
            
            // ✅ CORREÇÃO: Verificar autenticação antes de adicionar
            // Tentar ambos os nomes de token para compatibilidade
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            
            if (!token) {
                mostrarNotificacao('Você precisa estar logado para adicionar ao carrinho', 'warning');
                setTimeout(() => {
                    window.location.href = '/login?redirect=/veiculos_pg';
                }, 1500);
                return;
            }
            
            await adicionarAoCarrinho(veiculoId, veiculoNome);
        });
    });
}

async function adicionarAoCarrinho(veiculoId, veiculoNome) {
    console.log(`🛒 Adicionando veículo ${veiculoId} ao carrinho`);
    
    // ✅ CORREÇÃO: Buscar token com ambos os nomes
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token) {
        console.error('❌ Token não encontrado');
        mostrarNotificacao('Você precisa estar logado', 'warning');
        setTimeout(() => {
            window.location.href = '/login?redirect=/veiculos_pg';
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
                tipo_item: 'veiculo',
                item_id: parseInt(veiculoId),
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
                    window.location.href = '/login?redirect=/veiculos_pg';
                }, 1500);
                return;
            }
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Veículo adicionado ao carrinho:', result);
        
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
        
        mostrarNotificacao(`${veiculoNome} adicionado ao carrinho!`, 'success');
        
    } catch (error) {
        console.error('❌ Erro ao adicionar ao carrinho:', error);
        mostrarNotificacao('Erro ao adicionar ao carrinho', 'error');
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
// FILTROS E BUSCA
// ==========================================

// ✅ Função de busca aprimorada
function buscarVeiculos(termo) {
    console.log('🔍 Buscando:', termo);
    
    if (!termo) {
        renderizarVeiculos(todosVeiculos);
        return;
    }
    
    const termoLower = termo.toLowerCase();
    const veiculosFiltrados = todosVeiculos.filter(veiculo => {
        const nomeCompleto = `${veiculo.marca} ${veiculo.modelo} ${veiculo.versao}`.toLowerCase();
        return nomeCompleto.includes(termoLower);
    });
    
    renderizarVeiculos(veiculosFiltrados);
    console.log(`🔍 ${veiculosFiltrados.length} veículos encontrados`);
}

// ✅ Aplicar filtros (ano, ordenação, etc)
function aplicarFiltros() {
    const selects = document.querySelectorAll('.filter-options select');
    let veiculosFiltrados = [...todosVeiculos];
    
    selects.forEach(select => {
        const valor = select.value;
        
        if (!valor) return;
        
        // Filtro por ano
        if (valor === '90') {
            veiculosFiltrados = veiculosFiltrados.filter(v => {
                const ano = parseInt(v.ano);
                return ano >= 1990 && ano < 2000;
            });
        } else if (valor === '00') {
            veiculosFiltrados = veiculosFiltrados.filter(v => {
                const ano = parseInt(v.ano);
                return ano >= 2000 && ano < 2010;
            });
        }
        
        // Ordenação
        if (valor === 'menor-preco') {
            veiculosFiltrados.sort((a, b) => parseFloat(a.preco) - parseFloat(b.preco));
        } else if (valor === 'maior-preco') {
            veiculosFiltrados.sort((a, b) => parseFloat(b.preco) - parseFloat(a.preco));
        }
    });
    
    renderizarVeiculos(veiculosFiltrados);
}

// ==========================================
// INICIALIZAR QUANDO A PÁGINA CARREGAR
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Página de veículos carregada');
    
    // Busca
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            buscarVeiculos(this.value);
        });
    }
    
    // Selects de filtro
    const selects = document.querySelectorAll('.filter-options select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            console.log('Filtro alterado:', this.value);
            aplicarFiltros();
        });
    });
    
    // Carregar veículos da API
    carregarVeiculos();
});

// Adicionar CSS para spinner
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log('✅ veiculos.js carregado com sucesso!');