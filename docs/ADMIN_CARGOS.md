# Sistema de Seleção Hierárquica de Cargos no Admin

## Visão Geral

O sistema de administração do Django foi aprimorado para permitir a seleção hierárquica de cargos governamentais diretamente no painel de usuários. Agora é possível selecionar individualmente o **Poder**, **Órgão**, **Entidade** e **Cargo** de cada usuário.

## Funcionalidades Implementadas

### 1. Interface de Seleção Hierárquica

- **Campos em cascata**: Poder → Órgão → Entidade → Cargo
- **Seleção dinâmica**: Os campos são atualizados automaticamente baseado na seleção anterior
- **Validação**: O sistema valida se a hierarquia está correta antes de salvar

### 2. Melhorias no Admin de Usuários

#### Lista de Usuários
- **Nova coluna "Cargo Atual"**: Mostra o cargo, entidade e poder do usuário
- **Filtros aprimorados**: Filtrar por símbolo de gestão e poder
- **Busca expandida**: Buscar também pelo nome do cargo

#### Edição de Usuário
- **Seção "Cargo e Posição no Governo"**: Nova seção inline para gerenciar cargos
- **Campos hierárquicos**: Poder, Órgão, Entidade e Cargo em cascata
- **Instruções claras**: Orientações sobre como preencher os campos

### 3. Sistema AJAX

#### Endpoints Criados
- `/users/admin/ajax/orgaos/` - Retorna órgãos baseado no poder
- `/users/admin/ajax/entidades/` - Retorna entidades baseado no órgão  
- `/users/admin/ajax/cargos/` - Retorna cargos baseado na entidade

#### JavaScript Dinâmico
- Atualização automática dos campos de seleção
- Validação em tempo real
- Interface responsiva

## Como Usar

### 1. Acessar o Admin
1. Acesse `/admin/`
2. Vá em **Usuários** → **Users**
3. Clique em um usuário para editar

### 2. Definir Cargo
1. Role até a seção **"Cargo e Posição no Governo"**
2. Selecione o **Poder** (Executivo, Judiciário, Legislativo, Imprensa)
3. Selecione o **Órgão** (será carregado automaticamente)
4. Selecione a **Entidade** (será carregada automaticamente)
5. Selecione o **Cargo** (será carregado automaticamente)
6. Clique em **Salvar**

### 3. Validações Automáticas
- O sistema verifica se a hierarquia está correta
- Não permite salvar se houver inconsistências
- Mostra mensagens de erro claras

## Estrutura Técnica

### Arquivos Modificados

#### `users/admin.py`
- `ProfileInlineForm`: Formulário com campos hierárquicos
- `ProfileInline`: Inline admin para Profile
- `UserAdmin`: Admin aprimorado com nova coluna e filtros

#### `users/views.py`
- `ajax_orgaos()`: View para buscar órgãos
- `ajax_entidades()`: View para buscar entidades
- `ajax_cargos()`: View para buscar cargos

#### `users/urls.py`
- Rotas AJAX para seleção hierárquica

#### `static/admin/js/profile_hierarchy.js`
- JavaScript para atualização dinâmica dos campos
- Funções AJAX para comunicação com o backend

### Fluxo de Funcionamento

1. **Usuário seleciona Poder**
   - JavaScript detecta mudança
   - Faz requisição AJAX para `/users/admin/ajax/orgaos/`
   - Atualiza campo Órgão com opções filtradas
   - Limpa campos Entidade e Cargo

2. **Usuário seleciona Órgão**
   - JavaScript detecta mudança
   - Faz requisição AJAX para `/users/admin/ajax/entidades/`
   - Atualiza campo Entidade com opções filtradas
   - Limpa campo Cargo

3. **Usuário seleciona Entidade**
   - JavaScript detecta mudança
   - Faz requisição AJAX para `/users/admin/ajax/cargos/`
   - Atualiza campo Cargo com opções filtradas

4. **Usuário seleciona Cargo e salva**
   - Formulário valida hierarquia
   - Salva cargo no Profile do usuário
   - Atualiza histórico de cargos automaticamente

## Permissões

- Apenas usuários com permissão de **staff** podem acessar as views AJAX
- Decorador `@staff_member_required` protege os endpoints
- Validação CSRF em todas as requisições

## Benefícios

1. **Interface Intuitiva**: Seleção guiada passo a passo
2. **Validação Robusta**: Impossível criar hierarquias inválidas
3. **Performance**: Carregamento dinâmico reduz dados desnecessários
4. **Usabilidade**: Campos se atualizam automaticamente
5. **Manutenibilidade**: Código bem estruturado e documentado

## Troubleshooting

### Campos não carregam dinamicamente
- Verifique se o JavaScript está sendo carregado
- Confirme se as URLs AJAX estão corretas
- Verifique o console do navegador para erros

### Erro de validação ao salvar
- Certifique-se de que a hierarquia está correta
- Verifique se todos os campos obrigatórios estão preenchidos
- Confirme se o cargo pertence à entidade selecionada

### Permissão negada nas requisições AJAX
- Usuário deve ter permissão de staff
- Verificar se está logado no admin
- Confirmar token CSRF

## Próximos Passos

1. **Melhorias na Interface**
   - Adicionar ícones aos campos
   - Melhorar feedback visual
   - Adicionar tooltips explicativos

2. **Funcionalidades Avançadas**
   - Histórico de alterações de cargo
   - Notificações de mudanças
   - Relatórios de cargos

3. **Otimizações**
   - Cache das consultas AJAX
   - Paginação para listas grandes
   - Busca em tempo real 