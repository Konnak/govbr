# Configuração do Discord OAuth2

## Visão Geral

O sistema agora suporta vinculação automática de contas Discord através do OAuth2, capturando automaticamente:
- ID do Discord
- Username (@usuario)
- Nome de exibição
- Avatar
- Email (se autorizado)

## Configuração

### 1. Criar Aplicação no Discord

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Dê um nome para sua aplicação (ex: "GovBR Roleplay")
4. Vá para a aba "OAuth2"

### 2. Configurar OAuth2

**Redirect URIs:**
```
http://127.0.0.1:8000/usuarios/discord/callback/
http://localhost:8000/usuarios/discord/callback/
```

**Scopes necessários:**
- `identify` - Para obter informações básicas do usuário
- `email` - Para obter o email (opcional)

### 3. Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```env
# Discord OAuth2 Settings
DISCORD_CLIENT_ID=seu-client-id-aqui
DISCORD_CLIENT_SECRET=seu-client-secret-aqui
DISCORD_REDIRECT_URI=http://127.0.0.1:8000/usuarios/discord/callback/
DISCORD_BOT_TOKEN=seu-bot-token-opcional
```

### 4. Obter Credenciais

1. **Client ID**: Disponível na aba "General Information"
2. **Client Secret**: Disponível na aba "OAuth2" > "Client Secret"
3. **Bot Token**: (Opcional) Disponível na aba "Bot"

## Como Funciona

### Fluxo de Vinculação

1. Usuário clica em "Vincular Discord" no perfil
2. Sistema gera URL de autorização com `state` único
3. Usuário é redirecionado para o Discord
4. Discord solicita autorização do usuário
5. Usuário autoriza e é redirecionado de volta
6. Sistema valida o `state` e troca código por tokens
7. Sistema obtém dados do usuário via API do Discord
8. Dados são salvos no banco e conta é vinculada

### Dados Capturados

```json
{
  "id": "123456789012345678",
  "username": "usuario",
  "global_name": "Nome de Exibição",
  "avatar": "hash-do-avatar",
  "email": "usuario@email.com"
}
```

### Segurança

- **State Parameter**: Previne ataques CSRF
- **Token Encryption**: Tokens são armazenados de forma segura
- **Unique Constraint**: Um Discord ID só pode ser vinculado a uma conta
- **Token Revocation**: Tokens são revogados ao desvincular

## APIs Disponíveis

### Iniciar Vinculação
```
GET /usuarios/api/iniciar-vinculacao-discord/
```

### Callback OAuth
```
GET /usuarios/discord/callback/?code=...&state=...
```

### Desvincular Discord
```
POST /usuarios/api/desvincular-discord/
```

## Interface do Usuário

### Botão de Vinculação
- Aparece apenas se Discord não estiver vinculado
- Inicia fluxo OAuth2 automaticamente

### Card do Discord Vinculado
- Mostra avatar, nome de exibição e username
- Data de vinculação
- Botão para desvincular

### Informações Exibidas
- Avatar do Discord (se disponível)
- Nome de exibição principal
- Username como informação secundária
- Data e hora da vinculação

## Troubleshooting

### Erro: "Invalid Redirect URI"
- Verifique se a URI está configurada corretamente no Discord
- Certifique-se de que não há barras extras ou caracteres especiais

### Erro: "Invalid Client"
- Verifique se CLIENT_ID e CLIENT_SECRET estão corretos
- Confirme se a aplicação está ativa no Discord

### Erro: "State Inválido"
- O state expira em 10 minutos
- Tente novamente o processo de vinculação

### Erro: "Discord já vinculado"
- Cada conta Discord só pode ser vinculada a um usuário
- Desvincule da conta anterior se necessário

## Desenvolvimento

### Testando Localmente

1. Configure as variáveis de ambiente
2. Use `http://127.0.0.1:8000` como base URL
3. Certifique-se de que o redirect URI está configurado no Discord

### Logs de Debug

O sistema registra logs detalhados:
- Início do processo OAuth
- Troca de códigos por tokens
- Vinculação/desvinculação de contas
- Erros de API

## Produção

### Configurações Adicionais

1. Use HTTPS em produção
2. Configure domínio real no redirect URI
3. Use variáveis de ambiente seguras
4. Configure rate limiting se necessário

### Monitoramento

- Monitore logs de erro da API Discord
- Acompanhe taxa de sucesso das vinculações
- Verifique tokens expirados periodicamente 