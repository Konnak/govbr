# Guia do Painel Administrativo - GovBR Roleplay

## Acesso ao Painel

Para acessar o painel administrativo, visite:
```
http://localhost:8000/admin/
```

Use as credenciais de superusuário criadas durante a instalação.

## Funcionalidades do Painel

### 1. Gerenciamento de Notícias

#### Criando uma Nova Notícia
1. Acesse **Main > Notícias**
2. Clique em **Adicionar Notícia**
3. Preencha os campos:
   - **Título**: Título da notícia
   - **Resumo**: Breve descrição (máx. 300 caracteres)
   - **Conteúdo**: Texto completo da notícia
   - **Tipo**: Governo ou Imprensa
   - **Imagem**: Upload da imagem (opcional)
   - **Publicado**: Marque para exibir no site
   - **Destaque**: Marque para aparecer no slide principal

#### Configurações Importantes
- **Data de Publicação**: Define quando a notícia foi publicada
- **Destaque**: Notícias marcadas aparecem no slide principal
- **Visualizações**: Atualizado automaticamente pelo sistema

### 2. Botões Configuráveis

#### Criando um Botão
1. Acesse **Main > Botões Configuráveis**
2. Clique em **Adicionar Botão Configurável**
3. Configure:
   - **Título**: Nome do botão
   - **Descrição**: Texto explicativo
   - **Ícone**: Classe CSS do ícone (ex: `fas fa-user`, `bi bi-house`)
   - **Link**: URL de destino
   - **Cor de Fundo**: Cor em hexadecimal
   - **Ordem**: Define a posição de exibição

#### Exemplos de Ícones
- Font Awesome: `fas fa-user`, `fas fa-home`, `fas fa-cog`
- Bootstrap Icons: `bi bi-person`, `bi bi-house`, `bi bi-gear`

### 3. Estatísticas do Sistema

#### Configuração
1. Acesse **Main > Estatísticas do Sistema**
2. Edite os valores:
   - **Total de Usuários**: Atualizado automaticamente
   - **Total de Imigrantes**: Baseado no nível de acesso
   - **Total de Cidadãos**: Baseado no nível de acesso
   - **Usuários Últimos 7 Dias**: Novos usuários

**Nota**: O sistema permite apenas uma instância de estatísticas.

### 4. Anúncios

#### Criando um Anúncio
1. Acesse **Main > Anúncios**
2. Clique em **Adicionar Anúncio**
3. Configure:
   - **Título**: Título do anúncio
   - **Descrição**: Texto do anúncio
   - **Imagem**: Upload obrigatório
   - **Link**: URL opcional
   - **Data de Início/Fim**: Período de exibição
   - **Ativo**: Controla se está visível
   - **Ordem**: Define posição

### 5. Configurações do Site

#### Configuração Geral
1. Acesse **Main > Configurações do Site**
2. Edite:
   - **Nome do Site**: Aparece no título
   - **Logo**: Upload da logo
   - **Favicon**: Ícone do navegador
   - **Link do Discord**: URL do servidor Discord
   - **Mensagem do Discord**: Texto da seção Discord
   - **Cores**: Primária e secundária em hexadecimal
   - **Texto do Rodapé**: Informações do footer

## Dicas de Uso

### Otimização de Imagens
- **Notícias**: Use imagens 800x400px para melhor exibição
- **Anúncios**: Recomendado 600x300px
- **Logo**: Máximo 200x60px
- **Favicon**: 32x32px ou 16x16px

### SEO e Performance
- Preencha sempre o resumo das notícias
- Use títulos descritivos
- Otimize o tamanho das imagens
- Configure as datas de publicação corretamente

### Organização de Conteúdo
- Use a funcionalidade de ordem para organizar botões e anúncios
- Marque apenas as melhores notícias como destaque
- Mantenha anúncios com datas atualizadas

## Fluxo de Trabalho Recomendado

### Para Notícias
1. Criar notícia como rascunho (não publicada)
2. Adicionar imagem e revisar conteúdo
3. Definir data de publicação
4. Marcar como publicada
5. Se necessário, marcar como destaque

### Para Configurações
1. Configurar informações básicas do site primeiro
2. Adicionar logo e favicon
3. Configurar cores do tema
4. Adicionar link do Discord
5. Personalizar texto do rodapé

### Para Botões de Serviço
1. Planejar a disposição dos botões
2. Definir ordem lógica (mais importantes primeiro)
3. Escolher ícones consistentes
4. Testar links antes de ativar
5. Usar cores que combinem com o tema

## Permissões e Segurança

### Níveis de Acesso
- **Superusuário**: Acesso total ao sistema
- **Staff**: Pode acessar admin mas com permissões limitadas
- **Usuário comum**: Apenas acesso ao site público

### Recomendações de Segurança
- Use senhas fortes para superusuários
- Limite o número de superusuários
- Faça backup regular do banco de dados
- Monitore logs de acesso ao admin

## Manutenção

### Tarefas Regulares
- Atualizar estatísticas manualmente se necessário
- Remover anúncios expirados
- Revisar e atualizar notícias antigas
- Verificar links quebrados nos botões
- Backup do banco de dados

### Monitoramento
- Verificar visualizações das notícias
- Acompanhar crescimento de usuários
- Validar funcionamento dos links
- Testar responsividade em diferentes dispositivos

## Troubleshooting

### Problemas Comuns

#### Imagens não aparecem
- Verifique se o arquivo foi enviado corretamente
- Confirme as configurações de MEDIA_URL
- Verifique permissões da pasta media

#### Botões não funcionam
- Teste o link em nova aba
- Verifique se o ícone existe
- Confirme se está marcado como ativo

#### Estatísticas incorretas
- Acesse o admin e atualize manualmente
- Verifique se há usuários cadastrados
- Execute os cálculos de atualização

### Logs e Debug
- Verifique o console do navegador para erros JavaScript
- Monitore logs do Django para erros de servidor
- Use o modo DEBUG apenas em desenvolvimento

## Próximas Funcionalidades

### Em Desenvolvimento
- Sistema completo de usuários
- Integração com API do Roblox
- Newsletter automática
- Comentários em notícias
- Dashboard de analytics

### Planejadas
- Editor WYSIWYG para notícias
- Sistema de tags
- Busca avançada
- API REST
- Notificações push 