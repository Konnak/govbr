# Sistema de Notícias - Separação Governo e Imprensa

## Visão Geral

Este documento detalha as implementações realizadas para separar e melhorar a exibição de notícias do governo e da imprensa no sistema GovBR Roleplay.

## Principais Melhorias Implementadas

### 1. Separação de Slides na Página Inicial

#### Antes
- Um único slide com todas as notícias em destaque
- Não havia distinção visual entre governo e imprensa

#### Depois
- **Slide do Governo**: Notícias oficiais do governo com `tipo='governo'` e `destaque=True`
- **Slide da Imprensa**: Notícias da imprensa com `tipo='imprensa'` e `destaque=True`
- Cada slide tem seu próprio Swiper independente com cores e estilos distintos

### 2. Sistema de Órgãos com Logos

#### Novos Campos no Modelo `Orgao`
```python
logo = models.ImageField(
    upload_to='orgaos/logos/', 
    blank=True, 
    null=True, 
    verbose_name="Logo do Órgão"
)
descricao = models.TextField(blank=True, verbose_name="Descrição")
site_oficial = models.URLField(blank=True, verbose_name="Site Oficial")
ativo = models.BooleanField(default=True, verbose_name="Ativo")
```

#### Funcionalidades
- Gestores podem fazer upload da logo do órgão via admin
- Logo é exibida automaticamente nas notícias da imprensa
- Suporte a diferentes formatos de imagem (PNG, JPG, etc.)

### 3. Métodos Avançados no Modelo `Noticia`

#### Novos Métodos
```python
def get_orgao_autor(self):
    """Retorna o órgão do autor da notícia"""
    
def get_logo_orgao(self):
    """Retorna a URL da logo do órgão do autor"""
    
def get_nome_orgao(self):
    """Retorna o nome do órgão do autor"""
```

### 4. Melhorias na Exibição de Notícias da Imprensa

#### Informações Exibidas
- **Logo do Órgão**: Exibida em destaque
- **Nome do Órgão**: Identificação clara da fonte
- **Nome do Jornalista**: Autor da notícia (nome RP)
- **Data e Hora**: Formato completo (dd/mm/yyyy HH:mm)
- **Informações do Editor**: Se a notícia foi editada por outra pessoa

#### Elementos Visuais
- Bordas vermelhas para identificar notícias da imprensa
- Logos circulares com bordas estilizadas
- Gradientes específicos para a seção da imprensa
- Hover effects diferenciados

### 5. Página de Detalhes da Notícia

#### Melhorias Específicas para Imprensa
- **Cabeçalho Especial**: Seção dedicada com logo e informações do órgão
- **Badge Personalizado**: Cor vermelha para notícias da imprensa
- **Informações Completas**: Órgão, jornalista, editor, datas
- **Estilo Visual Diferenciado**: Cores e elementos específicos

### 6. Atualização do Admin

#### Painel de Órgãos
- Campo para upload de logo
- Descrição do órgão
- Site oficial
- Status ativo/inativo
- Indicador visual se possui logo

#### Organização Melhorada
- Fieldsets organizados por categoria
- Tooltips explicativos
- Validações de permissão

## Implementação Técnica

### 1. Modelo de Dados

#### Migração Criada
```bash
python manage.py makemigrations main --name add_orgao_fields
python manage.py migrate
```

#### Campos Adicionados
- `logo`: ImageField para upload da logo
- `descricao`: TextField para descrição do órgão
- `site_oficial`: URLField para site oficial
- `ativo`: BooleanField para status

### 2. Views Atualizadas

#### View `home`
```python
# Notícias do governo em destaque
noticias_governo_destaque = Noticia.objects.filter(
    publicado=True, 
    destaque=True,
    tipo='governo'
).select_related('autor', 'autor__profile', 'autor__profile__cargo_atual', 
                'autor__profile__cargo_atual__entidade__orgao')

# Notícias da imprensa em destaque
noticias_imprensa_destaque = Noticia.objects.filter(
    publicado=True,
    destaque=True,
    tipo='imprensa'
).select_related('autor', 'autor__profile', 'autor__profile__cargo_atual', 
                'autor__profile__cargo_atual__entidade__orgao')
```

