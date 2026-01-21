// Elementos do DOM
const btnCadastrarVenda = document.getElementById('btnCadastrarVenda');
const modal = document.getElementById('modalCadastro');
const closeModal = document.querySelector('.close');
const btnsTipo = document.querySelectorAll('.btn-tipo');
const formVeiculo = document.getElementById('formVeiculo');
const formPeca = document.getElementById('formPeca');

// Abrir modal
btnCadastrarVenda.onclick = () => {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden'; // Previne scroll do body
};

// Fechar modal
closeModal.onclick = () => {
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
};

// Fechar modal ao clicar fora
window.onclick = (event) => {
    if (event.target === modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
};

// Trocar entre Veículo e Peça
btnsTipo.forEach(btn => {
    btn.onclick = () => {
        // Remove active de todos
        btnsTipo.forEach(b => b.classList.remove('active'));
        
        // Adiciona active no clicado
        btn.classList.add('active');
        
        // Pega o tipo (veiculo ou peca)
        const tipo = btn.dataset.tipo;
        
        // Mostra/esconde formulários
        if (tipo === 'veiculo') {
            formVeiculo.classList.add('active');
            formPeca.classList.remove('active');
        } else {
            formPeca.classList.add('active');
            formVeiculo.classList.remove('active');
        }
    };
});

// Submit do formulário de veículo
formVeiculo.onsubmit = (e) => {
    e.preventDefault();
    
    const dados = {
        tipo: 'veiculo',
        marca: document.getElementById('veiculoMarca').value,
        modelo: document.getElementById('veiculoModelo').value,
        ano: document.getElementById('veiculoAno').value,
        km: document.getElementById('veiculoKm').value,
        cor: document.getElementById('veiculoCor').value,
        preco: document.getElementById('veiculoPreco').value,
        descricao: document.getElementById('veiculoDescricao').value,
        fotos: document.getElementById('veiculoFotos').files
    };
    
    console.log('Dados do veículo:', dados);
    
    // Aqui você faria a requisição para o backend
    alert('Veículo cadastrado com sucesso!');
    
    // Fecha o modal e reseta o form
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
    formVeiculo.reset();
};

// Submit do formulário de peça
formPeca.onsubmit = (e) => {
    e.preventDefault();
    
    const dados = {
        tipo: 'peca',
        nome: document.getElementById('pecaNome').value,
        categoria: document.getElementById('pecaCategoria').value,
        marca: document.getElementById('pecaMarca').value,
        modelo: document.getElementById('pecaModelo').value,
        estado: document.getElementById('pecaEstado').value,
        preco: document.getElementById('pecaPreco').value,
        descricao: document.getElementById('pecaDescricao').value,
        fotos: document.getElementById('pecaFotos').files
    };
    
    console.log('Dados da peça:', dados);
    
    // Aqui você faria a requisição para o backend
    alert('Peça cadastrada com sucesso!');
    
    // Fecha o modal e reseta o form
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
    formPeca.reset();
};

// Fechar modal com tecla ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('show')) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
});