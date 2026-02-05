// ==================== CARREGAMENTO DE DADOS DO USUÁRIO ====================

let dadosUsuario = null; // Variável global para armazenar dados do usuário

document.addEventListener('DOMContentLoaded', function() {
    carregarDadosUsuario();
    configurarBotoes();
    configurarUploadFoto();
    configurarModais();
});

// Função para carregar dados do usuário
async function carregarDadosUsuario() {
    try {
        const token = localStorage.getItem('token') || localStorage.getItem('access_token');
        
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
                localStorage.removeItem('access_token');
                alert('Sessão expirada. Faça login novamente.');
                window.location.href = '/login';
                return;
            }
            throw new Error('Erro ao carregar dados do usuário');
        }

        dadosUsuario = await response.json();
        preencherDadosUsuario(dadosUsuario);

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
            profilePhoto.innerHTML = `<img src="${user.foto_perfil}" alt="Foto de perfil" class="profile-image">`;
        } else {
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

// ==================== CONFIGURAÇÃO DOS MODAIS ====================

function configurarModais() {
    // Fechar modais com X
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            fecharModal(modalId);
        });
    });

    // Fechar modais com botão cancelar
    document.querySelectorAll('.btn-cancel').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            fecharModal(modalId);
        });
    });

    // Fechar modal ao clicar fora
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            fecharModal(event.target.id);
        }
    });

    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                fecharModal(modal.id);
            });
        }
    });

    // Configurar formulário de edição
    document.getElementById('formEditarPerfil').addEventListener('submit', salvarEdicaoPerfil);
    
    // Configurar formulário de alteração de senha
    document.getElementById('formAlterarSenha').addEventListener('submit', alterarSenha);
}

function abrirModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function fecharModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// ==================== EDIÇÃO DE PERFIL ====================

function abrirModalEdicao() {
    if (!dadosUsuario) {
        alert('Dados do usuário não carregados');
        return;
    }

    // Preencher formulário com dados atuais
    document.getElementById('editNome').value = dadosUsuario.nome || '';
    document.getElementById('editEmail').value = dadosUsuario.email || '';
    document.getElementById('editCPF').value = dadosUsuario.cpf || '';
    document.getElementById('editIdade').value = dadosUsuario.idade || '';
    document.getElementById('editCEP').value = dadosUsuario.cep || '';

    abrirModal('modalEditarPerfil');
}

async function salvarEdicaoPerfil(e) {
    e.preventDefault();

    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    if (!token) {
        alert('Você precisa estar logado');
        return;
    }

    const dadosEditados = {
        nome: document.getElementById('editNome').value,
        email: document.getElementById('editEmail').value,
        cpf: document.getElementById('editCPF').value,
        idade: parseInt(document.getElementById('editIdade').value),
        cep: document.getElementById('editCEP').value
    };

    try {
        const response = await fetch('https://kaido-house.onrender.com/atualizar-user', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosEditados)
        });

        if (response.ok) {
            alert('Perfil atualizado com sucesso!');
            fecharModal('modalEditarPerfil');
            await carregarDadosUsuario(); // Recarregar dados
        } else {
            const error = await response.json();
            alert(`Erro: ${error.error || 'Erro ao atualizar perfil'}`);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao atualizar perfil. Tente novamente.');
    }
}

// ==================== ALTERAÇÃO DE SENHA ====================

async function alterarSenha(e) {
    e.preventDefault();

    const senhaAtual = document.getElementById('senhaAtual').value;
    const novaSenha = document.getElementById('novaSenha').value;
    const confirmarNovaSenha = document.getElementById('confirmarNovaSenha').value;

    // Validar senhas
    if (novaSenha !== confirmarNovaSenha) {
        alert('As senhas não coincidem!');
        return;
    }

    if (novaSenha.length < 6) {
        alert('A nova senha deve ter no mínimo 6 caracteres!');
        return;
    }

    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    if (!token) {
        alert('Você precisa estar logado');
        return;
    }

    try {
        const response = await fetch('https://kaido-house.onrender.com/alterar-senha', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                senha_atual: senhaAtual,
                nova_senha: novaSenha
            })
        });

        if (response.ok) {
            alert('Senha alterada com sucesso!');
            fecharModal('modalAlterarSenha');
            document.getElementById('formAlterarSenha').reset();
        } else {
            const error = await response.json();
            alert(`Erro: ${error.error || 'Senha atual incorreta'}`);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao alterar senha. Tente novamente.');
    }
}

