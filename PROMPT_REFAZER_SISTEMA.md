# PROMPT PARA REFAZER SISTEMA GOVBR ROLEPLAY

## OBJETIVO PRINCIPAL
Refazer completamente o sistema GovBR Roleplay - uma plataforma web que simula o Governo Brasileiro no ambiente Roblox. O sistema deve ser moderno, escalável, seguro e profissional, mantendo todas as funcionalidades existentes e melhorando a experiência do usuário.

## 1. IDENTIDADE VISUAL E DESIGN

### 1.1 Cores Principais (Baseadas na Bandeira do Brasil)
- **Azul Principal**: `#002776` (azul da bandeira)
- **Azul Claro**: `#1e4d8b`
- **Azul Médio**: `#0039a6`
- **Amarelo Principal**: `#ffcc00` (amarelo da bandeira)
- **Amarelo Claro**: `#ffd633`
- **Amarelo Escuro**: `#e6b800`
- **Verde Principal**: `#009c3b` (verde da bandeira)
- **Verde Claro**: `#00b841`
- **Verde Escuro**: `#007f2f`
- **Branco**: `#ffffff`

### 1.2 Tipografia
- **Fonte Principal**: Inter (Google Fonts)
- **Fonte Secundária**: System fonts (fallback)
- **Tamanhos**: 12px, 14px, 16px, 18px, 24px, 32px

### 1.3 Layout e Interface
- **Design**: Moderno, limpo e profissional
- **Responsividade**: Mobile-first
- **Framework CSS**: Bootstrap 5.3.2 ou superior
- **Ícones**: Font Awesome 6.5.1 ou superior
- **Animations**: Smooth transitions (0.3s ease)

## 2. TECNOLOGIAS E ARQUITETURA

### 2.1 Backend
- **Framework**: Django 4.2+ (Python 3.11+)
- **Banco de Dados**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Servidor Web**: Nginx + Gunicorn
- **Celery**: Para tarefas assíncronas

### 2.2 Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5.3.2
- **JavaScript**: Vanilla JS + jQuery 3.7+
- **Font Awesome**: 6.5.1
- **Editor Rico**: TinyMCE 6+

### 2.3 Integrações
- **Roblox API**: Para verificação de usuários
  - Endpoints: `/v1/users/{id}`, `/v1/users/avatar-headshot`
  - Rate limiting: 100 req/min por IP
  - Fallback para dados offline
- **Discord OAuth**: Autenticação opcional
  - Client ID/Secret configuráveis
  - Scopes: `identify`, `email`
  - Webhook integration para notificações
- **PDFs**: ReportLab + PyPDF2 + xhtml2pdf
  - Geração de documentos oficiais
  - Merge de PDFs para protocolos consolidados
  - Assinaturas digitais com timestamps
- **Imagens**: Pillow + pdf2image
  - Processamento e redimensionamento
  - Conversão PDF para imagem
  - Suporte: JPG, PNG, GIF, BMP (máx 10MB)

### 2.4 Bibliotecas Python Específicas
```
Django==4.2+
psycopg2-binary==2.9+
redis==4.5+
celery==5.3+
pillow==10.0+
reportlab==4.0+
PyPDF2==3.0+
xhtml2pdf==0.2+
pdf2image==1.16+
requests==2.31+
python-decouple==3.8+
django-cors-headers==4.3+
```

### 2.5 Configurações de Banco de Dados
```sql
-- Configurações específicas PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c default_transaction_isolation=serializable'
        },
        'CONN_MAX_AGE': 600,
    }
}

-- Índices obrigatórios
CREATE INDEX idx_historico_cargo_usuario ON main_historicocargo(usuario_id);
CREATE INDEX idx_historico_cargo_cargo ON main_historicocargo(cargo_id);
CREATE INDEX idx_protocolo_numero ON main_protocolo(numero_protocolo);
CREATE INDEX idx_noticia_slug ON main_noticia(slug);
CREATE INDEX idx_noticia_publicado ON main_noticia(publicado, status);
```

## 3. SISTEMA DE USUÁRIOS E PERMISSÕES

### 3.1 Níveis de Acesso (6 níveis)
1. **Imigrante** - Usuário novo sem verificação
2. **Cidadão** - Usuário verificado com documentos
3. **Servidor** - Usuário com cargo no governo
4. **Administrador** - Gestão de alto nível
5. **Coordenador** - Coordenação geral do sistema
6. **Fundador** - Acesso total ao sistema

### 3.2 Autenticação e Verificação
- **Obrigatório**: Username, senha, email
- **Verificação Roblox**: Username + ID do Roblox (obrigatório)
- **Discord (Opcional)**: OAuth2 integration
- **Campos**: Nome completo RP, avatar do Roblox, data de nascimento

### 3.3 Sistema de Cidadania
- Solicitação via formulário web
- Upload de documentos (RG, CPF, comprovante residência)
- Análise por órgãos competentes (configurável)
- Aprovação/rejeição com observações
- Mudança automática de nível de acesso

## 4. HIERARQUIA GOVERNAMENTAL COMPLETA

### 4.1 Estrutura de Poderes
O sistema deve suportar **3 Poderes**:

