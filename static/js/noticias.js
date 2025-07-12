class NoticiasManager {
    constructor() {
        this.setupEventListeners();
        this.initializeComponents();
    }
    
    setupEventListeners() {
        // Formulário de busca
        const searchForm = document.getElementById('filtrosForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitSearch();
            });
        }
        
        // Filtros de tipo
        document.querySelectorAll('input[name="tipo"]').forEach(input => {
            input.addEventListener('change', () => {
                searchForm.submit();
            });
        });
        
        // Preview de imagem
        const imagemPrincipal = document.getElementById('imagem_principal');
        if (imagemPrincipal) {
            imagemPrincipal.addEventListener('change', (e) => {
                this.handleImagePreview(e);
            });
        }
        
        // Formulário de notícia
        const noticiaForm = document.getElementById('noticiaForm');
        if (noticiaForm) {
            noticiaForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitNoticia(e);
            });
        }
    }
    
    initializeComponents() {
        // O TinyMCE foi removido - usando textarea simples
        
        // Inicializar Select2
        if (document.getElementById('categorias')) {
            $('#categorias').select2({
                placeholder: 'Selecione as categorias',
                allowClear: true
            });
        }
        
        if (document.getElementById('tags')) {
            $('#tags').select2({
                placeholder: 'Selecione as tags',
                allowClear: true,
                tags: true,
                createTag: (params) => {
                    return {
                        id: params.term,
                        text: params.term,
                        newTag: true
                    }
                }
            });
        }
        
        // Inicializar Dropzone
        if (document.getElementById('galeriaDropzone')) {
            Dropzone.autoDiscover = false;
            new Dropzone("#galeriaDropzone", {
                url: window.location.href,
                paramName: "galeria_imagens",
                maxFilesize: 5, // MB
                acceptedFiles: "image/*",
                addRemoveLinks: true,
                dictDefaultMessage: "Arraste imagens ou clique aqui",
                dictRemoveFile: "Remover",
                autoProcessQueue: false,
                uploadMultiple: true,
                init: function() {
                    this.on("addedfile", file => {
                        // Criar campos ocultos para legenda e ordem
                        const uniqueId = Math.random().toString(36).substr(2, 9);
                        file.uniqueId = uniqueId;
                        
                        const legendaInput = document.createElement('input');
                        legendaInput.type = 'text';
                        legendaInput.name = `legenda_${file.name}`;
                        legendaInput.placeholder = 'Legenda da imagem';
                        legendaInput.className = 'form-control form-control-sm mt-2';
                        
                        const ordemInput = document.createElement('input');
                        ordemInput.type = 'number';
                        ordemInput.name = `ordem_${file.name}`;
                        ordemInput.value = this.files.length;
                        ordemInput.className = 'form-control form-control-sm mt-2';
                        
                        file.previewElement.appendChild(legendaInput);
                        file.previewElement.appendChild(ordemInput);
                    });
                }
            });
        }
    }
    
    handleImagePreview(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.getElementById('imagemPreview');
                preview.style.display = 'block';
                preview.querySelector('img').src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    }
    
    submitSearch() {
        const form = document.getElementById('filtrosForm');
        const formData = new FormData(form);
        
        // Construir URL com parâmetros
        const params = new URLSearchParams();
        for (let [key, value] of formData.entries()) {
            if (value) params.append(key, value);
        }
        
        // Redirecionar para a URL com os filtros
        window.location.href = `${window.location.pathname}?${params.toString()}`;
    }
    
    submitNoticia(e) {
        const form = e.target;
        const formData = new FormData(form);
        
        // O conteúdo já está no FormData automaticamente
        
        // Adicionar imagens da galeria
        const dropzone = Dropzone.forElement("#galeriaDropzone");
        if (dropzone) {
            dropzone.files.forEach(file => {
                formData.append('galeria_imagens', file);
                
                // Adicionar legenda e ordem
                const legenda = file.previewElement.querySelector(`input[name="legenda_${file.name}"]`).value;
                const ordem = file.previewElement.querySelector(`input[name="ordem_${file.name}"]`).value;
                
                formData.append(`legenda_${file.name}`, legenda);
                formData.append(`ordem_${file.name}`, ordem);
            });
        }
        
        // Enviar formulário
        form.submit();
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new NoticiasManager();
    
    // Verificar se há swipers na página antes de inicializar
    const heroSwiperElement = document.querySelector('.hero-swiper');
    const heroSwiperImprensaElement = document.querySelector('.hero-swiper-imprensa');

    // Swiper do Governo
    if (heroSwiperElement) {
        // Verificar número de slides
        const slideCount = heroSwiperElement.querySelectorAll('.swiper-slide').length;
        
    const heroSwiper = new Swiper('.hero-swiper', {
        // Configurações básicas
        slidesPerView: 1,
        spaceBetween: 30,
            loop: slideCount > 1, // Só ativar loop se houver mais de 1 slide
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        },
            autoplay: slideCount > 1 ? {
            delay: 5000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
            } : false, // Só ativar autoplay se houver mais de 1 slide
        speed: 800,
        
        // Navegação
        navigation: {
            nextEl: '.hero-swiper .swiper-button-next',
            prevEl: '.hero-swiper .swiper-button-prev',
        },
        
        // Paginação
        pagination: {
            el: '.hero-swiper .swiper-pagination',
            clickable: true,
            dynamicBullets: true
        },
        
        // Lazy loading
        lazy: {
            loadPrevNext: true,
            loadPrevNextAmount: 2
        },
        
        // Callbacks
        on: {
                init: function() {
                    console.log('Hero Swiper inicializado com', slideCount, 'slides');
                    if (this.slides && this.slides[this.activeIndex]) {
                        animateSlide(this.slides[this.activeIndex]);
                    }
                    
                    // Ocultar navegação se houver apenas 1 slide
                    if (slideCount <= 1) {
                        const nextBtn = document.querySelector('.hero-swiper .swiper-button-next');
                        const prevBtn = document.querySelector('.hero-swiper .swiper-button-prev');
                        const pagination = document.querySelector('.hero-swiper .swiper-pagination');
                        
                        if (nextBtn) nextBtn.style.display = 'none';
                        if (prevBtn) prevBtn.style.display = 'none';
                        if (pagination) pagination.style.display = 'none';
                    }
                },
            slideChange: function() {
                    if (this.slides && this.slides[this.activeIndex]) {
                animateSlide(this.slides[this.activeIndex]);
                    }
            }
        }
    });
    }
    
    // Swiper da Imprensa
    if (heroSwiperImprensaElement) {
    const heroSwiperImprensa = new Swiper('.hero-swiper-imprensa', {
        // Configurações básicas
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        effect: 'slide',
        autoplay: {
            delay: 6000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        },
        speed: 1000,
        
        // Navegação
        navigation: {
            nextEl: '.hero-swiper-imprensa .swiper-button-next',
            prevEl: '.hero-swiper-imprensa .swiper-button-prev',
        },
        
        // Paginação
        pagination: {
            el: '.hero-swiper-imprensa .swiper-pagination',
            clickable: true,
            dynamicBullets: true
        },
        
        // Lazy loading
        lazy: {
            loadPrevNext: true,
            loadPrevNextAmount: 2
        },
        
        // Acessibilidade
        a11y: {
            prevSlideMessage: 'Notícia anterior',
            nextSlideMessage: 'Próxima notícia',
            firstSlideMessage: 'Primeira notícia',
            lastSlideMessage: 'Última notícia',
            paginationBulletMessage: 'Ir para notícia {{index}}'
        },
        
        // Eventos
        on: {
            init: function() {
                    console.log('Hero Swiper Imprensa inicializado');
                animateSlide(this.slides[this.activeIndex]);
            },
            slideChange: function() {
                animateSlide(this.slides[this.activeIndex]);
            }
        }
    });
    }
    
    // Função para animar elementos do slide
    function animateSlide(slide) {
        const elements = [
            slide.querySelector('.hero-category'),
            slide.querySelector('.hero-title'),
            slide.querySelector('.hero-description'),
            slide.querySelector('.hero-meta'),
            slide.querySelector('.btn-read-more'),
            slide.querySelector('.hero-image')
        ];
        
        elements.forEach((el, index) => {
            if (el) {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                
                setTimeout(() => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, 100 * index);
            }
        });
    }
    
    // Função para ler notícia
    window.lerNoticia = function(noticiaSlug) {
        // Redirecionar diretamente para a página da notícia
        window.location.href = `/noticias/${noticiaSlug}/`;
    };
    
    // Lazy loading para imagens
    const lazyImages = document.querySelectorAll('.news-image img');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
});

// Função auxiliar para obter o token CSRF
function getCookie(name) {
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