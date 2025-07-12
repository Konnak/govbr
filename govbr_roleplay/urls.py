"""
URL configuration for govbr_roleplay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
import os

def service_worker_view(request):
    """Serve o Service Worker"""
    content = """
/**
 * Service Worker para GovBR Roleplay
 */
const CACHE_NAME = 'govbr-roleplay-v1';

self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker ativado');
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
    // Deixar o navegador lidar com as requisições normalmente
    return;
});
"""
    response = HttpResponse(content, content_type='application/javascript')
    response['Cache-Control'] = 'no-cache'
    return response

def favicon_view(request):
    """Serve um favicon simples"""
    return HttpResponse('', content_type='image/x-icon', status=204)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('usuarios/', include('users.urls')),
    path('sw.js', service_worker_view, name='service_worker'),
    path('favicon.ico', favicon_view, name='favicon'),
]

# Configuração para servir arquivos de media e static durante desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuração do painel administrativo
admin.site.site_header = "GovBR Roleplay - Painel Administrativo"
admin.site.site_title = "GovBR Admin"
admin.site.index_title = "Bem-vindo ao Painel Administrativo"
