from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
import logging

User = get_user_model()

# Configurar logger específico para o diário oficial
logger = logging.getLogger('diario_oficial')


class Noticia(models.Model):
    TIPO_CHOICES = [
        ('governo', 'Notícia do Governo'),
        ('imprensa', 'Notícia da Imprensa'),
    ]
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('revisao', 'Em Revisão'),
        ('publicado', 'Publicado'),
        ('arquivado', 'Arquivado'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    resumo = models.TextField(max_length=300, blank=True, verbose_name="Resumo")
    conteudo = models.TextField(verbose_name="Conteúdo")
    conteudo_html = models.TextField(verbose_name="Conteúdo HTML", blank=True)
    imagem_principal = models.ImageField(
        upload_to='noticias/principais/', 
        blank=True, 
        null=True, 
        verbose_name="Imagem Principal",
        help_text="Imagem principal da notícia, exibida no topo"
    )
    galeria_imagens = models.ManyToManyField(
        'NoticiaImagem',
        blank=True,
        related_name='noticias',
        verbose_name="Galeria de Imagens"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='governo', verbose_name="Tipo")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    editor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='noticias_editadas',
        verbose_name="Editor"
    )
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    data_publicacao = models.DateTimeField(blank=True, null=True, verbose_name="Data de Publicação")
    publicado = models.BooleanField(default=False, verbose_name="Publicado")
    destaque = models.BooleanField(default=False, verbose_name="Destaque no Slide")
    visualizacoes = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    tags = models.ManyToManyField('NoticiaTag', blank=True, verbose_name="Tags")
    categorias = models.ManyToManyField('NoticiaCategoria', blank=True, verbose_name="Categorias")
    fonte = models.CharField(max_length=200, blank=True, verbose_name="Fonte")
    link_fonte = models.URLField(blank=True, verbose_name="Link da Fonte")
    permitir_comentarios = models.BooleanField(default=True, verbose_name="Permitir Comentários")
    orgao_publicacao = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Órgão na Publicação",
        help_text="Nome do órgão do autor no momento da publicação (campo estático)"
    )
    
    class Meta:
        ordering = ['-data_publicacao', '-data_criacao']
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        permissions = [
            ("pode_publicar_noticias", "Pode publicar notícias"),
            ("pode_editar_noticias_outros", "Pode editar notícias de outros autores"),
            ("pode_moderar_noticias", "Pode moderar notícias"),
        ]
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        # Gerar slug único se não existir
        if not self.slug:
            self.slug = slugify(self.titulo)
            counter = 1
            while Noticia.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.titulo)}-{counter}"
                counter += 1
        
        # Gerar resumo automaticamente se não existir
        if not self.resumo and self.conteudo:
            import re
            # Remover tags HTML
            texto_limpo = re.sub('<[^<]+?>', '', self.conteudo)
            # Pegar as primeiras 200 palavras
            palavras = texto_limpo.split()[:30]
            self.resumo = ' '.join(palavras) + ('...' if len(palavras) == 30 else '')
            # Limitar a 300 caracteres
            if len(self.resumo) > 300:
                self.resumo = self.resumo[:297] + '...'
        
        # Processar conteúdo HTML
        if self.conteudo:
            # Aqui você pode usar uma biblioteca como bleach para sanitizar o HTML
            self.conteudo_html = self.conteudo
        
        # Atualizar data de publicação e capturar órgão
        if self.publicado and not self.data_publicacao:
            self.data_publicacao = timezone.now()
            self.status = 'publicado'
            
            # Capturar o órgão do autor no momento da publicação (campo estático)
            if not self.orgao_publicacao:
                orgao_atual = self.get_orgao_autor()
                if orgao_atual:
                    self.orgao_publicacao = orgao_atual.nome
                else:
                    self.orgao_publicacao = "Governo Federal"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('main:noticia_detalhe', kwargs={'slug': self.slug})
    
    def pode_editar(self, user):
        # Verifica se o usuário pode editar a notícia
        if user.is_superuser:
            return True
        if user == self.autor:
            return True
        if user.has_perm('main.pode_editar_noticias_outros'):
            return True
        return False
    
    def pode_publicar(self, user):
        # Verifica se o usuário pode publicar a notícia
        if user.is_superuser:
            return True
        if user.has_perm('main.pode_publicar_noticias'):
            return True
        return False
    
    def incrementar_visualizacoes(self):
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])
    
    def get_orgao_autor(self):
        """Retorna o órgão do autor da notícia"""
        try:
            profile = self.autor.profile
            if profile.cargo_atual:
                return profile.cargo_atual.entidade.orgao
        except:
            pass
        return None
    
    def get_logo_orgao(self):
        """Retorna a logo do órgão do autor"""
        orgao = self.get_orgao_autor()
        if orgao and orgao.logo:
            return orgao.logo.url
        return None
    
    def get_nome_orgao(self):
        """Retorna o nome do órgão do autor (estático após publicação)"""
        # Se a notícia foi publicada e tem o órgão salvo, usar o valor estático
        if self.publicado and self.orgao_publicacao:
            return self.orgao_publicacao
        
        # Caso contrário, buscar o órgão atual (para notícias em rascunho)
        orgao = self.get_orgao_autor()
        if orgao:
            return orgao.nome
        return "Governo Federal"


class NoticiaImagem(models.Model):
    imagem = models.ImageField(upload_to='noticias/galeria/', verbose_name="Imagem")
    legenda = models.CharField(max_length=200, blank=True, verbose_name="Legenda")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = "Imagem de Notícia"
        verbose_name_plural = "Imagens de Notícias"
    
    def __str__(self):
        return f"Imagem {self.id} - {self.legenda if self.legenda else 'Sem legenda'}"


