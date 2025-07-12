/**
 * GovBR Roleplay - JavaScript Premium
 * Funcionalidades avançadas e efeitos visuais modernos
 */

// =====================================
// SISTEMA DE NOTIFICAÇÕES
// =====================================
const NotificationManager = {
    init() {
        // Criar container de toasts se não existir
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        console.log('✅ Sistema de notificações inicializado');
    },

    show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
            </div>
        `;
        
        const container = document.getElementById('toast-container');
        if (!container) {
            this.init();
        }
        
        const toastContainer = document.getElementById('toast-container');
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover toast após ser ocultado
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'danger');
    },

    warning(message) {
        this.show(message, 'warning');
    },

    info(message) {
        this.show(message, 'info');
    },

    showValidationError: (form) => {
        const invalidFields = form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            const firstInvalid = invalidFields[0];
            const fieldName = firstInvalid.getAttribute('data-field-name') || firstInvalid.name || 'campo';
            NotificationManager.error(`Por favor, preencha corretamente o ${fieldName}.`);
            firstInvalid.focus();
        }
    },

    showFormSuccess: (message) => {
        NotificationManager.success(message);
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    },

    showFormError: (error) => {
        if (typeof error === 'string') {
            NotificationManager.error(error);
        } else if (error.message) {
            NotificationManager.error(error.message);
        } else {
            NotificationManager.error('Ocorreu um erro inesperado.');
        }
    },

    showConnectionError: () => {
        NotificationManager.error('Erro de conexão com o servidor. Verifique sua internet e tente novamente.');
    }
};

// Tornar NotificationManager global
window.NotificationManager = NotificationManager;

// =====================================
// CONFIGURAÇÕES GLOBAIS
// =====================================
const CONFIG = {
    apiUrl: window.location.origin,
    animationDuration: 400,
    scrollOffset: 100,
    typewriterSpeed: 100,
    counterSpeed: 2000
};

// =====================================
// UTILITÁRIOS
// =====================================
const Utils = {
    // Debounce para otimizar performance
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Smooth scroll
    smoothScrollTo: (element, offset = 0) => {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    },

    // Verificar se elemento está visível
    isElementInViewport: (el) => {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    // Formatar números
    formatNumber: (num) => {
        return new Intl.NumberFormat('pt-BR').format(num);
    },

    // Gerar ID único  
    generateId: () => {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    }
};

// =====================================
// GESTÃO DE TEMAS E CORES
// =====================================
const ThemeManager = {
    init: () => {
        ThemeManager.applyTheme();
        ThemeManager.setupColorScheme();
    },

    applyTheme: () => {
        // CSS Custom Properties dinâmicas
        const root = document.documentElement;
        
        // Cores dinâmicas baseadas na hora do dia
        const hour = new Date().getHours();
        let primaryColor, accentColor;
        
        if (hour >= 6 && hour < 12) {
            // Manhã - tons mais claros
            primaryColor = '#1565c0';
            accentColor = '#ff8f00';
        } else if (hour >= 12 && hour < 18) {
            // Tarde - tons normais
            primaryColor = '#1351b4';
            accentColor = '#ff7b00';
        } else {
            // Noite - tons mais escuros
            primaryColor = '#0d47a1';
            accentColor = '#f57c00';
        }
        
        root.style.setProperty('--dynamic-primary', primaryColor);
        root.style.setProperty('--dynamic-accent', accentColor);
    },

    setupColorScheme: () => {
        // Detectar preferência do sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode-preferred');
        }
    }
};

// =====================================
// ANIMAÇÕES E EFEITOS VISUAIS
// =====================================
const AnimationManager = {
    observers: new Map(),

    init: () => {
        AnimationManager.setupIntersectionObservers();
        AnimationManager.setupParallaxEffects();
        AnimationManager.setupHoverEffects();
        AnimationManager.setupScrollEffects();
    },

    setupIntersectionObservers: () => {
        // Observer para animações de entrada
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    
                    // Animações específicas por tipo
                    if (entry.target.classList.contains('stat-number')) {
                        AnimationManager.animateCounter(entry.target);
                    }
                    
                    if (entry.target.classList.contains('news-card')) {
                        AnimationManager.staggerAnimation(entry.target);
                    }
                }
            });
        }, observerOptions);

        // Aplicar observer a elementos
        document.querySelectorAll('.hero-card, .news-card, .stat-card, .service-card, .discord-card')
            .forEach(el => animationObserver.observe(el));

        AnimationManager.observers.set('animation', animationObserver);
    },

    animateCounter: (element) => {
        const target = parseInt(element.dataset.count || element.textContent.replace(/[^\d]/g, ''));
        const duration = CONFIG.counterSpeed;
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Utils.formatNumber(Math.floor(current));
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = Utils.formatNumber(target);
                element.classList.add('counter-complete');
            }
        };

        updateCounter();
    },

    staggerAnimation: (container) => {
        const children = container.children;
        Array.from(children).forEach((child, index) => {
            setTimeout(() => {
                child.classList.add('stagger-animate');
            }, index * 100);
        });
    },

    setupParallaxEffects: () => {
        const parallaxElements = document.querySelectorAll('.parallax');
        
        const handleParallax = Utils.debounce(() => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const rate = scrolled * -0.5;
                element.style.transform = `translateY(${rate}px)`;
            });
        }, 10);

        window.addEventListener('scroll', handleParallax);
    },

    setupHoverEffects: () => {
        // Efeito 3D nos cards
        document.querySelectorAll('.news-card, .service-card, .stat-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
            });
        });
    },

    setupScrollEffects: () => {
        let ticking = false;
        
        const updateScrollEffects = () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.3;
            
            // Parallax no hero
            const hero = document.querySelector('.hero-section');
            if (hero) {
                hero.style.backgroundPosition = `center ${rate}px`;
            }
            
            // Header transparência
            const header = document.querySelector('.header-govbr');
            if (header) {
                if (scrolled > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
            
            ticking = false;
        };
        
        const requestScrollUpdate = () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollEffects);
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', requestScrollUpdate);
    }
};

// =====================================
// MENU MOBILE RESPONSIVO
// =====================================
const MobileMenuManager = {
    menuToggle: null,
    menuContainer: null,
    isMenuOpen: false,

    init: () => {
        MobileMenuManager.menuToggle = document.querySelector('.mobile-menu-toggle');
        MobileMenuManager.menuContainer = document.querySelector('.nav-menu-container');
        
        if (MobileMenuManager.menuToggle && MobileMenuManager.menuContainer) {
            MobileMenuManager.setupEvents();
        }
    },

    setupEvents: () => {
        // Toggle do menu
        MobileMenuManager.menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            MobileMenuManager.toggle();
        });

        // Fechar menu ao clicar em link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 992) {
                    MobileMenuManager.close();
                }
            });
        });

        // Fechar menu ao clicar fora
        document.addEventListener('click', (e) => {
            if (MobileMenuManager.isMenuOpen && 
                !MobileMenuManager.menuContainer.contains(e.target) &&
                !MobileMenuManager.menuToggle.contains(e.target)) {
                MobileMenuManager.close();
            }
        });

        // Fechar menu ao redimensionar tela
        window.addEventListener('resize', Utils.debounce(() => {
            if (window.innerWidth > 992 && MobileMenuManager.isMenuOpen) {
                MobileMenuManager.close();
            }
        }, 250));

        // Fechar menu com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && MobileMenuManager.isMenuOpen) {
                MobileMenuManager.close();
            }
        });
    },

    toggle: () => {
        if (MobileMenuManager.isMenuOpen) {
            MobileMenuManager.close();
        } else {
            MobileMenuManager.open();
        }
    },

    open: () => {
        MobileMenuManager.isMenuOpen = true;
        MobileMenuManager.menuToggle.classList.add('active');
        MobileMenuManager.menuContainer.classList.add('active');
        
        // Adicionar blur ao fundo
        document.body.classList.add('menu-blur');
        
        // Animar links com delay
        const navLinks = MobileMenuManager.menuContainer.querySelectorAll('.nav-link');
        navLinks.forEach((link, index) => {
            link.style.animationDelay = `${index * 0.1}s`;
            link.classList.add('nav-link-animate');
        });
        
        // Bloquear scroll
        document.body.style.overflow = 'hidden';
    },

    close: () => {
        MobileMenuManager.isMenuOpen = false;
        MobileMenuManager.menuToggle.classList.remove('active');
        MobileMenuManager.menuContainer.classList.remove('active');
        
        // Remover blur do fundo
        document.body.classList.remove('menu-blur');
        
        // Remover animações dos links
        const navLinks = MobileMenuManager.menuContainer.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.style.animationDelay = '';
            link.classList.remove('nav-link-animate');
        });
        
        // Restaurar scroll
        document.body.style.overflow = '';
    }
};

// =====================================
// GESTÃO DE MODAIS
// =====================================
const ModalManager = {
    activeModal: null,
    
    init: () => {
        ModalManager.setupModalEvents();
        ModalManager.setupBlurEffect();
    },

    show: (modalId) => {
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        ModalManager.activeModal = modal;
        modal.show();
        
        // Adicionar blur ao fundo
        document.body.classList.add('modal-blur');
        
        // Animação de entrada personalizada
        const modalElement = document.getElementById(modalId);
        modalElement.classList.add('modal-enter');
        
        setTimeout(() => {
            modalElement.classList.remove('modal-enter');
        }, CONFIG.animationDuration);
    },

    hide: (modalId) => {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
        
        document.body.classList.remove('modal-blur');
        ModalManager.activeModal = null;
    },

    setupModalEvents: () => {
        // Botões de abertura de modais
        document.querySelectorAll('[data-modal-target]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = button.dataset.modalTarget;
                ModalManager.show(modalId);
            });
        });

        // Fechar modal com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && ModalManager.activeModal) {
                ModalManager.activeModal.hide();
            }
        });
    },

    setupBlurEffect: () => {
        // Eventos do Bootstrap para gerenciar blur
        document.addEventListener('show.bs.modal', () => {
            document.body.classList.add('modal-blur');
        });
        
        document.addEventListener('hidden.bs.modal', () => {
            document.body.classList.remove('modal-blur');
        });
    }
};

// =====================================
// SISTEMA DE BUSCA AVANÇADA
// =====================================
const SearchManager = {
    searchInput: null,
    searchResults: null,
    searchTimeout: null,

    init: () => {
        SearchManager.searchInput = document.getElementById('searchInput');
        SearchManager.setupSearchEvents();
        SearchManager.createSearchResults();
    },

    setupSearchEvents: () => {
        if (!SearchManager.searchInput) return;

        SearchManager.searchInput.addEventListener('input', Utils.debounce((e) => {
            const query = e.target.value.trim();
            
            if (query.length >= 2) {
                SearchManager.performSearch(query);
            } else {
                SearchManager.hideResults();
            }
        }, 300));

        SearchManager.searchInput.addEventListener('focus', () => {
            SearchManager.searchInput.parentElement.classList.add('search-focused');
        });

        SearchManager.searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                SearchManager.searchInput.parentElement.classList.remove('search-focused');
                SearchManager.hideResults();
            }, 200);
        });

        // Busca com Enter
        SearchManager.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = e.target.value.trim();
                if (query) {
                    SearchManager.executeSearch(query);
                }
            }
        });
    },

    createSearchResults: () => {
        const container = SearchManager.searchInput.parentElement;
        SearchManager.searchResults = document.createElement('div');
        SearchManager.searchResults.className = 'search-results';
        SearchManager.searchResults.style.display = 'none';
        container.appendChild(SearchManager.searchResults);
    },

    performSearch: async (query) => {
        try {
            SearchManager.showLoading();
            
            // Redirecionar para o Portal da Transparência para busca de servidores
            if (query.trim()) {
                window.location.href = `/portal-transparencia/?q=${encodeURIComponent(query)}`;
                return;
            }
            
            SearchManager.displayResults([]);
        } catch (error) {
            console.error('Erro na busca:', error);
            SearchManager.showError('Erro ao realizar busca');
        }
    },

    displayResults: (results) => {
        if (results.length === 0) {
            SearchManager.searchResults.innerHTML = `
                <div class="search-no-results">
                    <i class="fas fa-search"></i>
                    <p>Nenhum resultado encontrado</p>
                </div>
            `;
        } else {
            SearchManager.searchResults.innerHTML = results.map(result => `
                <div class="search-result-item" onclick="SearchManager.selectResult('${result.url}')">
                    <div class="search-result-icon">
                        <i class="${result.icon || 'fas fa-file-text'}"></i>
                    </div>
                    <div class="search-result-content">
                        <h6>${result.title}</h6>
                        <p>${result.description}</p>
                        <span class="search-result-type">${result.type}</span>
                    </div>
                </div>
            `).join('');
        }
        
        SearchManager.showResults();
    },

    selectResult: (url) => {
        window.location.href = url;
    },

    showLoading: () => {
        SearchManager.searchResults.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <p>Buscando...</p>
            </div>
        `;
        SearchManager.showResults();
    },

    showError: (message) => {
        SearchManager.searchResults.innerHTML = `
            <div class="search-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
        SearchManager.showResults();
    },

    showResults: () => {
        SearchManager.searchResults.style.display = 'block';
        SearchManager.searchResults.classList.add('search-results-show');
    },

    hideResults: () => {
        SearchManager.searchResults.style.display = 'none';
        SearchManager.searchResults.classList.remove('search-results-show');
    },

    executeSearch: (query) => {
        // Redirecionar para Portal da Transparência
        window.location.href = `/portal-transparencia/?q=${encodeURIComponent(query)}`;
    }
};

// =====================================
// SLIDE DE NOTÍCIAS AVANÇADO
// =====================================
const NewsSlider = {
    swiper: null,
    autoplayTimer: null,

    init: () => {
        if (typeof Swiper !== 'undefined') {
            NewsSlider.initSwiper();
        } else {
            NewsSlider.initFallback();
        }
        
        NewsSlider.setupNewsInteractions();
    },

    initSwiper: () => {
        NewsSlider.swiper = new Swiper('.news-swiper', {
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
                dynamicBullets: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            effect: 'coverflow',
            coverflowEffect: {
                rotate: 30,
                stretch: 0,
                depth: 100,
                modifier: 1,
                slideShadows: true,
            },
            breakpoints: {
                768: {
                    effect: 'slide',
                    slidesPerView: 1,
                },
                1024: {
                    effect: 'coverflow',
                    slidesPerView: 1,
                }
            }
        });
    },

    initFallback: () => {
        // Fallback para quando Swiper não está disponível
        const newsContainer = document.querySelector('.news-slider');
        if (!newsContainer) return;

        const slides = newsContainer.querySelectorAll('.news-slide');
        let currentSlide = 0;

        const showSlide = (index) => {
            slides.forEach((slide, i) => {
                slide.style.display = i === index ? 'block' : 'none';
                slide.classList.toggle('active', i === index);
            });
        };

        const nextSlide = () => {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        };

        // Auto-play
        NewsSlider.autoplayTimer = setInterval(nextSlide, 5000);

        // Controles manuais
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                currentSlide = currentSlide > 0 ? currentSlide - 1 : slides.length - 1;
                showSlide(currentSlide);
            } else if (e.key === 'ArrowRight') {
                nextSlide();
            }
        });

        showSlide(0);
    },

    setupNewsInteractions: () => {
        // Tracking de visualizações
        document.querySelectorAll('.news-card, .news-slide').forEach(element => {
            element.addEventListener('click', (e) => {
                const newsId = element.dataset.newsId;
                if (newsId) {
                    NewsSlider.trackView(newsId);
                }
            });
        });

        // Compartilhamento social
        document.querySelectorAll('.share-news').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const newsTitle = button.dataset.title;
                const newsUrl = button.dataset.url;
                
                if (navigator.share) {
                    navigator.share({
                        title: newsTitle,
                        url: newsUrl
                    });
                } else {
                    NewsSlider.showShareModal(newsTitle, newsUrl);
                }
            });
        });
    },

    trackView: async (newsId) => {
        try {
            await fetch(`${CONFIG.apiUrl}/api/noticias/${newsId}/visualizar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    'Content-Type': 'application/json',
                },
            });
        } catch (error) {
            console.error('Erro ao registrar visualização:', error);
        }
    },

    showShareModal: (title, url) => {
        const modal = document.createElement('div');
        modal.className = 'share-modal';
        modal.innerHTML = `
            <div class="share-modal-content">
                <h5>Compartilhar Notícia</h5>
                <p>${title}</p>
                <div class="share-buttons">
                    <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}" target="_blank" class="share-btn twitter">
                        <i class="fab fa-twitter"></i> Twitter
                    </a>
                    <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}" target="_blank" class="share-btn facebook">
                        <i class="fab fa-facebook"></i> Facebook
                    </a>
                    <a href="https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}" target="_blank" class="share-btn whatsapp">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </a>
                    <button onclick="navigator.clipboard.writeText('${url}'); this.textContent='Copiado!'" class="share-btn copy">
                        <i class="fas fa-copy"></i> Copiar Link
                    </button>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="btn-close-share">×</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Auto-remover após 10 segundos
        setTimeout(() => {
            if (modal.parentElement) {
                modal.remove();
            }
        }, 10000);
    }
};

// =====================================
// ESTATÍSTICAS DINÂMICAS
// =====================================
const StatsManager = {
    init: () => {
        StatsManager.setupCounters();
        StatsManager.setupRealTimeUpdates();
        StatsManager.setupStatCharts();
    },

    setupCounters: () => {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(element => {
            const finalValue = parseInt(element.dataset.count || element.textContent.replace(/[^\d]/g, ''));
            element.dataset.count = finalValue;
            element.textContent = '0';
        });
    },

    setupRealTimeUpdates: () => {
        // Atualizações em tempo real desabilitadas para o Portal da Transparência
        // As estatísticas são carregadas diretamente do servidor
        console.log('Real-time updates disabled for Portal da Transparência');
    },

    updateStats: (data) => {
        Object.keys(data).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                const newValue = data[key];
                const currentValue = parseInt(element.dataset.count);
                
                if (newValue !== currentValue) {
                    element.dataset.count = newValue;
                    AnimationManager.animateCounter(element);
                    
                    // Efeito visual de atualização
                    element.classList.add('stat-updated');
                    setTimeout(() => {
                        element.classList.remove('stat-updated');
                    }, 2000);
                }
            }
        });
    },

    setupStatCharts: () => {
        // Mini gráficos nas estatísticas (usando Chart.js se disponível)
        if (typeof Chart !== 'undefined') {
            document.querySelectorAll('.stat-chart').forEach(canvas => {
                const data = JSON.parse(canvas.dataset.chartData || '[]');
                
                new Chart(canvas, {
                    type: 'line',
                    data: {
                        labels: data.labels || [],
                        datasets: [{
                            data: data.values || [],
                            backgroundColor: 'rgba(19, 81, 180, 0.1)',
                            borderColor: '#1351b4',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: { display: false },
                            y: { display: false }
                        }
                    }
                });
            });
        }
    }
};

// =====================================
// NAVEGAÇÃO E SCROLL
// =====================================
const NavigationManager = {
    init: () => {
        NavigationManager.setupSmoothScroll();
        NavigationManager.setupActiveLinks();
        NavigationManager.setupScrollToTop();
        NavigationManager.setupMobileMenu();
    },

    setupSmoothScroll: () => {
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    Utils.smoothScrollTo(targetElement, CONFIG.scrollOffset);
                }
            });
        });
    },

    setupActiveLinks: () => {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        const updateActiveLink = () => {
            let current = '';
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - CONFIG.scrollOffset;
                if (pageYOffset >= sectionTop) {
                    current = section.getAttribute('id');
                }
            });
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        };
        
        window.addEventListener('scroll', Utils.debounce(updateActiveLink, 100));
    },

    setupScrollToTop: () => {
        const scrollTopBtn = document.createElement('button');
        scrollTopBtn.className = 'scroll-to-top';
        scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollTopBtn.style.display = 'none';
        document.body.appendChild(scrollTopBtn);
        
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        window.addEventListener('scroll', Utils.debounce(() => {
            if (window.pageYOffset > 300) {
                scrollTopBtn.style.display = 'block';
                setTimeout(() => scrollTopBtn.classList.add('show'), 10);
            } else {
                scrollTopBtn.classList.remove('show');
                setTimeout(() => scrollTopBtn.style.display = 'none', 300);
            }
        }, 100));
    },

    setupMobileMenu: () => {
        const mobileToggle = document.querySelector('.navbar-toggler');
        const mobileMenu = document.querySelector('.navbar-collapse');
        
        if (mobileToggle && mobileMenu) {
            mobileToggle.addEventListener('click', () => {
                mobileMenu.classList.toggle('show');
                mobileToggle.classList.toggle('active');
            });
            
            // Fechar menu ao clicar em link
            document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.remove('show');
                    mobileToggle.classList.remove('active');
                });
            });
        }
    }
};

// =====================================
// PERFORMANCE E MONITORAMENTO
// =====================================
const PerformanceManager = {
    metrics: new Map(),

    init: () => {
        PerformanceManager.measureLoadTime();
        PerformanceManager.setupErrorTracking();
        PerformanceManager.monitorConnectivity();
    },

    measureLoadTime: () => {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            PerformanceManager.metrics.set('loadTime', perfData.loadEventEnd - perfData.loadEventStart);
            
            // Log performance
            console.log('Performance Metrics:', Object.fromEntries(PerformanceManager.metrics));
        });
    },

    setupErrorTracking: () => {
        window.addEventListener('error', (e) => {
            console.error('JavaScript Error:', {
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
                colno: e.colno,
                error: e.error
            });
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled Promise Rejection:', e.reason);
        });
    },

    monitorConnectivity: () => {
        const updateOnlineStatus = () => {
            if (navigator.onLine) {
                NotificationManager.show('Conexão restaurada', 'success', 3000);
                document.body.classList.remove('offline');
            } else {
                NotificationManager.show('Você está offline', 'warning', 0);
                document.body.classList.add('offline');
            }
        };

        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
    }
};

// =====================================
// INICIALIZAÇÃO PRINCIPAL
// =====================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando GovBR Roleplay...');
    
    // Inicializar NotificationManager
    NotificationManager.init();
    
    // Inicializar outros módulos
    ThemeManager.init();
    AnimationManager.init();
    MobileMenuManager.init();
    ModalManager.init();
    SearchManager.init();
    NewsSlider.init();
    StatsManager.init();
    NavigationManager.init();
    PerformanceManager.init();
    AuthManager.init();
    DropdownManager.init();
    
    // Configurar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configurar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Configurar dropdowns
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });

    // Configurar modais
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });

    // Configurar formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                NotificationManager.showValidationError(form);
            }
            form.classList.add('was-validated');
        });

        // Adicionar nomes amigáveis aos campos
        const fields = form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            const label = form.querySelector(`label[for="${field.id}"]`);
            if (label) {
                field.setAttribute('data-field-name', label.textContent.replace('*', '').trim());
            }
        });
    });

    // Configurar formulário de login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!loginForm.checkValidity()) {
                NotificationManager.showValidationError(loginForm);
                return;
            }

            try {
                const formData = new FormData(loginForm);
                const response = await fetch('/usuarios/api/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        username: formData.get('username'),
                        password: formData.get('password')
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    NotificationManager.showFormSuccess('Login realizado com sucesso!');
                } else {
                    NotificationManager.showFormError(data.error || 'Erro ao fazer login');
                }
            } catch (error) {
                NotificationManager.showConnectionError();
            }
        });
    }

    // Configurar formulário de alteração de senha
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!changePasswordForm.checkValidity()) {
                NotificationManager.showValidationError(changePasswordForm);
                return;
            }

            try {
                const formData = new FormData(changePasswordForm);
                const response = await fetch('/usuarios/api/alterar-senha/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        senha_atual: formData.get('senha_atual'),
                        nova_senha: formData.get('nova_senha'),
                        confirmar_senha: formData.get('confirmar_senha')
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    NotificationManager.showFormSuccess('Senha alterada com sucesso!');
                    bootstrap.Modal.getInstance(document.getElementById('changePasswordModal')).hide();
                } else {
                    NotificationManager.showFormError(data.error || 'Erro ao alterar senha');
                }
            } catch (error) {
                NotificationManager.showConnectionError();
            }
        });
    }

    // Configurar formulário de alteração de nome
    const changeNameForm = document.getElementById('changeNameForm');
    if (changeNameForm) {
        changeNameForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!changeNameForm.checkValidity()) {
                NotificationManager.showValidationError(changeNameForm);
                return;
            }

            try {
                const formData = new FormData(changeNameForm);
                const response = await fetch('/usuarios/api/solicitar-alteracao-nome/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        novo_nome: formData.get('novo_nome'),
                        motivo: formData.get('motivo')
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    NotificationManager.showFormSuccess('Solicitação de alteração de nome enviada com sucesso!');
                    bootstrap.Modal.getInstance(document.getElementById('changeNameModal')).hide();
                } else {
                    NotificationManager.showFormError(data.error || 'Erro ao solicitar alteração de nome');
                }
            } catch (error) {
                NotificationManager.showConnectionError();
            }
        });
    }

    // Configurar formulário de cidadania
    const citizenshipForm = document.getElementById('citizenshipForm');
    if (citizenshipForm) {
        citizenshipForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!citizenshipForm.checkValidity()) {
                NotificationManager.showValidationError(citizenshipForm);
                return;
            }

            try {
                const formData = new FormData(citizenshipForm);
                const response = await fetch('/usuarios/api/solicitar-cidadania/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        motivo: formData.get('motivo')
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    NotificationManager.showFormSuccess('Solicitação de cidadania enviada com sucesso!');
                    bootstrap.Modal.getInstance(document.getElementById('citizenshipModal')).hide();
                } else {
                    NotificationManager.showFormError(data.error || 'Erro ao solicitar cidadania');
                }
            } catch (error) {
                NotificationManager.showConnectionError();
            }
        });
    }

    // Configurações globais
    setupGlobalEvents();
    setupAccessibility();
    setupPWA();
    
    console.log('✅ GovBR Roleplay carregado com sucesso!');
});

// =====================================
// CONFIGURAÇÕES GLOBAIS
// =====================================
function setupGlobalEvents() {
    // Lazy loading de imagens
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Prevenção de FOUC (Flash of Unstyled Content)
    document.documentElement.classList.add('loaded');
}

function setupAccessibility() {
    // Navegação por teclado
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });

    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });

    // Skip links
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Pular para o conteúdo principal';
    document.body.insertBefore(skipLink, document.body.firstChild);
}

function setupPWA() {
    // Verificar se é PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
        document.body.classList.add('pwa-mode');
    }

    // Prompt de instalação
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Mostrar botão de instalação personalizado
        const installBtn = document.createElement('button');
        installBtn.className = 'install-app-btn';
        installBtn.innerHTML = '<i class="fas fa-download"></i> Instalar App';
        installBtn.addEventListener('click', () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('PWA instalado');
                }
                deferredPrompt = null;
                installBtn.remove();
            });
        });
        
        document.body.appendChild(installBtn);
    });
}

// =====================================
// UTILITÁRIOS GLOBAIS
// =====================================
// =====================================
// SISTEMA DE AUTENTICAÇÃO
// =====================================
const AuthManager = {
    currentStep: 1,
    registrationData: {},

    init: () => {
        AuthManager.setupLoginForm();
        AuthManager.setupRegistrationForms();
        AuthManager.setupModalEvents();
    },

    setupLoginForm: () => {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', AuthManager.handleLogin);
        }
    },

    setupRegistrationForms: () => {
        // Passo 1 - Dados básicos
        const step1Form = document.getElementById('registerStep1Form');
        if (step1Form) {
            step1Form.addEventListener('submit', AuthManager.handleRegistrationStep1);
        }

        // Passo 2 - Verificação
        const verifyBtn = document.getElementById('verify-code-btn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', AuthManager.handleVerifyCode);
        }

        // Passo 3 - Criar senha
        const step3Form = document.getElementById('registerStep3Form');
        if (step3Form) {
            step3Form.addEventListener('submit', AuthManager.handleRegistrationStep3);
        }
    },

    setupModalEvents: () => {
        // Reset modal ao fechar
        const registerModal = document.getElementById('registerModal');
        if (registerModal) {
            registerModal.addEventListener('hidden.bs.modal', () => {
                AuthManager.resetRegistrationModal();
            });
        }
    },

    handleLogin: async (e) => {
        e.preventDefault();
        
        const btn = e.target.querySelector('button[type="submit"]');
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');
        
        const username = document.getElementById('login_username').value.trim();
        const password = document.getElementById('login_password').value;

        if (!username || !password) {
            NotificationManager.show('Preencha todos os campos', 'error');
            return;
        }

        // Mostrar loading
        btnText.classList.add('d-none');
        btnLoading.classList.remove('d-none');
        btn.disabled = true;

        try {
            const response = await fetch('/usuarios/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': AuthManager.getCSRFToken()
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (data.success) {
                NotificationManager.show(data.message, 'success');
                setTimeout(() => {
                    window.location.href = data.redirect || '/';
                }, 1000);
            } else {
                NotificationManager.show(data.error, 'error');
            }
        } catch (error) {
            NotificationManager.show('Erro de conexão. Tente novamente.', 'error');
        } finally {
            // Esconder loading
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
            btn.disabled = false;
        }
    },

    handleRegistrationStep1: async (e) => {
        e.preventDefault();
        
        const btn = e.target.querySelector('button[type="submit"]');
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');
        
        const nomeCompleto = document.getElementById('reg_nome_completo').value.trim();
        const robloxId = document.getElementById('reg_roblox_id').value.trim();

        if (!nomeCompleto || !robloxId) {
            NotificationManager.show('Preencha todos os campos', 'error');
            return;
        }

        // Mostrar loading
        btnText.classList.add('d-none');
        btnLoading.classList.remove('d-none');
        btn.disabled = true;

        try {
            const response = await fetch('/usuarios/api/registro/step1/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': AuthManager.getCSRFToken()
                },
                body: JSON.stringify({
                    nome_completo: nomeCompleto,
                    roblox_id: robloxId
                })
            });

            const data = await response.json();

            if (data.success) {
                AuthManager.registrationData = {
                    nome_completo: nomeCompleto,
                    roblox_id: robloxId,
                    roblox_username: data.roblox_username,
                    avatar_url: data.avatar_url
                };
                
                await AuthManager.proceedToStep2();
            } else {
                NotificationManager.show(data.error, 'error');
            }
        } catch (error) {
            NotificationManager.show('Erro de conexão. Tente novamente.', 'error');
        } finally {
            // Esconder loading
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
            btn.disabled = false;
        }
    },

    proceedToStep2: async () => {
        try {
            const response = await fetch('/usuarios/api/registro/step2/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': AuthManager.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                // Atualizar interface do passo 2
                document.getElementById('roblox-username').textContent = data.roblox_username;
                document.getElementById('roblox-avatar').src = AuthManager.registrationData.avatar_url || '/static/images/default-avatar.png';
                document.getElementById('verification-code').value = data.codigo;
                
                AuthManager.goToStep(2);
            } else {
                NotificationManager.show(data.error, 'error');
            }
        } catch (error) {
            NotificationManager.show('Erro ao gerar código de verificação', 'error');
        }
    },

    handleVerifyCode: async () => {
        const btn = document.getElementById('verify-code-btn');
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');

        // Mostrar loading
        btnText.classList.add('d-none');
        btnLoading.classList.remove('d-none');
        btn.disabled = true;

        try {
            const response = await fetch('/usuarios/api/verificar-codigo/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': AuthManager.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                NotificationManager.show(data.message, 'success');
                setTimeout(() => {
                    AuthManager.goToStep(3);
                }, 1000);
            } else {
                NotificationManager.show(data.error, 'error');
            }
        } catch (error) {
            NotificationManager.show('Erro de conexão. Tente novamente.', 'error');
        } finally {
            // Esconder loading
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
            btn.disabled = false;
        }
    },

    handleRegistrationStep3: async (e) => {
        e.preventDefault();
        
        const btn = e.target.querySelector('button[type="submit"]');
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');
        
        const password = document.getElementById('reg_password').value;
        const passwordConfirm = document.getElementById('reg_password_confirm').value;

        if (!password || !passwordConfirm) {
            NotificationManager.show('Preencha todos os campos', 'error');
            return;
        }

        if (password !== passwordConfirm) {
            NotificationManager.show('As senhas não coincidem', 'error');
            return;
        }

        if (password.length < 8) {
            NotificationManager.show('A senha deve ter pelo menos 8 caracteres', 'error');
            return;
        }

        // Mostrar loading
        btnText.classList.add('d-none');
        btnLoading.classList.remove('d-none');
        btn.disabled = true;

        try {
            const response = await fetch('/usuarios/api/registro/step3/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': AuthManager.getCSRFToken()
                },
                body: JSON.stringify({
                    password: password,
                    password_confirm: passwordConfirm
                })
            });

            const data = await response.json();

            if (data.success) {
                NotificationManager.show(data.message, 'success');
                setTimeout(() => {
                    window.location.href = data.redirect || '/';
                }, 2000);
            } else {
                NotificationManager.show(data.error, 'error');
            }
        } catch (error) {
            NotificationManager.show('Erro de conexão. Tente novamente.', 'error');
        } finally {
            // Esconder loading
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
            btn.disabled = false;
        }
    },

    goToStep: (step) => {
        // Esconder todos os passos
        for (let i = 1; i <= 3; i++) {
            const stepElement = document.getElementById(`register-step-${i}`);
            if (stepElement) {
                stepElement.classList.add('d-none');
            }
        }

        // Mostrar passo atual
        const currentStepElement = document.getElementById(`register-step-${step}`);
        if (currentStepElement) {
            currentStepElement.classList.remove('d-none');
        }

        // Atualizar título
        const titles = {
            1: 'Criar Conta - Passo 1',
            2: 'Criar Conta - Passo 2',
            3: 'Criar Conta - Passo 3'
        };
        
        const titleElement = document.getElementById('register-title');
        if (titleElement) {
            titleElement.textContent = titles[step];
        }

        AuthManager.currentStep = step;
    },

    resetRegistrationModal: () => {
        AuthManager.currentStep = 1;
        AuthManager.registrationData = {};
        
        // Limpar formulários
        const forms = ['registerStep1Form', 'registerStep3Form'];
        forms.forEach(formId => {
            const form = document.getElementById(formId);
            if (form) {
                form.reset();
            }
        });

        // Voltar ao passo 1
        AuthManager.goToStep(1);
    },

    getCSRFToken: () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            return token.value;
        }
        
        // Fallback: tentar obter do cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        return '';
    }
};

// Função global para copiar código
window.copyCode = () => {
    const codeInput = document.getElementById('verification-code');
    if (codeInput) {
        codeInput.select();
        document.execCommand('copy');
        NotificationManager.show('Código copiado!', 'success', 2000);
    }
};

// Função global para navegar entre passos
window.goToStep = (step) => {
    AuthManager.goToStep(step);
};

// =====================================
// GERENCIADOR DE DROPDOWN
// =====================================
const DropdownManager = {
    init: () => {
        DropdownManager.setupDropdownPositioning();
        DropdownManager.setupDropdownEvents();
    },

    setupDropdownPositioning: () => {
        // Garantir que o dropdown apareça corretamente
        document.addEventListener('shown.bs.dropdown', (e) => {
            const dropdown = e.target;
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (menu) {
                // Forçar reposicionamento
                menu.style.position = 'absolute';
                menu.style.zIndex = '1061';
            }
        });
    },

    setupDropdownEvents: () => {
        // Fechar dropdown ao rolar a página (comportamento padrão)
        window.addEventListener('scroll', Utils.debounce(() => {
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(menu => {
                const dropdown = menu.closest('.dropdown');
                if (dropdown) {
                    const dropdownToggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
                    if (dropdownToggle) {
                        const bsDropdown = bootstrap.Dropdown.getInstance(dropdownToggle);
                        if (bsDropdown) {
                            bsDropdown.hide();
                        }
                    }
                }
            });
        }, 50));
    }
};

window.GovBR = {
    Utils,
    ThemeManager,
    AnimationManager,
    MobileMenuManager,
    ModalManager,
    SearchManager,
    NewsSlider,
    StatsManager,
    NavigationManager,
    NotificationManager,
    PerformanceManager,
    AuthManager,
    DropdownManager
};

function nomearUsuario(userId, nomeCompleto) {
    // Obter lista de cargos disponíveis para nomeação
    fetch(`/api/cargos-disponiveis/`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || 'Erro ao carregar cargos');
            }
            
            // Preencher o select de cargos
            const cargoSelect = document.getElementById('cargoSelect');
            cargoSelect.innerHTML = '<option value="">Selecione...</option>';
            data.cargos.forEach(cargo => {
                const option = document.createElement('option');
                option.value = cargo.id;
                option.textContent = `${cargo.simbolo_display} ${cargo.nome} - ${cargo.entidade}`;
                cargoSelect.appendChild(option);
            });
            
            // Preencher os campos do modal
            document.getElementById('usuarioIdNomeacao').value = userId;
            document.getElementById('nomeUsuarioNomeacao').textContent = nomeCompleto;
            document.getElementById('observacoesNomeacao').value = '';
            
            // Mostrar o modal
            const modal = new bootstrap.Modal(document.getElementById('modalNomeacao'));
            modal.show();
        })
        .catch(error => {
            console.error('Erro ao carregar cargos:', error);
            alert('Erro ao carregar lista de cargos disponíveis. Por favor, tente novamente.');
        });
}

function confirmarNomeacao() {
    const usuarioId = document.getElementById('usuarioIdNomeacao').value;
    const cargoId = document.getElementById('cargoSelect').value;
    const observacoes = document.getElementById('observacoesNomeacao').value;
    
    if (!cargoId) {
        alert('Por favor, selecione um cargo.');
        return;
    }

    // Enviar requisição de nomeação
    fetch('/api/nomear-usuario/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            usuario_id: usuarioId,
            cargo_id: cargoId,
            observacoes: observacoes
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Erro ao nomear usuário');
            });
        }
        return response.json();
    })
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Erro ao nomear usuário');
        }
        
        // Fechar o modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalNomeacao'));
        if (modal) {
            modal.hide();
        }
        
        // Mostrar mensagem de sucesso
        alert(data.message || 'Usuário nomeado com sucesso!');
        
        // Recarregar a página para atualizar a lista
        window.location.reload();
    })
    .catch(error => {
        console.error('Erro na nomeação:', error);
        alert(error.message || 'Erro ao nomear usuário. Por favor, tente novamente.');
    });
}

// Função auxiliar para obter o token CSRF
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function promoverUsuario(usuarioId, nomeUsuario, cargoAtual, entidadeId) {
    console.log('🚀 Função promoverUsuario chamada:', {usuarioId, nomeUsuario, cargoAtual, entidadeId});
    
    // Preencher os campos do modal
    document.getElementById('usuarioIdPromocao').value = usuarioId;
    document.getElementById('entidadeIdPromocao').value = entidadeId;
    document.getElementById('nomeUsuarioPromocao').textContent = nomeUsuario;
    document.getElementById('cargoAtualPromocao').textContent = cargoAtual;
    document.getElementById('observacoesPromocao').value = '';
    
    // Carregar cargos da mesma entidade
    carregarCargosEntidade(entidadeId);
    
    // Mostrar o modal
    const modal = new bootstrap.Modal(document.getElementById('modalPromocao'));
    modal.show();
}

// Função para carregar cargos da entidade
function carregarCargosEntidade(entidadeId) {
    const select = document.getElementById('cargoPromocaoSelect');
    select.innerHTML = '<option value="">Carregando...</option>';
    
    fetch(`/api/cargos-por-entidade/${entidadeId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                select.innerHTML = '<option value="">Selecione um cargo...</option>';
                data.cargos.forEach(cargo => {
                    const option = document.createElement('option');
                    option.value = cargo.id;
                    option.textContent = `${cargo.simbolo_icon} ${cargo.nome}`;
                    select.appendChild(option);
                });
            } else {
                select.innerHTML = '<option value="">Erro ao carregar cargos</option>';
                console.error('Erro:', data.error);
            }
        })
        .catch(error => {
            select.innerHTML = '<option value="">Erro ao carregar cargos</option>';
            console.error('Erro:', error);
        });
}

