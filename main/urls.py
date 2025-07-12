from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
    
    # Estrutura do governo
    path('estrutura-governo/', views.estrutura_governo, name='estrutura_governo'),
    
    # Portal da Transparência
    path('portal-transparencia/', views.portal_transparencia, name='portal_transparencia'),
    path('api/portal-transparencia/estatisticas/', views.api_portal_transparencia_estatisticas, name='api_portal_transparencia_estatisticas'),
    path('api/portal-transparencia/orgaos/<int:poder_id>/', views.api_portal_transparencia_orgaos, name='api_portal_transparencia_orgaos'),
    path('api/portal-transparencia/entidades/<int:orgao_id>/', views.api_portal_transparencia_entidades, name='api_portal_transparencia_entidades'),
    path('api/portal-transparencia/cargos/<int:entidade_id>/', views.api_portal_transparencia_cargos, name='api_portal_transparencia_cargos'),
    path('api/portal-transparencia/buscar/', views.api_portal_transparencia_buscar, name='api_portal_transparencia_buscar'),
    path('api/portal-transparencia/exportar/', views.api_portal_transparencia_exportar, name='api_portal_transparencia_exportar'),
    
    # Gestão de cargos
    path('painel-gestao-cargos/', views.painel_gestao_cargos, name='painel_gestao_cargos'),
    path('api/nomear-usuario/', views.nomear_usuario, name='nomear_usuario'),
    path('api/exonerar-usuario/', views.exonerar_usuario, name='exonerar_usuario'),
    path('painel-gestao-cargos/promover/', views.promover_usuario, name='promover_usuario'),
    path('api/cargos-por-entidade/<int:entidade_id>/', views.api_cargos_por_entidade, name='api_cargos_por_entidade'),
    path('api/cargos-disponiveis/', views.cargos_disponiveis, name='cargos_disponiveis'),
    
    # Perfil público
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
    path('servidor-historico-detalhado/<str:username>/', views.servidor_historico_detalhado, name='servidor_historico_detalhado'),
    
    # Diário Oficial
    path('diario-oficial/', views.diario_oficial_lista, name='diario_oficial_lista'),
    path('diario-oficial/buscar/', views.diario_oficial_buscar, name='diario_oficial_buscar'),
    path('diario-oficial/criar-publicacao/', views.diario_oficial_criar_publicacao, name='diario_oficial_criar_publicacao'),
    path('diario-oficial/<int:numero>/', views.diario_oficial_detalhe, name='diario_oficial_detalhe'),
    path('diario-oficial/<int:numero>/pdf/', views.diario_oficial_pdf, name='diario_oficial_pdf'),
    
    # URLs de Notícias
    path('noticias/', views.noticia_lista, name='noticia_lista'),
    path('noticias/criar/', views.noticia_criar, name='noticia_criar'),
    path('noticias/<slug:slug>/', views.noticia_detalhe, name='noticia_detalhe'),
    path('noticias/<slug:slug>/editar/', views.noticia_editar, name='noticia_editar'),
    path('noticias/<slug:slug>/comentar/', views.noticia_comentar, name='noticia_comentar'),
    path('noticias/<slug:slug>/moderar/', views.noticia_moderar, name='noticia_moderar'),
    
    # APIs de Notícias
    path('api/noticia/<int:noticia_id>/like/', views.api_noticia_like, name='api_noticia_like'),
    path('api/noticia/<int:noticia_id>/like-status/', views.api_noticia_like_status, name='api_noticia_like_status'),
    path('api/noticia/<int:noticia_id>/view/', views.api_noticia_view, name='api_noticia_view'),
    
    # Sistema de Cidadania
    path('gestao-cidadania/', views.gestao_cidadania, name='gestao_cidadania'),
    path('gestao-cidadania/configurar/', views.configurar_cidadania, name='configurar_cidadania'),
    path('api/cidadania/aprovar/<int:solicitacao_id>/', views.aprovar_cidadania, name='aprovar_cidadania'),
    path('api/cidadania/rejeitar/<int:solicitacao_id>/', views.rejeitar_cidadania, name='rejeitar_cidadania'),
    
    # API de Upload
    path('api/upload-imagem/', views.api_upload_imagem, name='api_upload_imagem'),
    
    # API Utilitárias
    path('api/clear-messages/', views.clear_messages, name='clear_messages'),
    
    # ===== URLS DO SISTEMA DE PROTOCOLOS =====
    path('protocolos/', views.protocolos_home, name='protocolos_home'),
    path('protocolos/criar/', views.protocolo_criar, name='protocolo_criar'),
    path('protocolos/consultar/', views.protocolo_consultar, name='protocolo_consultar'),
    path('protocolos/<str:numero_protocolo>/', views.protocolo_detalhe, name='protocolo_detalhe'),
    
    # APIs para protocolos
    path('api/protocolos/entidades/<int:orgao_id>/', views.api_entidades_por_orgao_protocolo, name='api_entidades_por_orgao_protocolo'),
    path('api/protocolos/usuarios/<int:entidade_id>/', views.api_usuarios_por_entidade_protocolo, name='api_usuarios_por_entidade_protocolo'),
    path('api/protocolos/buscar-usuarios/', views.api_buscar_usuarios_protocolo, name='api_buscar_usuarios_protocolo'),
    
    # Funcionalidades do protocolo
    path('protocolos/<str:numero_protocolo>/upload-documento/', views.protocolo_upload_documento, name='protocolo_upload_documento'),
    path('protocolos/<str:numero_protocolo>/adicionar-interessado/', views.protocolo_adicionar_interessado, name='protocolo_adicionar_interessado'),
    path('protocolos/<str:numero_protocolo>/encaminhar/', views.protocolo_encaminhar, name='protocolo_encaminhar'),
    path('protocolos/<str:numero_protocolo>/solicitar-assinatura/', views.protocolo_solicitar_assinatura, name='protocolo_solicitar_assinatura'),
    path('protocolos/<str:numero_protocolo>/assinar-documento/<int:documento_id>/', views.protocolo_assinar_documento, name='protocolo_assinar_documento'),
    path('protocolos/<str:numero_protocolo>/rejeitar-assinatura/<int:documento_id>/', views.protocolo_rejeitar_assinatura, name='protocolo_rejeitar_assinatura'),
    path('protocolos/<str:numero_protocolo>/parar-monitorar/', views.protocolo_parar_monitorar, name='protocolo_parar_monitorar'),
    path('protocolos/<str:numero_protocolo>/remover-interessado/<int:interessado_id>/', views.protocolo_remover_interessado, name='protocolo_remover_interessado'),
    path('protocolos/<str:numero_protocolo>/excluir-documento/<int:documento_id>/', views.protocolo_excluir_documento, name='protocolo_excluir_documento'),
    # Múltiplas assinaturas
    path('protocolos/<str:numero_protocolo>/listar-assinaturas/<int:documento_id>/', views.protocolo_listar_assinaturas, name='protocolo_listar_assinaturas'),
    path('protocolos/<str:numero_protocolo>/documento-consolidado/', views.protocolo_documento_consolidado, name='protocolo_documento_consolidado'),
    path('protocolos/<str:numero_protocolo>/documento-consolidado/pdf/', views.protocolo_documento_consolidado_pdf, name='protocolo_documento_consolidado_pdf'),
] 