const menuBtn = document.getElementById('menu-btn');
const navbar = document.querySelector('.navbar');

menuBtn.onclick = () => {
    navbar.classList.toggle('active');
    // Troca o ícone de hambúrguer por um "X" ao abrir
    menuBtn.classList.toggle('fa-times');
};

// Fecha o menu ao clicar em qualquer link
document.querySelectorAll('.navbar a').forEach(link => {
    link.onclick = () => {
        navbar.classList.remove('active');
        menuBtn.classList.remove('fa-times');
    }
});

// Efeito de scroll no header
window.onscroll = () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.padding = '10px 5%';
        header.style.boxShadow = '0 5px 20px rgba(0,0,0,0.8)';
    } else {
        header.style.padding = '15px 5%';
        header.style.boxShadow = 'none';
    }
};
// ========================================
// AUTENTICAÇÃO E PERFIL DO USUÁRIO
// ========================================

// Função para obter a primeira letra do nome
function obterInicial(nome) {
    if (!nome) return '?';
    return nome.charAt(0).toUpperCase();
}

// Função para carregar dados do usuário e atualizar a navbar
async function carregarPerfilNavbar() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.log('Usuário não logado');
        mostrarEstadoDeslogado();
        return;
    }
    
    try {
        const response = await fetch('https://kaido-house.onrender.com/user-profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}`);
        }
        
        const dados = await response.json();
        
        // Atualizar a navbar com os dados do usuário
        atualizarNavbarLogado(dados);
        
    } catch (erro) {
        console.error('Erro ao carregar perfil na navbar:', erro);
        
        // Se houver erro de autenticação, limpar token e mostrar deslogado
        if (erro.message.includes('401') || erro.message.includes('422')) {
            localStorage.removeItem('token');
            mostrarEstadoDeslogado();
        }
    }
}

// Função para atualizar a navbar quando usuário está logado
function atualizarNavbarLogado(dados) {
    const loginState = document.querySelector('.login-state');
    const profileState = document.querySelector('.profile-state');
    const profileAvatar = document.querySelector('.profile-avatar');
    
    if (!loginState || !profileState) {
        console.error('Elementos da navbar não encontrados');
        return;
    }
    
    // Esconder ícone de login e mostrar ícone de perfil
    loginState.classList.add('hidden');
    profileState.classList.remove('hidden');
    
    // Obter a inicial do nome
    const inicial = obterInicial(dados.nome);
    
    // Se tiver foto de perfil, usar ela
    if (dados.foto_perfil && profileAvatar) {
        profileAvatar.src = dados.foto_perfil;
        profileAvatar.alt = dados.nome;
        profileAvatar.classList.remove('avatar-inicial');
    } else {
        // Usar a inicial como avatar
        criarAvatarComInicial(profileState, inicial, dados.nome);
    }
    
    // Criar ou atualizar dropdown de perfil
    criarDropdownPerfil(profileState, dados);
}

// Função para criar avatar com a inicial
function criarAvatarComInicial(container, inicial, nomeCompleto) {
    const avatar = container.querySelector('.profile-avatar');
    
    if (avatar) {
        // Substituir img por div com a inicial
        const avatarInicial = document.createElement('div');
        avatarInicial.className = 'profile-avatar avatar-inicial';
        avatarInicial.textContent = inicial;
        avatarInicial.title = nomeCompleto;
        
        avatar.replaceWith(avatarInicial);
    }
}

// Função para criar dropdown de perfil
function criarDropdownPerfil(container, dados) {
    // Remover dropdown existente se houver
    const dropdownExistente = container.querySelector('.profile-dropdown');
    if (dropdownExistente) {
        dropdownExistente.remove();
    }
    
    // Criar novo dropdown
    const dropdown = document.createElement('div');
    dropdown.className = 'profile-dropdown';
    dropdown.innerHTML = `
        <div class="dropdown-header">
            <div class="dropdown-nome">${dados.nome}</div>
            <div class="dropdown-email">${dados.email}</div>
        </div>
        
        <a href="/perfil" class="dropdown-item">
            <i class="fas fa-user"></i> Meu Perfil
        </a>
        <a href="/meus-anuncios" class="dropdown-item">
            <i class="fas fa-box"></i> Meus Anúncios
        </a>
        <a href="/favoritos" class="dropdown-item">
            <i class="fas fa-heart"></i> Favoritos
        </a>
        
        <div class="dropdown-divider"></div>
        
        <a href="#" class="dropdown-item logout" onclick="logout(); return false;">
            <i class="fas fa-sign-out-alt"></i> Sair
        </a>
    `;
    
    container.appendChild(dropdown);
}

// Função para mostrar estado deslogado
function mostrarEstadoDeslogado() {
    const loginState = document.querySelector('.login-state');
    const profileState = document.querySelector('.profile-state');
    
    if (loginState && profileState) {
        loginState.classList.remove('hidden');
        profileState.classList.add('hidden');
    }
}

// Função de logout
function logout() {
    // Limpar token
    localStorage.removeItem('token');
    
    // Redirecionar para login
    window.location.href = '/login';
}

// Verificar autenticação ao carregar a página
function verificarAutenticacao() {
    const token = localStorage.getItem('token');
    
    if (token) {
        carregarPerfilNavbar();
    } else {
        mostrarEstadoDeslogado();
    }
}

// Atualizar contador do carrinho
function atualizarContadorCarrinho() {
    const cartBadge = document.querySelector('.cart-badge');
    const carrinho = JSON.parse(localStorage.getItem('carrinho') || '[]');
    
    if (cartBadge) {
        const totalItens = carrinho.reduce((total, item) => total + (item.quantidade || 1), 0);
        cartBadge.textContent = totalItens;
        
        // Esconder badge se estiver vazio
        if (totalItens === 0) {
            cartBadge.style.display = 'none';
        } else {
            cartBadge.style.display = 'flex';
        }
    }
}

// Executar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    verificarAutenticacao();
    atualizarContadorCarrinho();
});