# Sistema de Promoções

## Visão Geral

O sistema de promoções permite que usuários com cargos de gestão promovam seus subordinados para outros cargos **dentro da mesma entidade/órgão**, sem a necessidade de exonerar e nomear novamente.

## Funcionalidades Implementadas

### 1. Botão "Promover" no Painel de Gestão

- **Localização**: Painel de Gestão de Cargos → Aba "Usuários Subordinados"
- **Aparência**: Botão amarelo com ícone de seta para cima (⬆️)
- **Posicionamento**: Ao lado dos botões "Exonerar" e "Ver Perfil"

### 2. Modal de Promoção

#### Campos do Modal:
- **Usuário Selecionado**: Exibe nome e cargo atual
- **Novo Cargo**: Lista apenas cargos da mesma entidade
- **Observações**: Campo opcional para justificar a promoção

#### Validações:
- ✅ Apenas cargos da mesma entidade são listados
- ✅ Verificação se o cargo de destino está disponível
- ✅ Verificação de permissões do gestor
- ✅ Impede promoção para o mesmo cargo atual

### 3. Backend - View `promover_usuario`

#### Validações de Segurança:
1. **Autenticação**: Usuário deve estar logado
2. **Cargo do Gestor**: Deve ter cargo com permissões de gestão
3. **Permissões**: Deve poder gerenciar tanto o cargo atual quanto o novo
4. **Mesma Entidade**: Promoção só permitida dentro da mesma entidade
5. **Cargo Disponível**: Verifica se o cargo de destino não está ocupado
6. **Cargo Diferente**: Impede promoção para o mesmo cargo

#### Processo de Promoção:
1. **Finalizar Cargo Atual**: 
   - Define `data_fim` no histórico atual
   - Marca como "Promovido para [Novo Cargo]"
   
2. **Atualizar Perfil**:
   - Altera `cargo_atual` no perfil do usuário
   
3. **Criar Novo Histórico**:
   - Cria registro no `HistoricoCargo` para o novo cargo
   - Define o gestor como `nomeado_por`
   - Adiciona observações da promoção

4. **Publicação no Diário Oficial**:
   - Cria automaticamente publicação tipo "promocao"
   - Usa template específico para decretos de promoção

### 4. Diário Oficial - Publicações de Promoção

#### Template do Decreto:
```
DECRETO DE PROMOÇÃO

O [Poder], no uso das atribuições que lhe confere a Constituição Federal...

CONSIDERANDO [motivo da promoção];
CONSIDERANDO a necessidade de reorganização administrativa...

DECRETA:

Art. 1º - PROMOVER [Nome], para exercer o cargo de [Novo Cargo]...
Art. 2º - A promoção tem caráter definitivo...
Art. 3º - Ficam mantidos todos os direitos e prerrogativas...
```

#### Características:
- **Tipo**: `promocao`
- **Seção**: Baseada no poder (executivo/legislativo/judiciario)
- **Automática**: Gerada automaticamente pelo sistema
- **Histórico**: Vinculada ao `HistoricoCargo` da promoção

### 5. Sistema de Logs

Logs detalhados para debugging incluem:
- 🚀 Início do processo de promoção
- 👤 Dados do usuário e gestor
- 💼 Cargos envolvidos (atual e novo)
- 🔍 Verificações de permissões
- ✅ Etapas concluídas com sucesso
- 📰 Criação da publicação no Diário Oficial

## API Endpoints

### POST `/painel-gestao-cargos/promover/`

**Parâmetros:**
```json
{
    "usuario_id": 123,
    "cargo_id": 456,
    "observacoes": "Reconhecimento pelos serviços prestados"
}
```

**Resposta de Sucesso:**
```json
{
    "success": true,
    "message": "João Silva foi promovido(a) de Secretário para Diretor com sucesso!"
}
```

**Resposta de Erro:**
```json
{
    "success": false,
    "error": "Você não tem permissão para gerenciar este cargo"
}
```

### GET `/api/cargos-por-entidade/<entidade_id>/`

Retorna cargos disponíveis para promoção dentro da entidade.

**Resposta:**
```json
{
    "success": true,
    "cargos": [
        {
            "id": 456,
            "nome": "Diretor",
            "simbolo_icon": "👑"
        }
    ]
}
```

## Diferenças entre Promoção e Nomeação

| Aspecto | Promoção | Nomeação |
|---------|----------|----------|
| **Escopo** | Mesma entidade | Qualquer cargo gerenciável |
| **Processo** | Finaliza cargo atual + cria novo | Apenas cria novo cargo |
| **Histórico** | Mantém continuidade | Pode ter gaps |
| **Diário Oficial** | "DECRETO DE PROMOÇÃO" | "DECRETO DE NOMEAÇÃO" |
| **Uso** | Progressão de carreira | Primeira nomeação ou mudança de órgão |

## Vantagens do Sistema

1. **Simplicidade**: Um clique para promover dentro da mesma entidade
2. **Continuidade**: Mantém histórico contínuo sem gaps
3. **Automação**: Publicação automática no Diário Oficial
4. **Segurança**: Múltiplas validações de permissões
5. **Auditoria**: Logs detalhados de todas as operações
6. **Flexibilidade**: Campo de observações personalizáveis

## Como Usar

1. **Acesse**: Painel de Gestão de Cargos
2. **Navegue**: Aba "Usuários Subordinados"
3. **Clique**: Botão "Promover" do usuário desejado
4. **Selecione**: Novo cargo na mesma entidade
5. **Justifique**: Adicione observações sobre a promoção
6. **Confirme**: Clique em "Confirmar Promoção"
7. **Verifique**: A publicação será criada automaticamente no Diário Oficial

## Notas Técnicas

- **Constraint de Banco**: Previne duplicações de publicações
- **Fuso Horário**: Usa horário de Brasília para datas
- **Performance**: Queries otimizadas para listagem de cargos
- **Compatibilidade**: Funciona com sistema existente de nomeações/exonerações

---

**Data de Implementação**: Dezembro 2024
**Versão**: 1.0
**Status**: ✅ Implementado e Testado 