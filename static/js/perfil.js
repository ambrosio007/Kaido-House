// ==================== CARREGAMENTO DE DADOS DO USUÁRIO ====================

document.addEventListener('DOMContentLoaded', function() {
    carregarDadosUsuario();
    configurarBotoes();
});

// Função para carregar dados do usuário
async function carregarDadosUsuario() {
    try {
        // Buscar token do localStorage
        const token = localStorage.getItem('token');
        
        if (!token) {
            // Se não houver token, redirecionar para login
            alert('Você precisa estar logado para acessar esta página');
            window.location.href = '/login';
            return;
        }

        // Fazer requisição para buscar dados do usuário
        const response = await fetch('https://kaido-house.onrender.com/user-profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Token inválido ou expirado
                localStorage.removeItem('token');
                alert('Sessão expirada. Faça login novamente.');
                window.location.href = '/login';
                return;
            }
            throw new Error('Erro ao carregar dados do usuário');
        }

        const userData = await response.json();
        
        // Preencher dados no HTML
        preencherDadosUsuario(userData);

    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        alert('Erro ao carregar dados do perfil. Tente novamente.');
    }
}

// Função para preencher os dados do usuário no HTML
function preencherDadosUsuario(user) {
    // Foto de perfil (iniciais)
    const profilePhoto = document.querySelector('.profile-photo');
    if (profilePhoto && user.nome) {
        const iniciais = obterIniciais(user.nome);
        profilePhoto.textContent = iniciais;
    }

    // Nome do usuário
    const nomeHeader = document.querySelector('.profile-header h1');
    if (nomeHeader && user.nome) {
        nomeHeader.textContent = user.nome;
    }

    // Preencher info-groups
    const infoGroups = document.querySelectorAll('.info-group');
    
    infoGroups.forEach(group => {
        const label = group.querySelector('label');
        const valueDiv = group.querySelector('.value');
        
        if (!label || !valueDiv) return;
        
        const labelText = label.textContent;
        
        if (labelText.includes('Nome Completo') && user.nome) {
            valueDiv.textContent = user.nome;
        }
        else if (labelText.includes('Email') && user.email) {
            valueDiv.textContent = user.email;
        }
        else if (labelText.includes('CPF') && user.cpf) {
            valueDiv.textContent = formatarCPF(user.cpf);
        }
        else if (labelText.includes('Data de Nascimento') && user.data_nascimento) {
            valueDiv.textContent = formatarData(user.data_nascimento);
        }
        else if (labelText.includes('CEP') && user.cep) {
            valueDiv.textContent = formatarCEP(user.cep);
        }
    });

    // Data de cadastro (Membro desde)
    if (user.data_cadastro) {
        const memberSince = document.querySelector('.profile-header p');
        if (memberSince) {
            const dataCadastro = new Date(user.data_cadastro);
            const mes = dataCadastro.toLocaleString('pt-BR', { month: 'long' });
            const ano = dataCadastro.getFullYear();
            memberSince.textContent = `Membro desde ${mes.charAt(0).toUpperCase() + mes.slice(1)} ${ano}`;
        }
    }

    // Estatísticas
    const statCards = document.querySelectorAll('.stat-card');
    
    if (statCards.length >= 3) {
        if (user.total_pedidos !== undefined) {
            statCards[0].querySelector('.number').textContent = user.total_pedidos;
        }
        
        if (user.avaliacao !== undefined) {
            statCards[1].querySelector('.number').textContent = user.avaliacao.toFixed(1);
        }
        
        if (user.total_favoritos !== undefined) {
            statCards[2].querySelector('.number').textContent = user.total_favoritos;
        }
    }
}

// Função auxiliar para obter iniciais do nome
function obterIniciais(nome) {
    const palavras = nome.trim().split(' ');
    if (palavras.length === 1) {
        return palavras[0].substring(0, 2).toUpperCase();
    }
    return (palavras[0][0] + palavras[palavras.length - 1][0]).toUpperCase();
}

// Função para formatar CPF
function formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

