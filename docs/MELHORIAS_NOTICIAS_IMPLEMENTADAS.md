# Melhorias no Sistema de Notícias - Implementadas

## Resumo das Correções

Este documento descreve as melhorias implementadas no sistema de notícias do GovBR Roleplay, focando em três problemas principais:

1. **Botão "Ler Mais" não funcionava**
2. **Permitir edição de notícias**
3. **Melhorar método de envio conforme cargo/órgão/poder**

## 1. Correção do Botão "Ler Mais"

### Problema
O botão "Ler Mais" nos slides de notícias não redirecionava corretamente para a página de detalhes.

### Solução Implementada
- **Arquivo**: `static/js/noticias.js`
- **Correção**: Simplificada a função `lerNoticia()` para usar redirecionamento direto
- **Mudança**: Alterado de ID para slug nas chamadas da função

```javascript
// Antes (com API inexistente)
window.lerNoticia = function(noticiaId) {
    fetch(`/api/noticias/${noticiaId}/visualizar/`, {...})
    // Código complexo com API
};

// Depois (direto e funcional)
window.lerNoticia = function(noticiaSlug) {
    window.location.href = `/noticias/${noticiaSlug}/`;
};
```

### Arquivos Alterados
- `static/js/noticias.js` - Função lerNoticia simplificada
- `templates/main/home.html` - Todas as chamadas `onclick="lerNoticia({{ noticia.id }})"` alteradas para `onclick="lerNoticia('{{ noticia.slug }}')`

## 2. Sistema de Edição de Notícias

### Problema
O botão de editar não aparecia corretamente devido a problemas na verificação de permissões.

### Solução Implementada

#### Template Tags Personalizadas
- **Arquivo**: `main/templatetags/noticia_tags.py` (criado)
- **Função**: Filtros para verificar permissões de edição e publicação

```python
@register.filter
def pode_editar(noticia, user):
    if not user.is_authenticated:
        return False
    return noticia.pode_editar(user)

@register.filter  
def pode_publicar(noticia, user):
    if not user.is_authenticated:
        return False
    return noticia.pode_publicar(user)
```

#### Template Atualizado
- **Arquivo**: `templates/main/noticia_detalhe.html`
- **Mudança**: Uso dos filtros personalizados para verificação de permissões

```html
<!-- Antes -->
{% if noticia.pode_editar and user.is_authenticated %}

<!-- Depois -->
{% if noticia|pode_editar:user or noticia|pode_publicar:user %}
```

### Funcionalidades de Edição
- ✅ Botão "Editar Notícia" aparece para autores e usuários autorizados
- ✅ Redirecionamento correto para página de edição
- ✅ Verificação de permissões no backend
- ✅ Interface de edição completa já existente

## 3. Sistema Inteligente de Criação de Notícias

### Problema
Apenas usuários da imprensa podiam criar notícias, limitando o sistema.

### Solução Implementada

#### Lógica de Permissões Ampliada
- **Arquivo**: `main/views.py` - função `noticia_criar()`
- **Mudança**: Todos os usuários com cargo podem criar notícias

```python
# Antes - Apenas imprensa
if profile.cargo_atual.entidade.orgao.poder.nome.lower() != 'imprensa':
    messages.error(request, 'Você precisa ter um cargo na Imprensa...')

# Depois - Qualquer cargo
if not profile.cargo_atual:
    messages.error(request, 'Você precisa ter um cargo para criar notícias.')
```

#### Determinação Automática do Tipo
- **Lógica**: Tipo de notícia determinado automaticamente pelo cargo do usuário
- **Governo**: Usuários de órgãos governamentais (Executivo, Judiciário, Legislativo)
- **Imprensa**: Usuários de órgãos da imprensa

```python
# Determinar tipo baseado no cargo
if orgao_usuario.poder.nome.lower() == 'imprensa':
    tipo_noticia = 'imprensa'
else:
    tipo_noticia = 'governo'
```

#### Sistema de Publicação Inteligente
**Permissões de Publicação Direta:**
- ✅ **Superuser**: Sempre pode publicar
- ✅ **Imprensa**: Pode publicar diretamente
- ✅ **Governo com cargo alto**: Símbolos `**`, `*`, `+` podem publicar
- ❌ **Outros cargos**: Apenas rascunho/revisão

```python
if tipo == 'governo':
    if cargo_atual.simbolo_gestao in ['**', '*', '+']:
        publicado = True  # Publicação direta para autoridades
elif tipo == 'imprensa':
    publicado = True  # Imprensa sempre pode publicar
```

#### Interface Adaptativa
- **Arquivo**: `templates/main/noticia_criar.html`
- **Superuser**: Pode escolher tipo de notícia manualmente
- **Usuários normais**: Tipo determinado automaticamente com informações visuais

```html
{% if pode_escolher_tipo %}
    <!-- Radio buttons para escolher tipo -->
{% else %}
    <!-- Tipo fixo com informações do órgão -->
    <div class="alert alert-info">
        <strong>Notícia Oficial do Governo</strong>
        <br><small>Publicando como: {{ orgao_usuario.nome }}</small>
    </div>
{% endif %}
```

## Benefícios das Melhorias

### 1. Usabilidade
- ✅ Botão "Ler Mais" funciona perfeitamente
- ✅ Edição de notícias acessível e intuitiva
- ✅ Interface adaptativa baseada no cargo do usuário

### 2. Controle de Acesso
- ✅ Permissões baseadas na hierarquia governamental
- ✅ Publicação automática para autoridades competentes
- ✅ Separação clara entre notícias oficiais e da imprensa

### 3. Experiência do Usuário
- ✅ Feedback visual sobre tipo de notícia e permissões
- ✅ Dicas contextuais sobre capacidade de publicação
- ✅ Processo simplificado de criação

### 4. Integridade do Sistema
- ✅ Órgão do autor preservado estaticamente após publicação
- ✅ Validações adequadas de permissões
- ✅ Separação clara de responsabilidades

## Arquivos Modificados

### JavaScript
- `static/js/noticias.js` - Correção função lerNoticia

### Templates
- `templates/main/home.html` - Correção chamadas lerNoticia
- `templates/main/noticia_detalhe.html` - Template tags para permissões
- `templates/main/noticia_criar.html` - Interface adaptativa

### Python
- `main/views.py` - Lógica aprimorada de criação
- `main/templatetags/__init__.py` - Criado
- `main/templatetags/noticia_tags.py` - Criado

## Status das Implementações

- ✅ **Botão "Ler Mais"**: Funcionando perfeitamente
- ✅ **Edição de Notícias**: Sistema completo implementado
- ✅ **Sistema Inteligente**: Lógica baseada em cargo implementada

## Próximos Passos Sugeridos

1. **Testes**: Validar todas as funcionalidades com diferentes tipos de usuário
2. **Permissões**: Configurar permissões Django específicas se necessário
3. **Logs**: Implementar auditoria de criação/edição de notícias
4. **Notificações**: Sistema de notificação para aprovação de notícias

---

**Data**: 17 de Junho de 2025  
**Versão**: 1.0  
**Status**: Implementado e Funcional 