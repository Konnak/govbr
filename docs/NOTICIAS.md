# Sistema de Notícias

O sistema de notícias permite a publicação e gerenciamento de notícias do governo e da imprensa. O sistema é altamente personalizável e possui recursos avançados de edição e moderação.

## Funcionalidades

### Tipos de Notícia
- **Notícias do Governo**: Publicadas por servidores com cargos governamentais
- **Notícias da Imprensa**: Publicadas por servidores com cargos na imprensa

### Editor Rico
O sistema utiliza o TinyMCE como editor de texto rico, permitindo:
- Formatação de texto (negrito, itálico, sublinhado)
- Alinhamento de texto
- Listas ordenadas e não ordenadas
- Inserção de links
- Upload e gerenciamento de imagens
- Tabelas
- Citações
- E muito mais

### Galeria de Imagens
- Upload múltiplo de imagens
- Ordenação personalizada
- Legendas para cada imagem
- Preview em tempo real
- Suporte a drag & drop

### Categorização
- Sistema de categorias com cores e ícones
- Tags dinâmicas
- Filtros por categoria e tag
- Busca por texto completo

### Comentários
- Sistema de comentários para usuários autenticados
- Moderação de comentários
- Opção para desativar comentários por notícia

### Moderação
- Sistema de status (rascunho, revisão, publicado, arquivado)
- Fluxo de aprovação para publicações
- Controle de permissões por cargo
- Histórico de edições

## Permissões

### Criação de Notícias
- Servidores com cargo no Poder Imprensa podem criar notícias
- Superusuários podem criar qualquer tipo de notícia

### Edição
- Autor da notícia
- Editores do mesmo órgão
- Moderadores
- Superusuários

### Moderação
- Chefes de órgãos da imprensa
- Moderadores designados
- Superusuários

## Fluxo de Publicação

1. **Criação**
   - Autor cria a notícia
   - Define tipo, título, conteúdo e mídia
   - Categoriza com tags e categorias
   - Salva como rascunho ou envia para revisão

2. **Revisão**
   - Moderadores revisam o conteúdo
   - Podem sugerir alterações
   - Aprovam ou rejeitam a publicação

3. **Publicação**
   - Notícia aprovada é publicada
   - Aparece na listagem pública
   - Disponível para comentários

4. **Arquivamento**
   - Notícias antigas podem ser arquivadas
   - Permanecem acessíveis mas não aparecem na listagem principal

## Personalização

### Categorias
As categorias podem ser personalizadas com:
- Nome
- Slug (URL amigável)
- Cor
- Ícone (FontAwesome)
- Descrição

### Tags
- Criação dinâmica
- Agrupamento de conteúdo relacionado
- Nuvem de tags

### Aparência
- Cards modernos com efeitos hover
- Imagens responsivas
- Suporte a tema escuro
- Animações suaves

## Integração

### Frontend
- Bootstrap 5
- Select2 para seleção múltipla
- Dropzone.js para upload de arquivos
- TinyMCE para edição de texto
- Toastify para notificações

### Backend
- Django
- PostgreSQL
- Sistema de permissões integrado
- Cache para otimização

## Endpoints da API

### Upload de Imagens
```
POST /api/upload-imagem/
Content-Type: multipart/form-data

Parameters:
- file: Arquivo de imagem (required)

Response:
{
    "location": "URL da imagem"
}
```

## Estrutura de Arquivos

```
templates/main/
  ├── noticia_criar.html
  ├── noticia_editar.html
  ├── noticia_detalhe.html
  └── noticia_lista.html

static/
  ├── css/
  │   └── noticias.css
  └── js/
      └── noticias.js

main/
  ├── models.py
  ├── views.py
  └── urls.py
```

## Próximos Passos

1. **Melhorias Planejadas**
   - Sistema de newsletters
   - Compartilhamento em redes sociais
   - Estatísticas avançadas
   - Sistema de destaques
   - Integração com Discord

2. **Otimizações**
   - Cache de consultas frequentes
   - Compressão de imagens
   - Lazy loading de imagens
   - Paginação infinita

3. **Recursos Futuros**
   - Editor colaborativo
   - Sistema de revisão
   - Versões de notícias
   - Programação de publicações 