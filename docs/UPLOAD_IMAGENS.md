# Sistema de Upload de Imagens

Este documento detalha o sistema de upload e gerenciamento de imagens do GovBR Roleplay.

## Funcionalidades

### Upload de Imagens
- Upload único ou múltiplo
- Suporte a drag & drop
- Preview em tempo real
- Validação de tipo e tamanho
- Geração de thumbnails
- Otimização automática

### Tipos de Upload

#### 1. Imagem Principal
- Uma imagem por notícia
- Exibida no topo da notícia
- Usada em cards e previews
- Dimensões recomendadas: 1200x630px

#### 2. Galeria de Imagens
- Múltiplas imagens por notícia
- Ordenação personalizada
- Legendas individuais
- Layout em grid responsivo

#### 3. Editor de Texto
- Upload direto no TinyMCE
- Inserção no conteúdo
- Redimensionamento inline
- Alinhamento flexível

## Configurações

### Limites e Restrições
```python
# settings.py

# Tipos de arquivo permitidos
ALLOWED_UPLOAD_IMAGES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
]

# Tamanhos máximos
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_DIMENSIONS = (2000, 2000)

# Qualidade de compressão
JPEG_QUALITY = 85
PNG_COMPRESSION = 9

# Thumbnails
THUMBNAIL_SIZES = {
    'small': (300, 300),
    'medium': (800, 800),
    'large': (1200, 1200)
}
```

### Estrutura de Diretórios
```
media/
  ├── noticias/
  │   ├── principais/     # Imagens principais
  │   ├── galeria/       # Galerias de imagens
  │   └── editor/        # Imagens do editor
  └── cache/
      └── thumbnails/    # Cache de thumbnails
```

## Implementação

### Models
```python
class ImagemNoticia(models.Model):
    noticia = models.ForeignKey('Noticia', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='noticias/galeria/')
    legenda = models.CharField(max_length=200, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordem', 'data_upload']
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Novo upload
            self.otimizar_imagem()
        super().save(*args, **kwargs)
    
    def otimizar_imagem(self):
        from PIL import Image
        import os
        
        # Abrir imagem
        img = Image.open(self.imagem)
        
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar se muito grande
        if img.size[0] > MAX_IMAGE_DIMENSIONS[0] or img.size[1] > MAX_IMAGE_DIMENSIONS[1]:
            img.thumbnail(MAX_IMAGE_DIMENSIONS)
        
        # Salvar com compressão
        img.save(self.imagem.path, 'JPEG', quality=JPEG_QUALITY)
```

### Views
```python
@login_required
def upload_imagem(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            imagem = request.FILES['file']
            
            # Validar tipo
            if imagem.content_type not in ALLOWED_UPLOAD_IMAGES:
                raise ValidationError('Tipo de arquivo não permitido')
            
            # Validar tamanho
            if imagem.size > MAX_UPLOAD_SIZE:
                raise ValidationError('Arquivo muito grande')
            
            # Gerar nome único
            nome_arquivo = f"{uuid.uuid4().hex}_{imagem.name}"
            
            # Salvar imagem
            caminho = os.path.join('noticias', 'editor', nome_arquivo)
            default_storage.save(caminho, imagem)
            
            # Retornar URL
            url = default_storage.url(caminho)
            
            return JsonResponse({
                'location': url
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'error': 'Método não permitido'
    }, status=400)
```

### Forms
```python
class ImagemForm(forms.ModelForm):
    class Meta:
        model = ImagemNoticia
        fields = ['imagem', 'legenda']
        widgets = {
            'legenda': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da imagem'
            })
        }
    
    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if imagem:
            # Validar tipo
            if imagem.content_type not in ALLOWED_UPLOAD_IMAGES:
                raise ValidationError('Tipo de arquivo não permitido')
            
            # Validar tamanho
            if imagem.size > MAX_UPLOAD_SIZE:
                raise ValidationError('Arquivo muito grande')
        
        return imagem
```

## JavaScript

