console.log('✅ Portal da Transparência - JavaScript carregado');

// Definir a classe primeiro
class PortalTransparencia {
    constructor() {
        console.log('🔄 Iniciando Portal da Transparência...');
        this.buscaRealizada = false; // Flag para controlar se já foi feita uma busca
        this.setupEventListeners();
        this.carregarEstatisticas();
        // Inicializar interface sem fazer busca automática
        this.inicializarInterface();
    }

    inicializarInterface() {
        // Inicializar a interface sem fazer busca
        const resultsContainer = document.getElementById('resultsContainer');
        const serversList = document.getElementById('serversList');
        
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        if (serversList) {
            serversList.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>Use os filtros acima para buscar servidores</h5>
                    <p class="text-muted">Digite um nome ou selecione filtros e clique em "Buscar Servidores"</p>
                </div>
            `;
        }
        
        console.log('✅ Interface inicializada sem busca automática');
    }

    setupEventListeners() {
        // Formulário de busca
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            console.log('✅ Formulário de busca encontrado');
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.buscarServidores(1);
            });
        } else {
            console.error('❌ Formulário de busca não encontrado');
        }

        // Filtros dependentes
        const poderFilter = document.getElementById('poderFilter');
        const orgaoFilter = document.getElementById('orgaoFilter');
        const entidadeFilter = document.getElementById('entidadeFilter');
        const cargoFilter = document.getElementById('cargoFilter');
        
        if (poderFilter) {
            console.log('✅ Filtro de poder encontrado');
            poderFilter.addEventListener('change', () => {
                console.log('🔄 Poder selecionado:', poderFilter.value);
                this.carregarOrgaos(poderFilter.value);
                // Só fazer busca se já existe uma busca em andamento
                if (this.buscaRealizada) {
                this.buscarServidores(1);
                }
            });
        } else {
            console.error('❌ Filtro de poder não encontrado');
        }

        if (orgaoFilter) {
            console.log('✅ Filtro de órgão encontrado');
            orgaoFilter.addEventListener('change', () => {
                console.log('🔄 Órgão selecionado:', orgaoFilter.value);
                this.carregarEntidades(orgaoFilter.value);
                // Só fazer busca se já existe uma busca em andamento
                if (this.buscaRealizada) {
                this.buscarServidores(1);
                }
            });
        } else {
            console.error('❌ Filtro de órgão não encontrado');
        }

        if (entidadeFilter) {
            console.log('✅ Filtro de entidade encontrado');
            entidadeFilter.addEventListener('change', () => {
                console.log('🔄 Entidade selecionada:', entidadeFilter.value);
                this.carregarCargos(entidadeFilter.value);
                // Só fazer busca se já existe uma busca em andamento
                if (this.buscaRealizada) {
                this.buscarServidores(1);
                }
            });
        } else {
            console.error('❌ Filtro de entidade não encontrado');
        }

        if (cargoFilter) {
            cargoFilter.addEventListener('change', () => {
                // Só fazer busca se já existe uma busca em andamento
                if (this.buscaRealizada) {
                this.buscarServidores(1);
                }
            });
        }

        // Limpar filtros
        const clearFilters = document.getElementById('clearFilters');
        if (clearFilters) {
            console.log('✅ Botão de limpar filtros encontrado');
            clearFilters.addEventListener('click', () => {
                this.limparFiltros();
            });
        } else {
            console.error('❌ Botão de limpar filtros não encontrado');
        }

        // Exportar CSV
        const exportButton = document.getElementById('exportButton');
        if (exportButton) {
            console.log('✅ Botão de exportar encontrado');
            exportButton.addEventListener('click', () => {
                this.exportarCSV();
            });
        } else {
            console.error('❌ Botão de exportar não encontrado');
        }
    }

    async carregarEstatisticas() {
        try {
            console.log('🔄 Carregando estatísticas...');
            const response = await fetch('/api/portal-transparencia/estatisticas/');
            const data = await response.json();

            if (data.success) {
                console.log('✅ Estatísticas carregadas:', data);
                // Atualizar os números nas estatísticas
                document.querySelector('[data-stat="total_usuarios"]').textContent = data.total_usuarios;
                document.querySelector('[data-stat="total_servidores"]').textContent = data.total_servidores;
                document.querySelector('[data-stat="total_imigrantes"]').textContent = data.total_imigrantes;
                document.querySelector('[data-stat="total_cidadaos"]').textContent = data.total_cidadaos;
            }
        } catch (error) {
            console.error('❌ Erro ao carregar estatísticas:', error);
            window.NotificationManager.showError('Erro ao carregar estatísticas');
        }
    }

    async carregarOrgaos(poderId) {
        const orgaoFilter = document.getElementById('orgaoFilter');
        const entidadeFilter = document.getElementById('entidadeFilter');
        const cargoFilter = document.getElementById('cargoFilter');
        
        if (!orgaoFilter || !entidadeFilter || !cargoFilter) return;
        
        try {
            // Resetar e desabilitar filtros dependentes
            orgaoFilter.innerHTML = '<option value="">Selecione um órgão</option>';
            entidadeFilter.innerHTML = '<option value="">Selecione uma entidade</option>';
            cargoFilter.innerHTML = '<option value="">Selecione um cargo</option>';
            
            orgaoFilter.disabled = true;
            entidadeFilter.disabled = true;
            cargoFilter.disabled = true;
            
            if (!poderId) {
                return;
            }
            
            const response = await fetch(`/api/portal-transparencia/orgaos/${poderId}/`);
            const data = await response.json();
            
            if (data.success) {
                // Habilitar filtro de órgão
                orgaoFilter.disabled = false;
                
                // Adicionar opções
                data.orgaos.forEach(orgao => {
                    const option = document.createElement('option');
                    option.value = orgao.id;
                    option.textContent = orgao.nome;
                    orgaoFilter.appendChild(option);
                });
            } else {
                window.NotificationManager.error('Erro ao carregar órgãos');
            }
        } catch (error) {
            console.error('Erro ao carregar órgãos:', error);
            window.NotificationManager.error('Erro ao carregar órgãos');
        }
    }
    
    async carregarEntidades(orgaoId) {
        const entidadeFilter = document.getElementById('entidadeFilter');
        const cargoFilter = document.getElementById('cargoFilter');
        
        if (!entidadeFilter || !cargoFilter) return;
        
        try {
            // Resetar e desabilitar filtros
            entidadeFilter.innerHTML = '<option value="">Selecione uma entidade</option>';
            cargoFilter.innerHTML = '<option value="">Selecione um cargo</option>';
            
            entidadeFilter.disabled = true;
            cargoFilter.disabled = true;
            
            if (!orgaoId) {
                return;
            }
            
            const response = await fetch(`/api/portal-transparencia/entidades/${orgaoId}/`);
            const data = await response.json();
            
            if (data.success) {
                // Habilitar filtro
                entidadeFilter.disabled = false;
                
                // Adicionar opções
                data.entidades.forEach(entidade => {
                    const option = document.createElement('option');
                    option.value = entidade.id;
                    option.textContent = entidade.nome;
                    entidadeFilter.appendChild(option);
                });
            } else {
                window.NotificationManager.error('Erro ao carregar entidades');
            }
        } catch (error) {
            console.error('Erro ao carregar entidades:', error);
            window.NotificationManager.error('Erro ao carregar entidades');
        }
    }
    
    async carregarCargos(entidadeId) {
        const cargoFilter = document.getElementById('cargoFilter');
        
        if (!cargoFilter) return;
        
        try {
            // Resetar e desabilitar filtro
            cargoFilter.innerHTML = '<option value="">Selecione um cargo</option>';
            cargoFilter.disabled = true;
            
            if (!entidadeId) {
                return;
            }
            
            const response = await fetch(`/api/portal-transparencia/cargos/${entidadeId}/`);
            const data = await response.json();
            
            if (data.success) {
                // Habilitar filtro
                cargoFilter.disabled = false;
                
                // Adicionar opções
                data.cargos.forEach(cargo => {
                    const option = document.createElement('option');
                    option.value = cargo.id;
                    option.textContent = cargo.nome;
                    cargoFilter.appendChild(option);
                });
            } else {
                window.NotificationManager.error('Erro ao carregar cargos');
            }
        } catch (error) {
            console.error('Erro ao carregar cargos:', error);
            window.NotificationManager.error('Erro ao carregar cargos');
        }
    }

    async buscarServidores(pagina = 1) {
        const searchForm = document.getElementById('searchForm');
        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData);
        params.append('page', pagina);

        try {
            // Marcar que uma busca foi realizada
            this.buscaRealizada = true;
            
            // Mostrar loading e esconder resultados anteriores
            const loadingSpinner = document.getElementById('loadingSpinner');
            const resultsContainer = document.getElementById('resultsContainer');
            const serversList = document.getElementById('serversList');

            if (loadingSpinner) loadingSpinner.style.display = 'block';
            if (resultsContainer) resultsContainer.style.display = 'block';

            const response = await fetch(`/api/portal-transparencia/buscar/?${params.toString()}`);
            const data = await response.json();

            // Esconder loading e mostrar container de resultados
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'block';

            if (data.success) {
                this.exibirResultados(data);
            } else {
                window.NotificationManager.error(data.error || 'Erro ao realizar busca');
                
                if (serversList) {
                    serversList.innerHTML = `
                        <div class="text-center py-5">
                            <i class="fas fa-exclamation-circle fa-3x text-danger mb-3"></i>
                            <h5>Erro ao realizar a busca</h5>
                            <p class="text-muted">Por favor, tente novamente mais tarde.</p>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Erro na busca:', error);
            window.NotificationManager.error('Erro ao realizar busca');
            
            const loadingSpinner = document.getElementById('loadingSpinner');
            const resultsContainer = document.getElementById('resultsContainer');
            const serversList = document.getElementById('serversList');
            
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'block';
            if (serversList) {
                serversList.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-exclamation-circle fa-3x text-danger mb-3"></i>
                        <h5>Erro ao realizar a busca</h5>
                        <p class="text-muted">Por favor, tente novamente mais tarde.</p>
                    </div>
                `;
            }
        }
    }

    exibirResultados(data) {
        const serversList = document.getElementById('serversList');
        const paginationContainer = document.getElementById('paginationContainer');
        const resultsInfo = document.getElementById('resultsInfo');
        
        if (!serversList) return;
        
        // Limpar lista atual
        serversList.innerHTML = '';
        
        if (data.servidores.length === 0) {
            serversList.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>Nenhum resultado encontrado</h5>
                    <p class="text-muted">Tente ajustar os filtros de busca.</p>
                </div>
            `;
            if (paginationContainer) paginationContainer.innerHTML = '';
            if (resultsInfo) resultsInfo.textContent = 'Nenhum resultado encontrado';
            return;
        }
        
        // Atualizar informações de resultados
        if (resultsInfo) {
            resultsInfo.textContent = `${data.total_results} resultado(s) encontrado(s)`;
        }
        
        // Exibir servidores
        data.servidores.forEach(servidor => {
            const card = document.createElement('div');
            card.className = 'card mb-3 border-0 shadow-sm';
            card.innerHTML = `
                <div class="card-body">
                    <div class="d-flex align-items-start">
                        <img src="${servidor.avatar_url}" alt="Avatar" 
                             class="rounded-circle me-3" style="width: 64px; height: 64px; object-fit: cover;">
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5 class="card-title mb-1">
                                        <a href="/perfil/${servidor.username}/" class="text-decoration-none">
                                            ${servidor.nome_completo}
                                        </a>
                                    </h5>
                                    <p class="card-text mb-2">
                                        <small class="text-muted">
                                            Discord: ${servidor.discord_username || 'Não informado'} | 
                                            Roblox: ${servidor.roblox_username}
                                        </small>
                                    </p>
                                </div>
                                <span class="badge bg-info">${servidor.nivel_acesso}</span>
                            </div>
                            
                            ${servidor.cargo_atual ? `
                                <div class="mt-2">
                                    <div class="d-flex align-items-center mb-1">
                                        <span class="badge bg-primary me-2">${servidor.cargo_atual}</span>
                                        <small class="text-muted">
                                            ${servidor.entidade} - ${servidor.orgao}
                                        </small>
                                    </div>
                                    <p class="card-text mb-0">
                                        <small class="text-muted">
                                            <i class="fas fa-calendar-alt me-1"></i>
                                            Nomeado em: ${servidor.data_nomeacao || 'Data não disponível'}
                                        </small>
                                    </p>
                                </div>
                            ` : `
                                <div class="mt-2">
                                    <span class="badge bg-secondary">Sem cargo</span>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `;
            serversList.appendChild(card);
        });
        
        // Atualizar paginação
        if (paginationContainer) {
            this.atualizarPaginacao(data.current_page, data.total_pages);
        }
    }

    getNivelBadgeClass(nivel) {
        const classes = {
            'Fundador': 'bg-danger',
            'Coordenador': 'bg-warning',
            'Administrador': 'bg-primary',
            'Moderador': 'bg-info',
            'Cidadão': 'bg-success',
            'Imigrante': 'bg-secondary'
        };
        return classes[nivel] || 'bg-secondary';
    }

    limparFiltros() {
        const searchForm = document.getElementById('searchForm');
        const poderFilter = document.getElementById('poderFilter');
        const orgaoFilter = document.getElementById('orgaoFilter');
        const entidadeFilter = document.getElementById('entidadeFilter');
        const cargoFilter = document.getElementById('cargoFilter');
        
        if (searchForm) {
            searchForm.reset();
            
            // Resetar e desabilitar filtros dependentes
            if (orgaoFilter) {
                orgaoFilter.innerHTML = '<option value="">Selecione um poder primeiro</option>';
                orgaoFilter.disabled = true;
            }
            
            if (entidadeFilter) {
                entidadeFilter.innerHTML = '<option value="">Selecione um órgão primeiro</option>';
                entidadeFilter.disabled = true;
            }
            
            if (cargoFilter) {
                cargoFilter.innerHTML = '<option value="">Selecione uma entidade primeiro</option>';
                cargoFilter.disabled = true;
            }
            
            // Resetar a interface e a flag de busca
            this.buscaRealizada = false;
            this.inicializarInterface();
        }
    }

    async exportarCSV() {
        try {
            const searchForm = document.getElementById('searchForm');
            const formData = new FormData(searchForm);
            const params = new URLSearchParams(formData);
            
            // Mostrar loading no botão
            const exportButton = document.getElementById('exportButton');
            const originalText = exportButton.innerHTML;
            exportButton.innerHTML = `
                <i class="fas fa-spinner fa-spin me-2"></i>
                Exportando...
            `;
            exportButton.disabled = true;

            const response = await fetch(`/api/portal-transparencia/exportar/?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error('Erro ao exportar dados');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'servidores.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Restaurar botão
            exportButton.innerHTML = originalText;
            exportButton.disabled = false;

            window.NotificationManager.success('Arquivo CSV exportado com sucesso!');
        } catch (error) {
            console.error('Erro ao exportar CSV:', error);
            window.NotificationManager.error('Erro ao exportar dados para CSV');
            
            // Restaurar botão
            const exportButton = document.getElementById('exportButton');
            exportButton.innerHTML = `
                <i class="fas fa-download me-2"></i>
                Exportar CSV
            `;
            exportButton.disabled = false;
        }
    }

    atualizarPaginacao(paginaAtual, totalPaginas) {
        const paginationContainer = document.getElementById('paginationContainer');
        if (!paginationContainer) return;
        
        paginationContainer.innerHTML = '';
        
        // Mostrar paginação apenas se houver mais de uma página
        if (totalPaginas > 1) {
            paginationContainer.style.display = 'block';
            
            // Botão Anterior
            const prevBtn = document.createElement('li');
            prevBtn.className = `page-item ${paginaAtual === 1 ? 'disabled' : ''}`;
            prevBtn.innerHTML = `
                <a class="page-link" href="#" aria-label="Anterior">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            `;
            if (paginaAtual > 1) {
                prevBtn.addEventListener('click', () => this.buscarServidores(paginaAtual - 1));
            }
            paginationContainer.appendChild(prevBtn);
            
            // Páginas
            for (let i = 1; i <= totalPaginas; i++) {
                if (
                    i === 1 || 
                    i === totalPaginas || 
                    (i >= paginaAtual - 2 && i <= paginaAtual + 2)
                ) {
                    const pageItem = document.createElement('li');
                    pageItem.className = `page-item ${i === paginaAtual ? 'active' : ''}`;
                    pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
                    pageItem.addEventListener('click', () => this.buscarServidores(i));
                    paginationContainer.appendChild(pageItem);
                } else if (
                    i === paginaAtual - 3 || 
                    i === paginaAtual + 3
                ) {
                    const ellipsis = document.createElement('li');
                    ellipsis.className = 'page-item disabled';
                    ellipsis.innerHTML = '<a class="page-link" href="#">...</a>';
                    paginationContainer.appendChild(ellipsis);
                }
            }
            
            // Botão Próximo
            const nextBtn = document.createElement('li');
            nextBtn.className = `page-item ${paginaAtual === totalPaginas ? 'disabled' : ''}`;
            nextBtn.innerHTML = `
                <a class="page-link" href="#" aria-label="Próximo">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            `;
            if (paginaAtual < totalPaginas) {
                nextBtn.addEventListener('click', () => this.buscarServidores(paginaAtual + 1));
            }
            paginationContainer.appendChild(nextBtn);
        } else {
            paginationContainer.style.display = 'none';
        }
    }
}

// Aguardar o DOM estar pronto e o NotificationManager estar disponível
document.addEventListener('DOMContentLoaded', () => {
    const waitForNotificationManager = setInterval(() => {
        if (window.NotificationManager) {
            console.log('✅ NotificationManager encontrado');
            clearInterval(waitForNotificationManager);
            window.portalTransparencia = new PortalTransparencia();
        } else {
            console.log('⏳ Aguardando NotificationManager...');
        }
    }, 100);
});