// ==================== DELETAR CONTA ====================

async function deletarConta() {
    const confirmacao = confirm(
        '⚠️ ATENÇÃO!\n\n' +
        'Esta ação é IRREVERSÍVEL!\n\n' +
        'Ao deletar sua conta:\n' +
        '• Todos os seus dados serão permanentemente apagados\n' +
        '• Seus veículos e peças cadastrados serão removidos\n' +
        '• Você não poderá recuperar esta conta\n\n' +
        'Tem certeza que deseja continuar?'
    );

    if (!confirmacao) return;

    const confirmaFinal = prompt(
        'Para confirmar, digite "DELETAR" (em maiúsculas):'
    );

    if (confirmaFinal !== 'DELETAR') {
        alert('Operação cancelada.');
        return;
    }

    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    if (!token) {
        alert('Você precisa estar logado');
        return;
    }

    try {
        const response = await fetch('https://kaido-house.onrender.com/deletar-user', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            alert('Conta deletada com sucesso. Você será redirecionado.');
            localStorage.clear();
            window.location.href = '/';
        } else {
            const error = await response.json();
            alert(`Erro: ${error.error || 'Erro ao deletar conta'}`);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao deletar conta. Tente novamente.');
    }
}

// ==================== UPLOAD DE FOTO ====================

function configurarUploadFoto() {
    const profilePhoto = document.querySelector('.profile-photo');
    
    if (profilePhoto) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);
        
        profilePhoto.style.cursor = 'pointer';
        profilePhoto.title = 'Clique para alterar a foto de perfil';
        
        profilePhoto.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            
            if (!file) return;
            
            if (!file.type.startsWith('image/')) {
                alert('Por favor, selecione uma imagem válida');
                return;
            }
            
            if (file.size > 5 * 1024 * 1024) {
                alert('A imagem deve ter no máximo 5MB');
                return;
            }
            
            await uploadFotoPerfil(file);
        });
    }
}