class NoticiaTag(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class NoticiaCategoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    icone = models.CharField(max_length=50, blank=True, verbose_name="Classe do Ícone")
    cor = models.CharField(max_length=7, default="#007bff", verbose_name="Cor (Hex)")
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class NoticiaComentario(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.TextField(verbose_name="Comentário")
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
    
    def __str__(self):
        return f"Comentário de {self.autor.username} em {self.noticia.titulo}"


class NoticiaLike(models.Model):
    """Modelo para curtidas das notícias"""
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='likes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('noticia', 'usuario')
        verbose_name = "Curtida"
        verbose_name_plural = "Curtidas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.usuario.username} curtiu {self.noticia.titulo}"


class BotaoConfiguravel(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descricao = models.TextField(max_length=200, verbose_name="Descrição")
    icone = models.CharField(max_length=50, verbose_name="Classe do Ícone", 
                           help_text="Ex: fas fa-user, bi bi-house, etc.")
    link = models.URLField(verbose_name="Link de Redirecionamento")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    cor_fundo = models.CharField(max_length=7, default="#007bff", verbose_name="Cor de Fundo (Hex)")
    
    class Meta:
        ordering = ['ordem', 'titulo']
        verbose_name = "Botão Configurável"
        verbose_name_plural = "Botões Configuráveis"
    
    def __str__(self):
        return self.titulo


class EstatisticaSistema(models.Model):
    total_usuarios = models.PositiveIntegerField(default=0, verbose_name="Total de Usuários")
    total_imigrantes = models.PositiveIntegerField(default=0, verbose_name="Total de Imigrantes")
    total_cidadaos = models.PositiveIntegerField(default=0, verbose_name="Total de Cidadãos")
    usuarios_ultimos_7_dias = models.PositiveIntegerField(default=0, verbose_name="Usuários Últimos 7 Dias")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Estatística do Sistema"
        verbose_name_plural = "Estatísticas do Sistema"
    
    def __str__(self):
        return f"Estatísticas - {self.data_atualizacao.strftime('%d/%m/%Y %H:%M')}"


class Anuncio(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    imagem = models.ImageField(upload_to='anuncios/', verbose_name="Imagem")
    link = models.URLField(blank=True, null=True, verbose_name="Link (Opcional)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    
    class Meta:
        ordering = ['ordem', '-data_inicio']
        verbose_name = "Anúncio"
        verbose_name_plural = "Anúncios"
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_ativo(self):
        agora = timezone.now()
        return self.ativo and self.data_inicio <= agora <= self.data_fim


class ConfiguracaoSite(models.Model):
    nome_site = models.CharField(max_length=100, default="GovBR Roleplay", verbose_name="Nome do Site")
    logo = models.ImageField(upload_to='configuracao/', blank=True, null=True, verbose_name="Logo")
    favicon = models.ImageField(upload_to='configuracao/', blank=True, null=True, verbose_name="Favicon")
    link_discord = models.URLField(blank=True, null=True, verbose_name="Link do Discord")
    mensagem_discord = models.CharField(max_length=200, default="Junte-se ao nosso Discord!", 
                                      verbose_name="Mensagem do Discord")
    rodape_texto = models.TextField(blank=True, null=True, verbose_name="Texto do Rodapé")
    cor_primaria = models.CharField(max_length=7, default="#0d6efd", verbose_name="Cor Primária (Hex)")
    cor_secundaria = models.CharField(max_length=7, default="#6c757d", verbose_name="Cor Secundária (Hex)")
    
    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"
    
    def __str__(self):
        return self.nome_site


class ConfiguracaoDiarioOficial(models.Model):
    """Configurações específicas do Diário Oficial"""
    logo_esquerda = models.ImageField(
        upload_to='diario_oficial/', 
        blank=True, 
        null=True, 
        verbose_name="Logo Esquerda (BR)",
        help_text="Imagem que aparece no lado esquerdo do cabeçalho do Diário Oficial. Recomendado: 60x60px"
    )
    texto_logo_esquerda = models.CharField(
        max_length=10, 
        default="BR", 
        verbose_name="Texto Logo Esquerda",
        help_text="Texto que aparece se não houver imagem (padrão: BR)"
    )
    logo_direita = models.ImageField(
        upload_to='diario_oficial/', 
        blank=True, 
        null=True, 
        verbose_name="Logo Direita (RP)",
        help_text="Imagem que aparece no lado direito do cabeçalho do Diário Oficial. Recomendado: 60x60px"
    )
    texto_logo_direita = models.CharField(
        max_length=10, 
        default="RP", 
        verbose_name="Texto Logo Direita",
        help_text="Texto que aparece se não houver imagem (padrão: RP)"
    )
    titulo_diario = models.CharField(
        max_length=100, 
        default="DIÁRIO OFICIAL DA UNIÃO", 
        verbose_name="Título do Diário"
    )
    subtitulo_diario = models.CharField(
        max_length=200, 
        default="REPÚBLICA FEDERATIVA DO BRASIL - IMPRENSA NACIONAL", 
        verbose_name="Subtítulo do Diário"
    )
    
    class Meta:
        verbose_name = "Configuração do Diário Oficial"
        verbose_name_plural = "Configurações do Diário Oficial"
    
    def __str__(self):
        return "Configurações do Diário Oficial"
    
    @classmethod
    def get_configuracao(cls):
        """Retorna a configuração única do diário oficial"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Poder(models.Model):
    """Modelo para os poderes do governo (Executivo, Judiciário, Legislativo, Imprensa)"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Poder")
    
    class Meta:
        verbose_name = "Poder"
        verbose_name_plural = "Poderes"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Orgao(models.Model):
    """Modelo para os órgãos dentro de cada poder"""
    nome = models.CharField(max_length=200, verbose_name="Nome do Órgão")
    poder = models.ForeignKey(Poder, on_delete=models.CASCADE, verbose_name="Poder")
    logo = models.ImageField(
        upload_to='orgaos/logos/', 
        blank=True, 
        null=True, 
        verbose_name="Logo do Órgão",
        help_text="Logo oficial do órgão. Recomendado: 200x200px"
    )
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    site_oficial = models.URLField(blank=True, verbose_name="Site Oficial")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Órgão"
        verbose_name_plural = "Órgãos"
        ordering = ['poder__nome', 'nome']
        unique_together = ['nome', 'poder']
    
    def __str__(self):
        return f"{self.nome} - {self.poder.nome}"


class Entidade(models.Model):
    """Modelo para as entidades dentro de cada órgão"""
    nome = models.CharField(max_length=200, verbose_name="Nome da Entidade")
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, verbose_name="Órgão")
    
    class Meta:
        verbose_name = "Entidade"
        verbose_name_plural = "Entidades"
        ordering = ['orgao__poder__nome', 'orgao__nome', 'nome']
        unique_together = ['nome', 'orgao']
    
    def __str__(self):
        return f"{self.nome} - {self.orgao.nome}"


class Cargo(models.Model):
    """Modelo para os cargos dentro de cada entidade"""
    
    SIMBOLO_CHOICES = [
        ('**', '** (Chefe de Poder)'),
        ('*', '* (Líder de Órgão)'),
        ('+', '+ (Chefe de Entidade)'),
        ('nenhum', 'Nenhum'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Cargo")
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE, verbose_name="Entidade")
    simbolo_gestao = models.CharField(
        max_length=10, 
        choices=SIMBOLO_CHOICES, 
        default='nenhum',
        verbose_name="Símbolo de Gestão"
    )
    
    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['entidade__orgao__poder__nome', 'entidade__orgao__nome', 'entidade__nome', 'nome']
        unique_together = ['nome', 'entidade']
    
    def __str__(self):
        return f"{self.nome} - {self.entidade.nome}"
    
    def get_simbolo_display_icon(self):
        """Retorna o ícone do símbolo de gestão"""
        if self.simbolo_gestao == '**':
            return '👑'  # Chefe de Poder
        elif self.simbolo_gestao == '*':
            return '⭐'  # Líder de Órgão
        elif self.simbolo_gestao == '+':
            return '🔹'  # Chefe de Entidade
        return ''
    
    def pode_gerenciar_cargo(self, outro_cargo):
        """Verifica se este cargo pode gerenciar outro cargo"""
        if self.simbolo_gestao == '**':
            # Chefe de Poder pode gerenciar TODOS os cargos dentro do mesmo poder
            return outro_cargo.entidade.orgao.poder == self.entidade.orgao.poder
        elif self.simbolo_gestao == '*':
            # Líder de Órgão pode gerenciar cargos subordinados dentro do mesmo órgão
            return (outro_cargo.simbolo_gestao in ['+', 'nenhum'] and 
                    outro_cargo.entidade.orgao == self.entidade.orgao)
        elif self.simbolo_gestao == '+':
            # Chefe de Entidade pode gerenciar cargos subordinados dentro da mesma entidade
            return (outro_cargo.simbolo_gestao == 'nenhum' and 
                    outro_cargo.entidade == self.entidade)
        return False
    
    def get_cargos_gerenciaveis(self):
        """Retorna os cargos que este cargo pode gerenciar"""
        if self.simbolo_gestao == '**':
            # Chefe de Poder pode gerenciar TODOS os cargos dentro do mesmo poder
            return Cargo.objects.filter(
                entidade__orgao__poder=self.entidade.orgao.poder
            ).exclude(id=self.id)  # Excluir o próprio cargo
        elif self.simbolo_gestao == '*':
            # Líder de Órgão pode gerenciar cargos subordinados dentro do mesmo órgão
            return Cargo.objects.filter(
                entidade__orgao=self.entidade.orgao,
                simbolo_gestao__in=['+', 'nenhum']
            )
        elif self.simbolo_gestao == '+':
            # Chefe de Entidade pode gerenciar cargos subordinados dentro da mesma entidade
            return Cargo.objects.filter(
                entidade=self.entidade,
                simbolo_gestao='nenhum'
            )
        return Cargo.objects.none()
    
    def get_ocupantes_atuais(self):
        """Retorna todos os históricos dos ocupantes atuais do cargo"""
        # Primeiro obtém os IDs únicos dos usuários mais recentes
        historicos = {}
        for historico in self.historicocargo_set.filter(
            data_fim__isnull=True,
            usuario__isnull=False
        ).select_related('usuario').order_by('-data_inicio'):
            if historico.usuario_id not in historicos:
                historicos[historico.usuario_id] = historico
        
        # Retorna a lista de históricos únicos ordenada por data de início
        return sorted(historicos.values(), key=lambda x: x.data_inicio)

    def get_ocupante_atual(self):
        """Retorna o usuário ocupante atual do cargo (mantido para compatibilidade)"""
        ocupantes = self.get_ocupantes_atuais()
        if ocupantes:
            return ocupantes[0].usuario
        return None


class Profile(models.Model):
    """Extensão do modelo User para incluir cargo atual"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    cargo_atual = models.ForeignKey(
        Cargo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Cargo Atual"
    )
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
    
    def __str__(self):
        return f"Perfil de {self.user.nome_completo_rp}"
    
    def pode_gerenciar_usuario(self, outro_usuario):
        """Verifica se este usuário pode gerenciar outro usuário"""
        if not self.cargo_atual:
            return False
        
        outro_profile = getattr(outro_usuario, 'profile', None)
        if not outro_profile or not outro_profile.cargo_atual:
            return False
        
        return self.cargo_atual.pode_gerenciar_cargo(outro_profile.cargo_atual)
    
    def get_usuarios_gerenciaveis(self):
        """Retorna os usuários que este perfil pode gerenciar"""
        if not self.cargo_atual:
            return User.objects.none()
        
        cargos_gerenciaveis = self.cargo_atual.get_cargos_gerenciaveis()
        return User.objects.filter(profile__cargo_atual__in=cargos_gerenciaveis)
    
    def get_avatar_url(self):
        """Retorna a URL do avatar do usuário"""
        if self.user.discord_avatar:
            return self.user.discord_avatar
        return '/static/images/default-avatar.svg'
    
    @property
    def nome_roleplay(self):
        """Retorna o nome de roleplay do usuário"""
        return self.user.nome_completo_rp


class HistoricoCargo(models.Model):
    """Histórico de cargos dos usuários"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, verbose_name="Cargo")
    data_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Início")
    data_fim = models.DateTimeField(null=True, blank=True, verbose_name="Data de Fim")
    nomeado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='nomeacoes_realizadas',
        verbose_name="Nomeado Por"
    )
    exonerado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='exoneracoes_realizadas',
        verbose_name="Exonerado Por"
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    publicado_diario = models.BooleanField(default=False, help_text="Se já foi publicado no Diário Oficial")
    
    class Meta:
        verbose_name = "Histórico de Cargo"
        verbose_name_plural = "Histórico de Cargos"
        ordering = ['-data_inicio']
    
    def __str__(self):
        status = "Atual" if not self.data_fim else f"Até {self.data_fim.strftime('%d/%m/%Y')}"
        return f"{self.usuario.nome_completo_rp} - {self.cargo.nome} ({status})"
    
    @property
    def is_atual(self):
        """Verifica se este é o cargo atual do usuário"""
        return self.data_fim is None
    
    def finalizar_cargo(self, exonerado_por=None, observacoes=""):
        """Finaliza este cargo (exoneração)"""
        self.data_fim = timezone.now()
        self.exonerado_por = exonerado_por
        if observacoes:
            self.observacoes = observacoes
        self.save()
        
        # Atualizar o perfil do usuário
        profile, created = Profile.objects.get_or_create(user=self.usuario)
        if profile.cargo_atual == self.cargo:
            profile.cargo_atual = None
            profile.save()


# Signals para automação do histórico
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria o perfil automaticamente quando um usuário é criado"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(pre_save, sender=Profile)
def handle_cargo_change(sender, instance, **kwargs):
    """Gerencia mudanças de cargo no perfil"""
    if instance.pk:  # Se o perfil já existe
        try:
            old_profile = Profile.objects.get(pk=instance.pk)
            old_cargo = old_profile.cargo_atual
            new_cargo = instance.cargo_atual
            
            # Se o cargo mudou
            if old_cargo != new_cargo:
                # Finalizar cargo anterior se existir
                if old_cargo:
                    historico_atual = HistoricoCargo.objects.filter(
                        usuario=instance.user,
                        cargo=old_cargo,
                        data_fim__isnull=True
                    ).first()
                    
                    if historico_atual:
                        # Só finalizar se ainda não foi finalizado
                        if not historico_atual.data_fim:
                            historico_atual.finalizar_cargo()
                
                # Criar novo histórico se há novo cargo
                if new_cargo:
                    HistoricoCargo.objects.create(
                        usuario=instance.user,
                        cargo=new_cargo
                    )
        except Profile.DoesNotExist:
            # Perfil novo, criar histórico se há cargo
            if instance.cargo_atual:
                HistoricoCargo.objects.create(
                    usuario=instance.user,
                    cargo=instance.cargo_atual
                )

@receiver(post_save, sender=HistoricoCargo)
def criar_publicacao_diario_oficial(sender, instance, created, **kwargs):
    """Cria publicação automática no Diário Oficial quando há mudança de cargo"""
    logger.info(f"🔄 SIGNAL NOMEAÇÃO - HistoricoCargo {instance.id} - Usuario: {instance.usuario.nome_completo_rp}")
    logger.info(f"   - created: {created}, publicado_diario: {instance.publicado_diario}")
    logger.info(f"   - Cargo: {instance.cargo.nome} ({instance.cargo.simbolo_gestao})")
    logger.info(f"   - Entidade: {instance.cargo.entidade.nome}")
    logger.info(f"   - Órgão: {instance.cargo.entidade.orgao.nome}")
    logger.info(f"   - Poder: {instance.cargo.entidade.orgao.poder.nome}")
    
    # Só criar publicação se for uma nova criação E ainda não foi publicado no diário
    # E não há data_fim (não é exoneração)
    if created and not instance.publicado_diario and not instance.data_fim:
        logger.info(f"✅ Condições iniciais atendidas para criar publicação de nomeação")
        
        # Verifica se o cargo é elegível para publicação (**, *, +)
        if instance.cargo.simbolo_gestao in ['**', '*', '+']:
            logger.info(f"✅ Cargo elegível para publicação: {instance.cargo.simbolo_gestao}")
            
            # Verifica se o poder é elegível (Executivo, Legislativo, Judiciário)
            poder_nome = instance.cargo.entidade.orgao.poder.nome.lower()
            logger.info(f"🔍 Verificando poder: '{poder_nome}'")
            
            if any(poder in poder_nome for poder in ['executivo', 'legislativo', 'judiciário', 'judiciario']):
                logger.info(f"✅ Poder elegível para publicação")
                
                # Verifica de forma mais rigorosa se já existe uma publicação
                publicacoes_existentes = PublicacaoDiarioOficial.objects.filter(
                    historico_cargo=instance, 
                    tipo='nomeacao'
                )
                
                logger.info(f"🔍 Verificando publicações existentes: {publicacoes_existentes.count()} encontradas")
                
                # Se não existe nenhuma publicação, criar uma
                if not publicacoes_existentes.exists():
                    logger.info(f"✅ Criando publicação de nomeação para {instance.usuario.nome_completo_rp}")
                    try:
                        publicacao = PublicacaoDiarioOficial.criar_publicacao_automatica(instance, 'nomeacao')
                        if publicacao:
                            logger.info(f"✅ Publicação criada com sucesso - ID: {publicacao.id}")
                        else:
                            logger.error(f"❌ Falha ao criar publicação - retorno None")
                    except Exception as e:
                        logger.error(f"❌ Erro ao criar publicação: {str(e)}")
                    instance.publicado_diario = True
                    instance.save(update_fields=['publicado_diario'])
                else:
                    logger.warning(f"⚠️ Publicação de nomeação já existe para {instance.usuario.nome_completo_rp}")
                    instance.publicado_diario = True
                    instance.save(update_fields=['publicado_diario'])
            else:
                logger.warning(f"❌ Poder não elegível: '{poder_nome}'")
        else:
            logger.warning(f"❌ Cargo não elegível: {instance.cargo.simbolo_gestao}")
    else:
        logger.info(f"❌ Condições não atendidas - created: {created}, publicado_diario: {instance.publicado_diario}")

@receiver(pre_save, sender=HistoricoCargo)
def criar_publicacao_exoneracao(sender, instance, **kwargs):
    """Cria publicação de exoneração quando um histórico é finalizado"""
    logger.info(f"🔄 SIGNAL EXONERAÇÃO - HistoricoCargo {instance.pk} - Usuario: {instance.usuario.nome_completo_rp}")
    
    if instance.pk:  # Se o histórico já existe
        try:
            old_instance = HistoricoCargo.objects.get(pk=instance.pk)
            logger.info(f"📋 Comparação de estados:")
            logger.info(f"   - old_instance.data_fim: {old_instance.data_fim}")
            logger.info(f"   - instance.data_fim: {instance.data_fim}")
            logger.info(f"   - Cargo: {instance.cargo.nome} ({instance.cargo.simbolo_gestao})")
            logger.info(f"   - Entidade: {instance.cargo.entidade.nome}")
            logger.info(f"   - Órgão: {instance.cargo.entidade.orgao.nome}")
            logger.info(f"   - Poder: {instance.cargo.entidade.orgao.poder.nome}")
            
            # Se foi finalizado agora (data_fim foi adicionada)
            if not old_instance.data_fim and instance.data_fim:
                logger.info(f"✅ Histórico foi finalizado agora (exoneração detectada)")
                
                # Verifica se o cargo é elegível para publicação (**, *, +)
                if instance.cargo.simbolo_gestao in ['**', '*', '+']:
                    logger.info(f"✅ Cargo elegível para publicação: {instance.cargo.simbolo_gestao}")
                    
                    # Verifica se o poder é elegível
                    poder_nome = instance.cargo.entidade.orgao.poder.nome.lower()
                    logger.info(f"🔍 Verificando poder: '{poder_nome}'")
                    
                    if any(poder in poder_nome for poder in ['executivo', 'legislativo', 'judiciário', 'judiciario']):
                        logger.info(f"✅ Poder elegível para publicação")
                        
                        # Verifica de forma mais rigorosa se já existe uma publicação
                        publicacoes_existentes = PublicacaoDiarioOficial.objects.filter(
                            historico_cargo=instance, 
                            tipo='exoneracao'
                        )
                        
                        logger.info(f"🔍 Verificando publicações de exoneração existentes: {publicacoes_existentes.count()} encontradas")
                        
                        # Se não existe nenhuma publicação, criar uma
                        if not publicacoes_existentes.exists():
                            logger.info(f"✅ Criando publicação de exoneração para {instance.usuario.nome_completo_rp}")
                            try:
                                publicacao = PublicacaoDiarioOficial.criar_publicacao_automatica(instance, 'exoneracao')
                                if publicacao:
                                    logger.info(f"✅ Publicação de exoneração criada com sucesso - ID: {publicacao.id}")
                                else:
                                    logger.error(f"❌ Falha ao criar publicação de exoneração - retorno None")
                            except Exception as e:
                                logger.error(f"❌ Erro ao criar publicação de exoneração: {str(e)}")
                        else:
                            logger.warning(f"⚠️ Publicação de exoneração já existe para {instance.usuario.nome_completo_rp}")
                    else:
                        logger.warning(f"❌ Poder não elegível: '{poder_nome}'")
                else:
                    logger.warning(f"❌ Cargo não elegível: {instance.cargo.simbolo_gestao}")
            else:
                logger.info(f"❌ Histórico não foi finalizado agora")
        except HistoricoCargo.DoesNotExist:
            logger.error("⚠️ HistoricoCargo não encontrado no signal de exoneração")
            pass
    else:
        logger.info(f"❌ Histórico novo (sem PK), não é exoneração")


class DiarioOficial(models.Model):
    """Modelo para representar uma edição do Diário Oficial"""
    SECOES_CHOICES = [
        ('executivo', 'Poder Executivo'),
        ('legislativo', 'Poder Legislativo'),
        ('judiciario', 'Poder Judiciário'),
    ]
    
    numero = models.PositiveIntegerField(unique=True, help_text="Número sequencial da edição")
    data_publicacao = models.DateField(default=timezone.now)
    ano = models.PositiveIntegerField(default=timezone.now().year)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_publicacao', '-numero']
        verbose_name = "Diário Oficial"
        verbose_name_plural = "Diários Oficiais"
    
    def __str__(self):
        return f"D.O. Nº {self.numero} - {self.data_publicacao.strftime('%d/%m/%Y')}"
    
    def get_absolute_url(self):
        return reverse('main:diario_oficial_detalhe', kwargs={'numero': self.numero})
    
    @classmethod
    def get_proximo_numero(cls):
        """Retorna o próximo número sequencial"""
        ultimo = cls.objects.order_by('-numero').first()
        return (ultimo.numero + 1) if ultimo else 1
    
    def get_publicacoes_por_secao(self):
        """Retorna as publicações organizadas por seção"""
        publicacoes = {}
        for secao_key, secao_nome in self.SECOES_CHOICES:
            publicacoes[secao_key] = {
                'nome': secao_nome,
                'publicacoes': self.publicacoes.filter(secao=secao_key).order_by('criado_em')
            }
        return publicacoes


class PublicacaoDiarioOficial(models.Model):
    """Modelo para representar uma publicação no Diário Oficial"""
    TIPOS_CHOICES = [
        ('nomeacao', 'Nomeação'),
        ('exoneracao', 'Exoneração'),
        ('transferencia', 'Transferência'),
        ('promocao', 'Promoção'),
        ('decreto', 'Decreto'),
        ('portaria', 'Portaria'),
        ('edital', 'Edital'),
        ('aviso', 'Aviso'),
    ]
    
    SECOES_CHOICES = [
        ('executivo', 'Poder Executivo'),
        ('legislativo', 'Poder Legislativo'),
        ('judiciario', 'Poder Judiciário'),
    ]
    
    diario = models.ForeignKey(DiarioOficial, on_delete=models.CASCADE, related_name='publicacoes')
    tipo = models.CharField(max_length=20, choices=TIPOS_CHOICES)
    secao = models.CharField(max_length=20, choices=SECOES_CHOICES)
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    
    # Campos para publicações automáticas
    historico_cargo = models.ForeignKey(
        'HistoricoCargo', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Histórico de cargo relacionado (para publicações automáticas)"
    )
    
    # Campos para controle
    automatica = models.BooleanField(default=False, help_text="Se a publicação foi gerada automaticamente")
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['tipo', 'criado_em']
        verbose_name = "Publicação do Diário Oficial"
        verbose_name_plural = "Publicações do Diário Oficial"
        # Constraint para evitar duplicações de publicações automáticas
        constraints = [
            models.UniqueConstraint(
                fields=['historico_cargo', 'tipo'],
                condition=models.Q(historico_cargo__isnull=False),
                name='unique_publicacao_historico_tipo'
            )
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo[:50]}..."
    
    def get_numero_formatado(self):
        """Retorna o número da publicação formatado"""
        publicacoes_anteriores = PublicacaoDiarioOficial.objects.filter(
            diario=self.diario,
            secao=self.secao,
            id__lt=self.id
        ).count()
        return publicacoes_anteriores + 1
    
    @classmethod
    def criar_publicacao_automatica(cls, historico_cargo, tipo_acao):
        """Cria uma publicação automática baseada em mudança de cargo"""
        logger.info(f"🏭 CRIAR_PUBLICACAO_AUTOMATICA - {tipo_acao.upper()}")
        logger.info(f"   - Usuario: {historico_cargo.usuario.nome_completo_rp}")
        logger.info(f"   - Cargo: {historico_cargo.cargo.nome}")
        logger.info(f"   - Símbolo: {historico_cargo.cargo.simbolo_gestao}")
        
        # Verifica se o cargo tem nível de gestão adequado
        if historico_cargo.cargo.simbolo_gestao not in ['**', '*', '+']:
            logger.warning(f"❌ Cargo sem nível de gestão adequado: {historico_cargo.cargo.simbolo_gestao}")
            return None
        
        logger.info(f"✅ Cargo com nível adequado: {historico_cargo.cargo.simbolo_gestao}")
        
        # Verifica se o poder está nos permitidos
        poder_nome = historico_cargo.cargo.entidade.orgao.poder.nome.lower()
        logger.info(f"🔍 Verificando poder: '{poder_nome}'")
        
        if 'executivo' not in poder_nome and 'legislativo' not in poder_nome and 'judiciário' not in poder_nome and 'judiciario' not in poder_nome:
            logger.warning(f"❌ Poder não permitido: '{poder_nome}'")
            return None
        
        logger.info(f"✅ Poder permitido: '{poder_nome}'")
        
        # Determina a seção baseada no poder
        secao = 'executivo'
        if 'legislativo' in poder_nome:
            secao = 'legislativo'
        elif 'judiciário' in poder_nome or 'judiciario' in poder_nome:
            secao = 'judiciario'
        
        logger.info(f"📂 Seção determinada: {secao}")
        
        # Obtém ou cria o diário oficial do dia (usando fuso horário do Brasil)
        try:
            from django.utils import timezone as django_timezone
            import pytz
            
            # Converte para o horário de Brasília
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            agora_brasilia = django_timezone.now().astimezone(brasilia_tz)
            data_hoje_brasil = agora_brasilia.date()
            
            diario, created = DiarioOficial.objects.get_or_create(
                data_publicacao=data_hoje_brasil,
                defaults={'numero': DiarioOficial.get_proximo_numero()}
            )
            logger.info(f"📰 Diário oficial {'criado' if created else 'obtido'} - Nº {diario.numero}")
        except Exception as e:
            logger.error(f"❌ Erro ao obter/criar diário oficial: {str(e)}")
            return None
        
        # Gera o conteúdo da publicação
        try:
            conteudo = cls._gerar_conteudo_automatico(historico_cargo, tipo_acao)
            titulo = cls._gerar_titulo_automatico(historico_cargo, tipo_acao)
            logger.info(f"📝 Conteúdo gerado - Título: {titulo[:50]}...")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar conteúdo: {str(e)}")
            return None
        
        # Cria a publicação
        try:
            publicacao = cls.objects.create(
                diario=diario,
                tipo=tipo_acao,
                secao=secao,
                titulo=titulo,
                conteudo=conteudo,
                historico_cargo=historico_cargo,
                automatica=True
            )
            
            logger.info(f"✅ Publicação criada com sucesso!")
            logger.info(f"   - ID: {publicacao.id}")
            logger.info(f"   - Diário: {diario.numero}")
            logger.info(f"   - Tipo: {tipo_acao}")
            logger.info(f"   - Seção: {secao}")
        
            return publicacao
        except Exception as e:
            logger.error(f"❌ Erro ao criar publicação no banco: {str(e)}")
            return None
    
    @classmethod
    def _gerar_titulo_automatico(cls, historico_cargo, tipo_acao):
        """Gera o título da publicação automática"""
        usuario = historico_cargo.usuario
        cargo = historico_cargo.cargo
        
        if tipo_acao == 'nomeacao':
            return f"NOMEAÇÃO - {usuario.nome_completo_rp}"
        elif tipo_acao == 'exoneracao':
            return f"EXONERAÇÃO - {usuario.nome_completo_rp}"
        elif tipo_acao == 'promocao':
            return f"PROMOÇÃO - {usuario.nome_completo_rp}"
        elif tipo_acao == 'transferencia':
            return f"TRANSFERÊNCIA - {usuario.nome_completo_rp}"
        else:
            return f"{tipo_acao.upper()} - {usuario.nome_completo_rp}"
    
    @classmethod
    def _gerar_conteudo_automatico(cls, historico_cargo, tipo_acao):
        """Gera o conteúdo da publicação automática"""
        from datetime import datetime
        import locale
        
        # Configura locale para português
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            pass
        
        usuario = historico_cargo.usuario
        cargo = historico_cargo.cargo
        
        if tipo_acao == 'nomeacao':
            data_formatada = historico_cargo.data_inicio.strftime('%d de %B de %Y')
            nomeado_por = historico_cargo.nomeado_por
            
            # Informações do responsável pela nomeação
            responsavel_info = ""
            if nomeado_por:
                try:
                    responsavel_cargo = nomeado_por.profile.cargo_atual
                    if responsavel_cargo:
                        responsavel_info = f"""

AUTORIDADE RESPONSÁVEL:
{nomeado_por.nome_completo_rp}
{responsavel_cargo.nome}, {responsavel_cargo.simbolo_gestao}
{responsavel_cargo.entidade.nome}
{responsavel_cargo.entidade.orgao.nome}"""
                except:
                    responsavel_info = f"\n\nAUTORIDADE RESPONSÁVEL:\n{nomeado_por.nome_completo_rp}"
            
            return f"""DECRETO DE NOMEAÇÃO

O {cargo.entidade.orgao.poder.nome}, no uso das atribuições que lhe confere a Constituição Federal e demais legislações aplicáveis,

CONSIDERANDO a necessidade de provimento do cargo de {cargo.nome} no âmbito do {cargo.entidade.nome};

CONSIDERANDO a competência técnica e os requisitos necessários para o exercício da função;

DECRETA:

Art. 1º - NOMEAR {usuario.nome_completo_rp}, para exercer o cargo de {cargo.nome}, símbolo {cargo.simbolo_gestao}, do {cargo.entidade.nome}, vinculado ao {cargo.entidade.orgao.nome}, do {cargo.entidade.orgao.poder.nome}.

Art. 2º - O nomeado deverá tomar posse no prazo de 30 (trinta) dias, contados da publicação deste Decreto.

Art. 3º - Esta nomeação entra em vigor na data de sua publicação.

Art. 4º - Revogam-se as disposições em contrário.

Brasília, {data_formatada}{responsavel_info}"""
        
        elif tipo_acao == 'exoneracao':
            data_exoneracao = historico_cargo.data_fim.strftime('%d de %B de %Y') if historico_cargo.data_fim else datetime.now().strftime('%d de %B de %Y')
            exonerado_por = historico_cargo.exonerado_por
            motivo = historico_cargo.observacoes.strip() if historico_cargo.observacoes else "A pedido do interessado"
            
            # Informações do responsável pela exoneração
            responsavel_info = ""
            if exonerado_por:
                try:
                    responsavel_cargo = exonerado_por.profile.cargo_atual
                    if responsavel_cargo:
                        responsavel_info = f"""

AUTORIDADE RESPONSÁVEL:
{exonerado_por.nome_completo_rp}
{responsavel_cargo.nome}, {responsavel_cargo.simbolo_gestao}
{responsavel_cargo.entidade.nome}
{responsavel_cargo.entidade.orgao.nome}"""
                except:
                    responsavel_info = f"\n\nAUTORIDADE RESPONSÁVEL:\n{exonerado_por.nome_completo_rp}"
            
            return f"""DECRETO DE EXONERAÇÃO

O {cargo.entidade.orgao.poder.nome}, no uso das atribuições que lhe confere a Constituição Federal e demais legislações aplicáveis,

CONSIDERANDO {motivo.lower()};

DECRETA:

Art. 1º - EXONERAR {usuario.nome_completo_rp}, do cargo de {cargo.nome}, símbolo {cargo.simbolo_gestao}, do {cargo.entidade.nome}, vinculado ao {cargo.entidade.orgao.nome}, do {cargo.entidade.orgao.poder.nome}.

Art. 2º - Esta exoneração entra em vigor na data de {data_exoneracao}.

Art. 3º - Fica o interessado desobrigado das funções inerentes ao cargo a partir da data de vigência deste Decreto.

Art. 4º - Revogam-se as disposições em contrário.

Brasília, {data_exoneracao}{responsavel_info}"""
        
        elif tipo_acao == 'promocao':
            data_formatada = historico_cargo.data_inicio.strftime('%d de %B de %Y')
            nomeado_por = historico_cargo.nomeado_por
            motivo = historico_cargo.observacoes.strip() if historico_cargo.observacoes else "Em reconhecimento aos serviços prestados e competência demonstrada"
            
            # Informações do responsável pela promoção
            responsavel_info = ""
            if nomeado_por:
                try:
                    responsavel_cargo = nomeado_por.profile.cargo_atual
                    if responsavel_cargo:
                        responsavel_info = f"""

AUTORIDADE RESPONSÁVEL:
{nomeado_por.nome_completo_rp}
{responsavel_cargo.nome}, {responsavel_cargo.simbolo_gestao}
{responsavel_cargo.entidade.nome}
{responsavel_cargo.entidade.orgao.nome}"""
                except:
                    responsavel_info = f"\n\nAUTORIDADE RESPONSÁVEL:\n{nomeado_por.nome_completo_rp}"
            
            return f"""DECRETO DE PROMOÇÃO

O {cargo.entidade.orgao.poder.nome}, no uso das atribuições que lhe confere a Constituição Federal e demais legislações aplicáveis,

CONSIDERANDO {motivo.lower()};

CONSIDERANDO a necessidade de reorganização administrativa e otimização dos serviços públicos;

DECRETA:

Art. 1º - PROMOVER {usuario.nome_completo_rp}, para exercer o cargo de {cargo.nome}, símbolo {cargo.simbolo_gestao}, do {cargo.entidade.nome}, vinculado ao {cargo.entidade.orgao.nome}, do {cargo.entidade.orgao.poder.nome}.

Art. 2º - A promoção tem caráter definitivo e entra em vigor na data de {data_formatada}.

Art. 3º - Ficam mantidos todos os direitos e prerrogativas inerentes ao novo cargo.

Art. 4º - Revogam-se as disposições em contrário.

Brasília, {data_formatada}{responsavel_info}"""
        
        else:
            data_formatada = historico_cargo.data_inicio.strftime('%d de %B de %Y')
            return f"""PORTARIA

O {cargo.entidade.orgao.poder.nome}, no uso de suas atribuições legais,

RESOLVE:

Art. 1º - {tipo_acao.upper()} de {usuario.nome_completo_rp}, referente ao cargo de {cargo.nome}, símbolo {cargo.simbolo_gestao}, do {cargo.entidade.nome}, vinculado ao {cargo.entidade.orgao.nome}.

Art. 2º - Esta decisão entra em vigor na data de {data_formatada}.

Art. 3º - Revogam-se as disposições em contrário.

Brasília, {data_formatada}

{cargo.entidade.orgao.poder.nome}"""


class ConfiguracaoCidadania(models.Model):
    """Configurações do sistema de cidadania"""
    
    # Configurações básicas
    prazo_analise_dias = models.PositiveIntegerField(
        default=7,
        verbose_name="Prazo para Análise (Dias)",
        help_text="Prazo padrão em dias para análise das solicitações"
    )
    
    documentos_obrigatorios = models.TextField(
        default="RG ou CNH\nCPF\nComprovante de Residência",
        verbose_name="Documentos Obrigatórios",
        help_text="Lista de documentos obrigatórios (um por linha)"
    )
    
    instrucoes = models.TextField(
        default="Para solicitar sua cidadania brasileira, preencha o formulário abaixo com seus dados pessoais e anexe os documentos necessários.",
        verbose_name="Instruções",
        help_text="Instruções exibidas na página de solicitação"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Sistema Ativo",
        help_text="Se o sistema de cidadania está aceitando novas solicitações"
    )
    
    # Configurações de órgão responsável
    orgao_responsavel = models.ForeignKey(
        'Orgao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Órgão Responsável",
        help_text="Órgão responsável pelo processamento de solicitações de cidadania"
    )
    
    # Configurações de cargos autorizados
    cargos_autorizados = models.ManyToManyField(
        'Cargo',
        blank=True,
        verbose_name="Cargos Autorizados",
        help_text="Cargos que podem aprovar/rejeitar solicitações de cidadania"
    )
    
    # Datas de controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Cidadania"
        verbose_name_plural = "Configurações de Cidadania"
    
    def __str__(self):
        return f"Configuração de Cidadania - {self.orgao_responsavel or 'Sem órgão definido'}"
    
    @classmethod
    def get_configuracao(cls):
        """Retorna a configuração atual ou cria uma padrão"""
        config, created = cls.objects.get_or_create(
            defaults={
                'prazo_analise_dias': 7,
                'documentos_obrigatorios': 'RG ou CNH\nCPF\nComprovante de Residência',
                'instrucoes': 'Para solicitar sua cidadania brasileira, preencha o formulário abaixo com seus dados pessoais e anexe os documentos necessários.',
                'ativo': True,
            }
        )
        return config
    
    def get_cargos_autorizados_display(self):
        """Retorna lista formatada dos cargos autorizados"""
        cargos = self.cargos_autorizados.all()
        if not cargos.exists():
            return "Nenhum cargo definido"
        
        return ", ".join([f"{cargo.nome} ({cargo.entidade.nome})" for cargo in cargos[:3]]) + \
               (f" e mais {cargos.count() - 3}" if cargos.count() > 3 else "")
    
    def pode_solicitar(self):
        """Verifica se o sistema está aceitando solicitações"""
        return self.ativo
    
    def usuario_pode_aprovar(self, usuario):
        """Verifica se o usuário pode aprovar solicitações de cidadania"""
        # Superusuários e níveis altos sempre podem
        if usuario.is_superuser or usuario.nivel_acesso in ['administrador', 'coordenador', 'fundador']:
            return True
        
        # Verificar se tem cargo autorizado
        if self.cargos_autorizados.exists():
            try:
                profile = usuario.profile
                if profile.cargo_atual and profile.cargo_atual in self.cargos_autorizados.all():
                    return True
            except:
                pass
        
        return False


# ===== SISTEMA DE PROTOCOLOS =====

class EspecieDocumento(models.Model):
    """Espécies de documentos para protocolos"""
    nome = models.CharField(max_length=100, verbose_name="Nome da Espécie")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Espécie de Documento"
        verbose_name_plural = "Espécies de Documentos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Protocolo(models.Model):
    """Modelo principal para protocolos"""
    
    RESTRICAO_CHOICES = [
        ('publico', 'Público'),
        ('restrito', 'Restrito'),
        ('sigiloso', 'Sigiloso'),
    ]
    
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
        ('arquivado', 'Arquivado'),
    ]
    
    URGENCIA_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]
    
    # Identificação
    numero_protocolo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número do Protocolo",
        help_text="Formato: XX.XXX.XXX-X"
    )
    ano = models.PositiveIntegerField(verbose_name="Ano")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    # Conteúdo
    assunto = models.CharField(max_length=200, verbose_name="Assunto")
    detalhamento = models.TextField(
        max_length=2400,
        verbose_name="Detalhamento",
        help_text="Máximo 2.400 caracteres"
    )
    especie_documento = models.ForeignKey(
        EspecieDocumento,
        on_delete=models.CASCADE,
        verbose_name="Espécie de Documento"
    )
    
    # Origem (cadastro)
    usuario_cadastro = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='protocolos_criados',
        verbose_name="Usuário de Cadastro"
    )
    orgao_cadastro = models.ForeignKey(
        'Orgao',
        on_delete=models.CASCADE,
        related_name='protocolos_cadastrados',
        verbose_name="Órgão de Cadastro",
        null=True,
        blank=True
    )
    entidade_cadastro = models.ForeignKey(
        'Entidade',
        on_delete=models.CASCADE,
        related_name='protocolos_cadastrados',
        verbose_name="Setor de Cadastro",
        null=True,
        blank=True
    )
    
    # Destino
    orgao_destinatario = models.ForeignKey(
        'Orgao',
        on_delete=models.CASCADE,
        related_name='protocolos_recebidos',
        verbose_name="Órgão Destinatário"
    )
    entidade_destinatario = models.ForeignKey(
        'Entidade',
        on_delete=models.CASCADE,
        related_name='protocolos_recebidos',
        verbose_name="Setor Destinatário",
        null=True,
        blank=True
    )
    usuario_destinatario = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocolos_recebidos',
        verbose_name="Destinatário Específico"
    )
    
    # Configurações
    urgencia = models.CharField(
        max_length=3,
        choices=URGENCIA_CHOICES,
        default='nao',
        verbose_name="Urgência"
    )
    restricao_acesso = models.CharField(
        max_length=10,
        choices=RESTRICAO_CHOICES,
        default='publico',
        verbose_name="Restrição de Acesso"
    )
    
    # Controle
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='aberto',
        verbose_name="Status"
    )
    monitorado_por_usuario = models.BooleanField(
        default=False,
        verbose_name="Monitorado pelo Usuário"
    )
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Protocolo"
        verbose_name_plural = "Protocolos"
        ordering = ['-data_cadastro']
        permissions = [
            ('pode_gerenciar_protocolos', 'Pode gerenciar protocolos'),
            ('pode_assinar_documentos', 'Pode assinar documentos'),
            ('pode_encaminhar_protocolos', 'Pode encaminhar protocolos'),
        ]
    
    def save(self, *args, **kwargs):
        """Gerar número de protocolo único"""
        if not self.numero_protocolo:
            import datetime
            import random
            
            now = datetime.datetime.now()
            self.ano = now.year
            
            # Contar protocolos do ano
            count = Protocolo.objects.filter(ano=self.ano).count() + 1
            
            # Formato: XX.XXX.XXX-X (baseado no exemplo 19.186.860-9)
            base_number = f"{count:08d}"  # 8 dígitos com zeros à esquerda
            formatted = f"{base_number[:2]}.{base_number[2:5]}.{base_number[5:8]}"
            
            # Calcular dígito verificador simples
            digits = [int(d) for d in base_number]
            check_digit = sum(digits) % 10
            
            self.numero_protocolo = f"{formatted}-{check_digit}"
            
            # Verificar se já existe (muito improvável)
            while Protocolo.objects.filter(numero_protocolo=self.numero_protocolo).exists():
                count += 1
                base_number = f"{count:08d}"
                formatted = f"{base_number[:2]}.{base_number[2:5]}.{base_number[5:8]}"
                digits = [int(d) for d in base_number]
                check_digit = sum(digits) % 10
                self.numero_protocolo = f"{formatted}-{check_digit}"
        
        # Garantir que existe um órgão "Cidadão" para usuários sem cargo
        if not self.orgao_cadastro_id:
            self.orgao_cadastro = self.get_or_create_orgao_cidadao()
        if not self.entidade_cadastro_id:
            self.entidade_cadastro = self.get_or_create_entidade_cidadao()
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_or_create_orgao_cidadao(cls):
        """Cria ou retorna o órgão especial 'Cidadão'"""
        # Primeiro, garantir que existe um poder "Cidadão"
        poder_cidadao, created = Poder.objects.get_or_create(
            nome="Cidadão",
            defaults={}
        )
        
        # Depois, garantir que existe o órgão "Cidadão"
        orgao_cidadao, created = Orgao.objects.get_or_create(
            nome="Cidadão",
            poder=poder_cidadao,
            defaults={
                'descricao': 'Órgão especial para cidadãos sem cargo específico',
                'ativo': True
            }
        )
        
        return orgao_cidadao
    
    @classmethod
    def get_or_create_entidade_cidadao(cls):
        """Cria ou retorna a entidade especial 'Cidadão'"""
        orgao_cidadao = cls.get_or_create_orgao_cidadao()
        
        entidade_cidadao, created = Entidade.objects.get_or_create(
            nome="Cidadão",
            orgao=orgao_cidadao,
            defaults={}
        )
        
        return entidade_cidadao
    
    @classmethod
    def get_orgao_usuario(cls, usuario):
        """Retorna o órgão do usuário ou o órgão 'Cidadão' se não tiver cargo"""
        try:
            profile = usuario.profile
            if profile.cargo_atual:
                return profile.cargo_atual.entidade.orgao
        except:
            pass
        return cls.get_or_create_orgao_cidadao()
    
    @classmethod
    def get_entidade_usuario(cls, usuario):
        """Retorna a entidade do usuário ou a entidade 'Cidadão' se não tiver cargo"""
        try:
            profile = usuario.profile
            if profile.cargo_atual:
                return profile.cargo_atual.entidade
        except:
            pass
        return cls.get_or_create_entidade_cidadao()
    
    def pode_visualizar(self, usuario):
        """Verifica se o usuário pode visualizar este protocolo"""
        # Criador sempre pode ver
        if self.usuario_cadastro == usuario:
            return True
        
        # Destinatário específico pode ver
        if self.usuario_destinatario == usuario:
            return True
        
        # Verificar por restrição de acesso
        if self.restricao_acesso == 'publico':
            return True
        elif self.restricao_acesso == 'restrito':
            # Membros dos órgãos de origem e destino
            try:
                profile = usuario.profile
                if profile.cargo_atual:
                    if (profile.cargo_atual.entidade.orgao == self.orgao_cadastro or 
                        profile.cargo_atual.entidade.orgao == self.orgao_destinatario):
                        return True
            except:
                pass
        elif self.restricao_acesso == 'sigiloso':
            # Apenas pessoas específicas cadastradas como interessadas
            return ProtocoloInteressado.objects.filter(
                protocolo=self,
                usuario=usuario
            ).exists()
        
        # Administradores sempre podem ver
        if usuario.nivel_acesso in ['administrador', 'coordenador', 'fundador']:
            return True
        
        return False
    
    def pode_gerenciar(self, usuario):
        """Verifica se o usuário pode gerenciar este protocolo"""
        # Criador pode gerenciar
        if self.usuario_cadastro == usuario:
            return True
        
        # Destinatário específico pode gerenciar
        if self.usuario_destinatario == usuario:
            return True
        
        # Membros do órgão/entidade de destino podem gerenciar
        try:
            profile = usuario.profile
            if profile.cargo_atual:
                if (profile.cargo_atual.entidade.orgao == self.orgao_destinatario or
                    profile.cargo_atual.entidade == self.entidade_destinatario):
                    return True
        except:
            pass
        
        # Administradores sempre podem gerenciar
        if usuario.nivel_acesso in ['administrador', 'coordenador', 'fundador']:
            return True
        
        return False
    
    def __str__(self):
        return f"Protocolo {self.numero_protocolo} - {self.assunto}"
    