### Upload com Dropzone
```javascript
Dropzone.options.galeriaDropzone = {
    url: uploadUrl,
    paramName: "file",
    maxFilesize: 5, // MB
    acceptedFiles: "image/*",
    addRemoveLinks: true,
    dictDefaultMessage: "Arraste imagens ou clique aqui",
    dictRemoveFile: "Remover",
    
    init: function() {
        this.on("success", function(file, response) {
            // Adicionar input para legenda
            const wrapper = document.createElement('div');
            wrapper.className = 'mt-2';
            
            const input = document.createElement('input');
            input.type = 'text';
            input.name = `legenda_${file.name}`;
            input.className = 'form-control form-control-sm';
            input.placeholder = 'Legenda da imagem';
            
            wrapper.appendChild(input);
            file.previewElement.appendChild(wrapper);
        });
    }
};
```

### Preview de Imagem
```javascript
function handleImagePreview(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById('imagemPreview');
            preview.style.display = 'block';
            preview.querySelector('img').src = e.target.result;
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}
```

## Templates

### Upload Único
```html
<div class="mb-3">
    <label for="imagem_principal" class="form-label">Imagem Principal</label>
    <input type="file" class="form-control" id="imagem_principal" 
           name="imagem_principal" accept="image/*">
    <div class="form-text">
        Dimensões recomendadas: 1200x630px. Máximo: 5MB.
    </div>
</div>

<div id="imagemPreview" class="mt-3" style="display: none;">
    <img src="" alt="Preview" class="img-fluid rounded">
</div>
```

### Galeria
```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title mb-0">Galeria de Imagens</h5>
    </div>
    <div class="card-body">
        <div id="galeriaDropzone" class="dropzone"></div>
        <div class="form-text mt-2">
            Arraste imagens ou clique para fazer upload. Máximo: 5MB por imagem.
        </div>
    </div>
</div>
```

## Processamento de Imagens

### Otimização
```python
def otimizar_imagem(imagem_path):
    from PIL import Image
    import os
    
    # Abrir imagem
    img = Image.open(imagem_path)
    
    # Converter para RGB se necessário
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Redimensionar se muito grande
    if img.size[0] > MAX_IMAGE_DIMENSIONS[0] or img.size[1] > MAX_IMAGE_DIMENSIONS[1]:
        img.thumbnail(MAX_IMAGE_DIMENSIONS)
    
    # Salvar com compressão
    img.save(imagem_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
```

### Thumbnails
```python
def gerar_thumbnail(imagem_path, size):
    from PIL import Image
    import os
    
    # Abrir imagem
    img = Image.open(imagem_path)
    
    # Criar thumbnail
    img.thumbnail(size)
    
    # Gerar nome do thumbnail
    nome_base = os.path.basename(imagem_path)
    nome_thumb = f"thumb_{size[0]}x{size[1]}_{nome_base}"
    caminho_thumb = os.path.join('cache', 'thumbnails', nome_thumb)
    
    # Salvar thumbnail
    img.save(caminho_thumb, 'JPEG', quality=85)
    
    return caminho_thumb
```

## Segurança

### Validação de Tipo
```python
def validar_tipo_arquivo(arquivo):
    import magic
    
    # Verificar tipo MIME
    mime = magic.from_buffer(arquivo.read(1024), mime=True)
    arquivo.seek(0)
    
    return mime in ALLOWED_UPLOAD_IMAGES
```

### Sanitização de Nome
```python
def sanitizar_nome_arquivo(nome):
    import re
    from unidecode import unidecode
    
    # Remover acentos
    nome = unidecode(nome)
    
    # Substituir espaços por underscores
    nome = re.sub(r'\s+', '_', nome)
    
    # Remover caracteres especiais
    nome = re.sub(r'[^\w\-_.]', '', nome)
    
    return nome.lower()
```

## Próximos Passos

### 1. Melhorias Planejadas
- Crop de imagens
- Filtros e efeitos
- Upload direto da área de transferência
- Suporte a WebP

### 2. Otimizações
- CDN para imagens
- Cache de thumbnails
- Compressão progressiva
- Lazy loading

### 3. Recursos Futuros
- Biblioteca de mídia
- Reconhecimento facial
- Marca d'água automática
- OCR para imagens com texto 