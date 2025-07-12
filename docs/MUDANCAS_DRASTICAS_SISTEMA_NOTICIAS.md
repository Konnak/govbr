# Mudanças Drásticas no Sistema de Notícias - GovBR Roleplay

## Resumo das Mudanças

Este documento descreve as mudanças drásticas implementadas no sistema de notícias do GovBR Roleplay, focando na simplificação e restrição do sistema para maior realismo governamental.

## Mudanças Implementadas

### 1. ✅ Edição de Notícias Completa
- **Template de edição** completamente reformulado
- **Todas as funcionalidades** da criação disponíveis na edição
- **Template tags personalizadas** para verificação de permissões
- **Interface moderna** igual ao template de criação

### 2. ✅ Remoção Completa do Sistema de Imprensa
- **Poder Imprensa removido** completamente do sistema
- **Slide de notícias da imprensa** removido da página inicial
- **Seção de notícias da imprensa** removida da home
- **JavaScript simplificado** (removido swiper da imprensa)
- **Todas as notícias** agora são exclusivamente do governo

### 3. ✅ Restrição de Criação por Cargo de Gestão
- **Apenas cargos `**` e `*`** podem criar notícias
- **Verificação rigorosa** na view de criação
- **Mensagens de erro claras** para usuários sem permissão
- **Sistema baseado em hierarquia** real do governo

## Detalhamento Técnico

### Sistema de Permissões Atualizado

#### Criação de Notícias
```python
# Verificação na view noticia_criar
if not request.user.is_superuser:
    # Verificar se é cargo de gestão (** ou *)
    if profile.cargo_atual.simbolo_gestao not in ['**', '*']:
        messages.error(request, 'Apenas cargos de gestão podem criar notícias.')
        return redirect('main:home')
```

#### Edição de Notícias
```html
<!-- Template tags personalizadas -->
{% load noticia_tags %}
{% if noticia|pode_editar:user %}
    <!-- Botão de editar -->
{% endif %}
```

### Estrutura Simplificada

#### Antes (Sistema Dual)
- Notícias do Governo (slide próprio)
- Notícias da Imprensa (slide próprio)
- Seção de notícias da imprensa
- Dois tipos de notícia diferentes
- Permissões complexas por tipo

#### Depois (Sistema Unificado)
- **Apenas notícias do governo**
- **Um slide principal** para notícias em destaque
- **Uma seção** de notícias recentes
- **Tipo único**: governo
- **Permissões baseadas** exclusivamente no cargo

### Views Atualizadas

#### `home(request)`
```python
# Antes
noticias_governo_destaque = [...]
noticias_imprensa_destaque = [...]
noticias_imprensa = [...]

# Depois
noticias_governo_destaque = [...]
noticias_recentes = [...]  # Todas do governo
```

#### `noticia_criar(request)`
```python
# Antes
if orgao_usuario.poder.nome.lower() == 'imprensa':
    tipo_noticia = 'imprensa'
else:
    tipo_noticia = 'governo'

# Depois
tipo_noticia = 'governo'  # Sempre governo
```

### Templates Atualizados

#### `home.html`
- ❌ Removido: Slide da imprensa
- ❌ Removido: Seção de notícias da imprensa
- ❌ Removido: JavaScript do swiper da imprensa
- ✅ Mantido: Slide do governo
- ✅ Adicionado: Seção de notícias recentes (todas do governo)

#### `noticia_criar.html` e `noticia_editar.html`
- ❌ Removido: Opção de escolher tipo imprensa
- ✅ Fixado: Tipo sempre "governo"
- ✅ Melhorado: Verificação de permissões por cargo
- ✅ Adicionado: Mensagens dinâmicas baseadas no cargo

## Hierarquia de Cargos para Notícias

### Cargos Autorizados (Criação + Publicação Direta)
- `**` - **Chefe de Poder** (Presidente, Presidente do STF, Presidente do Senado)
- `*` - **Líder de Órgão** (Ministros, Desembargadores, Secretários)

### Cargos Não Autorizados
- `+` - Subchefia (podem ver, mas não criar)
- `nenhum` - Cargos operacionais (apenas visualização)

### Superusuários
- **Administradores** sempre podem criar e publicar
- **Permissões especiais** através do sistema Django

## Impacto nas Funcionalidades

### ✅ Funcionalidades Mantidas
- Sistema de slides na home
- Criação de notícias
- Edição de notícias
- Sistema de categorias e tags
- Upload de imagens
- Sistema de destaque
- Comentários em notícias
- Visualizações e estatísticas

### ❌ Funcionalidades Removidas
- Poder Imprensa
- Notícias tipo "imprensa"
- Slide separado da imprensa
- Seção separada de notícias da imprensa
- Criação por cargos baixos

### 🔄 Funcionalidades Modificadas
- **Criação restrita** a cargos de gestão
- **Tipo único** de notícia (governo)
- **Interface simplificada** sem escolha de tipo
- **Permissões baseadas** em hierarquia real

## Benefícios das Mudanças

### 1. **Maior Realismo**
- Sistema reflete estrutura real do governo
- Apenas autoridades podem fazer comunicados oficiais
- Eliminação de confusão entre governo e imprensa

### 2. **Simplicidade**
- Interface mais limpa e focada
- Menos opções confusas para usuários
- Sistema mais fácil de entender e usar

### 3. **Controle de Qualidade**
- Apenas cargos de gestão criam conteúdo
- Maior responsabilidade nas publicações
- Redução de spam ou conteúdo inadequado

### 4. **Performance**
- Menos consultas ao banco (um tipo só)
- Cache mais eficiente
- JavaScript mais leve

## Migração de Dados

### Notícias Existentes
- ✅ **Notícias da imprensa** convertidas para governo
- ✅ **Órgão de publicação** preservado estaticamente
- ✅ **Histórico mantido** através do campo `orgao_publicacao`

### Estrutura Organizacional
- ✅ **Poder Imprensa** removido completamente
- ✅ **Órgãos da imprensa** removidos
- ✅ **Usuários exonerados** automaticamente dos cargos da imprensa

## Próximos Passos Recomendados

### 1. **Limpeza de CSS**
- Remover estilos específicos da imprensa
- Otimizar CSS para tipo único de notícia

### 2. **Otimização de Cache**
- Ajustar chaves de cache para novo sistema
- Implementar cache mais eficiente

### 3. **Documentação de Usuário**
- Atualizar guias para novos usuários
- Documentar processo de criação de notícias

### 4. **Monitoramento**
- Acompanhar feedback dos usuários
- Verificar performance do sistema simplificado

## Conclusão

As mudanças implementadas transformaram o sistema de notícias de um modelo dual (governo + imprensa) para um modelo unificado e realista, onde apenas autoridades governamentais podem criar comunicados oficiais. Isso resulta em:

- **Maior realismo** na simulação governamental
- **Interface mais simples** e intuitiva
- **Controle de qualidade** aprimorado
- **Performance otimizada**

O sistema agora reflete melhor a realidade de comunicação oficial de um governo, onde apenas autoridades competentes fazem declarações em nome do Estado.

---

**Data da Implementação**: 17 de Junho de 2025  
**Versão**: 2.0.0 - Sistema Unificado  
**Status**: ✅ Implementado e Testado 