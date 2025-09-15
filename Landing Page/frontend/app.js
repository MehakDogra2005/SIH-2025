// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize slider
    initSlider();

    // Initialize scroll animations
    initScrollAnimations();

    // Initialize mobile menu
    initMobileMenu();

    // Initialize timeline animation
    initTimelineAnimation();

    // Apply color palettes to cards/icons (keeps main blue theme while adding variety)
    applyCardPalettes();

    // small accessibility: keyboard slider controls
    initSliderKeyboardShortcuts();
});

/* ---------- Slider functionality with small parallax + keyboard ---------- */
/* ---------- Slider functionality with exact 4s auto loop ---------- */
function initSlider() {
    const slides = document.querySelectorAll('.slide');
    const dotsContainer = document.querySelector('.slider-dots');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentSlide = 0;
    let slideInterval;

    // Create dots
    slides.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(i));
        dotsContainer.appendChild(dot);
    });

    const dots = document.querySelectorAll('.dot');

    function goToSlide(n) {
        slides[currentSlide].classList.remove('active');
        dots[currentSlide].classList.remove('active');

        currentSlide = (n + slides.length) % slides.length;

        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    function nextSlide() {
        goToSlide(currentSlide + 1);
    }

    function prevSlide() {
        goToSlide(currentSlide - 1);
    }

    function startSlideInterval() {
        slideInterval = setInterval(nextSlide, 3500); // 4s each slide
    }

    prevBtn.addEventListener('click', () => {
        prevSlide();
        resetSlideInterval();
    });

    nextBtn.addEventListener('click', () => {
        nextSlide();
        resetSlideInterval();
    });

    function resetSlideInterval() {
        clearInterval(slideInterval);
        startSlideInterval();
    }

    startSlideInterval();

    const slider = document.querySelector('.hero-slider');
    slider.addEventListener('mouseenter', () => clearInterval(slideInterval));
    slider.addEventListener('mouseleave', startSlideInterval);

    // gentle parallax effect (moves inner content slightly based on pointer)
    slider.addEventListener('mousemove', (e) => {
        const activeInner = document.querySelector('.slide.active .slide-inner');
        if (!activeInner) return;
        const x = (e.clientX / window.innerWidth - 0.5) * 18; // -9..9 px
        const y = (e.clientY / window.innerHeight - 0.5) * 10; // -5..5 px
        activeInner.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    });

    slider.addEventListener('mouseleave', () => {
        const activeInner = document.querySelector('.slide.active .slide-inner');
        if (!activeInner) return;
        activeInner.style.transform = '';
    });
}


/* ---------- Scroll animations (kept simple & performant) ---------- */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-card, .timeline-content, .stakeholder-card, .trust-item');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // prefer classes instead of inline styles so CSS handles transitions
                entry.target.classList.add('in-view');
                // For timeline items we want an extra class applied up the tree
                if (entry.target.classList.contains('timeline-content')) {
                    const parent = entry.target.closest('.timeline-item');
                    if (parent) parent.classList.add('in-view');
                }
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(el => {
        // set initial state via class so CSS transitions apply
        el.classList.add('pre-inview'); // optional, used if you want to style initial state in CSS
        observer.observe(el);
    });
}

/* ---------- Mobile menu functionality ---------- */
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (!hamburger || !navMenu) return;

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
}

/* ---------- Timeline animation (entrance) ---------- */
function initTimelineAnimation() {
    const timelineItems = document.querySelectorAll('.timeline-item');

    const timelineObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.12 });

    timelineItems.forEach(item => {
        // initial offset is set by CSS or inline style
        timelineObserver.observe(item);
    });
}