class ProtocoloDocumento(models.Model):
    """Documentos anexados ao protocolo"""
    
    TIPO_CHOICES = [
        ('documento', 'Documento'),
        ('anexo', 'Anexo'),
        ('parecer', 'Parecer'),
    ]
    
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name="Protocolo"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Documento")
    arquivo = models.FileField(
        upload_to='protocolos/documentos/',
        verbose_name="Arquivo"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='documento',
        verbose_name="Tipo"
    )
    usuario_upload = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Usuário que fez Upload"
    )
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data do Upload")
    identificador = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Identificador",
        help_text="Identificador único do documento no protocolo (ex: DOC-001)"
    )
    assinado = models.BooleanField(default=False, verbose_name="Assinado")
    data_assinatura = models.DateTimeField(null=True, blank=True, verbose_name="Data da Assinatura")
    usuario_assinatura = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_assinados',
        verbose_name="Usuário que Assinou"
    )
    observacoes_assinatura = models.TextField(
        blank=True,
        verbose_name="Observações da Assinatura",
        help_text="Observações opcionais sobre a assinatura"
    )
    
    class Meta:
        verbose_name = "Documento do Protocolo"
        verbose_name_plural = "Documentos do Protocolo"
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.protocolo.numero_protocolo} - {self.nome}"

    def tem_assinatura_multipla(self):
        """Verifica se o documento tem múltiplas assinaturas"""
        return self.assinaturas_multiplas.filter(ativa=True).exists()
    
    def get_todas_assinaturas(self):
        """Retorna todas as assinaturas ativas do documento"""
        return self.assinaturas_multiplas.filter(ativa=True).order_by('data_assinatura')
    
    def pode_assinar(self, usuario):
        """Verifica se o usuário pode assinar o documento"""
        # Não pode assinar se já assinou
        if self.assinaturas_multiplas.filter(usuario=usuario, ativa=True).exists():
            return False
        
        # Verificar se há solicitação pendente ou se tem permissão geral
        has_solicitacao = SolicitacaoAssinatura.objects.filter(
            documento=self,
            usuario_destinatario=usuario,
            status='pendente'
        ).exists()
        
        return has_solicitacao or self.protocolo.pode_visualizar(usuario)


