from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import string

class User(AbstractUser):
    """Modelo de usuário personalizado"""
    
    NIVEL_CHOICES = [
        ('imigrante', 'Imigrante'),
        ('cidadao', 'Cidadão'),
        ('moderador', 'Moderador'),
        ('administrador', 'Administrador'),
        ('coordenador', 'Coordenador'),
        ('fundador', 'Fundador'),
    ]
    
    # Campos obrigatórios
    nome_completo_rp = models.CharField(max_length=100, verbose_name="Nome Completo (RP)")
    roblox_id = models.BigIntegerField(unique=True, verbose_name="ID do Roblox")
    roblox_username = models.CharField(max_length=50, blank=True, verbose_name="Username do Roblox")
    
    # Níveis de acesso
    nivel_acesso = models.CharField(
        max_length=20, 
        choices=NIVEL_CHOICES, 
        default='imigrante',
        verbose_name="Nível de Acesso"
    )
    
    # Verificação
    verificado = models.BooleanField(default=False, verbose_name="Conta Verificada")
    codigo_verificacao = models.CharField(max_length=10, blank=True, verbose_name="Código de Verificação")
    data_verificacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Verificação")
    
    # Discord
    discord_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name="ID do Discord")
    discord_username = models.CharField(max_length=50, blank=True, verbose_name="Username do Discord")
    discord_display_name = models.CharField(max_length=100, blank=True, verbose_name="Nome de Exibição do Discord")
    discord_avatar = models.CharField(max_length=100, blank=True, verbose_name="Avatar Hash do Discord")
    discord_email = models.EmailField(blank=True, verbose_name="Email do Discord")
    discord_access_token = models.TextField(blank=True, verbose_name="Token de Acesso Discord")
    discord_refresh_token = models.TextField(blank=True, verbose_name="Token de Refresh Discord")
    discord_vinculado = models.BooleanField(default=False, verbose_name="Discord Vinculado")
    discord_data_vinculacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Vinculação Discord")
    
    # Dados adicionais
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    biografia = models.TextField(blank=True, verbose_name="Biografia")
    avatar_url = models.URLField(blank=True, verbose_name="URL do Avatar")
    
    # Controle
    data_ultimo_login = models.DateTimeField(null=True, blank=True, verbose_name="Último Login")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.nome_completo_rp} (@{self.username})"
    
    def gerar_codigo_verificacao(self):
        """Gera um código de verificação único"""
        self.codigo_verificacao = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.save()
        return self.codigo_verificacao
    
    def verificar_conta(self):
        """Marca a conta como verificada"""
        self.verificado = True
        self.data_verificacao = timezone.now()
        self.codigo_verificacao = ''
        self.save()
    
    def pode_aprovar_cidadania(self):
        """Verifica se o usuário pode aprovar cidadania"""
        return self.nivel_acesso in ['administrador', 'coordenador', 'fundador']
    
    @property
    def is_cidadao(self):
        """Verifica se o usuário é cidadão brasileiro"""
        return self.nivel_acesso in ['cidadao', 'moderador', 'administrador', 'coordenador', 'fundador']
    
    def get_nivel_display_color(self):
        """Retorna a cor do nível de acesso"""
        colors = {
            'imigrante': '#6c757d',
            'cidadao': '#28a745',
            'moderador': '#17a2b8',
            'administrador': '#ffc107',
            'coordenador': '#fd7e14',
            'fundador': '#dc3545',
        }
        return colors.get(self.nivel_acesso, '#6c757d')
    
    def get_discord_avatar_url(self, size=128):
        """Retorna a URL do avatar do Discord"""
        if self.discord_avatar and self.discord_id:
            return f"https://cdn.discordapp.com/avatars/{self.discord_id}/{self.discord_avatar}.png?size={size}"
        return f"https://cdn.discordapp.com/embed/avatars/{(int(self.discord_id) >> 22) % 6 if self.discord_id else 0}.png"
    
    def get_discord_avatar_small(self):
        """Retorna a URL do avatar do Discord em tamanho pequeno (64px)"""
        return self.get_discord_avatar_url(64)
    
    def get_discord_avatar_medium(self):
        """Retorna a URL do avatar do Discord em tamanho médio (128px)"""
        return self.get_discord_avatar_url(128)
    
    def get_discord_avatar_large(self):
        """Retorna a URL do avatar do Discord em tamanho grande (256px)"""
        return self.get_discord_avatar_url(256)
    
    def vincular_discord(self, discord_data):
        """Vincula os dados do Discord ao usuário"""
        self.discord_id = discord_data.get('id')
        self.discord_username = discord_data.get('username')
        self.discord_display_name = discord_data.get('global_name') or discord_data.get('display_name', '')
        self.discord_avatar = discord_data.get('avatar', '')
        self.discord_email = discord_data.get('email', '')
        self.discord_vinculado = True
        self.discord_data_vinculacao = timezone.now()
        self.save()
    
    def desvincular_discord(self):
        """Remove a vinculação do Discord"""
        self.discord_id = None
        self.discord_username = ''
        self.discord_display_name = ''
        self.discord_avatar = ''
        self.discord_email = ''
        self.discord_access_token = ''
        self.discord_refresh_token = ''
        self.discord_vinculado = False
        self.discord_data_vinculacao = None
        self.save()

    def get_roblox_description(self):
        """Retorna a descrição do perfil do Roblox"""
        try:
            from .views import get_roblox_user_info
            roblox_data = get_roblox_user_info(self.roblox_id)
            if roblox_data and roblox_data.get('description'):
                return roblox_data['description']
        except Exception as e:
            print(f"Erro ao obter descrição do Roblox: {e}")
        return None

    def get_roblox_avatar_url(self):
        """Retorna a URL do avatar do Roblox"""
        try:
            from .views import get_roblox_user_info
            roblox_data = get_roblox_user_info(self.roblox_id, size="48x48")
            if roblox_data and roblox_data.get('avatar_url'):
                return roblox_data['avatar_url']
        except Exception as e:
            print(f"Erro ao obter avatar do Roblox: {e}")
        
        # Se não conseguir obter o avatar do Roblox, retorna o avatar padrão
        return '/static/images/default-avatar.svg'

    def get_avatar_url(self):
        """Retorna a URL do avatar do usuário (Roblox ou Discord)"""
        # Se tiver um avatar personalizado salvo, retorna ele
        if self.avatar_url:
            return self.avatar_url
        
        # Se tiver Discord vinculado, tenta usar o avatar do Discord
        if self.discord_vinculado and self.discord_avatar:
            return self.get_discord_avatar_url()
        
        # Tenta obter o avatar do Roblox
        return self.get_roblox_avatar_url()


