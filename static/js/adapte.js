function preencherDados(item, tipo) {
    document.getElementById('product-title').innerText = item.nome || `${item.marca} ${item.modelo}`;
    document.getElementById('product-price').innerText = parseFloat(item.preco).toLocaleString('pt-BR');
    
    const specsGrid = document.getElementById('specs-grid');
    specsGrid.innerHTML = ''; // Limpa

    if (tipo === 'veiculo') {
        specsGrid.innerHTML = `
            <div class="spec-item"><label>Ano</label><span>${item.ano}</span></div>
            <div class="spec-item"><label>KM</label><span>${item.km}</span></div>
            <div class="spec-item"><label>Câmbio</label><span>${item.cambio}</span></div>
            <div class="spec-item"><label>Cor</label><span>${item.cor}</span></div>
        `;
        document.getElementById('breadcrumb-category').innerText = "Veículos";
    } else {
        specsGrid.innerHTML = `
            <div class="spec-item"><label>Marca</label><span>${item.marca}</span></div>
            <div class="spec-item"><label>Modelo</label><span>${item.modelo_carro}</span></div>
            <div class="spec-item"><label>Categoria</label><span>${item.categoria}</span></div>
        `;
        document.getElementById('breadcrumb-category').innerText = "Peças";
    }
}