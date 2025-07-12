from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

# Importar shared_task apenas se Celery estiver configurado
try:
    from celery import shared_task
    CELERY_ENABLED = hasattr(settings, 'CELERY_BROKER_URL') and settings.CELERY_BROKER_URL
except ImportError:
    CELERY_ENABLED = False
    def shared_task(func):
        return func

def atualizar_cache_noticias():
    """
    Atualiza o cache das notícias mais recentes
    """
    from .models import Noticia
    noticias = Noticia.objects.filter(
        publicado=True,
        data_publicacao__lte=timezone.now()
    ).order_by('-data_publicacao')[:10]
    
    cache.set('noticias_recentes', list(noticias), timeout=60*15)
    return 'Cache de notícias atualizado'

def limpar_comentarios_antigos():
    """
    Remove comentários mais antigos que 30 dias
    """
    from .models import NoticiaComentario
    data_limite = timezone.now() - timezone.timedelta(days=30)
    comentarios = NoticiaComentario.objects.filter(
        data_criacao__lt=data_limite
    )
    total = comentarios.count()
    comentarios.delete()
    return f'{total} comentários antigos removidos'

def notificar_novos_comentarios(noticia_id):
    """
    Notifica sobre novos comentários em uma notícia
    """
    from .models import Noticia
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        # Aqui você pode implementar a lógica de notificação
        # Por exemplo, enviar e-mail, notificação push, etc.
        return f'Notificações enviadas para a notícia {noticia.titulo}'
    except Noticia.DoesNotExist:
        return f'Notícia {noticia_id} não encontrada'

# Versões assíncronas se Celery estiver habilitado
if CELERY_ENABLED:
    atualizar_cache_noticias = shared_task(atualizar_cache_noticias)
    limpar_comentarios_antigos = shared_task(limpar_comentarios_antigos)
    notificar_novos_comentarios = shared_task(notificar_novos_comentarios) 