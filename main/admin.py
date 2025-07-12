from django.contrib import admin
from .models import (
    ConfiguracaoSite, ConfiguracaoDiarioOficial, Noticia, NoticiaLike, NoticiaComentario, Poder, Orgao, Entidade, 
    Cargo, Profile, HistoricoCargo,
    BotaoConfiguravel, EstatisticaSistema,
    Anuncio,
    DiarioOficial, PublicacaoDiarioOficial,
    ConfiguracaoCidadania, AssinaturaDocumento
)
from django.utils import timezone
import pytz


@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    list_display = ['nome_site', 'cor_primaria', 'cor_secundaria']
    search_fields = ['nome_site', 'rodape_texto']


@admin.register(ConfiguracaoDiarioOficial)
class ConfiguracaoDiarioOficialAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'titulo_diario', 'texto_logo_esquerda', 'texto_logo_direita']
    
    fieldsets = (
        ('Logos do Cabeçalho', {
            'fields': (
                ('logo_esquerda', 'texto_logo_esquerda'),
                ('logo_direita', 'texto_logo_direita')
            ),
            'description': 'Configure as logos que aparecem ao lado do título do Diário Oficial. Se não houver imagem, será usado o texto.'
        }),
        ('Textos do Cabeçalho', {
            'fields': ('titulo_diario', 'subtitulo_diario'),
            'description': 'Configure os textos principais do cabeçalho do Diário Oficial.'
        }),
    )
    
    def has_add_permission(self, request):
        # Permite apenas uma configuração
        return not self.model.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permite deletar a configuração
        return False


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'orgao_publicacao', 'data_publicacao', 'publicado', 'destaque']
    list_filter = ['publicado', 'destaque', 'tipo', 'data_publicacao', 'autor', 'orgao_publicacao']
    search_fields = ['titulo', 'resumo', 'conteudo', 'orgao_publicacao']
    date_hierarchy = 'data_publicacao'
    ordering = ['-data_publicacao']
    readonly_fields = ['orgao_publicacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'slug', 'resumo', 'autor')
        }),
        ('Conteúdo', {
            'fields': ('conteudo', 'imagem_principal')
        }),
        ('Configurações', {
            'fields': ('tipo', 'status', 'publicado', 'destaque', 'permitir_comentarios')
        }),
        ('Metadados de Publicação', {
            'fields': ('orgao_publicacao', 'data_publicacao', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',),
            'description': 'O órgão é capturado automaticamente no momento da publicação e não pode ser alterado.'
        }),
        ('Fonte e Tags', {
            'fields': ('fonte', 'link_fonte', 'tags', 'categorias'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Poder)
class PoderAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    ordering = ['nome']


@admin.register(Orgao)
class OrgaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'poder', 'ativo', 'has_logo']
    list_filter = ['poder', 'ativo']
    search_fields = ['nome', 'poder__nome', 'descricao']
    ordering = ['poder__nome', 'nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'poder', 'ativo')
        }),
        ('Identidade Visual', {
            'fields': ('logo', 'descricao'),
            'description': 'Configure a logo e descrição do órgão. A logo será exibida nas notícias da imprensa.'
        }),
        ('Informações Adicionais', {
            'fields': ('site_oficial',),
            'classes': ('collapse',)
        }),
    )
    
    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Possui Logo'