// Função para confirmar promoção
function confirmarPromocao() {
    const usuarioId = document.getElementById('usuarioIdPromocao').value;
    const cargoId = document.getElementById('cargoPromocaoSelect').value;
    const observacoes = document.getElementById('observacoesPromocao').value;
    
    if (!cargoId) {
        alert('Por favor, selecione um cargo.');
        return;
    }
    
    // Enviar requisição de promoção
    fetch('/painel-gestao-cargos/promover/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            usuario_id: usuarioId,
            cargo_id: cargoId,
            observacoes: observacoes
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Erro ao promover usuário');
            });
        }
        return response.json();
    })
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Erro ao promover usuário');
        }
        
        // Fechar o modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalPromocao'));
        if (modal) {
            modal.hide();
        }
        
        // Mostrar mensagem de sucesso
        alert(data.message || 'Usuário promovido com sucesso!');
        
        // Recarregar a página para atualizar a lista
        window.location.reload();
    })
    .catch(error => {
        console.error('Erro na promoção:', error);
        alert(error.message || 'Erro ao promover usuário. Por favor, tente novamente.');
    });
}

function exonerarUsuario(usuarioId, nomeUsuario, cargoUsuario) {
    // Preencher os campos do modal
    document.getElementById('usuarioIdExoneracao').value = usuarioId;
    document.getElementById('nomeUsuarioExoneracao').textContent = nomeUsuario;
    document.getElementById('cargoUsuarioExoneracao').textContent = cargoUsuario;
    document.getElementById('observacoesExoneracao').value = '';
    
    // Mostrar o modal
    const modal = new bootstrap.Modal(document.getElementById('modalExoneracao'));
    modal.show();
}

function confirmarExoneracao() {
    const usuarioId = document.getElementById('usuarioIdExoneracao').value;
    const observacoes = document.getElementById('observacoesExoneracao').value;
    
    if (!observacoes.trim()) {
        alert('Por favor, informe o motivo da exoneração.');
        return;
    }

    // Enviar requisição de exoneração
    fetch('/api/exonerar-usuario/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            usuario_id: usuarioId,
            observacoes: observacoes
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Erro ao exonerar usuário');
            });
        }
        return response.json();
    })
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Erro ao exonerar usuário');
        }
        
        // Fechar o modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalExoneracao'));
        if (modal) {
            modal.hide();
        }
        
        // Mostrar mensagem de sucesso
        alert(data.message || 'Usuário exonerado com sucesso!');
        
        // Recarregar a página para atualizar a lista
        window.location.reload();
    })
    .catch(error => {
        console.error('Erro na exoneração:', error);
        alert(error.message || 'Erro ao exonerar usuário. Por favor, tente novamente.');
    });
} 