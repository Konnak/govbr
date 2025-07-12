# Sistema de PDF para Protocolos - Documentação Técnica

## 📄 Visão Geral

O sistema de PDF para protocolos foi implementado para gerar documentos consolidados em formato PDF profissional, incluindo previews visuais de todos os arquivos anexados (imagens e PDFs).

## 🚀 Funcionalidades Implementadas

### 1. Geração de PDF Consolidado
- **Documento oficial** em formato PDF com layout profissional
- **Cabeçalho governamental** com identificação oficial
- **Informações completas** do protocolo organizadas em tabelas
- **Histórico cronológico** de todos os encaminhamentos
- **Status de assinaturas** detalhado para cada documento

### 2. Inclusão Completa de Anexos
- **Imagens**: Preview visual direto no PDF (JPG, PNG, GIF, BMP)
- **PDFs**: Anexo completo com todas as páginas extraídas como texto
- **Outros arquivos**: Informações detalhadas com tipo e tamanho
- **Redimensionamento automático** para imagens

### 3. Metadados Completos
- **Identificadores únicos** para cada documento
- **Informações de upload** (usuário, data, tipo)
- **Status de assinatura** com detalhes completos
- **Solicitações de assinatura** com histórico de respostas

## 🛠️ Tecnologias Utilizadas

### Bibliotecas Python
```python
# Geração de PDF
reportlab==4.0.7          # Criação de PDFs profissionais
PyPDF2==3.0.1            # Manipulação de PDFs existentes
pdf2image==1.16.3        # Conversão de PDF para imagem
Pillow==10.0.1           # Processamento de imagens
```

### Componentes ReportLab
- `SimpleDocTemplate`: Estrutura base do documento
- `Paragraph`: Textos formatados com estilos
- `Table`: Tabelas organizadas com dados
- `Image`: Inclusão de imagens com redimensionamento
- `Spacer`: Espaçamento entre elementos

## 📋 Estrutura do PDF Gerado

### 1. Cabeçalho Oficial
```
GOVERNO BRASILEIRO ROLEPLAY
DOCUMENTO CONSOLIDADO DE PROTOCOLO
Protocolo: XX.XXX.XXX-X
```

### 2. Seções Organizadas
1. **📋 Informações do Protocolo**
   - Assunto, espécie, data, status
   - Usuário, órgão, urgência
   - Detalhamento completo

2. **📍 Destinatário**
   - Órgão de destino
   - Setor e usuário específico

3. **📁 Documentos Anexados**
   - Lista numerada com identificadores
   - Metadados completos
   - Status de assinatura
   - **Conteúdo completo** dos arquivos (PDFs integrais, imagens visuais)
   - Histórico de solicitações

4. **👥 Interessados**
   - Lista de todos os interessados
   - Órgão e data de inclusão

5. **🔄 Histórico de Encaminhamentos**
   - Cronologia completa
   - Pareceres detalhados
   - Origem e destino

6. **Rodapé Oficial**
   - Data e hora de geração
   - Usuário responsável

## 🎨 Estilos e Formatação

### Estilos Customizados
```python
# Título principal
title_style = ParagraphStyle(
    fontSize=18,
    alignment=TA_CENTER,
    textColor=blue,
    spaceAfter=20
)

# Subtítulos de seção
subtitle_style = ParagraphStyle(
    fontSize=14,
    borderWidth=1,
    borderColor=grey,
    backColor=colors.lightgrey
)

# Texto normal
normal_style = ParagraphStyle(
    fontSize=10,
    spaceAfter=6
)
```

### Tabelas Formatadas
- **Cabeçalhos**: Fundo cinza claro, texto em negrito
- **Bordas**: Linhas pretas definidas
- **Alinhamento**: Texto à esquerda, dados organizados
- **Cores**: Azul claro para metadados de documentos

## 🖼️ Processamento de Imagens

### Tipos Suportados
- **Imagens diretas**: JPG, JPEG, PNG, GIF, BMP
- **PDFs**: Primeira página convertida para PNG
- **Redimensionamento**: Máximo 4x3 polegadas mantendo proporção

### Algoritmo de Processamento
```python
# Para imagens
if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
    img = Image(arquivo_path, width=4*inch, height=3*inch, kind='proportional')
    
# Para PDFs - anexar completo
elif file_ext == '.pdf':
    pdf_reader = PdfReader(arquivo_path)
    for page_num, page in enumerate(pdf_reader.pages, 1):
        page_text = page.extract_text()
        # Inclui cada página como texto formatado no PDF final
```

## 🔗 URLs e Integração