@admin.register(Entidade)
class EntidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'orgao', 'get_poder']
    list_filter = ['orgao__poder', 'orgao']
    search_fields = ['nome', 'orgao__nome', 'orgao__poder__nome']
    ordering = ['orgao__poder__nome', 'orgao__nome', 'nome']
    
    def get_poder(self, obj):
        return obj.orgao.poder.nome
    get_poder.short_description = 'Poder'
    get_poder.admin_order_field = 'orgao__poder__nome'


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'entidade', 'get_orgao', 'get_poder', 'simbolo_gestao', 'get_simbolo_icon']
    list_filter = ['simbolo_gestao', 'entidade__orgao__poder', 'entidade__orgao']
    search_fields = ['nome', 'entidade__nome', 'entidade__orgao__nome', 'entidade__orgao__poder__nome']
    ordering = ['entidade__orgao__poder__nome', 'entidade__orgao__nome', 'entidade__nome', 'nome']
    
    def get_orgao(self, obj):
        return obj.entidade.orgao.nome
    get_orgao.short_description = 'Órgão'
    get_orgao.admin_order_field = 'entidade__orgao__nome'
    
    def get_poder(self, obj):
        return obj.entidade.orgao.poder.nome
    get_poder.short_description = 'Poder'
    get_poder.admin_order_field = 'entidade__orgao__poder__nome'
    
    def get_simbolo_icon(self, obj):
        return obj.get_simbolo_display_icon()
    get_simbolo_icon.short_description = 'Ícone'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_nome_completo', 'cargo_atual', 'get_cargo_poder']
    list_filter = ['cargo_atual__simbolo_gestao', 'cargo_atual__entidade__orgao__poder']
    search_fields = ['user__nome_completo_rp', 'user__username', 'cargo_atual__nome']
    ordering = ['user__nome_completo_rp']
    
    def get_nome_completo(self, obj):
        return obj.user.nome_completo_rp
    get_nome_completo.short_description = 'Nome Completo'
    get_nome_completo.admin_order_field = 'user__nome_completo_rp'
    
    def get_cargo_poder(self, obj):
        if obj.cargo_atual:
            return obj.cargo_atual.entidade.orgao.poder.nome
        return '-'
    get_cargo_poder.short_description = 'Poder'


@admin.register(HistoricoCargo)
class HistoricoCargoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'get_nome_completo', 'cargo', 'data_inicio', 'data_fim', 'is_atual', 'nomeado_por']
    list_filter = ['data_inicio', 'data_fim', 'cargo__simbolo_gestao', 'cargo__entidade__orgao__poder']
    search_fields = ['usuario__nome_completo_rp', 'usuario__username', 'cargo__nome']
    date_hierarchy = 'data_inicio'
    ordering = ['-data_inicio']
    readonly_fields = ['data_inicio']
    
    def get_nome_completo(self, obj):
        return obj.usuario.nome_completo_rp
    get_nome_completo.short_description = 'Nome Completo'
    get_nome_completo.admin_order_field = 'usuario__nome_completo_rp'
    
    def is_atual(self, obj):
        return obj.is_atual
    is_atual.boolean = True
    is_atual.short_description = 'Cargo Atual'


@admin.register(DiarioOficial)
class DiarioOficialAdmin(admin.ModelAdmin):
    list_display = ['numero', 'data_publicacao', 'ano', 'total_publicacoes', 'criado_em']
    list_filter = ['ano', 'data_publicacao']
    search_fields = ['numero']
    readonly_fields = ['numero', 'criado_em', 'atualizado_em']
    ordering = ['-numero']
    
    def total_publicacoes(self, obj):
        return obj.publicacoes.count()
    total_publicacoes.short_description = 'Total de Publicações'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.numero = DiarioOficial.get_proximo_numero()
        super().save_model(request, obj, form, change)


