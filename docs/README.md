# GovBR Roleplay - Sistema Web

## Descrição do Projeto

O **GovBR Roleplay** é um sistema web desenvolvido para simular o Governo Brasileiro no ambiente do Roblox. O projeto oferece uma plataforma completa com sistema de notícias, painel administrativo, autenticação de usuários e diversas funcionalidades interativas.

## Características Principais

### 🎨 Design Moderno
- Interface inspirada no site oficial do gov.br
- Design responsivo e moderno
- Efeitos visuais e animações suaves
- Cantos arredondados e sombras
- Cores oficiais do governo brasileiro

### 📰 Sistema de Notícias
- Notícias do governo com sistema de slides
- Notícias da imprensa em geral
- Sistema de visualizações
- Categorização automática
- Busca em tempo real

### 📊 Estatísticas Dinâmicas
- Contador de usuários cadastrados
- Separação por níveis (Imigrantes/Cidadãos)
- Novos usuários dos últimos 7 dias
- Animações nos contadores

### ⚙️ Painel Administrativo
- Gerenciamento de notícias
- Configuração de botões personalizáveis
- Controle de anúncios
- Configurações do site
- Estatísticas detalhadas

### 🔐 Sistema de Autenticação
- Modal de login com blur
- Sistema de registro
- Integração com avatares do Roblox
- Recuperação de senha

## Tecnologias Utilizadas

### Backend
- **Django 4.2.7** - Framework web Python
- **PostgreSQL** - Banco de dados
- **Python 3.8+** - Linguagem de programação

### Frontend
- **Bootstrap 5.3.2** - Framework CSS
- **jQuery 3.7.1** - Biblioteca JavaScript
- **Swiper.js** - Slider/Carousel
- **Font Awesome & Bootstrap Icons** - Ícones
- **Google Fonts (Inter)** - Tipografia

### Bibliotecas Python
- `psycopg2-binary` - Conexão PostgreSQL
- `python-dotenv` - Variáveis de ambiente
- `Pillow` - Processamento de imagens
- `django-cors-headers` - CORS
- `requests` - Requisições HTTP
- `django-crispy-forms` - Formulários
- `whitenoise` - Arquivos estáticos

## Estrutura do Projeto

```
GOV_BR/
├── govbr_roleplay/          # Configurações principais do Django
│   ├── settings.py          # Configurações
│   ├── urls.py              # URLs principais
│   └── wsgi.py              # WSGI
├── main/                    # App principal
│   ├── models.py            # Modelos de dados
│   ├── views.py             # Views
│   ├── admin.py             # Configuração admin
│   └── urls.py              # URLs do app
├── users/                   # App de usuários
├── templates/               # Templates HTML
│   ├── base.html            # Template base
│   └── main/
│       └── home.html        # Página inicial
├── static/                  # Arquivos estáticos
│   ├── css/
│   │   └── main.css         # CSS personalizado
│   ├── js/
│   │   └── main.js          # JavaScript personalizado
│   └── images/              # Imagens
├── media/                   # Uploads de usuários
├── docs/                    # Documentação
└── requirements.txt         # Dependências
```

## Modelos de Dados

### Noticia
- Título, resumo e conteúdo
- Tipo (Governo/Imprensa)
- Imagem e autor
- Status de publicação
- Sistema de visualizações

### BotaoConfiguravel
- Título e descrição
- Ícone personalizável
- Link de redirecionamento
- Cor de fundo
- Status ativo/inativo

### EstatisticaSistema
- Contadores de usuários
- Níveis de acesso
- Dados dos últimos 7 dias
- Atualização automática

### Anuncio
- Título e descrição
- Imagem e link opcional
- Período de exibição
- Sistema de ordenação

### ConfiguracaoSite
- Nome e logo do site
- Link do Discord
- Configurações de cores
- Textos personalizáveis

## Funcionalidades Implementadas

### ✅ Página Inicial
- [x] Header com design gov.br
- [x] Sistema de busca
- [x] Botão de login/perfil
- [x] Menu de navegação
- [x] Slide de notícias principais
- [x] Grid de notícias da imprensa
- [x] Estatísticas animadas
- [x] Botões configuráveis
- [x] Seção do Discord
- [x] Anúncios administrativos
- [x] Footer

### ✅ Sistema de Modais
- [x] Modal de login com blur
- [x] Modal de registro
- [x] Validação de formulários
- [x] Alternância entre modais

### ✅ Painel Administrativo
- [x] Gerenciamento de notícias
- [x] Configuração de botões
- [x] Controle de estatísticas
- [x] Gestão de anúncios
- [x] Configurações gerais

### ✅ JavaScript Interativo
- [x] Busca em tempo real
- [x] Animações on scroll
- [x] Contador animado
- [x] Sistema de notificações
- [x] Scroll suave
- [x] Botão voltar ao topo

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- PostgreSQL
- Git

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd GOV_BR
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o banco de dados PostgreSQL:**
- Crie um banco chamado `govbr_roleplay`
- Configure as credenciais no `settings.py`

4. **Execute as migrações:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crie um superusuário:**
```bash
python manage.py createsuperuser
```

6. **Execute o servidor:**
```bash
python manage.py runserver
```

7. **Acesse o sistema:**
- Site: http://localhost:8000
- Admin: http://localhost:8000/admin

## Próximos Passos

### Funcionalidades Pendentes
- [ ] Sistema completo de autenticação
- [ ] Integração com API do Roblox
- [ ] Páginas de detalhes das notícias
- [ ] Sistema de comentários
- [ ] Newsletter
- [ ] API REST
- [ ] Testes unitários
- [ ] Deploy em produção

## Contribuição

Este projeto está sendo desenvolvido de forma incremental. Cada funcionalidade é implementada e testada antes de prosseguir para a próxima etapa.

## Licença

Projeto desenvolvido para fins educacionais e de roleplay.

## Suporte

Para dúvidas ou suporte, consulte a documentação completa na pasta `docs/` ou entre em contato com a equipe de desenvolvimento. 