#### 🏛️ **PODER EXECUTIVO**
- **Cor Tema**: Verde (`#009c3b`)
- **Ícone**: 🏛️

#### ⚖️ **PODER JUDICIÁRIO** 
- **Cor Tema**: Amarelo (`#ffcc00`)
- **Ícone**: ⚖️

#### 📜 **PODER LEGISLATIVO**
- **Cor Tema**: Azul (`#002776`)
- **Ícone**: 📜




### 4.2 Símbolos de Gestão (Hierarquia de Cargos)
- **👑 `**`** = Chefe de Poder (ex: Presidente, Presidente do STF)
- **⭐ `*`** = Líder de Órgão (ex: Ministro, Desembargador)  
- **🔹 `+`** = Chefe de Entidade (ex: Diretor, Coordenador)
- **Nenhum** = Cargo operacional

### 4.3 Regras de Gestão
- **Chefe de Poder (`**`)**: Pode gerenciar TODOS os cargos do seu poder
- **Líder de Órgão (`*`)**: Pode gerenciar cargos `+` e sem símbolo do seu órgão
- **Chefe de Entidade (`+`)**: Pode gerenciar cargos sem símbolo da sua entidade

## 5. ESTRUTURA DETALHADA DE ÓRGÃOS, ENTIDADES E CARGOS

### 5.1 🏛️ PODER EXECUTIVO

#### **Presidência da República**
**Entidades:**
- **Casa Civil**
  - Chefe da Casa Civil (`*`)
  - Secretário-Executivo (`+`)
  - Assessor Especial
  - Analista de Políticas Públicas

- **Secretaria de Governo**
  - Secretário de Governo (`+`)
  - Coordenador de Articulação Política
  - Analista de Governo

- **Gabinete de Segurança Institucional**
  - Chefe do GSI (`+`)
  - Assessor de Segurança
  - Analista de Inteligência

**Cargos Principais:**
- Presidente da República (`**`)
- Vice-Presidente da República
- Porta-Voz da Presidência (`+`)

#### **Ministério da Justiça e Segurança Pública**
**Entidades:**
- **Polícia Federal**
  - Diretor-Geral da PF (`*`)
  - Superintendente Regional (`+`)
  - Delegado Federal
  - Agente Federal
  - Escrivão Federal
  - Papiloscopista Federal

- **Polícia Rodoviária Federal**
  - Diretor-Geral da PRF (`*`)
  - Superintendente Regional (`+`)
  - Inspetor PRF
  - Policial Rodoviário Federal

- **DEPEN** (Departamento Penitenciário Nacional)
  - Diretor-Geral do DEPEN (`+`)
  - Coordenador Regional
  - Agente Penitenciário Federal

**Cargos Principais:**
- Ministro da Justiça e Segurança Pública (`**`)
- Secretário-Executivo (`+`)

#### **Ministério da Defesa**
**Entidades:**
- **Exército Brasileiro**
  - Comandante do Exército (`*`)
  - General de Divisão (`+`)
  - General de Brigada
  - Coronel
  - Tenente-Coronel
  - Major
  - Capitão
  - Tenente
  - Soldado

- **Marinha do Brasil**
  - Comandante da Marinha (`*`)
  - Almirante de Esquadra (`+`)
  - Vice-Almirante
  - Contra-Almirante
  - Capitão de Mar e Guerra
  - Capitão de Fragata
  - Capitão de Corveta
  - Marinheiro

- **Força Aérea Brasileira**
  - Comandante da Aeronáutica (`*`)
  - Tenente-Brigadeiro (`+`)
  - Major-Brigadeiro
  - Brigadeiro
  - Coronel Aviador
  - Tenente-Coronel Aviador
  - Major Aviador
  - Sargento

**Cargos Principais:**
- Ministro da Defesa (`**`)

#### **Ministério da Economia**
**Entidades:**
- **Secretaria do Tesouro Nacional**
  - Secretário do Tesouro (`+`)
  - Coordenador-Geral
  - Analista de Finanças

- **Receita Federal do Brasil**
  - Secretário da Receita Federal (`*`)
  - Delegado da Receita Federal (`+`)
  - Auditor-Fiscal da Receita Federal
  - Analista-Tributário da Receita Federal

- **Banco Central do Brasil**
  - Presidente do Banco Central (`*`)
  - Diretor (`+`)
  - Analista do Banco Central

**Cargos Principais:**
- Ministro da Economia (`**`)

#### **Ministério da Saúde**
**Entidades:**
- **ANVISA** (Agência Nacional de Vigilância Sanitária)
  - Diretor-Presidente da ANVISA (`*`)
  - Diretor (`+`)
  - Especialista em Regulação

- **FIOCRUZ**
  - Presidente da FIOCRUZ (`+`)
  - Pesquisador Senior
  - Tecnologista

**Cargos Principais:**
- Ministro da Saúde (`**`)

#### **Ministério da Educação**
**Entidades:**
- **INEP** (Instituto Nacional de Estudos e Pesquisas Educacionais)
  - Presidente do INEP (`+`)
  - Coordenador de Avaliação
  - Analista de Educação

**Cargos Principais:**
- Ministro da Educação (`**`)

