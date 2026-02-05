/**
 * ✅ VEICULOS.JS - Carregamento dinâmico de veículos da API
 */

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
        const response = await fetch('/api/veiculos');
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const veiculos = await response.json();
        console.log('✅ Veículos carregados:', veiculos);
        
        if (!veiculos || veiculos.length === 0) {
            mostrarMensagemVazia();
            return;
        }
        
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
    
    const veiculosHTML = veiculos.map(veiculo => criarVeiculoCard(veiculo)).join('');
    container.innerHTML = veiculosHTML;
    
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
    
    // Formatar preço
    const preco = parseFloat(veiculo.preco).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Determinar status
    let statusTag = '';
    let statusStyle = '';
    
    if (veiculo.disponivel === false || veiculo.status === 'vendido') {
        statusTag = 'Vendido';
        statusStyle = 'background: #95a5a6; color: #fff;';
    } else if (veiculo.status === 'reservado') {
        statusTag = 'Reservado';
        statusStyle = 'background: #ffcc00; color: #000;';
    } else {
        statusTag = 'Disponível';
        statusStyle = 'background: #27ae60; color: #fff;';
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
                <a href="/veiculo/${veiculo.id}" class="btn-view">Ver Detalhes</a>
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
// FILTROS E BUSCA
// ==========================================

// Função de busca
function buscarVeiculos(termo) {
    console.log('🔍 Buscando:', termo);
    // TODO: Implementar busca no backend
}

// Adicionar event listener para busca
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const termo = this.value.toLowerCase();
            const cards = document.querySelectorAll('.vehicle-card');
            
            cards.forEach(card => {
                const texto = card.textContent.toLowerCase();
                if (texto.includes(termo)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Selects de filtro
    const selects = document.querySelectorAll('.filter-options select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            console.log('Filtro alterado:', this.value);
            // TODO: Implementar filtros no backend
        });
    });
});

// ==========================================
// INICIALIZAR QUANDO A PÁGINA CARREGAR
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Página de veículos carregada');
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