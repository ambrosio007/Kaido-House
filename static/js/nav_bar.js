const menuBtn = document.getElementById('menu-btn');
const navbar = document.querySelector('.navbar');
const profileArea = document.querySelector('.profile-area');

// Elementos de perfil que serão movidos (deslogado ou logado, dependendo do estado real)
const profileContainer = profileArea.querySelector('.auth-icon-container:not(.hidden)');

// Cria o wrapper que manterá o ícone de perfil quando movido para dentro da NAV
const mobileProfileWrapper = document.createElement('div');
mobileProfileWrapper.classList.add('mobile-profile-item');
mobileProfileWrapper.setAttribute('id', 'mobile-profile-wrapper');

// Função para alternar o menu
menuBtn.onclick = () => {
    navbar.classList.toggle('active');
    // Fechar o menu se o clique for fora dele (opcional, mas bom)
};

// Função para mover o ícone de perfil/login para dentro ou para fora da navbar
function handleMobileLayout() {
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        // 1. Esconde o profileArea no header (feito no CSS, mas reforçamos)
        profileArea.style.display = 'none';

        // 2. Move o ícone de perfil/login para o final da navbar
        if (profileContainer && !document.getElementById('mobile-profile-wrapper')) {
            mobileProfileWrapper.appendChild(profileContainer);
            navbar.appendChild(mobileProfileWrapper);
        }
    } else {
        // 1. Garante que o menu esteja fechado no desktop
        navbar.classList.remove('active');

        // 2. Move o ícone de perfil/login de volta para o header
        if (profileContainer && mobileProfileWrapper.parentNode === navbar) {
            profileArea.appendChild(profileContainer);
            profileArea.style.display = 'flex'; // Exibe novamente no desktop
            mobileProfileWrapper.remove();
        }
    }
}

// Chama a função na carga da página e no redimensionamento da janela
window.addEventListener('load', handleMobileLayout);
window.addEventListener('resize', handleMobileLayout);

// Se o usuário estiver logado, garante que o ícone correto seja movido
// Esta é uma lógica que deve ser implementada no seu back-end/JS real.
// Aqui, garantimos que apenas um esteja ativo no JS.
if (document.querySelector('.profile-state:not(.hidden)')) {
    const loggedInProfile = document.querySelector('.profile-state:not(.hidden)');
    profileContainer = loggedInProfile; // Atualiza qual container será movido
}