@admin.register(PublicacaoDiarioOficial)
class PublicacaoDiarioOficialAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'secao', 'diario', 'automatica', 'criado_por', 'criado_em']
    list_filter = ['tipo', 'secao', 'automatica', 'diario__ano', 'criado_em']
    search_fields = ['titulo', 'conteudo']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['-criado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('diario', 'tipo', 'secao', 'titulo')
        }),
        ('Conteúdo', {
            'fields': ('conteudo',)
        }),
        ('Metadados', {
            'fields': ('automatica', 'historico_cargo', 'criado_por', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.criado_por = request.user
            if not obj.diario_id:
                # Cria ou obtém o diário oficial do dia
                diario, created = DiarioOficial.objects.get_or_create(
                    data_publicacao=timezone.now().astimezone(pytz.timezone('America/Sao_Paulo')).date(),
                    defaults={'numero': DiarioOficial.get_proximo_numero()}
                )
                obj.diario = diario
        super().save_model(request, obj, form, change)


@admin.register(NoticiaComentario)
class NoticiaComentarioAdmin(admin.ModelAdmin):
    list_display = ['noticia', 'autor', 'get_texto_resumo', 'data_criacao', 'ativo']
    list_filter = ['ativo', 'data_criacao', 'noticia__tipo']
    search_fields = ['conteudo', 'autor__username', 'autor__nome_completo_rp', 'noticia__titulo']
    date_hierarchy = 'data_criacao'
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao']
    
    def get_texto_resumo(self, obj):
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
    get_texto_resumo.short_description = 'Comentário'
    
    actions = ['ativar_comentarios', 'desativar_comentarios']
    
    def ativar_comentarios(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, f'{queryset.count()} comentários ativados.')
    ativar_comentarios.short_description = 'Ativar comentários selecionados'
    
    def desativar_comentarios(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, f'{queryset.count()} comentários desativados.')
    desativar_comentarios.short_description = 'Desativar comentários selecionados'


@admin.register(NoticiaLike)
class NoticiaLikeAdmin(admin.ModelAdmin):
    list_display = ['noticia', 'usuario', 'get_usuario_nome', 'data_criacao']
    list_filter = ['data_criacao', 'noticia__tipo']
    search_fields = ['usuario__username', 'usuario__nome_completo_rp', 'noticia__titulo']
    date_hierarchy = 'data_criacao'
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao']
    
    def get_usuario_nome(self, obj):
        return obj.usuario.nome_completo_rp or obj.usuario.username
    get_usuario_nome.short_description = 'Nome do Usuário'
    get_usuario_nome.admin_order_field = 'usuario__nome_completo_rp'


@admin.register(ConfiguracaoCidadania)
class ConfiguracaoCidadaniaAdmin(admin.ModelAdmin):
    list_display = ['id', 'orgao_responsavel', 'ativo', 'prazo_analise_dias', 'data_atualizacao']
    list_filter = ['ativo', 'orgao_responsavel']
    search_fields = ['orgao_responsavel__nome']
    filter_horizontal = ['cargos_autorizados']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Configurações Básicas', {
            'fields': ('ativo', 'prazo_analise_dias', 'instrucoes', 'documentos_obrigatorios')
        }),
        ('Responsabilidade', {
            'fields': ('orgao_responsavel', 'cargos_autorizados')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Permitir apenas uma configuração
        return not ConfiguracaoCidadania.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar a configuração
        return False


@admin.register(AssinaturaDocumento)
class AssinaturaDocumentoAdmin(admin.ModelAdmin):
    list_display = ['documento', 'usuario', 'get_nome_completo', 'data_assinatura', 'ativa', 'cargo_assinante', 'validar_assinatura']
    list_filter = ['ativa', 'data_assinatura', 'cargo_assinante']
    search_fields = ['documento__nome', 'usuario__nome_completo_rp', 'usuario__username', 'cargo_assinante']
    date_hierarchy = 'data_assinatura'
    ordering = ['-data_assinatura']
    readonly_fields = ['data_assinatura', 'hash_documento']
    
    fieldsets = (
        ('Informações da Assinatura', {
            'fields': ('documento', 'usuario', 'data_assinatura', 'ativa')
        }),
        ('Detalhes do Assinante', {
            'fields': ('cargo_assinante', 'observacoes')
        }),
        ('Validação', {
            'fields': ('hash_documento',),
            'classes': ('collapse',),
            'description': 'Hash usado para validar a integridade da assinatura'
        }),
    )
    
    def get_nome_completo(self, obj):
        return obj.usuario.nome_completo_rp
    get_nome_completo.short_description = 'Nome Completo'
    get_nome_completo.admin_order_field = 'usuario__nome_completo_rp'
    
    def validar_assinatura(self, obj):
        return obj.validar_assinatura()
    validar_assinatura.boolean = True
    validar_assinatura.short_description = 'Válida'
