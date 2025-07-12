# Sistema de Permissões

Este documento detalha o sistema de permissões do GovBR Roleplay, incluindo cargos, níveis de acesso e funcionalidades específicas.

## Níveis de Acesso

### 1. Imigrante
- Acesso básico ao site
- Pode visualizar notícias públicas
- Pode solicitar cidadania

### 2. Cidadão
- Todos os acessos de Imigrante
- Pode comentar em notícias
- Pode participar de discussões
- Pode solicitar serviços básicos

### 3. Servidor
- Todos os acessos de Cidadão
- Acesso ao painel de gestão (se aplicável)
- Permissões específicas baseadas no cargo

### 4. Administrador
- Acesso total ao sistema
- Gerenciamento de usuários
- Configurações do sistema
- Logs e auditoria

## Cargos e Permissões

### Poder Imprensa

#### Repórter
- Criar notícias do tipo "imprensa"
- Editar suas próprias notícias
- Enviar notícias para revisão

#### Editor
- Todas as permissões de Repórter
- Editar notícias do seu órgão
- Moderar comentários
- Aprovar notícias para publicação

#### Chefe de Redação
- Todas as permissões de Editor
- Gerenciar equipe de reportagem
- Definir diretrizes editoriais
- Arquivar notícias

### Poder Executivo

#### Assessor de Imprensa
- Criar notícias do tipo "governo"
- Editar notícias do governo
- Enviar para revisão

#### Diretor de Comunicação
- Todas as permissões de Assessor
- Aprovar notícias do governo
- Gerenciar equipe de comunicação
- Definir estratégia de comunicação

## Fluxo de Aprovação

### Notícias da Imprensa
1. Repórter cria notícia
2. Editor revisa e aprova
3. Chefe de Redação pode intervir
4. Publicação

### Notícias do Governo
1. Assessor cria notícia
2. Diretor de Comunicação revisa
3. Publicação

## Moderação

### Comentários
- Editores podem moderar comentários
- Chefes podem banir usuários
- Sistema de denúncias

### Conteúdo
- Editores podem editar conteúdo
- Chefes podem remover conteúdo
- Log de alterações

## Grupos de Permissão

### Imprensa
```python
class GrupoImprensa:
    REPORTER = [
        'criar_noticia_imprensa',
        'editar_noticia_propria',
        'enviar_revisao',
    ]
    
    EDITOR = [
        *REPORTER,
        'editar_noticia_orgao',
        'moderar_comentarios',
        'aprovar_noticia',
    ]
    
    CHEFE = [
        *EDITOR,
        'gerenciar_equipe',
        'definir_diretrizes',
        'arquivar_noticia',
    ]
```

### Governo
```python
class GrupoGoverno:
    ASSESSOR = [
        'criar_noticia_governo',
        'editar_noticia_governo',
        'enviar_revisao',
    ]
    
    DIRETOR = [
        *ASSESSOR,
        'aprovar_noticia_governo',
        'gerenciar_equipe',
        'definir_estrategia',
    ]
```

## Verificações de Permissão

### Decoradores
```python
@login_required
@permission_required('main.criar_noticia_imprensa')
def criar_noticia(request):
    # ...
```

### Templates
```html
{% if perms.main.criar_noticia_imprensa %}
    <a href="{% url 'main:noticia_criar' %}" class="btn btn-primary">
        Nova Notícia
    </a>
{% endif %}
```

### Views
```python
def get_queryset(self):
    qs = super().get_queryset()
    if not self.request.user.has_perm('main.ver_noticia_privada'):
        qs = qs.filter(status='publicado')
    return qs
```

## Auditoria

### Logs de Ação
- Todas as ações são registradas
- Histórico de alterações
- Quem fez o quê e quando

### Relatórios
- Atividade por usuário
- Ações por tipo
- Histórico de moderação

## Segurança

### Proteção contra Elevação de Privilégios
- Verificações em múltiplas camadas
- Validação de permissões em cada request
- Sanitização de input

### Sessões
- Timeout de sessão
- Renovação de tokens
- Proteção contra CSRF

## Melhores Práticas

### 1. Princípio do Menor Privilégio
- Conceder apenas as permissões necessárias
- Revisar permissões periodicamente
- Remover acessos não utilizados

### 2. Separação de Responsabilidades
- Cada cargo tem funções específicas
- Evitar sobreposição de permissões
- Manter hierarquia clara

### 3. Auditoria e Monitoramento
- Registrar todas as ações
- Monitorar atividades suspeitas
- Manter histórico de alterações

## Implementação

### 1. Modelos
```python
class Permissao(models.Model):
    nome = models.CharField(max_length=100)
    codename = models.CharField(max_length=100)
    descricao = models.TextField()

class GrupoPermissao(models.Model):
    nome = models.CharField(max_length=100)
    permissoes = models.ManyToManyField(Permissao)
    nivel_acesso = models.CharField(max_length=50)
```

### 2. Middleware
```python
class PermissaoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.permissoes = request.user.get_all_permissions()
        return self.get_response(request)
```

### 3. Decoradores
```python
def cargo_required(cargo_nome):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.tem_cargo(cargo_nome):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
```

## Próximos Passos

### 1. Melhorias Planejadas
- Sistema de roles dinâmicas
- Permissões baseadas em contexto
- Interface de gerenciamento melhorada

### 2. Integrações
- Single Sign-On (SSO)
- Autenticação em dois fatores
- Integração com Active Directory

### 3. Automação
- Atribuição automática de permissões
- Revogação automática de acessos
- Notificações de alterações 