// ==================== CARREGAMENTO DE DADOS DO USUÁRIO ====================

document.addEventListener('DOMContentLoaded', function() {
    carregarDadosUsuario();
    configurarBotoes();
    configurarUploadFoto();
});

// Função para carregar dados do usuário
async function carregarDadosUsuario() {
    try {
        const token = localStorage.getItem('token');
        
        if (!token) {
            alert('Você precisa estar logado para acessar esta página');
            window.location.href = '/login';
            return;
        }

        const response = await fetch('https://kaido-house.onrender.com/user-profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('token');
                alert('Sessão expirada. Faça login novamente.');
                window.location.href = '/login';
                return;
            }
            throw new Error('Erro ao carregar dados do usuário');
        }

        const userData = await response.json();
        preencherDadosUsuario(userData);

    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        alert('Erro ao carregar dados do perfil. Tente novamente.');
    }
}

// Função para preencher os dados do usuário no HTML
function preencherDadosUsuario(user) {
    // Foto de perfil
    const profilePhoto = document.querySelector('.profile-photo');
    if (profilePhoto && user.nome) {
        if (user.foto_perfil) {
            // Se tem foto, exibir a imagem
            profilePhoto.innerHTML = `<img src="${user.foto_perfil}" alt="Foto de perfil" class="profile-image">`;
        } else {
            // Se não tem foto, exibir iniciais
            const iniciais = obterIniciais(user.nome);
            profilePhoto.textContent = iniciais;
            profilePhoto.classList.add('sem-foto');
        }
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
        // ✅ CORRIGIDO: Agora exibe idade ao invés de data de nascimento
        else if (labelText.includes('Data de Nascimento') && user.idade) {
            valueDiv.textContent = `${user.idade} anos`;
        }
        else if (labelText.includes('CEP') && user.cep) {
            valueDiv.textContent = formatarCEP(user.cep);
        }
    });

    // Data de cadastro
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

// Configurar upload de foto
function configurarUploadFoto() {
    const profilePhoto = document.querySelector('.profile-photo');
    
    if (profilePhoto) {
        // Criar input de arquivo (oculto)
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);
        
        // Adicionar cursor pointer e título
        profilePhoto.style.cursor = 'pointer';
        profilePhoto.title = 'Clique para alterar a foto de perfil';
        
        // Evento de clique na foto
        profilePhoto.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Evento quando selecionar arquivo
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            
            if (!file) return;
            
            // Validar tipo de arquivo
            if (!file.type.startsWith('image/')) {
                alert('Por favor, selecione uma imagem válida');
                return;
            }
            
            // Validar tamanho (máx 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('A imagem deve ter no máximo 5MB');
                return;
            }
            
            // Fazer upload
            await uploadFotoPerfil(file);
        });
    }
}

