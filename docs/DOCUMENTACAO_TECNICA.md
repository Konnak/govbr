# Documentação Técnica Completa - GovBR Roleplay

## Índice
1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Arquitetura e Tecnologias](#arquitetura-e-tecnologias)
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Modelos de Dados](#modelos-de-dados)
5. [Sistema de Autenticação](#sistema-de-autenticação)
6. [Sistema de Diário Oficial](#sistema-de-diário-oficial)
7. [APIs e Endpoints](#apis-e-endpoints)
8. [Frontend e Templates](#frontend-e-templates)
9. [Sistema de PDF](#sistema-de-pdf)
10. [Configurações](#configurações)
11. [Deployment](#deployment)

---

## 1. Visão Geral do Sistema

### Objetivo
O **GovBR Roleplay** é uma plataforma web desenvolvida em Django para simular um governo brasileiro no ambiente do Roblox. O sistema permite:

- Gestão completa de estrutura governamental (Poderes, Órgãos, Entidades, Cargos)
- Sistema de autenticação integrado com Discord
- Diário Oficial digital com geração de PDF
- Portal de notícias e anúncios
- Painel administrativo para gestão de usuários e cargos
- Sistema de transparência pública

### Características Principais
- **Multiplataforma**: Responsivo para desktop, tablet e mobile
- **Integração Discord**: OAuth2 e sincronização de dados
- **Geração de PDF**: Diário Oficial com numeração automática
- **Sistema de Cargos**: Hierarquia governamental completa
- **Portal Transparência**: Visualização pública da estrutura
- **PWA**: Progressive Web App com Service Worker

---

## 2. Arquitetura e Tecnologias

### Stack Tecnológico

#### Backend
- **Django 4.2.7**: Framework web principal
- **Python 3.8+**: Linguagem de programação
- **PostgreSQL**: Banco de dados principal (produção)
- **SQLite**: Banco de dados para desenvolvimento

#### Frontend
- **Bootstrap 5**: Framework CSS
- **JavaScript ES6+**: Funcionalidades interativas
- **HTML5/CSS3**: Estrutura e estilização
- **Service Worker**: Cache e funcionalidades offline

#### Bibliotecas Principais
```python
Django==4.2.7                 # Framework web
psycopg2-binary==2.9.9        # Driver PostgreSQL
python-dotenv==1.0.0          # Variáveis de ambiente
Pillow==10.1.0                # Processamento de imagens
django-cors-headers==4.3.1    # CORS para APIs
requests==2.31.0              # Requisições HTTP
django-crispy-forms==2.1      # Formulários estilizados
crispy-bootstrap5==0.7        # Integração Bootstrap
whitenoise==6.6.0             # Servir arquivos estáticos
reportlab==4.0.7              # Geração de PDF
xhtml2pdf                     # HTML para PDF
```

### Arquitetura de Aplicações

```
govbr_roleplay/          # Projeto principal
├── main/                # App principal (governo, diário)
├── users/               # App de usuários e autenticação
└── govbr_roleplay/      # Configurações do projeto
```

---

## 3. Estrutura do Projeto

### Organização de Diretórios

```
GOV_BR/
├── govbr_roleplay/          # Configurações Django
│   ├── __init__.py
│   ├── settings.py          # Configurações principais
│   ├── urls.py             # URLs raiz
│   ├── wsgi.py             # WSGI para produção
│   └── asgi.py             # ASGI para WebSockets
├── main/                    # App principal
│   ├── migrations/         # Migrações do banco
│   ├── models.py           # Modelos de dados
│   ├── views.py            # Views/Controllers
│   ├── urls.py             # URLs do app
│   ├── admin.py            # Configuração admin
│   └── apps.py             # Configuração do app
├── users/                   # App de usuários
│   ├── migrations/         # Migrações de usuários
│   ├── models.py           # Modelo User customizado
│   ├── views.py            # Views de autenticação
│   ├── urls.py             # URLs de usuários
│   ├── admin.py            # Admin de usuários
│   └── discord_service.py  # Integração Discord
├── templates/               # Templates HTML
│   ├── base.html           # Template base
│   ├── main/               # Templates do app main
│   └── users/              # Templates de usuários
├── static/                  # Arquivos estáticos
│   ├── css/                # Estilos CSS
│   ├── js/                 # JavaScript
│   └── images/             # Imagens
├── media/                   # Uploads de usuários
├── docs/                    # Documentação
├── requirements.txt         # Dependências Python
└── manage.py               # CLI do Django
```

---

## 4. Modelos de Dados

### 4.1 Estrutura Governamental

#### Poder
```python
class Poder(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    # Exemplos: "Poder Executivo", "Poder Judiciário", "Poder Legislativo"
```

#### Órgão
```python
class Orgao(models.Model):
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20)
    poder = models.ForeignKey(Poder, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)
    
    # Exemplos: "Presidência da República", "Supremo Tribunal Federal"
```

#### Entidade
```python
class Entidade(models.Model):
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=50)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    
    # Exemplos: "Casa Civil", "Ministério da Justiça"
```

#### Cargo
```python
class Cargo(models.Model):
    NATUREZA_CHOICES = [
        ('efetivo', 'Cargo Efetivo'),
        ('comissionado', 'Cargo em Comissão'),
        ('funcao', 'Função de Confiança'),
    ]
    
    nome = models.CharField(max_length=200)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    natureza = models.CharField(max_length=20, choices=NATUREZA_CHOICES)
    simbolo_gestao = models.CharField(max_length=20)  # Ex: "DAS-6", "FC-1"
    nivel_hierarquico = models.PositiveIntegerField()
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    permite_acumulacao = models.BooleanField(default=False)
```

### 4.2 Sistema de Usuários

#### User (Customizado)
```python
class User(AbstractUser):
    NIVEL_CHOICES = [
        ('imigrante', 'Imigrante'),
        ('cidadao', 'Cidadão'),
        ('moderador', 'Moderador'),
        ('administrador', 'Administrador'),
        ('coordenador', 'Coordenador'),
        ('fundador', 'Fundador'),
    ]
    
    # Campos RP
    nome_completo_rp = models.CharField(max_length=100)
    roblox_id = models.BigIntegerField(unique=True)
    roblox_username = models.CharField(max_length=50)
    
    # Níveis de acesso
    nivel_acesso = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    verificado = models.BooleanField(default=False)
    
    # Discord OAuth
    discord_id = models.BigIntegerField(unique=True)
    discord_username = models.CharField(max_length=50)
    discord_access_token = models.TextField()
```

#### Profile
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo_atual = models.ForeignKey(Cargo, on_delete=models.SET_NULL)
    data_nascimento_rp = models.DateField()
    biografia = models.TextField()
    avatar_roblox = models.URLField()
```

### 4.3 Sistema de Diário Oficial

#### DiarioOficial
```python
class DiarioOficial(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    data_publicacao = models.DateField(default=timezone.now)
    ano = models.PositiveIntegerField(default=timezone.now().year)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def get_proximo_numero(cls):
        ultimo = cls.objects.order_by('-numero').first()
        return (ultimo.numero + 1) if ultimo else 1
```

#### PublicacaoDiarioOficial
```python
class PublicacaoDiarioOficial(models.Model):
    SECOES_CHOICES = [
        ('executivo', 'Poder Executivo'),
        ('legislativo', 'Poder Legislativo'),
        ('judiciario', 'Poder Judiciário'),
    ]
    
    TIPOS_CHOICES = [
        ('nomeacao', 'Nomeação'),
        ('exoneracao', 'Exoneração'),
        ('decreto', 'Decreto'),
        ('portaria', 'Portaria'),
        ('lei', 'Lei'),
    ]
    
    diario = models.ForeignKey(DiarioOficial, on_delete=models.CASCADE)
    secao = models.CharField(max_length=20, choices=SECOES_CHOICES)
    tipo = models.CharField(max_length=20, choices=TIPOS_CHOICES)
    titulo = models.CharField(max_length=300)
    conteudo = models.TextField()
    historico_cargo = models.ForeignKey(HistoricoCargo, on_delete=models.CASCADE)
    automatica = models.BooleanField(default=True)
```

---

## 5. Sistema de Autenticação

### 5.1 Integração Discord OAuth2

#### Configuração
```python
# settings.py
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
```

#### Fluxo de Autenticação
1. **Redirecionamento**: Usuário clica em "Login com Discord"
2. **Autorização**: Redirecionado para Discord OAuth
3. **Callback**: Discord retorna com código de autorização
4. **Token Exchange**: Troca código por access_token
5. **Dados do Usuário**: Busca informações do usuário
6. **Criação/Login**: Cria conta ou faz login

#### Service Discord
```python
class DiscordService:
    @staticmethod
    def get_authorization_url():
        params = {
            'client_id': settings.DISCORD_CLIENT_ID,
            'redirect_uri': settings.DISCORD_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'identify email'
        }
        return f"{settings.DISCORD_AUTHORIZATION_BASE_URL}?{urlencode(params)}"
    
    @staticmethod
    def exchange_code_for_token(code):
        data = {
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.DISCORD_REDIRECT_URI
        }
        response = requests.post(settings.DISCORD_TOKEN_URL, data=data)
        return response.json()
```

### 5.2 Sistema de Níveis

#### Hierarquia de Acesso
1. **Imigrante**: Acesso básico, visualização
2. **Cidadão**: Acesso a funcionalidades básicas
3. **Moderador**: Gestão de conteúdo
4. **Administrador**: Gestão de usuários e cargos
5. **Coordenador**: Gestão completa do sistema
6. **Fundador**: Acesso total

#### Decorators de Permissão
```python
def nivel_required(nivel_minimo):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:login')
            
            niveis = ['imigrante', 'cidadao', 'moderador', 'administrador', 'coordenador', 'fundador']
            nivel_usuario = niveis.index(request.user.nivel_acesso)
            nivel_necessario = niveis.index(nivel_minimo)
            
            if nivel_usuario < nivel_necessario:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return redirect('main:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
```

---

## 6. Sistema de Diário Oficial

### 6.1 Geração Automática

#### Trigger de Nomeação/Exoneração
```python
@receiver(post_save, sender=HistoricoCargo)
def criar_publicacao_diario(sender, instance, created, **kwargs):
    if created and instance.publicado_diario:
        # Obtém ou cria diário do dia
        diario, created = DiarioOficial.objects.get_or_create(
            data_publicacao=timezone.now().date(),
            defaults={'numero': DiarioOficial.get_proximo_numero()}
        )
        
        # Cria publicação automática
        PublicacaoDiarioOficial.objects.create(
            diario=diario,
            secao=instance.cargo.entidade.orgao.poder.nome.lower(),
            tipo='nomeacao' if instance.ativo else 'exoneracao',
            titulo=f"{'Nomeação' if instance.ativo else 'Exoneração'} - {instance.cargo.nome}",
            conteudo=gerar_conteudo_publicacao(instance),
            historico_cargo=instance,
            automatica=True
        )
```

### 6.2 Geração de PDF

#### Biblioteca xhtml2pdf
```python
def diario_oficial_pdf(request, numero):
    from xhtml2pdf import pisa
    
    diario = get_object_or_404(DiarioOficial, numero=numero)
    
    # Converter imagens para base64
    def image_to_base64(image_field):
        if image_field and hasattr(image_field, 'path'):
            with open(image_field.path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return f'data:image/png;base64,{img_data}'
        return None
    
    # Renderizar template HTML
    context = {
        'diario': diario,
        'publicacoes_por_secao': diario.get_publicacoes_por_secao(),
        'logo_esquerda_base64': image_to_base64(config.logo_esquerda),
        'logo_direita_base64': image_to_base64(config.logo_direita),
    }
    
    html_string = render_to_string('main/diario_oficial_pdf.html', context)
    
    # Converter para PDF
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=buffer)
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="diario_oficial_{numero}.pdf"'
    
    return response
```

#### Template PDF com Frames
```html
<style>
    @page {
        size: A4 portrait;
        margin: 2cm 2cm 3cm 2cm;
        
        @frame footer_frame {
            -pdf-frame-content: footer_content;
            left: 2cm;
            right: 2cm;
            bottom: 1cm;
            height: 1cm;
        }
    }
</style>

<body>
    <!-- Conteúdo principal -->
    <div class="diario-oficial">
        <!-- Cabeçalho, publicações, etc. -->
    </div>

    <!-- Rodapé com numeração -->
    <div id="footer_content">
        Página <pdf:pagenumber> de <pdf:pagecount> - Gerado em {% now "d/m/Y H:i" %}
    </div>
</body>
```

---

## 7. APIs e Endpoints

### 7.1 URLs Principais

```python
# main/urls.py
urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
    
    # Estrutura do governo
    path('estrutura-governo/', views.estrutura_governo, name='estrutura_governo'),
    
    # Gestão de cargos
    path('painel-gestao-cargos/', views.painel_gestao_cargos, name='painel_gestao_cargos'),
    path('api/nomear-usuario/', views.nomear_usuario, name='nomear_usuario'),
    path('api/exonerar-usuario/', views.exonerar_usuario, name='exonerar_usuario'),
    
    # Diário Oficial
    path('diario-oficial/', views.diario_oficial_lista, name='diario_oficial_lista'),
    path('diario-oficial/<int:numero>/', views.diario_oficial_detalhe, name='diario_oficial_detalhe'),
    path('diario-oficial/<int:numero>/pdf/', views.diario_oficial_pdf, name='diario_oficial_pdf'),
    
    # Perfil público
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
]
```

### 7.2 APIs REST

#### Nomear Usuário
```python
@login_required
@require_http_methods(["POST"])
def nomear_usuario(request):
    try:
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        cargo_id = data.get('cargo_id')
        
        # Validações
        usuario = get_object_or_404(User, id=usuario_id)
        cargo = get_object_or_404(Cargo, id=cargo_id)
        
        # Verificar se cargo está disponível
        if HistoricoCargo.objects.filter(cargo=cargo, ativo=True).exists():
            return JsonResponse({'success': False, 'error': 'Cargo já ocupado'})
        
        # Criar histórico
        historico = HistoricoCargo.objects.create(
            usuario=usuario,
            cargo=cargo,
            data_nomeacao=timezone.now(),
            nomeado_por=request.user,
            ativo=True,
            publicado_diario=True
        )
        
        return JsonResponse({'success': True, 'message': 'Usuário nomeado com sucesso!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
```

#### Buscar Cargos por Entidade
```python
@require_http_methods(["GET"])
def api_cargos_por_entidade(request, entidade_id):
    try:
        entidade = get_object_or_404(Entidade, id=entidade_id)
        cargos = Cargo.objects.filter(entidade=entidade, ativo=True)
        
        cargos_data = []
        for cargo in cargos:
            ocupado = HistoricoCargo.objects.filter(cargo=cargo, ativo=True).exists()
            cargos_data.append({
                'id': cargo.id,
                'nome': cargo.nome,
                'simbolo_gestao': cargo.simbolo_gestao,
                'salario': str(cargo.salario),
                'ocupado': ocupado
            })
        
        return JsonResponse({'cargos': cargos_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

## 8. Frontend e Templates

### 8.1 Template Base

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GovBR Roleplay{% endblock %}</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- CSS Customizado -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    
    <!-- PWA -->
    <link rel="manifest" href="{% static 'manifest.json' %}">
    <meta name="theme-color" content="#0d6efd">
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- Navegação -->
    </nav>
    
    <!-- Conteúdo Principal -->
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <!-- Rodapé -->
    <footer class="bg-dark text-light py-4">
        <!-- Footer content -->
    </footer>
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'js/main.js' %}"></script>
    
    <!-- Service Worker -->
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
    </script>
</body>
</html>
```

### 8.2 JavaScript Principal

```javascript
// static/js/main.js
class GovBRApp {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadEstruturaGoverno();
        this.setupNotificacoes();
    }
    
    setupEventListeners() {
        // Event listeners para formulários AJAX
        document.addEventListener('DOMContentLoaded', () => {
            this.setupFormularios();
            this.setupModals();
        });
    }
    
    async nomearUsuario(usuarioId, cargoId) {
        try {
            const response = await fetch('/api/nomear-usuario/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    usuario_id: usuarioId,
                    cargo_id: cargoId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Usuário nomeado com sucesso!', 'success');
                this.reloadCargos();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Erro ao nomear usuário', 'error');
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Inicializar aplicação
const app = new GovBRApp();
```

---

## 9. Sistema de PDF

### 9.1 Configuração xhtml2pdf

#### Dependências
```bash
pip install xhtml2pdf
```

#### Configuração de Página
```css
@page {
    size: A4 portrait;
    margin: 2cm 2cm 3cm 2cm;
    
    @frame footer_frame {
        -pdf-frame-content: footer_content;
        left: 2cm;
        right: 2cm;
        bottom: 1cm;
        height: 1cm;
    }
}
```

### 9.2 Features Implementadas

#### Numeração de Páginas
```html
<div id="footer_content">
    Página <pdf:pagenumber> de <pdf:pagecount> - Gerado em {% now "d/m/Y H:i" %}
</div>
```

#### Imagens Base64
```python
def image_to_base64(image_field):
    if image_field and hasattr(image_field, 'path'):
        with open(image_field.path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
            ext = os.path.splitext(image_field.path)[1].lower()
            mime_type = 'image/png' if ext == '.png' else 'image/jpeg'
            return f'data:{mime_type};base64,{img_data}'
    return None
```

#### Quebras de Página
```css
.publicacao {
    page-break-inside: avoid;
    page-break-after: always;
}

.secao-titulo {
    page-break-after: avoid;
}
```

---

## 10. Configurações

### 10.1 Settings.py

```python
# Configurações principais
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-secreta')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'govbr_roleplay'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# Arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Discord OAuth
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
```

### 10.2 Variáveis de Ambiente

```bash
# .env
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,seudominio.com

# Database
DATABASE_NAME=govbr_roleplay
DATABASE_USER=postgres
DATABASE_PASSWORD=sua-senha
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Discord OAuth
DISCORD_CLIENT_ID=seu-client-id
DISCORD_CLIENT_SECRET=seu-client-secret
DISCORD_REDIRECT_URI=http://127.0.0.1:8000/usuarios/discord/callback/
DISCORD_BOT_TOKEN=seu-bot-token
```

---

## 11. Deployment

### 11.1 Preparação para Produção

#### Requirements.txt
```txt
Django==4.2.7
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Pillow==10.1.0
django-cors-headers==4.3.1
requests==2.31.0
django-crispy-forms==2.1
crispy-bootstrap5==0.7
whitenoise==6.6.0
gunicorn==21.2.0
xhtml2pdf
```

#### Configurações de Produção
```python
# settings.py (produção)
DEBUG = False
ALLOWED_HOSTS = ['seudominio.com', 'www.seudominio.com']

# Segurança
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# CSRF e Session
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

### 11.2 Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "govbr_roleplay.wsgi:application"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_HOST=db
    depends_on:
      - db
    volumes:
      - media_volume:/app/media

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: govbr_roleplay
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: sua-senha
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  media_volume:
```

### 11.3 Comandos de Deploy

```bash
# Migrações
python manage.py makemigrations
python manage.py migrate

# Arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
gunicorn --bind 0.0.0.0:8000 govbr_roleplay.wsgi:application
```

---

## Conclusão

Esta documentação técnica cobre todos os aspectos principais do sistema GovBR Roleplay, desde a arquitetura até o deployment. O sistema foi projetado para ser escalável, maintível e seguro, utilizando as melhores práticas do Django e tecnologias modernas.

Para informações específicas sobre instalação e configuração, consulte os documentos complementares na pasta `docs/`:

- `INSTALACAO.md` - Guia de instalação completo
- `DISCORD_OAUTH.md` - Configuração do Discord OAuth
- `ADMIN_GUIDE.md` - Guia do administrador
- `ADMIN_CARGOS.md` - Gestão de cargos

**Versão**: 1.0.0  
**Data**: Junho 2025  
**Autor**: Sistema GovBR Roleplay 