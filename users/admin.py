from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django import forms
from .models import User, SolicitacaoAlteracaoNome, SolicitacaoCidadania, LogAcesso
from main.models import Profile, Poder, Orgao, Entidade, Cargo


class ProfileInlineForm(forms.ModelForm):
    """Form personalizado para o Profile inline"""
    
    class Meta:
        model = Profile
        fields = ['cargo_atual']


class ProfileInline(admin.StackedInline):
    """Inline admin para Profile"""
    model = Profile
    form = ProfileInlineForm
    can_delete = False
    verbose_name_plural = 'Cargo e Posição no Governo'
    extra = 0
    
    fieldsets = (
        ('Cargo no Governo', {
            'fields': ('cargo_atual',),
            'description': 'Selecione o cargo do usuário. Use os campos auxiliares abaixo para navegar na hierarquia.'
        }),
    )
    
    class Media:
        js = ('admin/js/profile_hierarchy.js',)
        css = {
            'all': ('admin/css/profile_hierarchy.css',)
        }
    
    def get_readonly_fields(self, request, obj=None):
        """Campos somente leitura"""
        return []
    
    def has_delete_permission(self, request, obj=None):
        """Não permitir deletar o profile"""
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'nome_completo_rp', 'roblox_username', 'get_cargo_info', 'nivel_acesso_badge', 'verificado', 'ativo', 'date_joined')
    list_filter = ('nivel_acesso', 'verificado', 'ativo', 'discord_vinculado', 'date_joined', 'profile__cargo_atual__simbolo_gestao', 'profile__cargo_atual__entidade__orgao__poder')
    search_fields = ('username', 'nome_completo_rp', 'roblox_username', 'roblox_id', 'profile__cargo_atual__nome')
    ordering = ('-date_joined',)
    
    inlines = [ProfileInline]
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {
            'fields': ('nome_completo_rp', 'first_name', 'last_name', 'email', 'data_nascimento', 'biografia')
        }),
        ('Roblox', {
            'fields': ('roblox_id', 'roblox_username', 'avatar_url')
        }),
        ('Discord', {
            'fields': ('discord_id', 'discord_username', 'discord_vinculado')
        }),
        ('Permissões', {
            'fields': ('nivel_acesso', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Verificação', {
            'fields': ('verificado', 'data_verificacao', 'codigo_verificacao')
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined', 'data_ultimo_login')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nome_completo_rp', 'roblox_id', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'data_ultimo_login', 'data_verificacao')
    
    def get_cargo_info(self, obj):
        """Exibe informações do cargo atual do usuário"""
        try:
            profile = obj.profile
            if profile.cargo_atual:
                cargo = profile.cargo_atual
                simbolo = cargo.get_simbolo_display_icon()
                return format_html(
                    '{} <strong>{}</strong><br/><small>{} - {}</small>',
                    simbolo,
                    cargo.nome,
                    cargo.entidade.nome,
                    cargo.entidade.orgao.poder.nome
                )
            return format_html('<em>Sem cargo</em>')
        except Profile.DoesNotExist:
            return format_html('<em>Perfil não encontrado</em>')
    get_cargo_info.short_description = 'Cargo Atual'
    get_cargo_info.allow_tags = True
    
    def nivel_acesso_badge(self, obj):
        color = obj.get_nivel_display_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_nivel_acesso_display()
        )
    nivel_acesso_badge.short_description = 'Nível de Acesso'


@admin.register(SolicitacaoAlteracaoNome)
class SolicitacaoAlteracaoNomeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nome_atual', 'nome_solicitado', 'status_badge', 'data_solicitacao')
    list_filter = ('status', 'data_solicitacao', 'data_resposta')
    search_fields = ('usuario__nome_completo_rp', 'nome_atual', 'nome_solicitado')
    ordering = ('-data_solicitacao',)
    
    fieldsets = (
        ('Solicitação', {
            'fields': ('usuario', 'nome_atual', 'nome_solicitado', 'motivo')
        }),
        ('Status', {
            'fields': ('status', 'data_solicitacao', 'data_resposta')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'observacoes_staff')
        }),
    )
    
    readonly_fields = ('data_solicitacao', 'nome_atual')
    
    def status_badge(self, obj):
        colors = {
            'pendente': '#ffc107',
            'aprovada': '#28a745',
            'rejeitada': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status in ['aprovada', 'rejeitada']:
                obj.aprovado_por = request.user
                obj.data_resposta = timezone.now()
                
                # Se aprovado, alterar o nome do usuário
                if obj.status == 'aprovada':
                    obj.usuario.nome_completo_rp = obj.nome_solicitado
                    obj.usuario.save()
        
        super().save_model(request, obj, form, change)


@admin.register(SolicitacaoCidadania)
class SolicitacaoCidadaniaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'status_badge', 'data_solicitacao', 'aprovado_por')
    list_filter = ('status', 'data_solicitacao', 'data_resposta')
    search_fields = ('usuario__nome_completo_rp', 'motivo')
    ordering = ('-data_solicitacao',)
    
    fieldsets = (
        ('Solicitação', {
            'fields': ('usuario', 'motivo', 'documentos')
        }),
        ('Status', {
            'fields': ('status', 'data_solicitacao', 'data_resposta')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'observacoes_staff')
        }),
    )
    
    readonly_fields = ('data_solicitacao',)
    
    def status_badge(self, obj):
        colors = {
            'pendente': '#ffc107',
            'aprovada': '#28a745',
            'rejeitada': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status in ['aprovada', 'rejeitada']:
                obj.aprovado_por = request.user
                obj.data_resposta = timezone.now()
                
                # Se aprovado, alterar nível para cidadão
                if obj.status == 'aprovada':
                    obj.usuario.nivel_acesso = 'cidadao'
                    obj.usuario.save()
        
        super().save_model(request, obj, form, change)


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ip_address', 'sucesso_badge', 'data_acesso')
    list_filter = ('sucesso', 'data_acesso')
    search_fields = ('usuario__nome_completo_rp', 'ip_address')
    ordering = ('-data_acesso',)
    
    readonly_fields = ('usuario', 'ip_address', 'user_agent', 'data_acesso', 'sucesso')
    
    def sucesso_badge(self, obj):
        color = '#28a745' if obj.sucesso else '#dc3545'
        text = 'Sucesso' if obj.sucesso else 'Falha'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            text
        )
    sucesso_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
