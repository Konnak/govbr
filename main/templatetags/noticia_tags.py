from django import template

register = template.Library()

@register.filter
def pode_editar(noticia, user):
    """
    Template filter para verificar se o usuário pode editar a notícia
    Uso: {{ noticia|pode_editar:user }}
    """
    if not user.is_authenticated:
        return False
    return noticia.pode_editar(user)

@register.filter  
def pode_publicar(noticia, user):
    """
    Template filter para verificar se o usuário pode publicar a notícia
    Uso: {{ noticia|pode_publicar:user }}
    """
    if not user.is_authenticated:
        return False
    return noticia.pode_publicar(user) 