### Rotas Implementadas
```python
# Documento HTML
path('protocolos/<numero>/documento-consolidado/', 
     views.protocolo_documento_consolidado, 
     name='protocolo_documento_consolidado')

# PDF com anexos
path('protocolos/<numero>/documento-consolidado/pdf/', 
     views.protocolo_documento_consolidado_pdf, 
     name='protocolo_documento_consolidado_pdf')
```

### Botões de Acesso
- **Tela principal**: "PDF com Anexos" (botão primário)
- **Documento HTML**: "Baixar PDF com Anexos" (botão verde)
- **Download automático** do arquivo PDF

## 🔒 Segurança e Permissões

### Controle de Acesso
- **Autenticação obrigatória**: `@login_required`
- **Verificação de permissões**: `protocolo.pode_visualizar(request.user)`
- **Validação de dados**: Verificação de existência de arquivos
- **Tratamento de erros**: Mensagens informativas para falhas

### Tratamento de Arquivos
- **Verificação de existência**: `os.path.exists(arquivo_path)`
- **Arquivos temporários**: Limpeza automática após uso
- **Fallback**: Mensagens informativas para arquivos não encontrados

## 📊 Performance e Otimização

### Otimizações Implementadas
- **Consultas eficientes**: `select_related` e `prefetch_related`
- **Processamento sob demanda**: Imagens carregadas apenas quando necessário
- **Arquivos temporários**: Limpeza automática para evitar acúmulo
- **Redimensionamento inteligente**: Mantém qualidade e reduz tamanho

### Limitações Técnicas
- **DPI das imagens**: 150 DPI para PDFs (equilibrio qualidade/tamanho)
- **Tamanho máximo**: 4x3 polegadas para previews
- **Primeira página apenas**: Para PDFs com múltiplas páginas
- **Tipos suportados**: Limitado aos formatos mais comuns

## 🚨 Tratamento de Erros

### Cenários Cobertos
1. **Arquivo não encontrado**: Mensagem informativa no PDF
2. **Erro de conversão**: Fallback para informação textual
3. **Problemas de permissão**: Retorno HTTP 403
4. **Falhas de processamento**: Logs detalhados e mensagens de erro

### Exemplo de Tratamento
```python
try:
    img = Image(arquivo_path, width=4*inch, height=3*inch, kind='proportional')
    elements.append(img)
except Exception as e:
    elements.append(Paragraph(f"<i>Erro ao carregar imagem: {str(e)}</i>", normal_style))
```

## 📈 Melhorias Futuras Sugeridas

### Funcionalidades Avançadas
1. **Assinatura digital**: Integração com certificados digitais
2. **Marca d'água**: Identificação de autenticidade
3. **Compressão**: Otimização de tamanho para arquivos grandes
4. **OCR**: Reconhecimento de texto em imagens
5. **Múltiplas páginas**: Preview completo de PDFs longos

### Otimizações Técnicas
1. **Cache**: Armazenamento de previews gerados
2. **Processamento assíncrono**: Para documentos grandes
3. **Compressão de imagens**: Redução de tamanho sem perda de qualidade
4. **Formatos adicionais**: Suporte a DOC, XLS, etc.

## 🔧 Configuração e Deploy

### Dependências do Sistema
```bash
# No Windows (pode ser necessário)
pip install poppler-utils  # Para pdf2image

# No Linux
sudo apt-get install poppler-utils

# No macOS
brew install poppler
```

### Configurações Django
```python
# settings.py
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Para arquivos temporários
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
```

## 📝 Exemplo de Uso

### Geração de PDF
```python
# Acesso direto via URL
GET /protocolos/00.000.001-1/documento-consolidado/pdf/

# Resposta
Content-Type: application/pdf
Content-Disposition: attachment; filename="protocolo_00.000.001-1_consolidado.pdf"
```

### Estrutura do Arquivo Gerado
```
protocolo_00.000.001-1_consolidado.pdf
├── Cabeçalho oficial
├── Informações do protocolo (tabela)
├── Destinatário (tabela)
├── Documentos anexados
│   ├── DOC-001 - Documento.pdf
│   │   ├── Metadados (tabela)
│   │   ├── Status de assinatura
│   │   └── 📄 ANEXO PDF COMPLETO
│   │       ├── PÁGINA 1 de 5 - Conteúdo integral
│   │       ├── PÁGINA 2 de 5 - Conteúdo integral
│   │       └── ... (todas as páginas)
│   └── DOC-002 - Imagem.jpg
│       ├── Metadados (tabela)
│       └── 🖼️ Imagem visual completa
├── Interessados (lista)
├── Histórico de encaminhamentos
└── Rodapé com data de geração
```

---

**Data de Implementação**: 19/06/2025
**Versão**: 1.0
**Status**: ✅ Funcional e Testado 