### 5.2 ⚖️ PODER JUDICIÁRIO

#### **Supremo Tribunal Federal (STF)**
**Entidades:**
- **Plenário do STF**
  - Presidente do STF (`**`)
  - Vice-Presidente do STF
  - Ministro do STF
  - Secretário-Geral (`+`)
  - Assessor de Ministro

#### **Superior Tribunal de Justiça (STJ)**
**Entidades:**
- **Plenário do STJ**
  - Presidente do STJ (`*`)
  - Ministro do STJ
  - Secretário-Geral (`+`)

#### **Tribunal Superior Eleitoral (TSE)**
**Entidades:**
- **Plenário do TSE**
  - Presidente do TSE (`*`)
  - Ministro do TSE
  - Secretário-Geral (`+`)

#### **Tribunal de Justiça**
**Entidades:**
- **Primeira Instância**
  - Desembargador (`*`)
  - Juiz de Direito (`+`)
  - Promotor de Justiça
  - Defensor Público
  - Escrivão Judicial
  - Oficial de Justiça

#### **Ministério Público**
**Entidades:**
- **Ministério Público Federal**
  - Procurador-Geral da República (`*`)
  - Procurador Regional da República (`+`)
  - Procurador da República
  - Promotor de Justiça

### 5.3 📜 PODER LEGISLATIVO

#### **Senado Federal**
**Entidades:**
- **Mesa Diretora**
  - Presidente do Senado (`*`)
  - Vice-Presidente do Senado (`+`)
  - Senador da República
  - Secretário-Geral (`+`)

- **Comissões Permanentes**
  - Presidente de Comissão (`+`)
  - Relator
  - Consultor Legislativo

#### **Câmara dos Deputados**
**Entidades:**
- **Mesa Diretora**
  - Presidente da Câmara (`*`)
  - Vice-Presidente da Câmara (`+`)
  - Deputado Federal
  - Secretário-Geral (`+`)

- **Comissões Permanentes**
  - Presidente de Comissão (`+`)
  - Relator
  - Consultor Legislativo

#### **Tribunal de Contas da União (TCU)**
**Entidades:**
- **Plenário do TCU**
  - Presidente do TCU (`*`)
  - Ministro do TCU
  - Auditor Federal de Controle Externo (`+`)
  - Analista de Controle Externo



### 5.4 👤 PODER CIDADÃO (Especial)
**Entidades:**
- **Cidadão**
  - Cidadão (sem cargo específico)

*Obs: Este poder é criado automaticamente para usuários sem cargo no sistema de protocolos.*

## 6. SISTEMA DE NOTÍCIAS

### 6.1 Tipos de Notícia
- **Governo**: Notícias oficiais dos órgãos (único tipo mantido)
- Categorias: Política, Economia, Segurança, Educação, Saúde, Tecnologia, Esportes, Cultura

### 6.2 Permissões para Criação
- **Cargos de Gestão**: `**` (Chefe de Poder) e `*` (Líder de Órgão)
- **Status**: Rascunho → Em Análise → Publicado → Arquivado
- **Funcionalidades**: Upload de imagens, galeria, tags, categorias, comentários, likes

### 6.3 Sistema de Moderação
- Aprovação automática para cargos `**` e `*`
- Editor rico TinyMCE com upload de imagens
- SEO otimizado (meta tags, structured data)

## 7. SISTEMA ADMINISTRATIVO

### 7.1 Django Admin Personalizado
- Interface em português brasileiro
- Hierarquia de cargos visual
- Filtros avançados por poder/órgão/entidade
- Seleção hierárquica (Poder → Órgão → Entidade → Cargo)

### 7.2 Gestão de Cargos
- **Nomeação**: Atribuir cargo a usuário
- **Promoção**: Mudar cargo dentro da mesma entidade
- **Transferência**: Mudar entre entidades
- **Exoneração**: Remover cargo
- **Histórico**: Rastreamento completo de movimentações

### 7.3 Publicação Automática no Diário Oficial
- Nomeações, promoções e exonerações
- Formatação oficial brasileira
- PDF com marca d'água e assinatura digital
- Numeração sequencial automática

## 8. SISTEMA DE CIDADANIA

### 8.1 Processo de Solicitação
- Formulário web com dados pessoais
- Upload de documentos (RG, CPF, comprovante residência)
- Sistema de protocolo interno
- Prazo configurável para análise (padrão: 7 dias)

### 8.2 Análise e Aprovação
- **Órgão Responsável**: Configurável (padrão: Polícia Federal)
- **Cargos Autorizados**: Lista configurável de quem pode aprovar
- **Status**: Pendente → Aprovada/Rejeitada
- **Observações**: Campo para feedback

### 8.3 Configurações Administrativas
- Órgão responsável pelo processamento
- Lista de cargos autorizados a aprovar
- Documentos obrigatórios (editável)
- Instruções para o cidadão
- Ativar/desativar sistema

## 9. SISTEMA DE PROTOCOLOS

### 9.1 Criação de Protocolos
- **Numeração**: Formato XX.XXX.XXX-X (automático)
- **Campos**: Assunto, detalhamento (máx 2400 chars), espécie documento
- **Origem/Destino**: Órgão, entidade, usuário específico
- **Configurações**: Urgência (sim/não), restrição acesso, monitoramento

