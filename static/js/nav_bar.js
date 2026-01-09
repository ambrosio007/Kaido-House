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