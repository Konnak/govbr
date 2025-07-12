/**
 * GovBR Roleplay - Autenticação e Notificações
 */

// Função para obter o token CSRF
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

// Função para fazer login
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    
    const username = document.getElementById('login_username').value.trim();
    const password = document.getElementById('login_password').value;

    if (!username || !password) {
        NotificationManager.show('Usuário e senha são obrigatórios', 'error');
        return;
    }

    // Mostrar loading
    btnText.classList.add('d-none');
    btnLoading.classList.remove('d-none');
    submitBtn.disabled = true;

    try {
        const response = await fetch('/usuarios/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            NotificationManager.show('Login realizado com sucesso!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            NotificationManager.show(data.error || 'Erro ao fazer login. Verifique suas credenciais.', 'error');
            
            // Esconder loading
            btnText.classList.remove('d-none');
            btnLoading.classList.add('d-none');
            submitBtn.disabled = false;
        }
    } catch (error) {
        NotificationManager.show('Erro ao conectar ao servidor. Tente novamente.', 'error');
        
        // Esconder loading
        btnText.classList.remove('d-none');
        btnLoading.classList.add('d-none');
        submitBtn.disabled = false;
    }
}

// Função para fazer logout
async function handleLogout() {
    try {
        const response = await fetch('/usuarios/logout/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (response.ok) {
            NotificationManager.show('Logout realizado com sucesso!', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            NotificationManager.show('Erro ao fazer logout. Tente novamente.', 'error');
        }
    } catch (error) {
        NotificationManager.show('Erro ao conectar ao servidor. Tente novamente.', 'error');
    }
}

// Função para vincular Discord
async function handleDiscordLink() {
    try {
        const response = await fetch('/usuarios/api/iniciar-vinculacao-discord/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();

        if (response.ok && data.url) {
            NotificationManager.show('Redirecionando para o Discord...', 'info');
            window.location.href = data.url;
        } else {
            NotificationManager.show('Erro ao iniciar vinculação com Discord. Tente novamente.', 'error');
        }
    } catch (error) {
        NotificationManager.show('Erro ao conectar ao servidor. Tente novamente.', 'error');
    }
}

// Função para desvincular Discord
async function handleDiscordUnlink() {
    try {
        const response = await fetch('/usuarios/api/desvincular-discord/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            NotificationManager.show('Conta do Discord desvinculada com sucesso!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            NotificationManager.show('Erro ao desvincular conta do Discord. Tente novamente.', 'error');
        }
    } catch (error) {
        NotificationManager.show('Erro ao conectar ao servidor. Tente novamente.', 'error');
    }
}

// Adicionar event listeners quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Logout button
    const logoutBtn = document.querySelector('[data-action="logout"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // Discord link button
    const discordLinkBtn = document.querySelector('[data-action="discord-link"]');
    if (discordLinkBtn) {
        discordLinkBtn.addEventListener('click', handleDiscordLink);
    }

    // Discord unlink button
    const discordUnlinkBtn = document.querySelector('[data-action="discord-unlink"]');
    if (discordUnlinkBtn) {
        discordUnlinkBtn.addEventListener('click', handleDiscordUnlink);
    }
}); 