### 9.2 Gestão de Documentos
- Upload múltiplo (PDF, DOC, DOCX, imagens)
- Controle de versão
- Sistema de assinaturas digitais
- Solicitação de assinatura para usuários específicos

### 9.3 Tramitação
- **Encaminhamentos**: Com parecer obrigatório
- **Interessados**: Adicionar usuários para acompanhar
- **Histórico**: Rastreamento completo de movimentações
- **Status**: Aberto → Em Andamento → Finalizado → Arquivado

### 9.4 Documento Consolidado
- PDF profissional com todas as informações do protocolo
- Anexação integral de PDFs incluídos na ordem cronológica
- Histórico completo de tramitação com pareceres
- Metadados de assinaturas e timestamps precisos
- Marca d'água "GOVERNO BRASILEIRO" em 45°
- Moldura oficial em cada página
- Separadores entre documentos com informações detalhadas
- Imagens incorporadas com qualidade preservada
- Numeração automática de anexos (ANEXO 01/XX)
- Rodapé com data/hora de geração

### 9.5 Validações e Regras de Negócio
- **Assunto**: Máximo 200 caracteres, obrigatório
- **Detalhamento**: Máximo 2.400 caracteres, obrigatório
- **Arquivos**: Máximo 10MB por arquivo
- **Tipos permitidos**: PDF, DOC, DOCX, JPG, PNG, TXT, XLS, XLSX
- **Numeração**: Formato XX.XXX.XXX-X (automático, sequencial)
- **Acesso**: Configurável (público, restrito, confidencial)
- **Urgência**: Binário (sim/não) com notificações automáticas
- **Status**: Aberto → Em Andamento → Finalizado → Arquivado
- **Permissões**: Baseadas em cargo e hierarquia organizacional

### 9.6 APIs do Sistema de Protocolos
- **`/protocolos/api/entidades/{orgao_id}/`** - Entidades por órgão
- **`/protocolos/api/usuarios/{entidade_id}/`** - Usuários por entidade
- **`/protocolos/api/buscar-usuarios/`** - Busca de usuários para interessados
- **`/protocolos/{numero}/upload-documento/`** - Upload de documentos
- **`/protocolos/{numero}/adicionar-interessado/`** - Adicionar interessado
- **`/protocolos/{numero}/encaminhar/`** - Encaminhar protocolo
- **`/protocolos/{numero}/solicitar-assinatura/`** - Solicitar assinatura
- **`/protocolos/{numero}/assinar/{doc_id}/`** - Assinar documento
- **`/protocolos/{numero}/rejeitar-assinatura/{doc_id}/`** - Rejeitar assinatura
- **`/protocolos/{numero}/consolidado/`** - Documento consolidado
- **`/protocolos/{numero}/consolidado-pdf/`** - PDF consolidado

## 10. DIÁRIO OFICIAL

### 10.1 Estrutura
- **Seções por Poder**: Executivo, Judiciário, Legislativo
- **Tipos**: Decreto, Portaria, Resolução, Comunicado, Edital
- **Numeração**: Sequencial por ano
- **Publicação**: Diária (quando há conteúdo)

### 10.2 Geração de PDF
- Layout oficial brasileiro
- Cabeçalho com brasão e logos
- Marca d'água sutil
- Rodapé com data/hora de geração
- Numeração de páginas

### 10.3 Funcionalidades
- Busca avançada (data, tipo, seção, palavra-chave)
- Criação manual de publicações por staff autorizado
- Publicação automática de nomeações/exonerações/promoções
- Histórico completo de edições com auditoria
- URLs amigáveis: `/diario-oficial/{numero}/`
- RSS feed para assinantes
- Notificações por email para publicações importantes

### 10.4 Configurações Administrativas
- **Logo Esquerda**: Upload configurável (brasão oficial)
- **Logo Direita**: Upload configurável (logo do governo)
- **Cabeçalho**: Texto editável com formatação
- **Rodapé**: Informações de contato e data
- **Marca d'água**: Configurável, padrão "OFICIAL"
- **Numeração**: Sequencial automática por ano
- **Horário Publicação**: Configurável (padrão: 00:00)
- **Timezone**: America/Sao_Paulo (Brasília)

### 10.5 Tipos de Publicação Específicos
- **DECRETO**: Atos do Chefe do Executivo
- **PORTARIA**: Atos administrativos internos
- **RESOLUÇÃO**: Atos normativos dos tribunais
- **COMUNICADO**: Informações gerais
- **EDITAL**: Convocações e avisos públicos
- **NOMEAÇÃO**: Automática via sistema de cargos
- **EXONERAÇÃO**: Automática via sistema de cargos
- **PROMOÇÃO**: Automática via sistema de cargos

### 10.6 Formato PDF Oficial
- **Tamanho**: A4 (210x297mm)
- **Margens**: 25mm superior/inferior, 25mm laterais
- **Fonte**: Times New Roman 12pt para texto, Helvetica Bold para títulos
- **Espaçamento**: 1.15 entre linhas
- **Numeração**: Rodapé direito
- **Cabeçalho**: Logo + "REPÚBLICA FEDERATIVA DO BRASIL"
- **Cores**: Escala de cinza para impressão econômica
- **Assinatura Digital**: Timestamp com certificado interno

