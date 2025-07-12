/**
 * JavaScript para gerenciar a seleção hierárquica de cargos no admin do Django
 */

// URLs para as APIs AJAX (serão definidas dinamicamente)
const AJAX_URLS = {
    orgaos: '/usuarios/admin/ajax/orgaos/',
    entidades: '/usuarios/admin/ajax/entidades/',
    cargos: '/usuarios/admin/ajax/cargos/'
};

// Função helper para encontrar select por nome
function findSelectByName(fieldName) {
    // Tentar diferentes padrões de ID
    const possibleIds = [
        `#id_${fieldName}`,
        `#id_profile-0-${fieldName}`,
        `#id_profile-TOTAL_FORMS-${fieldName}`
    ];
    
    for (let id of possibleIds) {
        const element = document.querySelector(id);
        if (element) {
            return element;
        }
    }
    
    // Tentar buscar por atributo name
    const byName = document.querySelector(`select[name*="${fieldName}"]`);
    if (byName) {
        return byName;
    }
    
    return null;
}

// Função para obter o token CSRF
function getCSRFToken() {
    // Método 1: Campo hidden do formulário
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Método 2: Cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    // Método 3: Meta tag
    const csrfMeta = document.querySelector('meta[name=csrf-token]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    console.error('CSRF token não encontrado!');
    return '';
}

// Função para fazer requisições AJAX
function makeAjaxRequest(url, data, callback) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        callback(data);
    })
    .catch(error => {
        console.error('Erro na requisição AJAX:', error);
    });
}

// Função para atualizar um select com novas opções
function updateSelect(selectElement, options, emptyLabel) {
    // Limpar opções existentes
    selectElement.innerHTML = '';
    
    // Adicionar opção vazia
    const emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = emptyLabel;
    selectElement.appendChild(emptyOption);
    
    // Adicionar novas opções
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.id;
        optionElement.textContent = option.nome;
        selectElement.appendChild(optionElement);
    });
}

// Função para atualizar órgãos baseado no poder selecionado
function updateOrgaos(poderId) {
    const orgaoSelect = findSelectByName('orgao');
    const entidadeSelect = findSelectByName('entidade');
    const cargoSelect = findSelectByName('cargo_atual');
    
    if (!poderId) {
        updateSelect(orgaoSelect, [], 'Selecione um órgão...');
        updateSelect(entidadeSelect, [], 'Selecione uma entidade...');
        updateSelect(cargoSelect, [], 'Selecione um cargo...');
        return;
    }
    
    // Fazer requisição AJAX para buscar órgãos
    makeAjaxRequest('/usuarios/admin/ajax/orgaos/', { poder_id: poderId }, function(data) {
        if (data.success && data.orgaos) {
            updateSelect(orgaoSelect, data.orgaos, 'Selecione um órgão...');
            updateSelect(entidadeSelect, [], 'Selecione uma entidade...');
            updateSelect(cargoSelect, [], 'Selecione um cargo...');
        }
    });
}

// Função para atualizar entidades baseado no órgão selecionado
function updateEntidades(orgaoId) {
    const entidadeSelect = findSelectByName('entidade');
    const cargoSelect = findSelectByName('cargo_atual');
    
    if (!orgaoId) {
        updateSelect(entidadeSelect, [], 'Selecione uma entidade...');
        updateSelect(cargoSelect, [], 'Selecione um cargo...');
        return;
    }
    
    // Fazer requisição AJAX para buscar entidades
    makeAjaxRequest('/usuarios/admin/ajax/entidades/', { orgao_id: orgaoId }, function(data) {
        updateSelect(entidadeSelect, data.entidades, 'Selecione uma entidade...');
        updateSelect(cargoSelect, [], 'Selecione um cargo...');
    });
}

// Função para atualizar cargos baseado na entidade selecionada
function updateCargos(entidadeId) {
    const cargoSelect = findSelectByName('cargo_atual');
    
    if (!entidadeId) {
        updateSelect(cargoSelect, [], 'Selecione um cargo...');
        return;
    }
    
    // Fazer requisição AJAX para buscar cargos
    makeAjaxRequest('/usuarios/admin/ajax/cargos/', { entidade_id: entidadeId }, function(data) {
        updateSelect(cargoSelect, data.cargos, 'Selecione um cargo...');
    });
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Encontrar os selects usando a função helper
    const poderSelect = findSelectByName('poder');
    const orgaoSelect = findSelectByName('orgao');
    const entidadeSelect = findSelectByName('entidade');
    
    if (poderSelect) {
        poderSelect.addEventListener('change', function() {
            updateOrgaos(this.value);
        });
    }
    
    if (orgaoSelect) {
        orgaoSelect.addEventListener('change', function() {
            updateEntidades(this.value);
        });
    }
    
    if (entidadeSelect) {
        entidadeSelect.addEventListener('change', function() {
            updateCargos(this.value);
        });
    }
}); 