/* ---------- Apply colorful palettes to cards/icons (keeps the main blue but adds variety) ---------- */
function applyCardPalettes() {
    // palettes are intentionally soft and friendly
    const palettes = [
        { bg: 'linear-gradient(135deg,#4facfe 0%, #00f2fe 100%)', accent: '#4facfe' }, // cool blue
        { bg: 'linear-gradient(135deg,#FFB75E 0%, #ED8F03 100%)', accent: '#FFB75E' }, // warm orange
        { bg: 'linear-gradient(135deg,#a18cd1 0%, #fbc2eb 100%)', accent: '#a18cd1' }, // purple
        { bg: 'linear-gradient(135deg,#84fab0 0%, #8fd3f4 100%)', accent: '#84fab0' }, // mint/teal
        { bg: 'linear-gradient(135deg,#ff9a9e 0%, #fecfef 100%)', accent: '#ff9a9e' }, // pink
        { bg: 'linear-gradient(135deg,#FFB3B3 0%, #FF7B7B 100%)', accent: '#ff7b7b' }  // soft red
    ];

    // features
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((el, i) => {
        const p = palettes[i % palettes.length];
        el.style.setProperty('--card-accent', p.accent);
        // icon background (circle)
        const icon = el.querySelector('.feature-icon');
        if (icon) icon.style.setProperty('--icon-bg', p.bg);
    });

    // stakeholders (4 cards)
    const stakeholderPalettes = [
        { bg: 'linear-gradient(135deg,#4facfe,#00f2fe)', accent: '#4facfe' },
        { bg: 'linear-gradient(135deg,#f6d365,#fda085)', accent: '#f6d365' },
        { bg: 'linear-gradient(135deg,#84fab0,#8fd3f4)', accent: '#84fab0' },
        { bg: 'linear-gradient(135deg,#a18cd1,#fbc2eb)', accent: '#a18cd1' }
    ];
    const stakeholderCards = document.querySelectorAll('.stakeholder-card');
    stakeholderCards.forEach((el, i) => {
        const p = stakeholderPalettes[i % stakeholderPalettes.length];
        const img = el.querySelector('.stakeholder-img');
        if (img) img.style.background = p.bg;
    });

    // trust items
    const trustPalettes = [
        { bg: 'linear-gradient(135deg,#1a73e8,#4facfe)', accent: '#1a73e8' },
        { bg: 'linear-gradient(135deg,#7F7FD5,#86A8E7)', accent: '#7F7FD5' },
        { bg: 'linear-gradient(135deg,#f6d365,#fda085)', accent: '#f6d365' }
    ];
    const trustItems = document.querySelectorAll('.trust-item');
    trustItems.forEach((el, i) => {
        const p = trustPalettes[i % trustPalettes.length];
        el.style.setProperty('--icon-bg', p.bg);
        const icon = el.querySelector('i');
        if (icon) icon.style.background = p.bg;
    });

    // timeline icons (choose from a varied palette)
    const timelinePalettes = [
        { bg: 'linear-gradient(135deg,#4facfe,#00f2fe)' },
        { bg: 'linear-gradient(135deg,#FFB75E,#ED8F03)' },
        { bg: 'linear-gradient(135deg,#a18cd1,#fbc2eb)' },
        { bg: 'linear-gradient(135deg,#84fab0,#8fd3f4)' },
        { bg: 'linear-gradient(135deg,#ff9a9e,#fecfef)' }
    ];
    const timelineIcons = document.querySelectorAll('.timeline-icon');
    timelineIcons.forEach((el, i) => {
        const p = timelinePalettes[i % timelinePalettes.length];
        el.style.background = p.bg;
        el.style.color = '#fff';
        el.style.border = 'none';
    });
}

/* ---------- Keyboard support for slider ---------- */
function initSliderKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            const prevBtn = document.querySelector('.prev-btn');
            if (prevBtn) prevBtn.click();
        } else if (e.key === 'ArrowRight') {
            const nextBtn = document.querySelector('.next-btn');
            if (nextBtn) nextBtn.click();
        }
    });
}

/* ---------- Small tweak: Navbar scroll effect (kept from original) ---------- */
window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
});
