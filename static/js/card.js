async function carregarVitrine() {
    const response = await fetch('/api/home/vitrine');
    const data = await response.json();

    renderizarSecao(data.pecas_novas, 'pecas-novas', 'peca');
    renderizarSecao(data.pecas_usadas, 'pecas-usadas', 'peca');
    renderizarSecao(data.carros_novos, 'carros-novos', 'veiculo');
    renderizarSecao(data.carros_usados, 'carros-usados', 'veiculo');
}

function renderizarSecao(lista, sufixo, tipo) {
    const container = document.getElementById(`container-${sufixo}`);
    const section = document.getElementById(`section-${sufixo}`);

    if (lista && lista.length > 0) {
        section.classList.remove('hidden'); // Mostra a seção
        
        container.innerHTML = lista.map(item => `
            <div class="swiper-slide">
                <div class="product-card">
                    <div class="card-image">
                        <img src="${item.fotos || 'default.jpg'}" alt="${item.nome || item.modelo}">
                        ${item.estado === 'novo' ? '<span class="discount-tag">NOVO</span>' : ''}
                    </div>
                    <div class="card-content">
                        <h3>${item.nome || (item.marca + ' ' + item.modelo)}</h3>
                        <p class="price">R$ ${parseFloat(item.preco).toLocaleString('pt-BR')}</p>
                        <a href="/detalhes/${tipo}/${item.id}" class="btn-card">Ver Detalhes</a>
                    </div>
                </div>
            </div>
        `).join('');

        // Inicializa o Swiper para esta seção específica
        new Swiper(`.card-slider`, { /* suas configs de swiper */ });
    }
}

document.addEventListener('DOMContentLoaded', carregarVitrine);

async function carregarHome() {
    const response = await fetch('/api/vitrine-home');
    const data = await response.json();

    // Mapeamento: [Lista de Dados, ID do Container no HTML, Tipo do Item]
    const secoes = [
        [data.pecas_novas, 'pecas-novas', 'peca'],
        [data.pecas_usadas, 'pecas-usadas', 'peca'],
        [data.carros_novos, 'carros-novos', 'veiculo'],
        [data.carros_usados, 'carros-usados', 'veiculo']
    ];

    secoes.forEach(([lista, id, tipo]) => {
        const wrapper = document.getElementById(`container-${id}`);
        const section = document.getElementById(`section-${id}`);

        if (lista && lista.length > 0) {
            section.classList.remove('hidden'); // Mostra a seção se tiver pelo menos 1
            
            wrapper.innerHTML = lista.map(item => `
                <div class="swiper-slide">
                    <div class="${tipo === 'peca' ? 'product-card' : 'vehicle-card'}">
                        <div class="card-image">
                            <img src="${item.fotos.split(',')[0] || '/static/img/default.png'}" alt="Item">
                        </div>
                        <div class="card-content">
                            <h3>${item.nome || (item.marca + ' ' + item.modelo)}</h3>
                            <p class="price">R$ ${parseFloat(item.preco).toLocaleString('pt-BR')}</p>
                            <a href="/detalhes/${tipo}/${item.id}" class="btn-card">Ver Detalhes</a>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            section.classList.add('hidden'); // Esconde se estiver vazio
        }
    });

    // Inicializa o Swiper após carregar os cards
    inicializarSwipers();
}