## 11. PORTAL DA TRANSPARÊNCIA

### 11.1 Estatísticas Públicas
- Total de usuários, servidores, imigrantes, cidadãos
- Distribuição por poderes e órgãos
- Movimentações recentes (nomeações/exonerações)
- Servidores mais antigos

### 11.2 Busca de Servidores
- **Filtros**: Status (ativo/inativo), nível acesso, poder, órgão, entidade, cargo
- **Busca**: Nome, username, Discord, Roblox
- **Ordenação**: Nome, data cadastro, cargo
- **Exportação**: CSV com todos os dados

### 11.3 Dados Exibidos
- Informações pessoais (respeitando LGPD)
- Cargo atual e histórico
- Tempo no cargo atual
- Total de cargos ocupados
- Órgãos onde já atuou

## 12. SEGURANÇA E PERFORMANCE

### 12.1 Segurança
- **Autenticação**: Django session + 2FA opcional
- **Autorização**: Sistema de permissões por cargo
- **LGPD**: Controle de dados pessoais
- **Logs**: Auditoria completa de ações

### 12.2 Performance
- **Cache Redis**: Views, queries e sessões
- **Otimização**: select_related, prefetch_related
- **CDN**: Arquivos estáticos
- **Compressão**: Gzip/Brotli

### 12.3 Backup e Monitoramento
- Backup automático PostgreSQL
- Logs estruturados (JSON)
- Monitoramento de performance
- Alertas de erro

## 13. FUNCIONALIDADES ESPECIAIS

### 13.1 Integração Roblox - SISTEMA DE CADASTRO DETALHADO

#### 📋 **FLUXO COMPLETO DE VERIFICAÇÃO**

**PASSO 1: Coleta de Dados Básicos**
- Campo: Nome Completo RP (mínimo 3 caracteres)
- Campo: ID do Roblox (apenas números)
- Validação: ID não pode estar em uso por outro usuário

**PASSO 2: Verificação da Conta Roblox**
```javascript
// API 1: Verificar existência e dados do usuário
URL: https://users.roblox.com/v1/users/{roblox_id}
Método: GET
Headers: User-Agent padrão

Resposta esperada:
{
  "id": 123456789,
  "name": "NomeUsuario",
  "displayName": "Nome de Exibição", 
  "description": "Descrição do perfil (aqui será colocado código)",
  "created": "2019-01-01T00:00:00.000Z",
  "isBanned": false
}

// API 2: Buscar avatar do usuário
URL: https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size=420x420&format=Png&isCircular=false
Método: GET

Resposta esperada:
{
  "data": [
    {
      "targetId": 123456789,
      "state": "Completed",
      "imageUrl": "https://tr.rbxcdn.com/avatar.png"
    }
  ]
}
```

**PASSO 3: Geração e Verificação de Código**
```python
# Gerar código aleatório de 4 caracteres (evita filtros de tags do Roblox)
import secrets
import string
codigo = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))

# Exemplo: "A7B9"
```

**PASSO 4: Verificação do Código no Perfil**
- Usuário adiciona o código na descrição do perfil do Roblox
- Sistema faz nova chamada para `https://users.roblox.com/v1/users/{roblox_id}`
- Verifica se o código existe no campo `description`
- **IMPORTANTE**: Verificação é case-sensitive

**PASSO 5: Criação da Conta**
- Username automático: `user_{roblox_id}`
- Senha definida pelo usuário (mínimo 8 caracteres)
- Nível inicial: 'imigrante'
- Avatar automaticamente sincronizado

#### 🔧 **CONFIGURAÇÕES TÉCNICAS**

**Rate Limiting:**
- Máximo 100 requisições por minuto por IP
- Timeout de 10 segundos por requisição
- Retry automático em caso de falha (máx 3 tentativas)

**Cache de Dados:**
- Avatar: Cache por 24 horas
- Dados do usuário: Cache por 1 hora
- Verificação de código: Sem cache (sempre consulta)

**Tratamento de Erros:**
- Conta banida: Bloquear registro
- ID não existe: Mostrar erro específico
- API fora do ar: Fallback para dados em cache
- Avatar indisponível: Usar imagem padrão

**Validações de Segurança:**
- ID do Roblox: Apenas números, entre 1 e 999999999999
- Código: Deve estar exatamente na descrição (não em comentários)
- Timeout de sessão: 30 minutos para completar verificação
- Limpeza automática de códigos expirados

#### 🔄 **SINCRONIZAÇÃO CONTÍNUA**

**Atualização Automática de Avatares:**
```python
# Task diária para atualizar avatares
def atualizar_avatars_usuarios():
    usuarios = User.objects.filter(roblox_id__isnull=False)
    for usuario in usuarios:
        roblox_data = get_roblox_user_info(usuario.roblox_id)
        if roblox_data and roblox_data['avatar_url']:
            usuario.avatar_url = roblox_data['avatar_url']
            usuario.save()
```

