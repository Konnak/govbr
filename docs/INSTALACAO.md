# Instalação e Configuração

Este guia explica como configurar o ambiente de desenvolvimento para o sistema GovBR Roleplay.

## Requisitos

- Python 3.10 ou superior
- PostgreSQL 13 ou superior
- Redis 6 ou superior
- Node.js 18 ou superior (para compilação de assets)
- Git

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/govbr-roleplay.git
cd govbr-roleplay
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
DEBUG=True
SECRET_KEY=sua-chave-secreta
DATABASE_URL=postgres://usuario:senha@localhost:5432/govbr_roleplay
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Instale e configure o PostgreSQL:
```bash
# Linux
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser -P seu_usuario
sudo -u postgres createdb -O seu_usuario govbr_roleplay

# Windows
# Instale o PostgreSQL via instalador oficial
# Use o pgAdmin para criar o banco de dados
```

6. Instale e inicie o Redis:
```bash
# Linux
sudo apt install redis-server
sudo systemctl start redis-server

# Windows
# Baixe o Redis via GitHub ou WSL
# Inicie o servidor Redis
```

7. Execute as migrações:
```bash
python manage.py migrate
```

8. Crie um superusuário:
```bash
python manage.py createsuperuser
```

9. Colete os arquivos estáticos:
```bash
python manage.py collectstatic
```

10. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## Configuração do Celery

1. Inicie o worker do Celery:
```bash
celery -A govbr_roleplay worker -l info
```

2. Inicie o beat do Celery (para tarefas agendadas):
```bash
celery -A govbr_roleplay beat -l info
```

## Configuração do Redis

O Redis é usado para cache e como broker do Celery. Verifique se está rodando:
```bash
redis-cli ping
# Deve responder com PONG
```

## Configuração do TinyMCE

1. Registre-se em https://www.tiny.cloud/ para obter uma API key
2. Atualize o arquivo `.env`:
```env
TINYMCE_API_KEY=sua-api-key
```

## Configuração do Debug Toolbar

O Django Debug Toolbar está configurado para desenvolvimento. Ele aparecerá automaticamente quando:
- DEBUG=True
- O IP do cliente está em INTERNAL_IPS
- O usuário é um superusuário ou tem is_staff=True

## Configuração de Upload de Arquivos

1. Crie os diretórios necessários:
```bash
mkdir -p media/noticias/{principais,editor,galeria}
```

2. Configure as permissões:
```bash
# Linux
chmod -R 755 media
```

## Desenvolvimento

### Compilação de Assets

1. Instale as dependências do Node.js:
```bash
npm install
```

2. Compile os assets:
```bash
npm run build
```

3. Para desenvolvimento com hot-reload:
```bash
npm run dev
```

### Testes

Execute os testes:
```bash
python manage.py test
```

Com cobertura:
```bash
coverage run manage.py test
coverage report
```

### Linting

Execute o linting:
```bash
flake8
black .
isort .
```

## Produção

### Configuração do Gunicorn

1. Instale o Gunicorn:
```bash
pip install gunicorn
```

2. Execute com:
```bash
gunicorn govbr_roleplay.wsgi:application
```

### Configuração do Nginx

1. Instale o Nginx:
```bash
sudo apt install nginx
```