#### Otimizações
- `select_related` para evitar N+1 queries
- Cache separado para cada tipo de notícia
- Prefetch das relações necessárias

### 3. Templates Atualizados

#### `home.html`
- Dois swipers independentes
- Seções visuais distintas
- Informações específicas para cada tipo

#### `noticia_detalhe.html`
- Cabeçalho condicional baseado no tipo
- Informações específicas da imprensa
- Estilos CSS personalizados

### 4. CSS e JavaScript

#### Novos Estilos
```css
/* Seção da Imprensa */
.imprensa-section {
    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
}

.imprensa-card {
    border-left: 5px solid #e74c3c;
}

.orgao-logo {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2px solid #e74c3c;
}
```

#### JavaScript Atualizado
- Dois swipers independentes
- Configurações específicas para cada tipo
- Autoplay com tempos diferentes

## Benefícios Implementados

### 1. Organização Clara
- Separação visual entre governo e imprensa
- Identificação imediata da fonte da notícia
- Hierarquia visual bem definida

### 2. Informações Completas
- Dados do órgão de imprensa
- Identificação do jornalista
- Informações de edição
- Timestamps detalhados

### 3. Identidade Visual
- Logos dos órgãos de imprensa
- Cores específicas para cada tipo
- Elementos visuais diferenciados

### 4. Experiência do Usuário
- Navegação intuitiva
- Informações bem organizadas
- Feedback visual claro

## Como Usar

### 1. Configurar Órgão de Imprensa

1. Acesse o admin Django
2. Vá para "Órgãos"
3. Selecione o órgão de imprensa
4. Faça upload da logo (recomendado: 200x200px)
5. Preencha a descrição
6. Salve as alterações

### 2. Criar Notícia da Imprensa

1. Usuário deve ter cargo em órgão de imprensa
2. Criar notícia com `tipo='imprensa'`
3. Marcar `destaque=True` para aparecer no slide
4. A logo e informações serão exibidas automaticamente

### 3. Verificar Exibição

1. **Página Inicial**: Verificar slides separados
2. **Lista de Notícias**: Informações do órgão nos cards
3. **Detalhes**: Cabeçalho específico da imprensa

## Estrutura de Arquivos

```
GOV_BR/
├── main/
│   ├── models.py (Orgao atualizado, métodos em Noticia)
│   ├── views.py (home view atualizada)
│   ├── admin.py (OrgaoAdmin melhorado)
│   └── migrations/
│       └── 0008_add_orgao_fields.py
├── templates/main/
│   ├── home.html (slides separados)
│   └── noticia_detalhe.html (cabeçalho da imprensa)
├── static/
│   ├── css/noticias.css (estilos da imprensa)
│   └── js/noticias.js (swipers independentes)
└── media/orgaos/logos/ (logos dos órgãos)
```

## Próximos Passos Sugeridos

### 1. Funcionalidades Adicionais
- Sistema de assinatura para jornalistas
- Categorias específicas para imprensa
- Sistema de comentários com moderação

### 2. Melhorias Visuais
- Animações mais elaboradas
- Temas personalizáveis por órgão
- Modo escuro/claro

### 3. Funcionalidades Avançadas
- Newsletter automática
- RSS feeds separados
- Sistema de notificações

## Conclusão

As implementações realizadas criam uma separação clara e profissional entre notícias do governo e da imprensa, melhorando significativamente a experiência do usuário e a organização do conteúdo. O sistema agora oferece:

- **Identificação Clara**: Logos e informações completas dos órgãos
- **Separação Visual**: Slides e seções distintas
- **Informações Detalhadas**: Dados completos sobre autoria e edição
- **Facilidade de Gestão**: Admin intuitivo para configuração

O sistema está preparado para crescer e receber novas funcionalidades conforme a necessidade do roleplay. 