// Função para formatar data
function formatarData(data) {
    const date = new Date(data);
    const dia = String(date.getDate()).padStart(2, '0');
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const ano = date.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

// Função para formatar CEP
function formatarCEP(cep) {
    cep = cep.replace(/\D/g, '');
    return cep.replace(/(\d{5})(\d{3})/, '$1-$2');
}

// Configurar botões
function configurarBotoes() {
    // Botão de Sair
    const btnSair = document.querySelector('.btn-danger');
    if (btnSair) {
        btnSair.addEventListener('click', function() {
            if (confirm('Tem certeza que deseja sair?')) {
                localStorage.removeItem('token');
                window.location.href = '/login';
            }
        });
    }

    // Botão Editar Perfil
    const btnEditar = document.querySelector('.btn-primary');
    if (btnEditar) {
        btnEditar.addEventListener('click', function() {
            alert('Funcionalidade de edição em desenvolvimento');
        });
    }

    // Botão Alterar Senha
    const btnSenha = document.querySelector('.btn-secondary');
    if (btnSenha) {
        btnSenha.addEventListener('click', function() {
            alert('Funcionalidade de alteração de senha em desenvolvimento');
        });
    }
}


// ==================== CONTROLE DE MODAL E FORMULÁRIOS ====================

// Elementos do DOM
const btnCadastrarVenda = document.getElementById('btnCadastrarVenda');
const modal = document.getElementById('modalCadastro');
const closeModal = document.querySelector('.close');
const btnsTipo = document.querySelectorAll('.btn-tipo');
const formVeiculo = document.getElementById('formVeiculo');
const formPeca = document.getElementById('formPeca');

// Abrir modal
if (btnCadastrarVenda) {
    btnCadastrarVenda.onclick = () => {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    };
}

// Fechar modal
if (closeModal) {
    closeModal.onclick = () => {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    };
}

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
        btnsTipo.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const tipo = btn.dataset.tipo;
        
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
if (formVeiculo) {
    formVeiculo.onsubmit = async (e) => {
        e.preventDefault();
        
        const token = localStorage.getItem('token');
        if (!token) {
            alert('Você precisa estar logado');
            window.location.href = '/login';
            return;
        }
        
        const dados = {
            marca: document.getElementById('veiculoMarca').value,
            modelo: document.getElementById('veiculoModelo').value,
            ano: parseInt(document.getElementById('veiculoAno').value),
            km: parseInt(document.getElementById('veiculoKm').value),
            cor: document.getElementById('veiculoCor').value,
            preco: parseFloat(document.getElementById('veiculoPreco').value),
            descricao: document.getElementById('veiculoDescricao').value
        };
        
        try {
            const response = await fetch('https://kaido-house.onrender.com/cadastrar-veiculo', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });
            
            if (response.ok) {
                alert('Veículo cadastrado com sucesso!');
                modal.classList.remove('show');
                document.body.style.overflow = 'auto';
                formVeiculo.reset();
            } else {
                const error = await response.json();
                alert(`Erro: ${error.error || 'Erro ao cadastrar veículo'}`);
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao cadastrar veículo. Tente novamente.');
        }
    };
}

// Submit do formulário de peça
if (formPeca) {
    formPeca.onsubmit = async (e) => {
        e.preventDefault();
        
        const token = localStorage.getItem('token');
        if (!token) {
            alert('Você precisa estar logado');
            window.location.href = '/login';
            return;
        }
        
        const dados = {
            nome: document.getElementById('pecaNome').value,
            categoria: document.getElementById('pecaCategoria').value,
            marca: document.getElementById('pecaMarca').value,
            modelo: document.getElementById('pecaModelo').value,
            estado: document.getElementById('pecaEstado').value,
            preco: parseFloat(document.getElementById('pecaPreco').value),
            descricao: document.getElementById('pecaDescricao').value
        };
        
        try {
            const response = await fetch('https://kaido-house.onrender.com/cadastrar-peca', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });
            
            if (response.ok) {
                alert('Peça cadastrada com sucesso!');
                modal.classList.remove('show');
                document.body.style.overflow = 'auto';
                formPeca.reset();
            } else {
                const error = await response.json();
                alert(`Erro: ${error.error || 'Erro ao cadastrar peça'}`);
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao cadastrar peça. Tente novamente.');
        }
    };
}

// Fechar modal com tecla ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && modal.classList.contains('show')) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
});