**Verificação de Conta Banida:**
- Verificação semanal automática
- Suspender conta automaticamente se Roblox account estiver banida
- Notificar administradores

**Função Auxiliar Principal:**
```python
def get_roblox_user_info(roblox_id, size="420x420"):
    """
    Função principal para obter dados do Roblox
    Retorna: dict com id, username, display_name, description, 
             avatar_url, created, is_banned
    """
    # Implementação com cache e tratamento de erros
```

#### 📊 **DADOS ARMAZENADOS DO ROBLOX**

**Campos na Tabela User:**
```sql
roblox_id: BIGINT (PRIMARY KEY alternativa)
roblox_username: VARCHAR(100) 
avatar_url: URL
verificado: BOOLEAN (se passou pela verificação)
data_verificacao: DATETIME
ultimo_sync_roblox: DATETIME
```

**Logs de Verificação:**
- Histórico de códigos gerados
- IPs de tentativas de verificação
- Tentativas de reutilização de IDs

#### ⚠️ **MENSAGENS DE ERRO ESPECÍFICAS**

**Validação do ID Roblox:**
- "ID do Roblox deve ser um número válido"
- "Este ID do Roblox já está cadastrado" 
- "ID do Roblox não encontrado ou inválido"
- "Esta conta do Roblox está banida"

**Verificação de Código:**
- "Código não encontrado na descrição do seu perfil. Certifique-se de que adicionou o código corretamente."
- "Sessão expirada - Por favor, inicie o processo novamente"
- "Código de verificação não encontrado"

**Validação de Dados:**
- "Nome completo deve ter pelo menos 3 caracteres"
- "A senha deve ter pelo menos 8 caracteres"
- "As senhas não coincidem"

#### 🎯 **CASOS DE USO ESPECÍFICOS**

**Usuário Mudou Username no Roblox:**
- Sistema deve atualizar automaticamente o username
- Manter histórico de usernames anteriores
- Notificar sobre mudanças

**Avatar Não Carrega:**
- Usar imagem padrão: "/static/images/default-avatar.svg"
- Tentar recarregar automaticamente após 24h
- Log de falhas para debug

**Roblox API Offline:**
- Mensagem: "Serviços do Roblox temporariamente indisponíveis"
- Permitir login para usuários já verificados
- Queue de verificações para processar quando API voltar

### 13.2 Discord Integration (Opcional)
- OAuth2 login via Discord API
- Sync automático de avatar Discord
- Webhook notifications para nomeações importantes
- Rate limiting Discord (5 req/sec)
- Campos opcionais: discord_id, discord_username
- Integração com servidores Discord específicos

### 13.3 Responsividade e PWA
- Mobile-first design (breakpoints: 576px, 768px, 992px, 1200px)
- Service Worker para cache offline de páginas estáticas
- Manifesto PWA com ícones oficiais
- Offline functionality para consulta básica de protocolos
- Push notifications para solicitações urgentes

### 13.4 APIs Específicas Implementadas
- **`/api/portal-transparencia/estatisticas/`** - Estatísticas gerais
- **`/api/portal-transparencia/orgaos/{poder_id}/`** - Órgãos por poder
- **`/api/portal-transparencia/entidades/{orgao_id}/`** - Entidades por órgão
- **`/api/portal-transparencia/buscar/`** - Busca avançada de servidores
- **`/api/portal-transparencia/exportar/`** - Exportação CSV
- **`/api/cargos-por-entidade/{entidade_id}/`** - Cargos de uma entidade
- **`/api/upload-imagem/`** - Upload de imagens para notícias
- **`/api/noticia/{id}/like/`** - Sistema de likes
- **`/api/noticia/{id}/view/`** - Incrementar visualizações
- **`/usuarios/admin/ajax/orgaos/`** - Órgãos (admin)
- **`/usuarios/admin/ajax/entidades/`** - Entidades (admin)
- **`/usuarios/admin/ajax/cargos/`** - Cargos (admin)

### 13.5 Sistema de Cache Detalhado
- **Redis Configuração**:
  - `CACHE_TTL_DEFAULT = 900` (15 minutos)
  - `CACHE_TTL_NOTICIAS = 1800` (30 minutos)
  - `CACHE_TTL_ESTATISTICAS = 3600` (1 hora)
- **Cache Keys**:
  - `noticias_governo_destaque` - Notícias em destaque
  - `noticias_recentes` - Notícias recentes
  - `noticia_detalhe_{slug}` - Detalhes de notícia específica
  - `noticias_relacionadas_{id}` - Notícias relacionadas
  - `estatisticas_sistema` - Estatísticas globais
- **Cache Invalidation**:
  - Automática após criação/edição de notícias
  - Manual via admin para estatísticas
  - Por TTL para dados menos voláteis

### 13.6 Sistema de Logs e Auditoria
- **Logs Estruturados** (JSON format):
  - `user_action` - Ações de usuários
  - `cargo_changes` - Mudanças de cargo
  - `protocolo_operations` - Operações de protocolo
  - `sistema_access` - Acessos ao sistema
- **Campos Obrigatórios**:
  - `timestamp`, `user_id`, `action`, `resource_type`, `resource_id`, `ip_address`