class SolicitacaoAlteracaoNome(models.Model):
    """Solicitações de alteração de nome"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    nome_atual = models.CharField(max_length=100, verbose_name="Nome Atual")
    nome_solicitado = models.CharField(max_length=100, verbose_name="Nome Solicitado")
    motivo = models.TextField(verbose_name="Motivo da Alteração")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    data_resposta = models.DateTimeField(null=True, blank=True, verbose_name="Data da Resposta")
    
    aprovado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='aprovacoes_nome',
        verbose_name="Aprovado Por"
    )
    observacoes_staff = models.TextField(blank=True, verbose_name="Observações do Staff")
    
    class Meta:
        verbose_name = "Solicitação de Alteração de Nome"
        verbose_name_plural = "Solicitações de Alteração de Nome"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"{self.usuario.nome_completo_rp} -> {self.nome_solicitado}"


class SolicitacaoCidadania(models.Model):
    """Solicitações de cidadania brasileira"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('documentos_pendentes', 'Documentos Pendentes'),
    ]
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='solicitacoes_cidadania',
        verbose_name="Usuário"
    )
    
    # Dados pessoais
    nome_completo = models.CharField(max_length=200, blank=True, verbose_name="Nome Completo")
    nome_rp = models.CharField(max_length=100, blank=True, verbose_name="Nome no Roleplay")
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    nacionalidade_origem = models.CharField(max_length=100, blank=True, verbose_name="Nacionalidade de Origem")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    
    # Endereço
    endereco = models.CharField(max_length=300, blank=True, verbose_name="Endereço Completo")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=50, blank=True, verbose_name="Estado")
    cep = models.CharField(max_length=10, blank=True, verbose_name="CEP")
    
    # Antecedentes criminais
    possui_passagem_criminal = models.BooleanField(
        default=False,
        verbose_name="Possui Passagem Criminal",
        help_text="Marque se possui antecedentes criminais"
    )
    detalhes_criminal = models.TextField(
        blank=True,
        verbose_name="Detalhes da Passagem Criminal",
        help_text="Se possui passagem criminal, detalhe aqui"
    )
    
    # Motivo e documentos
    motivo = models.TextField(verbose_name="Motivo da Solicitação")
    documentos = models.FileField(
        upload_to='cidadania/', 
        blank=True, 
        null=True, 
        verbose_name="Documentos Anexos"
    )
    
    # Controle do processo
    numero_protocolo = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        verbose_name="Número do Protocolo",
        help_text="Número único do protocolo da solicitação"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    
    # Análise
    analisado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cidadanias_analisadas',
        verbose_name="Analisado Por"
    )
    data_analise = models.DateTimeField(null=True, blank=True, verbose_name="Data da Análise")
    observacoes_analise = models.TextField(
        blank=True,
        verbose_name="Observações da Análise",
        help_text="Observações do analista sobre a solicitação"
    )
    
    # Aprovação/Rejeição
    data_resposta = models.DateTimeField(null=True, blank=True, verbose_name="Data da Resposta")
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data da Aprovação")
    aprovado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='aprovacoes_cidadania',
        verbose_name="Aprovado Por"
    )
    observacoes_staff = models.TextField(blank=True, verbose_name="Observações do Staff")
    
    class Meta:
        verbose_name = "Solicitação de Cidadania"
        verbose_name_plural = "Solicitações de Cidadania"
        ordering = ['-data_solicitacao']
        permissions = [
            ('pode_analisar_cidadania', 'Pode analisar solicitações de cidadania'),
            ('pode_aprovar_cidadania', 'Pode aprovar solicitações de cidadania'),
            ('pode_configurar_cidadania', 'Pode configurar sistema de cidadania'),
        ]
    
    def save(self, *args, **kwargs):
        """Gerar número de protocolo único antes de salvar"""
        if not self.numero_protocolo:
            import datetime
            import random
            
            # Formato: CID-AAAAMMDDHHMM-XXX
            now = datetime.datetime.now()
            date_part = now.strftime("%Y%m%d%H%M")
            random_part = str(random.randint(100, 999))
            self.numero_protocolo = f"CID-{date_part}-{random_part}"
            
            # Verificar se já existe (muito improvável, mas por segurança)
            while SolicitacaoCidadania.objects.filter(numero_protocolo=self.numero_protocolo).exists():
                random_part = str(random.randint(100, 999))
                self.numero_protocolo = f"CID-{date_part}-{random_part}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Cidadania - {self.usuario.nome_completo_rp}"


class LogAcesso(models.Model):
    """Log de acessos dos usuários"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    user_agent = models.TextField(verbose_name="User Agent")
    data_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Data do Acesso")
    sucesso = models.BooleanField(default=True, verbose_name="Login com Sucesso")
    
    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-data_acesso']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.data_acesso}"