// Função para fazer upload da foto
async function uploadFotoPerfil(file) {
    try {
        const token = localStorage.getItem('token');
        
        if (!token) {
            alert('Você precisa estar logado');
            return;
        }
        
        const formData = new FormData();
        formData.append('foto', file);
        
        const response = await fetch('https://kaido-house.onrender.com/upload-foto-perfil', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Atualizar a foto na tela
            const profilePhoto = document.querySelector('.profile-photo');
            if (profilePhoto) {
                profilePhoto.innerHTML = `<img src="${data.foto_url}" alt="Foto de perfil" class="profile-image">`;
                profilePhoto.classList.remove('sem-foto');
            }
            
            alert('Foto de perfil atualizada com sucesso!');
        } else {
            const error = await response.json();
            alert(`Erro: ${error.error || 'Erro ao fazer upload da foto'}`);
        }
        
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao fazer upload da foto. Tente novamente.');
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
        
        // Usar FormData para enviar dados + arquivos juntos
        const formData = new FormData();
        formData.append('marca',     document.getElementById('veiculoMarca').value);
        formData.append('modelo',    document.getElementById('veiculoModelo').value);
        formData.append('ano',       document.getElementById('veiculoAno').value);
        formData.append('km',        document.getElementById('veiculoKm').value);
        formData.append('cor',       document.getElementById('veiculoCor').value);
        formData.append('preco',     document.getElementById('veiculoPreco').value);
        formData.append('descricao', document.getElementById('veiculoDescricao').value);

        // ✅ CORREÇÃO: Converter FileList para Array antes de usar forEach
        const fotosVeiculo = document.getElementById('veiculoFotos');
        if (fotosVeiculo && fotosVeiculo.files) {
            Array.from(fotosVeiculo.files).forEach(file => {
                formData.append('fotos', file);
            });
        }
        
        try {
            // Não define Content-Type: o navegador define automaticamente com o boundary do FormData
            const response = await fetch('https://kaido-house.onrender.com/cadastro-veiculo', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            // ✅ VERIFICAR SE A RESPOSTA É JSON ANTES DE PARSEAR
            const contentType = response.headers.get('content-type');
            
            if (response.ok) {
                // Se sucesso, tentar parsear JSON
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    alert('Veículo cadastrado com sucesso!');
                } else {
                    alert('Veículo cadastrado com sucesso!');
                }
                modal.classList.remove('show');
                document.body.style.overflow = 'auto';
                formVeiculo.reset();
            } else {
                // Se erro, tentar obter mensagem de erro
                let errorMessage = 'Erro ao cadastrar veículo';
                
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    errorMessage = error.error || error.message || errorMessage;
                } else if (response.status === 404) {
                    errorMessage = 'Rota não encontrada no servidor. Verifique a URL da API.';
                } else {
                    const textError = await response.text();
                    console.error('Resposta do servidor:', textError);
                }
                
                alert(`Erro: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao cadastrar veículo. Verifique sua conexão e tente novamente.');
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
        
        // Usar FormData para enviar dados + arquivos juntos
        const formData = new FormData();
        formData.append('nome',      document.getElementById('pecaNome').value);
        formData.append('categoria', document.getElementById('pecaCategoria').value);
        formData.append('marca',     document.getElementById('pecaMarca').value);
        formData.append('modelo',    document.getElementById('pecaModelo').value);
        formData.append('estado',    document.getElementById('pecaEstado').value);
        formData.append('preco',     document.getElementById('pecaPreco').value);
        formData.append('descricao', document.getElementById('pecaDescricao').value);

        // ✅ CORREÇÃO: Converter FileList para Array antes de usar forEach
        const fotos = document.getElementById('pecaFotos');
        if (fotos && fotos.files) {
            Array.from(fotos.files).forEach(file => {
                formData.append('fotos', file);
            });
        }
        
        try {
            // Não define Content-Type: o navegador define automaticamente com o boundary do FormData
            const response = await fetch('https://kaido-house.onrender.com/cadastro-peca', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            // ✅ VERIFICAR SE A RESPOSTA É JSON ANTES DE PARSEAR
            const contentType = response.headers.get('content-type');
            
            if (response.ok) {
                // Se sucesso, tentar parsear JSON
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    alert('Peça cadastrada com sucesso!');
                } else {
                    alert('Peça cadastrada com sucesso!');
                }
                modal.classList.remove('show');
                document.body.style.overflow = 'auto';
                formPeca.reset();
            } else {
                // Se erro, tentar obter mensagem de erro
                let errorMessage = 'Erro ao cadastrar peça';
                
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    errorMessage = error.error || error.message || errorMessage;
                } else if (response.status === 404) {
                    errorMessage = 'Rota não encontrada no servidor. Verifique se a rota /cadastro-peca existe na API.';
                } else {
                    const textError = await response.text();
                    console.error('Resposta do servidor:', textError);
                }
                
                alert(`Erro: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao cadastrar peça. Verifique sua conexão e tente novamente.');
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