- **Retenção**: 2 anos para logs de auditoria, 6 meses para logs de acesso
- **Alertas Automáticos**:
  - Múltiplas tentativas de login falhadas
  - Acesso negado a recursos sensíveis
  - Operações administrativas críticas

## 14. ESTRUTURA DE URLs E NAVEGAÇÃO

### 14.1 URLs Principais
```
/ - Página inicial
/estrutura-governo/ - Hierarquia completa
/noticias/ - Lista de notícias
/noticias/{slug}/ - Detalhe da notícia
/perfil/{username}/ - Perfil público
/protocolos/ - Sistema de protocolos
/protocolos/criar/ - Criar protocolo
/protocolos/consultar/ - Consultar por número
/protocolos/{numero}/ - Detalhe do protocolo
/diario-oficial/ - Lista de edições
/diario-oficial/{numero}/ - Edição específica
/diario-oficial/buscar/ - Busca no diário
/portal-transparencia/ - Portal público
/cidadania/solicitar/ - Solicitação de cidadania
/gestao/cargos/ - Painel de gestão
/gestao/cidadania/ - Gestão de cidadania
/admin/ - Django Admin customizado
```

### 14.2 Estrutura de Navegação
```
Header:
├── Logo GovBR
├── Menu Principal
│   ├── Início
│   ├── Estrutura do Governo
│   ├── Notícias
│   ├── Portal da Transparência
│   ├── Diário Oficial
│   └── Protocolos (se logado)
├── Busca Global
└── User Menu
    ├── Meu Perfil
    ├── Meus Protocolos
    ├── Painel Gestão (se gestor)
    └── Logout

Footer:
├── Links Institucionais
├── Contato
├── Termos de Uso
├── Política de Privacidade
└── © GovBR Roleplay 2024
```

### 14.3 Breadcrumbs Dinâmicos
- Implementação automática baseada na URL
- Contexto específico para cada seção
- Links funcionais para navegação rápida
- Título da página dinâmico baseado no conteúdo

## 15. DEPLOY E INFRAESTRUTURA

### 15.1 Ambiente de Produção
- **Servidor**: Ubuntu 22.04 LTS
- **Proxy**: Nginx 1.20+
- **WSGI**: Gunicorn
- **Processo**: Systemd services
- **SSL**: Let's Encrypt (Certbot)

### 15.2 Banco de Dados
- **PostgreSQL 15+**: Dados principais
- **Redis 7+**: Cache e sessões
- **Backup**: Automático diário

### 15.3 Variáveis de Ambiente
```
SECRET_KEY=...
DEBUG=False
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ROBLOX_API_KEY=...
DISCORD_CLIENT_ID=...
DISCORD_CLIENT_SECRET=...
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
TIMEZONE=America/Sao_Paulo
```

## 16. ASPECTOS TÉCNICOS ESPECÍFICOS

### 16.1 Modelos de Dados Críticos
```python
# Estrutura hierárquica
Poder → Orgao → Entidade → Cargo
User → Profile → HistoricoCargo

# Sistema de protocolos
Protocolo → ProtocoloDocumento
Protocolo → ProtocoloEncaminhamento
Protocolo → ProtocoloInteressado
Protocolo → SolicitacaoAssinatura

# Sistema de notícias
Noticia → NoticiaImagem
Noticia → NoticiaCategoria (M2M)
Noticia → NoticiaTag (M2M)
Noticia → NoticiaComentario
Noticia → NoticiaLike

# Sistema de cidadania
SolicitacaoCidadania → User
ConfiguracaoCidadania → Cargo (M2M)
```

### 16.2 Signals e Automações
- **post_save User**: Criar perfil automaticamente
- **post_save/post_delete HistoricoCargo**: Atualizar cargo atual no perfil
- **post_save HistoricoCargo**: Criar publicação no Diário Oficial
- **post_save Noticia**: Invalidar cache relacionado
- **pre_delete ProtocoloDocumento**: Limpeza de arquivos

### 16.3 Middlewares Customizados
- **TimezoneMiddleware**: Configurar timezone brasileiro
- **AuditMiddleware**: Log de ações de usuários
- **SecurityMiddleware**: Headers de segurança
- **CacheControlMiddleware**: Controle de cache HTTP

### 16.4 Validações Customizadas
- **RobloxUsernameValidator**: Verificar existência no Roblox
- **CPFValidator**: Validar CPF brasileiro
- **CargoHierarchyValidator**: Validar hierarquia de cargos
- **ProtocoloNumberValidator**: Formato XX.XXX.XXX-X
- **FileUploadValidator**: Tipos e tamanhos de arquivo

## 17. REQUISITOS FUNCIONAIS FINAIS

### 17.1 Interface do Usuário
- ✅ Design moderno com cores da bandeira brasileira
- ✅ Totalmente responsivo (mobile-first)
- ✅ Navegação intuitiva e acessível
- ✅ Loading states e feedback visual
- ✅ Tema escuro/claro (opcional)
- ✅ Breadcrumbs dinâmicos
- ✅ Busca global integrada
- ✅ Notificações em tempo real

