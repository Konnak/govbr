from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Autenticação
    path('api/registro/step1/', views.registro_step1, name='registro_step1'),
    path('api/registro/step2/', views.registro_step2, name='registro_step2'),
    path('api/registro/step3/', views.registro_step3, name='registro_step3'),
    path('api/verificar-codigo/', views.verificar_codigo_roblox, name='verificar_codigo'),
    path('api/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    path('api/alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('api/solicitar-alteracao-nome/', views.solicitar_alteracao_nome, name='solicitar_alteracao_nome'),
    path('api/solicitar-cidadania/', views.solicitar_cidadania, name='solicitar_cidadania'),
    
    # Discord OAuth
    path('api/iniciar-vinculacao-discord/', views.iniciar_vinculacao_discord, name='iniciar_vinculacao_discord'),
    path('discord/callback/', views.discord_callback, name='discord_callback'),
    path('api/desvincular-discord/', views.desvincular_discord, name='desvincular_discord'),
    
    # AJAX para admin - seleção hierárquica de cargos
    path('admin/ajax/orgaos/', views.ajax_orgaos, name='ajax_orgaos'),
    path('admin/ajax/entidades/', views.ajax_entidades, name='ajax_entidades'),
    path('admin/ajax/cargos/', views.ajax_cargos, name='ajax_cargos'),
    
    # Compatibilidade (será removida)
    path('api/vincular-discord/', views.vincular_discord, name='vincular_discord'),
] 