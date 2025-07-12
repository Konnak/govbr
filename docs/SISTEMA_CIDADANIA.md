# Sistema de Cidadania - GovBR Roleplay

## Visão Geral

O Sistema de Cidadania foi implementado para gerenciar solicitações de cidadania brasileira no roleplay. O sistema permite que imigrantes solicitem cidadania e que autoridades competentes analisem e respondam a essas solicitações.

## Funcionalidades Implementadas

### 1. Solicitação de Cidadania
- **Formulário de Solicitação**: Imigrantes podem solicitar cidadania através de um formulário próprio
- **Validações Automáticas**:
  - Usuário não pode ser cidadão já
  - Não pode ter solicitação pendente
  - Não pode ter solicitação já aprovada
  - Sistema deve estar ativo
- **Upload de Documentos**: Suporte a anexo de documentos necessários
- **Sistema de Status**: Pendente, Aprovada, Rejeitada

### 2. Gestão de Solicitações
- **Painel de Gestão**: Interface completa para visualizar e gerenciar solicitações
- **Filtros Avançados**: Por status, data, órgão responsável
- **Ações Disponíveis**:
  - Aprovar solicitação
  - Rejeitar solicitação  
  - Visualizar detalhes
  - Adicionar observações
- **Relatórios**: Estatísticas e métricas do sistema

### 3. Sistema de Configuração
- **Configurações Básicas**:
  - Prazo para análise (em dias)
  - Status do sistema (ativo/inativo)
  - Instruções para solicitantes
  - Lista de documentos obrigatórios
- **Órgão Responsável**: Configuração de qual órgão processa as solicitações
- **Cargos Autorizados**: Lista de cargos que podem aprovar/rejeitar
- **Seção Especial PF**: Destaque para cargos da Polícia Federal

## Permissões de Acesso

### Quem Pode Acessar a Gestão
1. **Níveis de Usuário**: Administrador, Coordenador, Fundador
2. **Cargos da Polícia Federal**: Todos os cargos configurados da PF
3. **Cargos Personalizados**: Conforme configuração do sistema

### Quem Pode Aprovar/Rejeitar
- Usuários com permissão `users.pode_analisar_cidadania`
- Cargos configurados na lista de "Cargos Autorizados"
- Níveis altos: Administrador, Coordenador, Fundador

## Regras de Negócio

### Solicitação
1. **Uma vez aprovado**: Usuário não pode solicitar novamente
2. **Se rejeitado**: Usuário pode fazer nova solicitação
3. **Pendente**: Usuário deve aguardar resposta antes de nova solicitação
4. **Sistema inativo**: Novas solicitações são bloqueadas

### Aprovação
1. **Mudança de Nível**: Aprovação muda usuário de "imigrante" para "cidadao"
2. **Registro**: Todas as ações são registradas com data e responsável
3. **Observações**: Campo para justificativas das decisões

## Arquivos Implementados

### Views (`main/views.py`)
- `gestao_cidadania()`: Painel principal de gestão
- `configurar_cidadania()`: Configuração do sistema
- `aprovar_cidadania()`: API para aprovação
- `rejeitar_cidadania()`: API para rejeição

### Models (`main/models.py`)
- `ConfiguracaoCidadania`: Configurações do sistema
- Adição de `is_cidadao` ao modelo `User`
- Permissions customizadas

### Templates
- `templates/main/gestao_cidadania.html`: Interface de gestão
- `templates/main/configurar_cidadania.html`: Configuração

### URLs (`main/urls.py`)
- `/gestao-cidadania/`: Painel de gestão
- `/gestao-cidadania/configurar/`: Configuração
- `/api/cidadania/aprovar/<id>/`: Aprovação
- `/api/cidadania/rejeitar/<id>/`: Rejeição

### Admin (`main/admin.py`)
- Configuração administrativa para `ConfiguracaoCidadania`
- Proteções: apenas uma configuração, não deletável

## Integrações

### Sistema de Usuários
- Propriedade `is_cidadao` no modelo User
- Atualização automática do nível de acesso
- Integração com sistema de permissões

### Interface de Gestão
- Link no painel de gestão de cargos
- Acesso contextual baseado em permissões
- Design consistente com o restante do sistema

## Segurança

### Validações
- Verificação de permissões em todas as operações
- CSRF protection em formulários
- Sanitização de dados de entrada

### Auditoria
- Log de todas as aprovações/rejeições
- Histórico completo de solicitações
- Rastreabilidade de responsáveis

## Configuração Inicial

### 1. Acessar Admin
```
/admin/main/configuracaocidadania/
```

### 2. Configurar Órgão Responsável
- Selecionar Polícia Federal ou outro órgão apropriado

### 3. Definir Cargos Autorizados
- Marcar cargos que podem aprovar/rejeitar
- Usar filtros por poder/órgão/entidade

### 4. Configurar Documentos
- Listar documentos obrigatórios (um por linha)
- Atualizar instruções para solicitantes

## Uso Operacional

### Para Gestores
1. Acessar painel através do botão "Gestão de Cidadania"
2. Visualizar solicitações pendentes
3. Analisar documentos e informações
4. Aprovar ou rejeitar com observações

### Para Imigrantes
1. Acessar formulário de solicitação existente
2. Preencher dados e anexar documentos
3. Aguardar análise da autoridade competente
4. Receber resposta com status atualizado

## Melhorias Futuras

### Possíveis Implementações
- [ ] Sistema de notificações por email/Discord
- [ ] Workflow de revisão (análise inicial + aprovação final)
- [ ] Dashboard com métricas detalhadas
- [ ] Histórico completo por usuário
- [ ] Sistema de recursos para solicitações rejeitadas
- [ ] Integração com Discord para roles automáticos

### Otimizações
- [ ] Cache para configurações frequentes
- [ ] Paginação otimizada para grandes volumes
- [ ] Filtros salvos para gestores
- [ ] Exportação de relatórios

## Considerações Técnicas

### Performance
- Queries otimizadas com `select_related` e `prefetch_related`
- Filtros eficientes no banco de dados
- Cache adequado para configurações

### Escalabilidade  
- Estrutura preparada para múltiplos órgãos
- Sistema de permissões flexível
- Separação clara de responsabilidades

### Manutenibilidade
- Código bem documentado
- Separação de concerns
- Padrões Django seguidos
- Testes unitários recomendados

---

## Conclusão

O Sistema de Cidadania está **completo e funcional**, atendendo a todos os requisitos solicitados:

✅ **Interface para receber solicitações**  
✅ **Acesso para PF e níveis administrativos**  
✅ **Configuração de órgão responsável**  
✅ **Configuração de cargos autorizados**  
✅ **Reutilização do formulário existente**  
✅ **Regras de negócio implementadas**  

O sistema está pronto para uso em produção e pode ser expandido conforme necessidades futuras. 