class AssinaturaDocumento(models.Model):
    """Modelo para múltiplas assinaturas em documentos"""
    
    documento = models.ForeignKey(
        ProtocoloDocumento,
        on_delete=models.CASCADE,
        related_name='assinaturas_multiplas',
        verbose_name="Documento"
    )
    usuario = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='assinaturas_realizadas',
        verbose_name="Usuário que Assinou"
    )
    data_assinatura = models.DateTimeField(auto_now_add=True, verbose_name="Data da Assinatura")
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Observações opcionais sobre a assinatura"
    )
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se false, a assinatura foi revogada"
    )
    cargo_assinante = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Cargo do Assinante",
        help_text="Cargo do usuário no momento da assinatura"
    )
    hash_documento = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Hash do Documento",
        help_text="Hash do documento no momento da assinatura para validação"
    )
    
    class Meta:
        verbose_name = "Assinatura de Documento"
        verbose_name_plural = "Assinaturas de Documentos"
        ordering = ['-data_assinatura']
        unique_together = ['documento', 'usuario']  # Um usuário só pode assinar uma vez cada documento
    
    def __str__(self):
        return f"{self.usuario.nome_completo_rp} - {self.documento.nome}"
    
    def save(self, *args, **kwargs):
        if not self.identificador:
            # Contar documentos existentes no protocolo
            count = ProtocoloDocumento.objects.filter(protocolo=self.protocolo).count() + 1
            self.identificador = f"DOC-{count:03d}"
        super().save(*args, **kwargs)