async function uploadFotoPerfil(file) {
    try {
        const token = localStorage.getItem('token') || localStorage.getItem('access_token');
        
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

// ==================== CONFIGURAÇÃO DOS BOTÕES ====================

function configurarBotoes() {
    // Botão Editar Perfil
    const btnEditarPerfil = document.getElementById('btnEditarPerfil');
    if (btnEditarPerfil) {
        btnEditarPerfil.addEventListener('click', abrirModalEdicao);
    }

    // Botão Meus Veículos
    const btnMeusVeiculos = document.getElementById('btnMeusVeiculos');
    if (btnMeusVeiculos) {
        btnMeusVeiculos.addEventListener('click', function() {
            window.location.href = '/meus-veiculos';
        });
    }

    // Botão Alterar Senha (dentro do modal de edição)
    const btnAlterarSenha = document.getElementById('btnAlterarSenha');
    if (btnAlterarSenha) {
        btnAlterarSenha.addEventListener('click', function() {
            fecharModal('modalEditarPerfil');
            abrirModal('modalAlterarSenha');
        });
    }

    // Botão Deletar Conta (dentro do modal de edição)
    const btnDeletarConta = document.getElementById('btnDeletarConta');
    if (btnDeletarConta) {
        btnDeletarConta.addEventListener('click', deletarConta);
    }

    // Botão Sair
    const btnSair = document.getElementById('btnSair');
    if (btnSair) {
        btnSair.addEventListener('click', function() {
            if (confirm('Deseja realmente sair?')) {
                localStorage.clear();
                window.location.href = '/';
            }
        });
    }
}

// ==================== FUNÇÕES AUXILIARES ====================

function obterIniciais(nome) {
    const palavras = nome.trim().split(' ');
    if (palavras.length >= 2) {
        return (palavras[0][0] + palavras[palavras.length - 1][0]).toUpperCase();
    }
    return nome.substring(0, 2).toUpperCase();
}

function formatarCPF(cpf) {
    if (!cpf) return '';
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

function formatarCEP(cep) {
    if (!cep) return '';
    cep = cep.replace(/\D/g, '');
    return cep.replace(/(\d{5})(\d{3})/, '$1-$2');
}

// ==================== MODAL DE CADASTRO DE VENDA ====================

const btnCadastrarVenda = document.getElementById('btnCadastrarVenda');
const modal = document.getElementById('modalCadastro');
const btnsTipo = document.querySelectorAll('.btn-tipo');
const formVeiculo = document.getElementById('formVeiculo');
const formPeca = document.getElementById('formPeca');

// Abrir modal
if (btnCadastrarVenda) {
    btnCadastrarVenda.onclick = () => {
        abrirModal('modalCadastro');
    };
}

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
        
        const token = localStorage.getItem('token') || localStorage.getItem('access_token');
        if (!token) {
            alert('Você precisa estar logado');
            window.location.href = '/login';
            return;
        }
        
        const formData = new FormData();
        formData.append('marca',     document.getElementById('veiculoMarca').value);
        formData.append('modelo',    document.getElementById('veiculoModelo').value);
        formData.append('ano',       document.getElementById('veiculoAno').value);
        formData.append('km',        document.getElementById('veiculoKm').value);
        formData.append('cor',       document.getElementById('veiculoCor').value);
        formData.append('estado',    document.getElementById('veiculoEstado').value);
        formData.append('preco',     document.getElementById('veiculoPreco').value);
        formData.append('descricao', document.getElementById('veiculoDescricao').value);

        const fotosVeiculo = document.getElementById('veiculoFotos');
        if (fotosVeiculo && fotosVeiculo.files) {
            Array.from(fotosVeiculo.files).forEach(file => {
                formData.append('fotos', file);
            });
        }
        
        try {
            const response = await fetch('https://kaido-house.onrender.com/cadastro-veiculo', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const contentType = response.headers.get('content-type');
            
            if (response.ok) {
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    alert('Veículo cadastrado com sucesso!');
                } else {
                    alert('Veículo cadastrado com sucesso!');
                }
                fecharModal('modalCadastro');
                formVeiculo.reset();
            } else {
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
        
        const token = localStorage.getItem('token') || localStorage.getItem('access_token');
        if (!token) {
            alert('Você precisa estar logado');
            window.location.href = '/login';
            return;
        }
        
        const formData = new FormData();
        formData.append('nome',      document.getElementById('pecaNome').value);
        formData.append('categoria', document.getElementById('pecaCategoria').value);
        formData.append('marca',     document.getElementById('pecaMarca').value);
        formData.append('modelo',    document.getElementById('pecaModelo').value);
        formData.append('estado',    document.getElementById('pecaEstado').value);
        formData.append('preco',     document.getElementById('pecaPreco').value);
        formData.append('descricao', document.getElementById('pecaDescricao').value);

        const fotos = document.getElementById('pecaFotos');
        if (fotos && fotos.files) {
            Array.from(fotos.files).forEach(file => {
                formData.append('fotos', file);
            });
        }
        
        try {
            const response = await fetch('https://kaido-house.onrender.com/cadastro-peca', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const contentType = response.headers.get('content-type');
            
            if (response.ok) {
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    alert('Peça cadastrada com sucesso!');
                } else {
                    alert('Peça cadastrada com sucesso!');
                }
                fecharModal('modalCadastro');
                formPeca.reset();
            } else {
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