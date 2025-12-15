// Inicializa o menu hambúrguer (mantendo a funcionalidade anterior)
const menuBtn = document.getElementById('menu-btn');
const navbar = document.querySelector('.navbar');

menuBtn.onclick = () => {
    navbar.classList.toggle('active');
};

// ====================================
// SWIPER JS - Inicialização dos Carrosséis
// ====================================

// 1. Banner Principal (Com autodeslize)
new Swiper('.banner-slider', {
    loop: true,
    autoplay: {
        delay: 5000, // 5 segundos
        disableOnInteraction: false,
    },
    pagination: {
        el: '.banner-pagination',
        clickable: true,
    },
});

// 2. Carrosséis de Cards (Promoções, Novas, Usadas) - Mesma configuração
const cardSwiperOptions = {
    loop: true,
    spaceBetween: 20, // Espaçamento entre os cards
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    breakpoints: {
        // Quando a tela tiver 0px ou mais
        0: {
            slidesPerView: 1.2,
        },
        // Quando a tela tiver 550px ou mais
        550: {
            slidesPerView: 2.2,
        },
        // Quando a tela tiver 800px ou mais
        800: {
            slidesPerView: 3.2,
        },
        // Quando a tela tiver 1200px ou mais
        1200: {
            slidesPerView: 4.2,
        },
    },
};

new Swiper('.promotions-slider', cardSwiperOptions);
new Swiper('.new-parts-slider', cardSwiperOptions);
new Swiper('.used-parts-slider', cardSwiperOptions);

// 3. Carrossel de Veículos (Pode ter menos slides por tela)
new Swiper('.used-vehicles-slider', {
    loop: true,
    spaceBetween: 30,
    navigation: {
        nextEl: '.used-vehicles-slider .swiper-button-next',
        prevEl: '.used-vehicles-slider .swiper-button-prev',
    },
    breakpoints: {
        0: {
            slidesPerView: 1.1,
        },
        600: {
            slidesPerView: 2.1,
        },
        1000: {
            slidesPerView: 3.1,
        },
    },
});