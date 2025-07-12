// Gerenciador da estrutura do governo
class EstruturaGoverno {
    constructor() {
        console.log('EstruturaGoverno: Inicializando...');
        this.init();
    }

    init() {
        console.log('EstruturaGoverno: Configurando event listeners...');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Evento para os botões de poder
        const poderButtons = document.querySelectorAll('.poder-button');
        console.log('EstruturaGoverno: Encontrados', poderButtons.length, 'botões de poder');
        
        poderButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                console.log('EstruturaGoverno: Botão de poder clicado', button.dataset.poderId);
                e.preventDefault();
                e.stopPropagation();
                const poderId = button.dataset.poderId;
                this.toggleOrgaos(poderId);
            });
        });

        // Evento para os cards de órgãos
        const orgaoCards = document.querySelectorAll('.orgao-card');
        console.log('EstruturaGoverno: Encontrados', orgaoCards.length, 'cards de órgãos');
        
        orgaoCards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Ignora o clique se vier de um ocupante
                if (e.target.closest('.ocupante-item')) {
                    return;
                }
                console.log('EstruturaGoverno: Card de órgão clicado', card.dataset.orgaoId);
                e.preventDefault();
                e.stopPropagation();
                const orgaoId = card.dataset.orgaoId;
                this.toggleEntidades(orgaoId);
            });
        });

        // Evento para os cards de entidades
        const entidadeCards = document.querySelectorAll('.entidade-card');
        console.log('EstruturaGoverno: Encontrados', entidadeCards.length, 'cards de entidades');
        
        entidadeCards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Ignora o clique se vier de um ocupante
                if (e.target.closest('.ocupante-item')) {
                    return;
                }
                console.log('EstruturaGoverno: Card de entidade clicado', card.dataset.entidadeId);
                e.preventDefault();
                e.stopPropagation();
                const entidadeId = card.dataset.entidadeId;
                this.toggleCargos(entidadeId);
            });
        });

        // Previne que o clique nos ocupantes se propague
        document.querySelectorAll('.ocupante-item').forEach(ocupante => {
            ocupante.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        });
    }

    toggleOrgaos(poderId) {
        console.log('EstruturaGoverno: Alternando órgãos do poder', poderId);
        const container = document.querySelector(`#orgaos-${poderId}`);
        console.log('EstruturaGoverno: Container encontrado:', container);
        
        if (!container) {
            console.error('EstruturaGoverno: Container não encontrado para o poder', poderId);
            return;
        }

        const allOrgaos = document.querySelectorAll('.orgaos-container');
        
        // Fecha todos os outros containers de órgãos
        allOrgaos.forEach(org => {
            if (org.id !== `orgaos-${poderId}`) {
                org.style.display = 'none';
                org.classList.remove('fade-in');
            }
        });

        // Toggle do container atual
        const isHidden = container.style.display === 'none' || !container.style.display;
        console.log('EstruturaGoverno: Container está oculto?', isHidden);

        if (isHidden) {
            container.style.display = 'block';
            container.classList.add('fade-in');
            
            // Fecha todos os containers de entidades e cargos dentro deste poder
            container.querySelectorAll('.entidades-container, .cargos-container').forEach(el => {
                el.style.display = 'none';
                el.classList.remove('fade-in');
            });
        } else {
            container.style.display = 'none';
            container.classList.remove('fade-in');
        }
    }

    toggleEntidades(orgaoId) {
        console.log('EstruturaGoverno: Alternando entidades do órgão', orgaoId);
        const container = document.querySelector(`#entidades-${orgaoId}`);
        console.log('EstruturaGoverno: Container encontrado:', container);
        
        if (!container) {
            console.error('EstruturaGoverno: Container não encontrado para o órgão', orgaoId);
            return;
        }
        
        const isHidden = container.style.display === 'none' || !container.style.display;
        console.log('EstruturaGoverno: Container está oculto?', isHidden);

        if (isHidden) {
            container.style.display = 'block';
            container.classList.add('fade-in');
            
            // Fecha todos os containers de cargos dentro desta entidade
            container.querySelectorAll('.cargos-container').forEach(el => {
                el.style.display = 'none';
                el.classList.remove('fade-in');
            });
        } else {
            container.style.display = 'none';
            container.classList.remove('fade-in');
        }
    }

    toggleCargos(entidadeId) {
        console.log('EstruturaGoverno: Alternando cargos da entidade', entidadeId);
        const container = document.querySelector(`#cargos-${entidadeId}`);
        console.log('EstruturaGoverno: Container encontrado:', container);
        
        if (!container) {
            console.error('EstruturaGoverno: Container não encontrado para a entidade', entidadeId);
            return;
        }
        
        const isHidden = container.style.display === 'none' || !container.style.display;
        console.log('EstruturaGoverno: Container está oculto?', isHidden);

        if (isHidden) {
            container.style.display = 'grid';
            container.classList.add('fade-in');
        } else {
            container.style.display = 'none';
            container.classList.remove('fade-in');
        }
    }
}

// Inicializa quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    console.log('EstruturaGoverno: DOM carregado, inicializando...');
    window.estruturaGoverno = new EstruturaGoverno();
}); 