### 17.2 Gestão de Usuários
- ✅ 6 níveis de acesso bem definidos
- ✅ Verificação obrigatória via Roblox
- ✅ Sistema de cidadania automatizado
- ✅ Perfis públicos com histórico detalhado
- ✅ Avatares automáticos do Roblox
- ✅ Integração Discord opcional
- ✅ Auditoria completa de ações

### 17.3 Hierarquia Governamental
- ✅ 3 poderes com estrutura completa
- ✅ Órgãos, entidades e cargos específicos
- ✅ Sistema de gestão hierárquica inteligente
- ✅ Histórico completo de movimentações
- ✅ Símbolos de gestão visuais
- ✅ Permissões baseadas em hierarquia
- ✅ Publicação automática no Diário Oficial

### 17.4 Sistemas Integrados
- ✅ Notícias oficiais do governo com moderação
- ✅ Protocolos com tramitação completa
- ✅ Diário Oficial automatizado
- ✅ Portal da Transparência público
- ✅ Sistema de assinaturas digitais
- ✅ APIs REST completas
- ✅ Cache inteligente Redis

### 17.5 Qualidade e Performance
- ✅ Código limpo e documentado
- ✅ Testes automatizados (unitários)
- ✅ Cache inteligente (Redis)
- ✅ Logs estruturados para auditoria
- ✅ Backup automático e monitoramento
- ✅ Segurança LGPD compliance
- ✅ Validações específicas brasileiras
- ✅ Timezone Brasil (UTC-3)

### 17.6 Funcionalidades Avançadas
- ✅ PDFs consolidados profissionais
- ✅ Merge de documentos automático
- ✅ Sistema de comentários e likes
- ✅ Upload de múltiplos arquivos
- ✅ Busca avançada com filtros
- ✅ Exportação CSV completa
- ✅ Notificações por email
- ✅ PWA com cache offline

## 18. TESTES E QUALIDADE DE CÓDIGO

### 18.1 Cobertura de Testes Obrigatória
- **Models**: 100% cobertura para models críticos
- **Views**: 90% cobertura para views principais
- **APIs**: 100% cobertura para todas as APIs
- **Utils/Helpers**: 95% cobertura para funções auxiliares
- **Templates**: Testes de renderização básica

### 18.2 Tipos de Testes
```python
# Testes unitários
class TestCargoModel(TestCase):
    def test_pode_gerenciar_cargo_hierarchy()
    def test_simbolo_gestao_display()
    def test_get_cargos_gerenciaveis()

# Testes de integração
class TestProtocoloAPI(APITestCase):
    def test_criar_protocolo_completo()
    def test_encaminhar_protocolo()
    def test_gerar_pdf_consolidado()

# Testes de performance
class TestCachePerformance(TestCase):
    def test_cache_hit_rate()
    def test_query_optimization()
```

### 18.3 Ferramentas de Qualidade
- **Coverage.py**: Cobertura de testes
- **PyLint**: Análise estática de código
- **Black**: Formatação automática
- **Pre-commit hooks**: Validação antes do commit
- **Django Debug Toolbar**: Análise de performance

### 18.4 CI/CD Pipeline
```yaml
stages:
  - test
  - security-scan
  - build
  - deploy

test:
  script:
    - python manage.py test
    - coverage report --fail-under=85
    - pylint main/ users/

security:
  script:
    - bandit -r .
    - safety check
```

---

## 📋 RESUMO EXECUTIVO

Este prompt define completamente o sistema **GovBR Roleplay** - uma plataforma web profissional que simula o Governo Brasileiro no ambiente Roblox com **580+ linhas de especificações técnicas detalhadas**.

### 🎯 **Características Principais**:
- **3 Poderes** governamentais completos (Executivo, Judiciário, Legislativo)
- **50+ Órgãos específicos** (Presidência, Ministérios, STF, PF, etc.)
- **200+ Cargos hierárquicos** com símbolos de gestão (👑**, ⭐*, 🔹+)
- **6 Níveis de acesso** (Imigrante → Fundador)
- **Sistema de protocolos** completo com assinaturas digitais
- **Diário Oficial** automatizado com PDFs profissionais
- **Portal da Transparência** público
- **Sistema de cidadania** com análise de documentos

### 🛠️ **Stack Tecnológica**:
- Django 4.2+ | PostgreSQL 15+ | Redis 7+ | Bootstrap 5.3
- APIs REST completas | Cache inteligente | PWA
- Integração Roblox + Discord | PDFs oficiais

### 🏛️ **Compliance Governamental**:
- Estrutura fiel ao governo brasileiro real
- Cores oficiais da bandeira nacional
- Documentos com formatação oficial
- Timezone Brasil (UTC-3) | LGPD compliance

---

**IMPORTANTE**: Este sistema deve ser uma representação fiel e respeitosa do Governo Brasileiro, mantendo a seriedade institucional mesmo em ambiente de roleplay. Todos os cargos, órgãos e procedimentos devem seguir a estrutura real do governo brasileiro, adaptada para o contexto do Roblox.

O foco deve estar na experiência do usuário, facilidade de uso, performance e segurança dos dados. O sistema deve ser escalável para suportar centenas de usuários simultâneos e milhares de protocolos/documentos.

**Total de linhas do prompt**: 750+ | **Última atualização**: 2024 