class SolicitacaoAssinatura(models.Model):
    """Solicitações de assinatura de documentos"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceita', 'Aceita'),
        ('recusada', 'Recusada'),
    ]
    
    documento = models.ForeignKey(
        ProtocoloDocumento,
        on_delete=models.CASCADE,
        related_name='solicitacoes_assinatura',
        verbose_name="Documento"
    )
    usuario_solicitante = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='solicitacoes_assinatura_enviadas',
        verbose_name="Usuário Solicitante"
    )
    usuario_destinatario = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='solicitacoes_assinatura_recebidas',
        verbose_name="Usuário Destinatário"
    )
    mensagem = models.TextField(
        blank=True,
        verbose_name="Mensagem",
        help_text="Mensagem opcional para o destinatário"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    data_resposta = models.DateTimeField(null=True, blank=True, verbose_name="Data da Resposta")
    motivo_recusa = models.TextField(
        blank=True,
        verbose_name="Motivo da Recusa",
        help_text="Obrigatório em caso de recusa"
    )
    
    class Meta:
        verbose_name = "Solicitação de Assinatura"
        verbose_name_plural = "Solicitações de Assinatura"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Assinatura para {self.usuario_destinatario.nome_completo_rp} - {self.documento.protocolo.numero_protocolo}"


class ProtocoloEncaminhamento(models.Model):
    """Histórico de encaminhamentos do protocolo"""
    
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name='encaminhamentos',
        verbose_name="Protocolo"
    )
    parecer = models.TextField(verbose_name="Parecer")
    data_encaminhamento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Encaminhamento")
    
    # Destino do encaminhamento
    entidade_destino = models.ForeignKey(
        'Entidade',
        on_delete=models.CASCADE,
        related_name='encaminhamentos_recebidos',
        verbose_name="Entidade de Destino",
        null=True,
        blank=True
    )
    orgao_destino = models.ForeignKey(
        'Orgao',
        on_delete=models.CASCADE,
        related_name='encaminhamentos_recebidos',
        verbose_name="Órgão de Destino"
    )
    usuario_destino = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encaminhamentos_recebidos',
        verbose_name="Usuário Destinatário"
    )
    
    # Origem do encaminhamento
    entidade_origem = models.ForeignKey(
        'Entidade',
        on_delete=models.CASCADE,
        related_name='encaminhamentos_enviados',
        verbose_name="Entidade de Origem",
        null=True,
        blank=True
    )
    orgao_origem = models.ForeignKey(
        'Orgao',
        on_delete=models.CASCADE,
        related_name='encaminhamentos_enviados',
        verbose_name="Órgão de Origem"
    )
    usuario_origem = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Usuário que Encaminhou"
    )
    
    class Meta:
        verbose_name = "Encaminhamento de Protocolo"
        verbose_name_plural = "Encaminhamentos de Protocolo"
        ordering = ['-data_encaminhamento']
    
    def __str__(self):
        return f"Encaminhamento {self.protocolo.numero_protocolo} - {self.data_encaminhamento.strftime('%d/%m/%Y')}"


class ProtocoloInteressado(models.Model):
    """Interessados no protocolo"""
    
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name='interessados',
        verbose_name="Protocolo"
    )
    usuario = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Usuário Interessado"
    )
    orgao = models.ForeignKey(
        'Orgao',
        on_delete=models.CASCADE,
        verbose_name="Órgão do Interessado"
    )
    entidade = models.ForeignKey(
        'Entidade',
        on_delete=models.CASCADE,
        verbose_name="Setor do Interessado"
    )
    data_inclusao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Inclusão")
    
    class Meta:
        verbose_name = "Interessado no Protocolo"
        verbose_name_plural = "Interessados no Protocolo"
        unique_together = ['protocolo', 'usuario']
    
    def __str__(self):
        return f"{self.usuario.nome_completo_rp} - {self.protocolo.numero_protocolo}"


class SolicitacaoAcesso(models.Model):
    """Solicitações de acesso ao protocolo"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name='solicitacoes_acesso',
        verbose_name="Protocolo"
    )
    usuario_solicitante = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='solicitacoes_acesso_protocolo',
        verbose_name="Usuário Solicitante"
    )
    justificativa = models.TextField(verbose_name="Justificativa")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    data_resposta = models.DateTimeField(null=True, blank=True, verbose_name="Data da Resposta")
    usuario_resposta = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respostas_acesso_protocolo',
        verbose_name="Usuário que Respondeu"
    )
    observacoes_resposta = models.TextField(blank=True, verbose_name="Observações da Resposta")
    
    class Meta:
        verbose_name = "Solicitação de Acesso ao Protocolo"
        verbose_name_plural = "Solicitações de Acesso ao Protocolo"
        unique_together = ['protocolo', 'usuario_solicitante']
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação de {self.usuario_solicitante.nome_completo_rp} - {self.protocolo.numero_protocolo}"