2. Configure o site:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location /static/ {
        alias /caminho/para/staticfiles/;
    }

    location /media/ {
        alias /caminho/para/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Configuração do SSL

1. Instale o Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Obtenha o certificado:
```bash
sudo certbot --nginx -d seu-dominio.com
```

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com o PostgreSQL**
   - Verifique se o serviço está rodando
   - Verifique as credenciais no `.env`
   - Verifique as permissões do usuário

2. **Erro de conexão com o Redis**
   - Verifique se o serviço está rodando
   - Verifique a URL no `.env`
   - Verifique se a porta está aberta

3. **Erro de permissão nos uploads**
   - Verifique as permissões dos diretórios
   - Verifique o usuário do processo
   - Verifique as configurações do SELinux

4. **Erro no Celery**
   - Verifique se o Redis está rodando
   - Verifique as configurações do broker
   - Verifique os logs do worker

### Logs

Os logs estão configurados para:
- Console em desenvolvimento
- Arquivo em produção

Verifique os logs em:
```bash
tail -f logs/govbr.log
```

## Atualização

Para atualizar o sistema:

1. Atualize o código:
```bash
git pull
```

2. Atualize as dependências:
```bash
pip install -r requirements.txt
```

3. Execute as migrações:
```bash
python manage.py migrate
```

4. Colete os estáticos:
```bash
python manage.py collectstatic
```

5. Reinicie os serviços:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

## Estrutura de Arquivos Criada

```
GOV_BR/
├── db.sqlite3                    # Banco de dados SQLite
├── manage.py                     # Script de gerenciamento Django
├── requirements.txt              # Dependências Python
├── govbr_roleplay/              # Configurações do projeto
│   ├── settings.py              # Configurações principais
│   ├── urls.py                  # URLs principais
│   └── wsgi.py                  # WSGI para produção
├── main/                        # App principal
│   ├── models.py                # Modelos de dados
│   ├── views.py                 # Views/Controllers
│   ├── admin.py                 # Configuração admin
│   ├── urls.py                  # URLs do app
│   └── migrations/              # Migrações do banco
├── users/                       # App de usuários (futuro)
├── templates/                   # Templates HTML
│   ├── base.html               # Template base
│   └── main/
│       └── home.html           # Página inicial
├── static/                      # Arquivos estáticos
│   ├── css/
│   │   └── main.css            # CSS personalizado
│   ├── js/
│   │   └── main.js             # JavaScript personalizado
│   └── images/                 # Imagens do sistema
├── media/                       # Uploads de usuários
│   ├── noticias/               # Imagens de notícias
│   ├── anuncios/               # Imagens de anúncios
│   └── configuracao/           # Logo e favicon
└── docs/                        # Documentação
    ├── README.md               # Documentação principal
    ├── ADMIN_GUIDE.md          # Guia do admin
    └── INSTALACAO.md           # Este arquivo
```

## Comandos Úteis

### Desenvolvimento
```bash
# Executar servidor de desenvolvimento
python manage.py runserver

# Criar migrações após mudanças nos models
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos (produção)
python manage.py collectstatic
```

### Backup e Restore
```bash
# Fazer backup do banco SQLite
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3

# Exportar dados
python manage.py dumpdata > backup_data.json

# Importar dados
python manage.py loaddata backup_data.json
```

## Solução de Problemas

### Erro: "No module named 'corsheaders'"
```bash
pip install django-cors-headers
```

### Erro: "psycopg2" não encontrado
```bash
pip install psycopg2-binary
```

### Erro: Arquivos estáticos não carregam
1. Verifique se `DEBUG = True` em settings.py
2. Execute: `python manage.py collectstatic`
3. Verifique as configurações de STATIC_URL

### Erro: Imagens não aparecem
1. Verifique se a pasta `media/` existe
2. Confirme as configurações de MEDIA_URL
3. Verifique permissões da pasta

## Próximos Passos

Após a instalação, você pode:

1. **Personalizar o Visual**:
   - Modificar cores em `static/css/main.css`
   - Adicionar logo e favicon
   - Personalizar textos

2. **Adicionar Conteúdo**:
   - Criar notícias
   - Configurar botões de serviço
   - Adicionar anúncios

3. **Configurar para Produção**:
   - Configurar PostgreSQL
   - Configurar servidor web (Nginx + Gunicorn)
   - Configurar SSL
   - Otimizar configurações

4. **Desenvolver Funcionalidades**:
   - Sistema de usuários
   - Integração com Roblox
   - API REST
   - Sistema de comentários

## Suporte

Para dúvidas ou problemas:
1. Consulte a documentação completa em `docs/`
2. Verifique os logs de erro
3. Entre em contato com a equipe de desenvolvimento

## Versionamento

- **v1.0.0**: Versão inicial com página principal e painel admin
- **Próximas versões**: Sistema de usuários, integração Roblox, API REST

---

**Desenvolvido para GovBR Roleplay - Simulação do Governo Brasileiro no Roblox** 