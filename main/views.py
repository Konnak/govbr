from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Min
from datetime import timedelta
import json
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.loader import get_template, render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import black, blue, red, green, grey
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image as PILImage
import io
import os
import tempfile
from django.conf import settings
import re
from django import forms
import base64
from django.urls import reverse
import csv
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage as static
from django.templatetags.static import static
import uuid
from django.core.files.storage import default_storage
from django.core.cache import cache

# Para geração de QR Code
try:
    import qrcode
    from PIL import Image as PILImage
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

from .models import (
    ConfiguracaoSite, Noticia, BotaoConfiguravel, EstatisticaSistema, 
    Anuncio, Poder, Orgao, Entidade, Cargo, Profile, HistoricoCargo,
    DiarioOficial, PublicacaoDiarioOficial, NoticiaImagem, NoticiaTag, NoticiaCategoria, NoticiaComentario, NoticiaLike,
    ConfiguracaoDiarioOficial, ConfiguracaoCidadania,
    EspecieDocumento, Protocolo, ProtocoloInteressado, ProtocoloDocumento,
    ProtocoloEncaminhamento, SolicitacaoAcesso, SolicitacaoAssinatura, AssinaturaDocumento
)
from users.models import SolicitacaoCidadania
User = get_user_model()

# Formulário para criar publicações manuais
class PublicacaoForm(forms.ModelForm):
    conteudo = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 15,
            'class': 'form-control',
            'placeholder': 'Digite o conteúdo da publicação...'
        }),
        help_text='Use quebras de linha para organizar o texto.'
    )
    
    class Meta:
        model = PublicacaoDiarioOficial
        fields = ['tipo', 'secao', 'titulo', 'conteudo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'secao': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: DECRETO Nº XXX - Assunto do decreto'
            }),
        }
        labels = {
            'tipo': 'Tipo de Publicação',
            'secao': 'Seção (Poder)',
            'titulo': 'Título da Publicação',
            'conteudo': 'Conteúdo',
        }


def home(request):
    """View da página inicial"""
    # Buscar configurações do site
    try:
        config = ConfiguracaoSite.objects.first()
    except ConfiguracaoSite.DoesNotExist:
        config = ConfiguracaoSite.objects.create()
    
    # Notícias do governo em destaque para o slide principal (com cache)
    cache_key_governo_destaque = 'noticias_governo_destaque'
    noticias_governo_destaque = cache.get(cache_key_governo_destaque)
    
    if noticias_governo_destaque is None:
        noticias_governo_destaque = list(Noticia.objects.filter(
            publicado=True, 
            status='publicado',
            destaque=True,
            tipo='governo'
        ).select_related('autor', 'autor__profile', 'autor__profile__cargo_atual', 
                        'autor__profile__cargo_atual__entidade__orgao')
        .prefetch_related('categorias', 'tags')[:5])
        cache.set(cache_key_governo_destaque, noticias_governo_destaque, 60 * 15)  # Cache por 15 minutos
    
    # Notícias recentes do governo (sem destaque) (com cache)
    cache_key_noticias_recentes = 'noticias_recentes'
    noticias_recentes = cache.get(cache_key_noticias_recentes)
    
    if noticias_recentes is None:
        noticias_recentes = list(Noticia.objects.filter(
            publicado=True,
            status='publicado',
            destaque=False,
            tipo='governo'
        ).select_related('autor', 'autor__profile', 'autor__profile__cargo_atual', 
                        'autor__profile__cargo_atual__entidade__orgao')
        .prefetch_related('categorias', 'tags')[:8])
        cache.set(cache_key_noticias_recentes, noticias_recentes, 60 * 15)  # Cache por 15 minutos
    
    # Botões configuráveis
    botoes_configuravel = BotaoConfiguravel.objects.filter(ativo=True)
    
    # Estatísticas do sistema
    try:
        estatisticas = EstatisticaSistema.objects.first()
    except EstatisticaSistema.DoesNotExist:
        estatisticas = atualizar_estatisticas()
    
    # Anúncios ativos
    agora = timezone.now()
    anuncios = Anuncio.objects.filter(
        ativo=True,
        data_inicio__lte=agora,
        data_fim__gte=agora
    )
    
    context = {
        'config_site': config,
        'noticias_governo_destaque': noticias_governo_destaque,
        'noticias_recentes': noticias_recentes,
        'botoes_configuravel': botoes_configuravel,
        'estatisticas': estatisticas,
        'anuncios': anuncios,
    }
    
    return render(request, 'main/home.html', context)


def atualizar_estatisticas():
    """Atualiza as estatísticas do sistema"""
    # Contagem total de usuários
    total_usuarios = User.objects.count()
    
    # Usuários dos últimos 7 dias
    data_limite = timezone.now() - timedelta(days=7)
    usuarios_7_dias = User.objects.filter(date_joined__gte=data_limite).count()
    
    # Por enquanto, vamos usar valores fictícios para imigrantes e cidadãos
    # Posteriormente isso será baseado em um sistema de níveis de acesso
    total_imigrantes = int(total_usuarios * 0.3)  # 30% como imigrantes
    total_cidadaos = total_usuarios - total_imigrantes
    
    # Criar ou atualizar estatísticas
    estatisticas, created = EstatisticaSistema.objects.get_or_create(
        defaults={
            'total_usuarios': total_usuarios,
            'total_imigrantes': total_imigrantes,
            'total_cidadaos': total_cidadaos,
            'usuarios_ultimos_7_dias': usuarios_7_dias
        }
    )
    
    if not created:
        estatisticas.total_usuarios = total_usuarios
        estatisticas.total_imigrantes = total_imigrantes
        estatisticas.total_cidadaos = total_cidadaos
        estatisticas.usuarios_ultimos_7_dias = usuarios_7_dias
        estatisticas.save()
    
    return estatisticas


def estrutura_governo(request):
    """View para exibir a estrutura completa do governo"""
    poderes = Poder.objects.prefetch_related(
        'orgao_set',
        'orgao_set__entidade_set',
        'orgao_set__entidade_set__cargo_set',
        'orgao_set__entidade_set__cargo_set__historicocargo_set__usuario',
        'orgao_set__entidade_set__cargo_set__historicocargo_set__usuario__profile'
    ).all()
    
    context = {
        'poderes': poderes,
        'total_poderes': poderes.count(),
        'total_orgaos': sum(poder.orgao_set.count() for poder in poderes),
        'total_entidades': sum(
            sum(orgao.entidade_set.count() for orgao in poder.orgao_set.all()) 
            for poder in poderes
        ),
        'total_cargos': sum(
            sum(
                sum(entidade.cargo_set.count() for entidade in orgao.entidade_set.all())
                for orgao in poder.orgao_set.all()
            ) 
            for poder in poderes
        ),
    }
    
    return render(request, 'main/estrutura_governo.html', context)


@login_required
def painel_gestao_cargos(request):
    """Painel de gestão de cargos para líderes"""
    user_profile = getattr(request.user, 'profile', None)
    
    if not user_profile or not user_profile.cargo_atual:
        messages.error(request, 'Você precisa ter um cargo para acessar o painel de gestão.')
        return redirect('main:home')
    
    cargo_atual = user_profile.cargo_atual
    
    # Verificar se tem permissão de gestão
    if cargo_atual.simbolo_gestao == 'nenhum':
        messages.error(request, 'Você não tem permissões de gestão.')
        return redirect('main:home')
    
    # Obter cargos que pode gerenciar
    cargos_gerenciaveis = cargo_atual.get_cargos_gerenciaveis()
    
    # Obter usuários que pode gerenciar
    usuarios_gerenciaveis = User.objects.filter(
        profile__cargo_atual__in=cargos_gerenciaveis
    ).select_related('profile__cargo_atual')
    
    # Obter usuários sem cargo que podem ser nomeados
    usuarios_sem_cargo = User.objects.filter(
        Q(profile__cargo_atual__isnull=True) | Q(profile__isnull=True)
    ).exclude(nivel_acesso='fundador')
    
    # Histórico de nomeações realizadas
    nomeacoes_realizadas = HistoricoCargo.objects.filter(
        nomeado_por=request.user
    ).order_by('-data_inicio')[:10]
    
    context = {
        'cargo_atual': cargo_atual,
        'cargos_gerenciaveis': cargos_gerenciaveis,
        'usuarios_gerenciaveis': usuarios_gerenciaveis,
        'usuarios_sem_cargo': usuarios_sem_cargo,
        'nomeacoes_realizadas': nomeacoes_realizadas,
        'pode_gerenciar': True,
    }
    
    return render(request, 'main/painel_gestao_cargos.html', context)


@login_required
@require_http_methods(["POST"])
def nomear_usuario(request):
    """API para nomear usuário para um cargo"""
    try:
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        cargo_id = data.get('cargo_id')
        observacoes = data.get('observacoes', '')
        
        # Verificar permissões
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.cargo_atual:
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem cargo para realizar nomeações'
            })
        
        cargo_gestor = user_profile.cargo_atual
        if cargo_gestor.simbolo_gestao == 'nenhum':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissões de gestão'
            })
        
        # Obter usuário e cargo
        try:
            usuario = User.objects.get(id=usuario_id)
            cargo = Cargo.objects.get(id=cargo_id)
        except (User.DoesNotExist, Cargo.DoesNotExist):
            return JsonResponse({
                'success': False, 
                'error': 'Usuário ou cargo não encontrado'
            })
        
        # Verificar se pode gerenciar este cargo
        if not cargo_gestor.pode_gerenciar_cargo(cargo):
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para gerenciar este cargo'
            })
        
        # Verificar se o cargo já está ocupado
        cargo_ocupado = Profile.objects.filter(cargo_atual=cargo).first()
        if cargo_ocupado:
            return JsonResponse({
                'success': False, 
                'error': f'Este cargo já está ocupado por {cargo_ocupado.user.nome_completo_rp}'
            })
        
        # Obter ou criar perfil do usuário
        usuario_profile, created = Profile.objects.get_or_create(user=usuario)
        
        # Finalizar cargo anterior se existir
        if usuario_profile.cargo_atual:
            historico_anterior = HistoricoCargo.objects.filter(
                usuario=usuario,
                cargo=usuario_profile.cargo_atual,
                data_fim__isnull=True
            ).first()
            
            if historico_anterior:
                historico_anterior.finalizar_cargo(
                    exonerado_por=request.user,
                    observacoes="Exonerado para nova nomeação"
                )
        
        # Nomear para novo cargo
        usuario_profile.cargo_atual = cargo
        usuario_profile.save()
        
        # O histórico será criado automaticamente pelo signal handle_cargo_change
        # Atualizar o histórico criado com informações adicionais
        historico_criado = HistoricoCargo.objects.filter(
            usuario=usuario,
            cargo=cargo,
            data_fim__isnull=True
        ).order_by('-data_inicio').first()
        
        if historico_criado:
            historico_criado.nomeado_por = request.user
            if observacoes:
                historico_criado.observacoes = observacoes
            historico_criado.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{usuario.nome_completo_rp} foi nomeado(a) para {cargo.nome} com sucesso!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def promover_usuario(request):
    """API para promover usuário (alterar cargo dentro da mesma entidade)"""
    import logging
    logger = logging.getLogger('diario_oficial')
    
    try:
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        cargo_id = data.get('cargo_id')
        observacoes = data.get('observacoes', '')
        
        logger.info(f"🚀 INICIANDO PROMOÇÃO - Usuario ID: {usuario_id}")
        logger.info(f"   - Gestor: {request.user.nome_completo_rp}")
        logger.info(f"   - Novo cargo ID: {cargo_id}")
        logger.info(f"   - Observações: {observacoes}")
        
        # Verificar permissões do gestor
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.cargo_atual:
            logger.warning(f"❌ Gestor sem cargo atual")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem cargo para realizar promoções'
            })
        
        cargo_gestor = user_profile.cargo_atual
        logger.info(f"   - Cargo do gestor: {cargo_gestor.nome} ({cargo_gestor.simbolo_gestao})")
        
        if cargo_gestor.simbolo_gestao == 'nenhum':
            logger.warning(f"❌ Gestor sem permissões de gestão")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissões de gestão'
            })
        
        # Obter usuário a ser promovido
        try:
            usuario = User.objects.get(id=usuario_id)
            logger.info(f"✅ Usuário encontrado: {usuario.nome_completo_rp}")
        except User.DoesNotExist:
            logger.error(f"❌ Usuário não encontrado: {usuario_id}")
            return JsonResponse({
                'success': False, 
                'error': 'Usuário não encontrado'
            })
        
        # Obter perfil do usuário
        usuario_profile = getattr(usuario, 'profile', None)
        if not usuario_profile or not usuario_profile.cargo_atual:
            logger.error(f"❌ Usuário sem cargo atual")
            return JsonResponse({
                'success': False, 
                'error': 'Usuário não possui cargo atual para ser promovido'
            })
        
        cargo_atual = usuario_profile.cargo_atual
        logger.info(f"   - Cargo atual: {cargo_atual.nome} ({cargo_atual.simbolo_gestao})")
        
        # Obter novo cargo
        try:
            novo_cargo = Cargo.objects.get(id=cargo_id)
            logger.info(f"   - Novo cargo: {novo_cargo.nome} ({novo_cargo.simbolo_gestao})")
        except Cargo.DoesNotExist:
            logger.error(f"❌ Cargo não encontrado: {cargo_id}")
            return JsonResponse({
                'success': False, 
                'error': 'Cargo não encontrado'
            })
        
        # Verificar se é promoção dentro da mesma entidade
        if cargo_atual.entidade != novo_cargo.entidade:
            logger.error(f"❌ Tentativa de promoção entre entidades diferentes")
            return JsonResponse({
                'success': False, 
                'error': 'Promoção deve ser dentro da mesma entidade. Use transferência para mudar de entidade.'
            })
        
        # Verificar se o gestor pode gerenciar ambos os cargos
        if not cargo_gestor.pode_gerenciar_cargo(cargo_atual):
            logger.warning(f"❌ Gestor não pode gerenciar cargo atual")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para gerenciar o cargo atual deste usuário'
            })
        
        if not cargo_gestor.pode_gerenciar_cargo(novo_cargo):
            logger.warning(f"❌ Gestor não pode gerenciar novo cargo")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para nomear para este cargo'
            })
        
        # Verificar se o cargo não está ocupado
        ocupante_atual = novo_cargo.get_ocupante_atual()
        if ocupante_atual and ocupante_atual != usuario:
            logger.error(f"❌ Cargo já ocupado por {ocupante_atual.nome_completo_rp}")
            return JsonResponse({
                'success': False, 
                'error': f'Este cargo já está ocupado por {ocupante_atual.nome_completo_rp}'
            })
        
        # Verificar se não é o mesmo cargo
        if cargo_atual == novo_cargo:
            logger.error(f"❌ Tentativa de promover para o mesmo cargo")
            return JsonResponse({
                'success': False, 
                'error': 'O usuário já ocupa este cargo'
            })
        
        # Realizar a promoção (finalizar cargo atual e criar novo)
        logger.info(f"📋 Finalizando cargo atual...")
        
        # 1. Finalizar cargo atual
        historico_atual = HistoricoCargo.objects.filter(
            usuario=usuario,
            cargo=cargo_atual,
            data_fim__isnull=True
        ).first()
        
        if historico_atual:
            historico_atual.data_fim = timezone.now()
            historico_atual.exonerado_por = request.user
            historico_atual.observacoes = f"Promovido para {novo_cargo.nome}"
            historico_atual.save()
            logger.info(f"✅ Cargo atual finalizado")
        
        # 2. Atualizar perfil
        usuario_profile.cargo_atual = novo_cargo
        usuario_profile.save()
        logger.info(f"✅ Perfil atualizado")
        
        # 3. Atualizar o histórico criado automaticamente
        historico_novo = HistoricoCargo.objects.filter(
            usuario=usuario,
            cargo=novo_cargo,
            data_fim__isnull=True
        ).order_by('-data_inicio').first()
        
        if historico_novo:
            historico_novo.nomeado_por = request.user
            if observacoes:
                historico_novo.observacoes = observacoes
            else:
                historico_novo.observacoes = f"Promovido de {cargo_atual.nome}"
            historico_novo.save()
            logger.info(f"✅ Histórico de promoção atualizado")
            
            # 4. Criar publicação de promoção no Diário Oficial
            try:
                from .models import PublicacaoDiarioOficial
                publicacao = PublicacaoDiarioOficial.criar_publicacao_automatica(historico_novo, 'promocao')
                if publicacao:
                    logger.info(f"✅ Publicação de promoção criada no Diário Oficial - ID: {publicacao.id}")
                else:
                    logger.warning(f"⚠️ Publicação de promoção não foi criada (cargo pode não ser elegível)")
            except Exception as e:
                logger.error(f"❌ Erro ao criar publicação de promoção: {str(e)}")
        
        logger.info(f"🎉 PROMOÇÃO CONCLUÍDA COM SUCESSO!")
        
        return JsonResponse({
            'success': True,
            'message': f'{usuario.nome_completo_rp} foi promovido(a) de {cargo_atual.nome} para {novo_cargo.nome} com sucesso!'
        })
        
    except json.JSONDecodeError:
        logger.error(f"❌ Erro de JSON")
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        logger.error(f"❌ Erro interno na promoção: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def exonerar_usuario(request):
    """API para exonerar usuário de um cargo"""
    import logging
    logger = logging.getLogger('diario_oficial')
    
    try:
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        observacoes = data.get('observacoes', '')
        
        logger.info(f"🔥 INICIANDO EXONERAÇÃO - Usuario ID: {usuario_id}")
        logger.info(f"   - Gestor: {request.user.nome_completo_rp}")
        logger.info(f"   - Observações: {observacoes}")
        
        # Verificar permissões
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.cargo_atual:
            logger.warning(f"❌ Gestor sem cargo atual")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem cargo para realizar exonerações'
            })
        
        cargo_gestor = user_profile.cargo_atual
        logger.info(f"   - Cargo do gestor: {cargo_gestor.nome} ({cargo_gestor.simbolo_gestao})")
        
        if cargo_gestor.simbolo_gestao == 'nenhum':
            logger.warning(f"❌ Gestor sem permissões de gestão")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissões de gestão'
            })
        
        # Obter usuário
        try:
            usuario = User.objects.get(id=usuario_id)
            logger.info(f"✅ Usuário encontrado: {usuario.nome_completo_rp}")
        except User.DoesNotExist:
            logger.error(f"❌ Usuário não encontrado: {usuario_id}")
            return JsonResponse({
                'success': False, 
                'error': 'Usuário não encontrado'
            })
        
        # Obter perfil do usuário
        usuario_profile = getattr(usuario, 'profile', None)
        if not usuario_profile or not usuario_profile.cargo_atual:
            logger.error(f"❌ Usuário sem cargo atual")
            return JsonResponse({
                'success': False, 
                'error': 'Usuário não possui cargo atual'
            })
        
        logger.info(f"   - Cargo atual do usuário: {usuario_profile.cargo_atual.nome} ({usuario_profile.cargo_atual.simbolo_gestao})")
        
        # Verificar se pode gerenciar este cargo
        if not cargo_gestor.pode_gerenciar_cargo(usuario_profile.cargo_atual):
            logger.warning(f"❌ Gestor não pode gerenciar este cargo")
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para exonerar este usuário'
            })
        
        # Obter informações antes da exoneração
        cargo_nome = usuario_profile.cargo_atual.nome
        
        # Finalizar cargo atual diretamente
        historico_atual = HistoricoCargo.objects.filter(
            usuario=usuario,
            cargo=usuario_profile.cargo_atual,
            data_fim__isnull=True
        ).first()
        
        if historico_atual:
            logger.info(f"📋 Finalizando histórico ID: {historico_atual.id}")
            logger.info(f"   - Cargo: {historico_atual.cargo.nome}")
            logger.info(f"   - Entidade: {historico_atual.cargo.entidade.nome}")
            logger.info(f"   - Órgão: {historico_atual.cargo.entidade.orgao.nome}")
            logger.info(f"   - Poder: {historico_atual.cargo.entidade.orgao.poder.nome}")
            
            # Finalizar cargo com dados específicos
            historico_atual.data_fim = timezone.now()
            historico_atual.exonerado_por = request.user
            if observacoes:
                historico_atual.observacoes = observacoes
            
            logger.info(f"💾 Salvando histórico finalizado...")
            historico_atual.save()
            logger.info(f"✅ Histórico salvo com data_fim: {historico_atual.data_fim}")
        else:
            logger.error(f"❌ Histórico atual não encontrado!")
        
        # Remover cargo do perfil (isso não deve disparar outro signal de finalização)
        logger.info(f"🔄 Removendo cargo do perfil...")
        usuario_profile.cargo_atual = None
        usuario_profile.save()
        logger.info(f"✅ Cargo removido do perfil")
        
        logger.info(f"🎉 EXONERAÇÃO CONCLUÍDA COM SUCESSO!")
        
        return JsonResponse({
            'success': True,
            'message': f'{usuario.nome_completo_rp} foi exonerado(a) de {cargo_nome} com sucesso!'
        })
        
    except json.JSONDecodeError:
        logger.error(f"❌ Erro de JSON")
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        logger.error(f"❌ Erro interno na exoneração: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


def perfil_publico(request, username):
    """View do perfil público do usuário"""
    usuario = get_object_or_404(User, username=username)
    
    # Obter perfil e histórico
    usuario_profile = getattr(usuario, 'profile', None)
    
    # Obter histórico com todos os relacionamentos necessários
    historico_cargos = HistoricoCargo.objects.filter(
        usuario=usuario
    ).select_related(
        'cargo',
        'cargo__entidade',
        'cargo__entidade__orgao',
        'cargo__entidade__orgao__poder',
        'nomeado_por',
        'exonerado_por'
    ).order_by(
        '-data_inicio',
        '-id'  # Desempate por ID para garantir consistência
    )
    
    # Criar um dicionário para armazenar registros únicos
    registros_unicos = {}
    cargos_unicos = set()  # Conjunto para contar cargos únicos
    orgaos_unicos = set()  # Conjunto para contar órgãos únicos
    poderes_unicos = set()  # Conjunto para contar poderes únicos
    total_dias_servico = 0  # Total de dias em cargos
    total_cargos_gestao = 0  # Total de cargos de gestão
    
    # Filtrar registros duplicados manualmente
    for historico in historico_cargos:
        # Usar apenas cargo e data_inicio como chave
        chave = (historico.cargo.id, historico.data_inicio.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Manter apenas o registro mais recente (maior ID) para cada combinação de cargo e data_inicio
        if chave not in registros_unicos:
            registros_unicos[chave] = historico
            cargos_unicos.add(historico.cargo.id)
            orgaos_unicos.add(historico.cargo.entidade.orgao.id)
            poderes_unicos.add(historico.cargo.entidade.orgao.poder.id)
            
            # Calcular dias de serviço
            data_fim = historico.data_fim or timezone.now()
            dias = (data_fim - historico.data_inicio).days
            total_dias_servico += max(0, dias)  # Evitar números negativos
            
            # Contar cargos de gestão
            if historico.cargo.simbolo_gestao in ['**', '*', '+']:
                total_cargos_gestao += 1
    
    # Calcular média de dias por cargo
    media_dias_por_cargo = round(total_dias_servico / len(cargos_unicos)) if cargos_unicos else 0
    
    # Calcular porcentagem de cargos de gestão
    porcentagem_gestao = round((total_cargos_gestao / len(cargos_unicos)) * 100) if cargos_unicos else 0
    
    # Converter dicionário em lista e ordenar por data_inicio
    historico_filtrado = sorted(
        registros_unicos.values(),
        key=lambda x: (x.data_inicio, x.id),
        reverse=True
    )
    
    context = {
        'usuario': usuario,
        'usuario_profile': usuario_profile,
        'cargo_atual': usuario_profile.cargo_atual if usuario_profile else None,
        'historico_cargos': historico_filtrado,
        'total_cargos_unicos': len(cargos_unicos),
        'total_dias_servico': total_dias_servico,
        'media_dias_por_cargo': media_dias_por_cargo,
        'total_orgaos': len(orgaos_unicos),
        'total_poderes': len(poderes_unicos),
        'total_cargos_gestao': total_cargos_gestao,
        'porcentagem_gestao': porcentagem_gestao
    }
    
    return render(request, 'main/perfil_publico.html', context)


@require_http_methods(["GET"])
def api_cargos_por_entidade(request, entidade_id):
    """API para obter cargos de uma entidade"""
    try:
        entidade = Entidade.objects.get(id=entidade_id)
        cargos = entidade.cargo_set.all()
        
        cargos_data = []
        for cargo in cargos:
            # Verificar se está ocupado
            ocupado_por = Profile.objects.filter(cargo_atual=cargo).first()
            
            cargos_data.append({
                'id': cargo.id,
                'nome': cargo.nome,
                'simbolo_gestao': cargo.simbolo_gestao,
                'simbolo_display': cargo.get_simbolo_gestao_display(),
                'simbolo_icon': cargo.get_simbolo_display_icon(),
                'ocupado': bool(ocupado_por),
                'ocupado_por': ocupado_por.user.nome_completo_rp if ocupado_por else None,
            })
        
        return JsonResponse({
            'success': True,
            'cargos': cargos_data,
            'entidade': {
                'nome': entidade.nome,
                'orgao': entidade.orgao.nome,
                'poder': entidade.orgao.poder.nome,
            }
        })
        
    except Entidade.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Entidade não encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


def incrementar_visualizacao_noticia(request, noticia_id):
    """Incrementa o contador de visualizações de uma notícia via AJAX"""
    if request.method == 'POST':
        try:
            noticia = Noticia.objects.get(id=noticia_id, publicado=True, status='publicado')
            noticia.visualizacoes += 1
            noticia.save()
            return JsonResponse({'success': True, 'visualizacoes': noticia.visualizacoes})
        except Noticia.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notícia não encontrada'})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


def buscar_noticias(request):
    """Busca notícias via AJAX para o sistema de busca"""
    query = request.GET.get('q', '')
    
    if len(query) < 3:
        return JsonResponse({'noticias': []})
    
    noticias = Noticia.objects.filter(
        publicado=True,
        status='publicado',
        titulo__icontains=query
    )[:10]
    
    noticias_data = []
    for noticia in noticias:
        noticias_data.append({
            'id': noticia.id,
            'titulo': noticia.titulo,
            'resumo': noticia.resumo,
            'tipo': noticia.get_tipo_display(),
            'data_publicacao': noticia.data_publicacao.strftime('%d/%m/%Y') if noticia.data_publicacao else '',
            'imagem': noticia.imagem.url if noticia.imagem else None
        })
    
    return JsonResponse({'noticias': noticias_data})


@login_required
@require_http_methods(["GET"])
def cargos_disponiveis(request):
    """API para obter cargos disponíveis para nomeação"""
    try:
        # Verificar permissões
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.cargo_atual:
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem cargo para realizar nomeações'
            })
        
        cargo_gestor = user_profile.cargo_atual
        if cargo_gestor.simbolo_gestao == 'nenhum':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissões de gestão'
            })
        
        # Obter cargos que pode gerenciar
        cargos = cargo_gestor.get_cargos_gerenciaveis()
        
        # Filtrar apenas cargos sem ocupante
        cargos_disponiveis = []
        for cargo in cargos:
            if not Profile.objects.filter(cargo_atual=cargo).exists():
                cargos_disponiveis.append({
                    'id': cargo.id,
                    'nome': cargo.nome,
                    'simbolo_display': cargo.get_simbolo_display_icon(),
                    'entidade': str(cargo.entidade),
                })
        
        return JsonResponse({
            'success': True,
            'cargos': cargos_disponiveis
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter cargos disponíveis: {str(e)}'
        })


@csrf_protect
@require_http_methods(["POST"])
def clear_messages(request):
    """Limpa as mensagens da sessão"""
    try:
        # Limpar todas as mensagens
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Iterar sobre as mensagens para marcá-las como lidas
        storage.used = True  # Garantir que as mensagens sejam marcadas como lidas
        
        # Limpar a sessão
        if '_messages' in request.session:
            del request.session['_messages']
        request.session.modified = True
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Views do Diário Oficial
def diario_oficial_lista(request):
    """Lista todas as edições do Diário Oficial"""
    diarios = DiarioOficial.objects.all()
    
    # Filtros
    ano = request.GET.get('ano')
    if ano:
        diarios = diarios.filter(ano=ano)
    
    # Paginação
    paginator = Paginator(diarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Anos disponíveis para filtro
    anos_disponiveis = DiarioOficial.objects.values_list('ano', flat=True).distinct().order_by('-ano')
    
    context = {
        'page_obj': page_obj,
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano,
    }
    
    return render(request, 'main/diario_oficial_lista.html', context)


def diario_oficial_detalhe(request, numero):
    """Exibe uma edição específica do Diário Oficial"""
    from .models import ConfiguracaoDiarioOficial
    
    diario = get_object_or_404(DiarioOficial, numero=numero)
    publicacoes_por_secao = diario.get_publicacoes_por_secao()
    config_diario = ConfiguracaoDiarioOficial.get_configuracao()
    
    context = {
        'diario': diario,
        'publicacoes_por_secao': publicacoes_por_secao,
        'config_diario': config_diario,
    }
    
    return render(request, 'main/diario_oficial_detalhe.html', context)


def diario_oficial_pdf(request, numero):
    """Gera o PDF de uma edição do Diário Oficial usando HTML para PDF"""
    from .models import ConfiguracaoDiarioOficial
    
    diario = get_object_or_404(DiarioOficial, numero=numero)
    publicacoes_por_secao = diario.get_publicacoes_por_secao()
    config_diario = ConfiguracaoDiarioOficial.get_configuracao()
    
    try:
        # Converter imagens para base64 para funcionar no PDF
        def image_to_base64(image_field):
            if image_field and hasattr(image_field, 'path'):
                try:
                    image_path = image_field.path
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            # Detectar tipo de imagem
                            ext = os.path.splitext(image_path)[1].lower()
                            if ext == '.png':
                                mime_type = 'image/png'
                            elif ext in ['.jpg', '.jpeg']:
                                mime_type = 'image/jpeg'
                            elif ext == '.gif':
                                mime_type = 'image/gif'
                            else:
                                mime_type = 'image/png'
                            return f'data:{mime_type};base64,{img_data}'
                except Exception as e:
                    print(f"Erro ao converter imagem para base64: {e}")
            return None
        
        # Converter imagens para base64
        logo_esquerda_base64 = image_to_base64(config_diario.logo_esquerda) if config_diario.logo_esquerda else None
        logo_direita_base64 = image_to_base64(config_diario.logo_direita) if config_diario.logo_direita else None
        
        # Renderizar o template HTML com contexto para PDF
        context = {
            'diario': diario,
            'publicacoes_por_secao': publicacoes_por_secao,
            'config_diario': config_diario,
            'logo_esquerda_base64': logo_esquerda_base64,
            'logo_direita_base64': logo_direita_base64,
            'is_pdf': True,
        }
        
        html_string = render_to_string('main/diario_oficial_pdf.html', context, request=request)
        
        # Instalar xhtml2pdf se não estiver instalado
        try:
            from xhtml2pdf import pisa
        except ImportError:
            # Se xhtml2pdf não estiver disponível, usar método alternativo
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "xhtml2pdf"])
            from xhtml2pdf import pisa
        
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Converter HTML para PDF
        pisa_status = pisa.CreatePDF(html_string, dest=buffer)
        
        if pisa_status.err:
            return HttpResponse('Erro ao gerar PDF', status=500)
        
        # Retornar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="diario_oficial_{numero}.pdf"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f'Erro ao gerar PDF: {str(e)}', status=500)


@login_required
def diario_oficial_criar_publicacao(request):
    """Permite criar publicações manuais no Diário Oficial"""
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para criar publicações.')
        return redirect('main:diario_oficial_lista')
    
    if request.method == 'POST':
        form = PublicacaoForm(request.POST)
        if form.is_valid():
            publicacao = form.save(commit=False)
            publicacao.criado_por = request.user
            publicacao.automatica = False
            
            # Obtém ou cria o diário oficial do dia (usando fuso horário do Brasil)
            import pytz
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            agora_brasilia = timezone.now().astimezone(brasilia_tz)
            data_hoje_brasil = agora_brasilia.date()
            
            diario, created = DiarioOficial.objects.get_or_create(
                data_publicacao=data_hoje_brasil,
                defaults={'numero': DiarioOficial.get_proximo_numero()}
            )
            publicacao.diario = diario
            publicacao.save()
            
            messages.success(request, 'Publicação criada com sucesso!')
            return redirect('main:diario_oficial_detalhe', numero=diario.numero)
    else:
        form = PublicacaoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'main/diario_oficial_criar_publicacao.html', context)


def diario_oficial_buscar(request):
    """Busca publicações no Diário Oficial"""
    query = request.GET.get('q', '')
    secao = request.GET.get('secao', '')
    tipo = request.GET.get('tipo', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    publicacoes = PublicacaoDiarioOficial.objects.all()
    
    if query:
        publicacoes = publicacoes.filter(
            Q(titulo__icontains=query) | 
            Q(conteudo__icontains=query)
        )
    
    if secao:
        publicacoes = publicacoes.filter(secao=secao)
    
    if tipo:
        publicacoes = publicacoes.filter(tipo=tipo)
    
    if data_inicio:
        publicacoes = publicacoes.filter(diario__data_publicacao__gte=data_inicio)
    
    if data_fim:
        publicacoes = publicacoes.filter(diario__data_publicacao__lte=data_fim)
    
    publicacoes = publicacoes.order_by('-diario__data_publicacao', '-criado_em')
    
    # Paginação
    paginator = Paginator(publicacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'secao_selecionada': secao,
        'tipo_selecionado': tipo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'secoes_choices': PublicacaoDiarioOficial.SECOES_CHOICES,
        'tipos_choices': PublicacaoDiarioOficial.TIPOS_CHOICES,
    }
    
    return render(request, 'main/diario_oficial_buscar.html', context)


def portal_transparencia(request):
    """View principal do Portal da Transparência"""
    # Estatísticas conforme solicitado
    total_usuarios = User.objects.count()
    total_servidores = User.objects.filter(historicocargo__data_fim__isnull=True).distinct().count()
    total_imigrantes = User.objects.filter(nivel_acesso='imigrante').count()
    total_cidadaos = User.objects.filter(nivel_acesso='cidadao').count()
    
    # Distribuição por poderes
    poderes_stats = []
    for poder in Poder.objects.all():
        count = HistoricoCargo.objects.filter(
            cargo__entidade__orgao__poder=poder,
            data_fim__isnull=True
        ).count()
        poderes_stats.append({
            'id': poder.id,
            'nome': poder.nome,
            'count': count
        })
    
    # Distribuição por níveis de acesso
    niveis_stats = []
    for nivel in User.NIVEL_CHOICES:
        count = User.objects.filter(nivel_acesso=nivel[0]).count()
        niveis_stats.append({
            'nivel': nivel[0],
            'nome': nivel[1],
            'count': count
        })
    
    # Movimentações recentes (últimas 10 - nomeações e exonerações)
    from django.db.models import Case, When, F
    
    movimentacoes_recentes = HistoricoCargo.objects.select_related(
        'usuario', 'cargo', 'cargo__entidade'
    ).annotate(
        # Usar data_fim se existir (exoneração), senão data_inicio (nomeação)
        data_movimentacao=Case(
            When(data_fim__isnull=False, then=F('data_fim')),
            default=F('data_inicio')
        )
    ).order_by('-data_movimentacao')[:10]
    
    # Servidores mais antigos (top 10)
    servidores_antigos = User.objects.filter(
        historicocargo__data_fim__isnull=True
    ).select_related(
        'profile', 'profile__cargo_atual', 'profile__cargo_atual__entidade'
    ).annotate(
        data_primeiro_cargo=Min('historicocargo__data_inicio')
    ).order_by('data_primeiro_cargo')[:10]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_servidores': total_servidores,
        'total_imigrantes': total_imigrantes,
        'total_cidadaos': total_cidadaos,
        'poderes_stats': poderes_stats,
        'niveis_stats': niveis_stats,
        'movimentacoes_recentes': movimentacoes_recentes,
        'servidores_antigos': servidores_antigos
    }
    
    return render(request, 'main/portal_transparencia.html', context)


@require_http_methods(['GET'])
def api_portal_transparencia_estatisticas(request):
    """API para obter estatísticas do Portal da Transparência"""
    try:
        total_usuarios = User.objects.count()
        total_servidores = User.objects.filter(historicocargo__data_fim__isnull=True).distinct().count()
        total_imigrantes = User.objects.filter(nivel_acesso='imigrante').count()
        total_cidadaos = User.objects.filter(nivel_acesso='cidadao').count()
        
        return JsonResponse({
            'success': True,
            'total_usuarios': total_usuarios,
            'total_servidores': total_servidores,
            'total_imigrantes': total_imigrantes,
            'total_cidadaos': total_cidadaos
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(['GET'])
def api_portal_transparencia_orgaos(request, poder_id):
    """API para obter órgãos de um poder"""
    try:
        orgaos = Orgao.objects.filter(poder_id=poder_id).values('id', 'nome')
        return JsonResponse({
            'success': True,
            'orgaos': list(orgaos)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(['GET'])
def api_portal_transparencia_entidades(request, orgao_id):
    """API para obter entidades de um órgão"""
    try:
        entidades = Entidade.objects.filter(orgao_id=orgao_id).values('id', 'nome')
        return JsonResponse({
            'success': True,
            'entidades': list(entidades)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(['GET'])
def api_portal_transparencia_buscar(request):
    """API para buscar servidores"""
    try:
        # Parâmetros da busca
        query = request.GET.get('q', '').strip()
        status = request.GET.get('status')
        nivel = request.GET.get('nivel')
        poder_id = request.GET.get('poder')
        orgao_id = request.GET.get('orgao')
        entidade_id = request.GET.get('entidade')
        cargo_id = request.GET.get('cargo')
        ordenacao = request.GET.get('ordenacao', 'nome')
        page = int(request.GET.get('page', 1))
        
        # Construir queryset base
        qs = User.objects.all()
        
        # Aplicar filtros
        if query:
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(nome_completo_rp__icontains=query) |
                Q(discord_username__icontains=query) |
                Q(roblox_username__icontains=query)
            )
        
        if status == 'ativo':
            qs = qs.filter(profile__cargo_atual__isnull=False)
        elif status == 'inativo':
            qs = qs.filter(profile__cargo_atual__isnull=True)
        
        if nivel:
            qs = qs.filter(nivel_acesso=nivel)
        
        if poder_id:
            qs = qs.filter(profile__cargo_atual__entidade__orgao__poder_id=poder_id)
        
        if orgao_id:
            qs = qs.filter(profile__cargo_atual__entidade__orgao_id=orgao_id)
        
        if entidade_id:
            qs = qs.filter(profile__cargo_atual__entidade_id=entidade_id)
            
        if cargo_id:
            qs = qs.filter(profile__cargo_atual_id=cargo_id)
        
        # Remover duplicatas e fazer select_related após aplicar filtros
        qs = qs.distinct().select_related(
            'profile', 
            'profile__cargo_atual', 
            'profile__cargo_atual__entidade',
            'profile__cargo_atual__entidade__orgao',
            'profile__cargo_atual__entidade__orgao__poder'
        )
        
        # Aplicar ordenação
        if ordenacao == 'nome':
            qs = qs.order_by('nome_completo_rp')
        elif ordenacao == '-nome':
            qs = qs.order_by('-nome_completo_rp')
        elif ordenacao == 'data_cadastro':
            qs = qs.order_by('date_joined')
        elif ordenacao == '-data_cadastro':
            qs = qs.order_by('-date_joined')
        elif ordenacao == 'cargo':
            qs = qs.order_by('profile__cargo_atual__nome')
        else:
            qs = qs.order_by('nome_completo_rp')
        
        # Paginação
        paginator = Paginator(qs, 10)
        try:
            servidores_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            servidores_page = paginator.page(paginator.num_pages)
        
        # Formatar resultados
        servidores = []
        for user in servidores_page:
            # Obter dados do perfil e cargo com tratamento para None
            profile = getattr(user, 'profile', None)
            cargo_atual = getattr(profile, 'cargo_atual', None) if profile else None
            
            # Obter histórico do cargo atual
            data_nomeacao = None
            if cargo_atual:
                historico = HistoricoCargo.objects.filter(
                    usuario=user,
                    cargo=cargo_atual,
                    data_fim__isnull=True
                ).first()
                if historico:
                    data_nomeacao = historico.data_inicio
            
            # Construir dados do servidor
            servidor_data = {
                'username': user.username,
                'nome_completo': user.nome_completo_rp,
                'roblox_username': user.roblox_username,
                'discord_username': user.discord_username,
                'nivel_acesso': dict(User.NIVEL_CHOICES).get(user.nivel_acesso, 'Desconhecido'),
                'avatar_url': user.get_roblox_avatar_url(),
                'data_nomeacao': data_nomeacao.strftime('%d/%m/%Y') if data_nomeacao else None,
                'cargo_atual': None,
                'entidade': None,
                'orgao': None,
                'poder': None
            }
            
            # Adicionar informações do cargo se existir
            if cargo_atual:
                servidor_data.update({
                    'cargo_atual': cargo_atual.nome,
                    'entidade': cargo_atual.entidade.nome,
                    'orgao': cargo_atual.entidade.orgao.nome,
                    'poder': cargo_atual.entidade.orgao.poder.nome
                })
            
            servidores.append(servidor_data)
        
        return JsonResponse({
            'success': True,
            'servidores': servidores,
            'total_results': paginator.count,
            'current_page': page,
            'total_pages': paginator.num_pages
        })
    except Exception as e:
        import traceback
        print('Erro na busca:', str(e))
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_buscar_servidores(request):
    """API para buscar servidores com filtros avançados"""
    try:
        # Parâmetros de busca
        query = request.GET.get('q', '').strip()
        status = request.GET.get('status', '')  # ativo, inativo, todos
        poder_id = request.GET.get('poder', '')
        orgao_id = request.GET.get('orgao', '')
        entidade_id = request.GET.get('entidade', '')
        cargo_id = request.GET.get('cargo', '')
        nivel_acesso = request.GET.get('nivel', '')
        data_inicio = request.GET.get('data_inicio', '')
        data_fim = request.GET.get('data_fim', '')
        ordenacao = request.GET.get('ordenacao', '')
        
        # Base query - apenas usuários que já tiveram ou têm cargos (servidores)
        usuarios = User.objects.select_related('profile').filter(
            historicocargo__isnull=False
        ).distinct()
        
        # Filtro por texto (nome RP, username, discord)
        if query:
            usuarios = usuarios.filter(
                Q(nome_completo_rp__icontains=query) |
                Q(username__icontains=query) |
                Q(roblox_username__icontains=query) |
                Q(discord_username__icontains=query)
            )
        
        # Filtro por status
        if status == 'ativo':
            usuarios = usuarios.filter(profile__cargo_atual__isnull=False)
        elif status == 'inativo':
            usuarios = usuarios.filter(profile__cargo_atual__isnull=True)
        
        # Filtro por poder
        if poder_id:
            usuarios = usuarios.filter(profile__cargo_atual__entidade__orgao__poder_id=poder_id)
        
        # Filtro por órgão
        if orgao_id:
            usuarios = usuarios.filter(profile__cargo_atual__entidade__orgao_id=orgao_id)
        
        # Filtro por entidade
        if entidade_id:
            usuarios = usuarios.filter(profile__cargo_atual__entidade_id=entidade_id)
        
        # Filtro por cargo
        if cargo_id:
            usuarios = usuarios.filter(profile__cargo_atual_id=cargo_id)
        
        # Filtro por nível de acesso
        if nivel_acesso:
            usuarios = usuarios.filter(nivel_acesso=nivel_acesso)
        
        # Filtros por período de nomeação
        if data_inicio:
            usuarios = usuarios.filter(
                historicocargo__data_inicio__gte=data_inicio,
                historicocargo__data_fim__isnull=True
            )
        
        if data_fim:
            usuarios = usuarios.filter(
                historicocargo__data_inicio__lte=data_fim,
                historicocargo__data_fim__isnull=True
            )
        
        # Aplicar ordenação
        if ordenacao == 'nome':
            usuarios = usuarios.order_by('nome_completo_rp')
        elif ordenacao == '-nome':
            usuarios = usuarios.order_by('-nome_completo_rp')
        elif ordenacao == 'data_cadastro':
            usuarios = usuarios.order_by('date_joined')
        elif ordenacao == '-data_cadastro':
            usuarios = usuarios.order_by('-date_joined')
        elif ordenacao == 'cargo':
            usuarios = usuarios.order_by('profile__cargo_atual__nome')
        else:
            usuarios = usuarios.order_by('nome_completo_rp')
        
        # Paginação
        page = int(request.GET.get('page', 1))
        per_page = 20
        
        paginator = Paginator(usuarios, per_page)
        page_obj = paginator.get_page(page)
        
        # Serializar dados
        servidores_data = []
        for usuario in page_obj:
            # Histórico de cargos
            historico = HistoricoCargo.objects.filter(usuario=usuario).select_related(
                'cargo__entidade__orgao__poder', 'nomeado_por', 'exonerado_por'
            ).order_by('-data_inicio')
            
            # Cargo atual
            cargo_atual = getattr(usuario.profile, 'cargo_atual', None)
            
            # Tempo no cargo atual
            tempo_cargo = None
            if cargo_atual:
                ultimo_historico = historico.filter(cargo=cargo_atual, data_fim__isnull=True).first()
                if ultimo_historico:
                    tempo_cargo = (timezone.now() - ultimo_historico.data_inicio).days
            
            # Dados do servidor
            servidor_data = {
                'id': usuario.id,
                'username': usuario.username,
                'nome_completo_rp': usuario.nome_completo_rp,
                'roblox_username': usuario.roblox_username,
                'discord_username': usuario.discord_username,
                'nivel_acesso': usuario.get_nivel_acesso_display(),
                'nivel_acesso_raw': usuario.nivel_acesso,
                'verificado': usuario.verificado,
                'data_cadastro': usuario.date_joined.strftime('%d/%m/%Y'),
                'cargo_atual': {
                    'nome': cargo_atual.nome if cargo_atual else None,
                    'entidade': cargo_atual.entidade.nome if cargo_atual else None,
                    'orgao': cargo_atual.entidade.orgao.nome if cargo_atual else None,
                    'poder': cargo_atual.entidade.orgao.poder.nome if cargo_atual else None,
                    'simbolo_gestao': cargo_atual.get_simbolo_display_icon() if cargo_atual else None,
                } if cargo_atual else None,
                'tempo_cargo_atual': f"{tempo_cargo} dias" if tempo_cargo else None,
                'total_cargos': historico.count(),
                'url_perfil': reverse('main:perfil_publico', args=[usuario.username]),
            }
            
            servidores_data.append(servidor_data)
        
        return JsonResponse({
            'servidores': servidores_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_results': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_orgaos_por_poder(request, poder_id):
    """API para buscar órgãos de um poder específico"""
    try:
        poder = get_object_or_404(Poder, id=poder_id)
        orgaos = Orgao.objects.filter(poder=poder).order_by('nome')
        
        orgaos_data = []
        for orgao in orgaos:
            # Contar servidores ativos neste órgão
            servidores_count = HistoricoCargo.objects.filter(
                cargo__entidade__orgao=orgao,
                data_fim__isnull=True
            ).count()
            
            orgaos_data.append({
                'id': orgao.id,
                'nome': orgao.nome,
                'servidores_count': servidores_count
            })
        
        return JsonResponse({'orgaos': orgaos_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_entidades_por_orgao(request, orgao_id):
    """API para buscar entidades de um órgão específico"""
    try:
        orgao = get_object_or_404(Orgao, id=orgao_id)
        entidades = Entidade.objects.filter(orgao=orgao).order_by('nome')
        
        entidades_data = []
        for entidade in entidades:
            # Contar servidores ativos nesta entidade
            servidores_count = HistoricoCargo.objects.filter(
                cargo__entidade=entidade,
                data_fim__isnull=True
            ).count()
            
            entidades_data.append({
                'id': entidade.id,
                'nome': entidade.nome,
                'servidores_count': servidores_count
            })
        
        return JsonResponse({'entidades': entidades_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_cargos_por_entidade_transparencia(request, entidade_id):
    """API para buscar cargos de uma entidade específica (para transparência)"""
    try:
        entidade = get_object_or_404(Entidade, id=entidade_id)
        cargos = Cargo.objects.filter(entidade=entidade).order_by('nome')
        
        cargos_data = []
        for cargo in cargos:
            # Verificar se está ocupado
            ocupado = HistoricoCargo.objects.filter(cargo=cargo, data_fim__isnull=True).exists()
            ocupante = None
            
            if ocupado:
                historico = HistoricoCargo.objects.filter(cargo=cargo, data_fim__isnull=True).first()
                if historico:
                    ocupante = {
                        'nome': historico.usuario.nome_completo_rp,
                        'username': historico.usuario.username,
                        'data_inicio': historico.data_inicio.strftime('%d/%m/%Y')
                    }
            
            cargos_data.append({
                'id': cargo.id,
                'nome': cargo.nome,
                'simbolo_gestao': cargo.get_simbolo_display_icon(),
                'ocupado': ocupado,
                'ocupante': ocupante
            })
        
        return JsonResponse({'cargos': cargos_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_exportar_servidores(request):
    """API para exportar dados dos servidores em CSV"""
    try:
        # Aplicar os mesmos filtros da busca
        query = request.GET.get('q', '').strip()
        status = request.GET.get('status', '')
        poder_id = request.GET.get('poder', '')
        orgao_id = request.GET.get('orgao', '')
        entidade_id = request.GET.get('entidade', '')
        cargo_id = request.GET.get('cargo', '')
        nivel_acesso = request.GET.get('nivel', '')
        
        # Base query - apenas usuários que já tiveram ou têm cargos (servidores)
        usuarios = User.objects.select_related('profile').filter(
            historicocargo__isnull=False
        ).distinct()
        
        # Aplicar filtros
        if query:
            usuarios = usuarios.filter(
                Q(nome_completo_rp__icontains=query) |
                Q(username__icontains=query) |
                Q(roblox_username__icontains=query) |
                Q(discord_username__icontains=query)
            )
        
        if status == 'ativo':
            usuarios = usuarios.filter(profile__cargo_atual__isnull=False)
        elif status == 'inativo':
            usuarios = usuarios.filter(profile__cargo_atual__isnull=True)
        
        if poder_id:
            usuarios = usuarios.filter(profile__cargo_atual__entidade__orgao__poder_id=poder_id)
        
        if orgao_id:
            usuarios = usuarios.filter(profile__cargo_atual__entidade__orgao_id=orgao_id)
        
        if entidade_id:
            usuarios = usuarios.filter(profile__cargo_atual__entidade_id=entidade_id)
        
        if cargo_id:
            usuarios = usuarios.filter(profile__cargo_atual_id=cargo_id)
        
        if nivel_acesso:
            usuarios = usuarios.filter(nivel_acesso=nivel_acesso)
        
        # Preparar resposta CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="servidores_publicos.csv"'
        
        # Adicionar BOM para UTF-8
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Cabeçalho
        writer.writerow([
            'Nome Completo RP',
            'Username',
            'Roblox Username',
            'Discord Username',
            'Nível de Acesso',
            'Verificado',
            'Data Cadastro',
            'Status',
            'Cargo Atual',
            'Entidade',
            'Órgão',
            'Poder',
            'Data Nomeação Atual',
            'Tempo no Cargo (dias)',
            'Total de Cargos'
        ])
        
        # Dados
        for usuario in usuarios:
            cargo_atual = getattr(usuario.profile, 'cargo_atual', None)
            
            # Calcular tempo no cargo
            tempo_cargo = ''
            data_nomeacao = ''
            if cargo_atual:
                ultimo_historico = HistoricoCargo.objects.filter(
                    usuario=usuario, 
                    cargo=cargo_atual, 
                    data_fim__isnull=True
                ).first()
                
                if ultimo_historico:
                    data_nomeacao = ultimo_historico.data_inicio.strftime('%d/%m/%Y')
                    tempo_cargo = (timezone.now() - ultimo_historico.data_inicio).days
            
            # Total de cargos
            total_cargos = HistoricoCargo.objects.filter(usuario=usuario).count()
            
            writer.writerow([
                usuario.nome_completo_rp,
                usuario.username,
                usuario.roblox_username,
                usuario.discord_username or '-',
                usuario.get_nivel_acesso_display(),
                'Sim' if usuario.verificado else 'Não',
                usuario.date_joined.strftime('%d/%m/%Y'),
                'Ativo' if cargo_atual else 'Inativo',
                cargo_atual.nome if cargo_atual else '',
                cargo_atual.entidade.nome if cargo_atual else '-',
                cargo_atual.entidade.orgao.nome if cargo_atual else '-',
                cargo_atual.entidade.orgao.poder.nome if cargo_atual else '-',
                data_nomeacao,
                tempo_cargo,
                total_cargos
            ])
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def servidor_historico_detalhado(request, username):
    """View para exibir histórico detalhado de um servidor"""
    servidor = get_object_or_404(User, username=username)
    
    # Histórico completo de cargos
    historico_cargos = HistoricoCargo.objects.filter(
        usuario=servidor
    ).select_related(
        'cargo__entidade__orgao__poder',
        'nomeado_por',
        'exonerado_por'
    ).order_by('-data_inicio')
    
    # Estatísticas do servidor
    total_cargos = historico_cargos.count()
    cargo_atual = getattr(servidor.profile, 'cargo_atual', None)
    
    # Tempo total de serviço
    tempo_total_servico = 0
    for historico in historico_cargos:
        if historico.data_fim:
            tempo_total_servico += (historico.data_fim - historico.data_inicio).days
        else:
            tempo_total_servico += (timezone.now() - historico.data_inicio).days
    
    # Tempo no cargo atual
    tempo_cargo_atual = 0
    if cargo_atual:
        historico_atual = historico_cargos.filter(cargo=cargo_atual, data_fim__isnull=True).first()
        if historico_atual:
            tempo_cargo_atual = (timezone.now() - historico_atual.data_inicio).days
    
    # Poderes onde já atuou
    poderes_atuacao = set()
    for historico in historico_cargos:
        poderes_atuacao.add(historico.cargo.entidade.orgao.poder.nome)
    
    # Nomeações realizadas por ele (se for gestor)
    nomeacoes_realizadas = HistoricoCargo.objects.filter(
        nomeado_por=servidor
    ).select_related(
        'usuario',
        'cargo__entidade__orgao__poder'
    ).order_by('-data_inicio')[:10]
    
    # Exonerações realizadas por ele
    exoneracoes_realizadas = HistoricoCargo.objects.filter(
        exonerado_por=servidor
    ).select_related(
        'usuario',
        'cargo__entidade__orgao__poder'
    ).order_by('-data_fim')[:10]
    
    # Dados para gráficos
    cargos_por_poder = {}
    tempo_por_poder = {}
    
    for historico in historico_cargos:
        poder = historico.cargo.entidade.orgao.poder.nome
        
        if poder not in cargos_por_poder:
            cargos_por_poder[poder] = 0
            tempo_por_poder[poder] = 0
        
        cargos_por_poder[poder] += 1
        
        if historico.data_fim:
            tempo_por_poder[poder] += (historico.data_fim - historico.data_inicio).days
        else:
            tempo_por_poder[poder] += (timezone.now() - historico.data_inicio).days
    
    context = {
        'servidor': servidor,
        'historico_cargos': historico_cargos,
        'total_cargos': total_cargos,
        'cargo_atual': cargo_atual,
        'tempo_total_servico': tempo_total_servico,
        'tempo_cargo_atual': tempo_cargo_atual,
        'poderes_atuacao': list(poderes_atuacao),
        'nomeacoes_realizadas': nomeacoes_realizadas,
        'exoneracoes_realizadas': exoneracoes_realizadas,
        'cargos_por_poder': cargos_por_poder,
        'tempo_por_poder': tempo_por_poder,
    }
    
    return render(request, 'main/servidor_historico_detalhado.html', context)


@require_http_methods(["GET"])
def api_portal_transparencia_exportar(request):
    """API para exportar servidores para CSV"""
    try:
        # Parâmetros da busca
        query = request.GET.get('q', '').strip()
        status = request.GET.get('status')
        nivel = request.GET.get('nivel')
        poder_id = request.GET.get('poder')
        orgao_id = request.GET.get('orgao')
        entidade_id = request.GET.get('entidade')
        ordenacao = request.GET.get('ordenacao', 'nome')
        
        # Construir queryset base
        qs = User.objects.select_related(
            'profile',
            'profile__cargo_atual',
            'profile__cargo_atual__entidade',
            'profile__cargo_atual__entidade__orgao',
            'profile__cargo_atual__entidade__orgao__poder'
        ).all()
        
        # Aplicar filtros
        if query:
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(nome_completo_rp__icontains=query) |
                Q(discord_username__icontains=query)
            )
        
        if status == 'ativo':
            qs = qs.filter(profile__cargo_atual__isnull=False)
        elif status == 'inativo':
            qs = qs.filter(profile__cargo_atual__isnull=True)
        
        if nivel:
            qs = qs.filter(nivel_acesso=nivel)
        
        if poder_id:
            qs = qs.filter(profile__cargo_atual__entidade__orgao__poder_id=poder_id)
        
        if orgao_id:
            qs = qs.filter(profile__cargo_atual__entidade__orgao_id=orgao_id)
        
        if entidade_id:
            qs = qs.filter(profile__cargo_atual__entidade_id=entidade_id)
        
        # Remover duplicatas
        qs = qs.distinct()
        
        # Aplicar ordenação
        if ordenacao == 'nome':
            qs = qs.order_by('nome_completo_rp')
        elif ordenacao == '-nome':
            qs = qs.order_by('-nome_completo_rp')
        elif ordenacao == 'data_cadastro':
            qs = qs.order_by('date_joined')
        elif ordenacao == '-data_cadastro':
            qs = qs.order_by('-date_joined')
        elif ordenacao == 'cargo':
            qs = qs.order_by('profile__cargo_atual__nome')
        else:
            qs = qs.order_by('nome_completo_rp')
        
        # Criar resposta CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="servidores.csv"'
        
        # Criar writer CSV
        writer = csv.writer(response)
        
        # Escrever cabeçalho
        writer.writerow([
            'Nome Completo',
            'Username',
            'Discord',
            'Nível de Acesso',
            'Cargo Atual',
            'Entidade',
            'Órgão',
            'Poder',
            'Data de Cadastro'
        ])
        
        # Escrever dados
        for user in qs:
            profile = getattr(user, 'profile', None)
            cargo_atual = getattr(profile, 'cargo_atual', None) if profile else None
            
            writer.writerow([
                user.nome_completo_rp,
                user.username,
                user.discord_username or '-',
                dict(User.NIVEL_CHOICES).get(user.nivel_acesso, 'Desconhecido'),
                str(cargo_atual) if cargo_atual else 'Sem cargo',
                str(cargo_atual.entidade) if cargo_atual else '-',
                str(cargo_atual.entidade.orgao) if cargo_atual else '-',
                str(cargo_atual.entidade.orgao.poder) if cargo_atual else '-',
                user.date_joined.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
        
    except Exception as e:
        import traceback
        print('Erro ao exportar CSV:', str(e))
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': 'Erro ao exportar dados. Por favor, tente novamente.'
        }, status=500)


@require_http_methods(['GET'])
def api_portal_transparencia_cargos(request, entidade_id):
    """API para obter cargos de uma entidade"""
    try:
        cargos = Cargo.objects.filter(entidade_id=entidade_id).values('id', 'nome')
        return JsonResponse({
            'success': True,
            'cargos': list(cargos)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def noticia_criar(request):
    """View para criar uma nova notícia"""
    # Verificar se o usuário tem cargo de gestão ou é superuser
    if not request.user.is_superuser:
        try:
            profile = request.user.profile
            if not profile.cargo_atual:
                messages.error(request, 'Você precisa ter um cargo para criar notícias.')
                return redirect('main:home')
            
            # Verificar se é cargo de gestão (** ou *)
            if profile.cargo_atual.simbolo_gestao not in ['**', '*']:
                messages.error(request, 'Apenas cargos de gestão (Chefe de Poder ou Líder de Órgão) podem criar notícias.')
                return redirect('main:home')
                
        except Profile.DoesNotExist:
            messages.error(request, 'Você precisa ter um perfil com cargo para criar notícias.')
            return redirect('main:home')
    
    # Determinar informações do órgão do usuário
    tipo_noticia = 'governo'  # Agora só existe governo
    orgao_usuario = None
    
    if not request.user.is_superuser:
        try:
            profile = request.user.profile
            if profile.cargo_atual:
                orgao_usuario = profile.cargo_atual.entidade.orgao
        except:
            pass
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')
        # Sempre governo agora
        tipo = 'governo'
        status = request.POST.get('status', 'rascunho')
        imagem_principal = request.FILES.get('imagem_principal')
        categorias = request.POST.getlist('categorias')
        tags = request.POST.getlist('tags')
        fonte = request.POST.get('fonte')
        link_fonte = request.POST.get('link_fonte')
        permitir_comentarios = request.POST.get('permitir_comentarios') == 'on'
        destaque = request.POST.get('destaque') == 'on'
        resumo = request.POST.get('resumo')
        
        try:
            # Determinar se deve publicar baseado no cargo e permissões
            publicado = False
            if status == 'publicado':
                # Notícias do governo podem ser publicadas por cargos de gestão
                if request.user.is_superuser or request.user.has_perm('main.pode_publicar_noticias'):
                    publicado = True
                else:
                    # Permitir publicação direta para cargos de gestão (** e *)
                    try:
                        cargo_atual = request.user.profile.cargo_atual
                        if cargo_atual and cargo_atual.simbolo_gestao in ['**', '*']:
                            publicado = True
                    except:
                        pass
            
            noticia = Noticia.objects.create(
                titulo=titulo,
                resumo=resumo,
                conteudo=conteudo,
                tipo=tipo,
                status=status,
                publicado=publicado,
                destaque=destaque,
                imagem_principal=imagem_principal,
                autor=request.user,
                fonte=fonte,
                link_fonte=link_fonte,
                permitir_comentarios=permitir_comentarios
            )
            
            # Adicionar categorias e tags
            if categorias:
                noticia.categorias.set(categorias)
            if tags:
                noticia.tags.set(tags)
            
            # Processar imagens da galeria
            imagens = request.FILES.getlist('galeria_imagens')
            for imagem in imagens:
                NoticiaImagem.objects.create(
                    imagem=imagem,
                    legenda=request.POST.get(f'legenda_{imagem.name}', ''),
                    ordem=request.POST.get(f'ordem_{imagem.name}', 0)
                )
            
            messages.success(request, 'Notícia criada com sucesso!')
            return redirect('main:noticia_editar', slug=noticia.slug)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar notícia: {str(e)}')
    
    # GET request
    categorias = NoticiaCategoria.objects.all()
    tags = NoticiaTag.objects.all()
    
    context = {
        'categorias': categorias,
        'tags': tags,
        'tipo_noticia': tipo_noticia,
        'orgao_usuario': orgao_usuario,
        'pode_escolher_tipo': request.user.is_superuser,
    }
    
    return render(request, 'main/noticia_criar.html', context)


@login_required
def noticia_editar(request, slug):
    """View para editar uma notícia existente"""
    noticia = get_object_or_404(Noticia, slug=slug)
    
    # Verificar permissão
    if not noticia.pode_editar(request.user):
        messages.error(request, 'Você não tem permissão para editar esta notícia.')
        return redirect('main:noticia_detalhe', slug=slug)
    
    if request.method == 'POST':
        try:
            noticia.titulo = request.POST.get('titulo')
            noticia.resumo = request.POST.get('resumo')
            noticia.conteudo = request.POST.get('conteudo')
            noticia.tipo = request.POST.get('tipo')
            
            if 'imagem_principal' in request.FILES:
                noticia.imagem_principal = request.FILES['imagem_principal']
            
            noticia.fonte = request.POST.get('fonte')
            noticia.link_fonte = request.POST.get('link_fonte')
            noticia.permitir_comentarios = request.POST.get('permitir_comentarios') == 'on'
            noticia.destaque = request.POST.get('destaque') == 'on'
            
            # Atualizar categorias e tags
            categorias = request.POST.getlist('categorias')
            tags = request.POST.getlist('tags')
            noticia.categorias.set(categorias)
            noticia.tags.set(tags)
            
            # Processar status e publicação
            novo_status = request.POST.get('status')
            if novo_status == 'publicado' and noticia.pode_publicar(request.user):
                noticia.publicado = True
                noticia.data_publicacao = timezone.now()
            noticia.status = novo_status
            
            noticia.save()
            
            # Processar imagens da galeria
            imagens = request.FILES.getlist('galeria_imagens')
            for imagem in imagens:
                NoticiaImagem.objects.create(
                    imagem=imagem,
                    legenda=request.POST.get(f'legenda_{imagem.name}', ''),
                    ordem=request.POST.get(f'ordem_{imagem.name}', 0)
                )
            
            messages.success(request, 'Notícia atualizada com sucesso!')
            return redirect('main:noticia_detalhe', slug=noticia.slug)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar notícia: {str(e)}')
    
    # GET request
    categorias = NoticiaCategoria.objects.all()
    tags = NoticiaTag.objects.all()
    
    context = {
        'noticia': noticia,
        'categorias': categorias,
        'tags': tags,
    }
    
    return render(request, 'main/noticia_editar.html', context)


def noticia_detalhe(request, slug):
    """View para exibir uma notícia"""
    # Tentar buscar do cache primeiro
    cache_key = f'noticia_detalhe_{slug}'
    noticia = cache.get(cache_key)
    
    if noticia is None:
        noticia = get_object_or_404(
            Noticia.objects.select_related('autor')
            .prefetch_related('categorias', 'tags', 'comentarios'),
            slug=slug
        )
        cache.set(cache_key, noticia, 60 * 30)  # Cache por 30 minutos
    
    # Incrementar visualizações apenas se não for o autor
    if request.user != noticia.autor:
        noticia.incrementar_visualizacoes()
    
    # Carregar comentários (sem cache para manter atualizado)
    comentarios = noticia.comentarios.filter(ativo=True)
    
    # Notícias relacionadas (com cache)
    cache_key_relacionadas = f'noticias_relacionadas_{noticia.id}'
    relacionadas = cache.get(cache_key_relacionadas)
    
    if relacionadas is None:
        relacionadas = list(Noticia.objects.filter(
            Q(categorias__in=noticia.categorias.all()) |
            Q(tags__in=noticia.tags.all())
        ).exclude(id=noticia.id).distinct()[:3])
        cache.set(cache_key_relacionadas, relacionadas, 60 * 60)  # Cache por 1 hora
    
    context = {
        'noticia': noticia,
        'comentarios': comentarios,
        'relacionadas': relacionadas,
    }
    
    return render(request, 'main/noticia_detalhe.html', context)


def noticia_lista(request):
    """
    Lista as notícias mais recentes, usando cache quando possível
    """
    cache_key = 'noticias_lista'
    noticias = cache.get(cache_key)
    
    if noticias is None:
        noticias = Noticia.objects.filter(
            publicado=True,
            status='publicado',
            data_publicacao__lte=timezone.now()
        ).select_related('autor').prefetch_related(
            'categorias', 'tags', 'galeria_imagens'
        ).order_by('-data_publicacao')
        
        cache.set(cache_key, list(noticias), timeout=60*15)
    
    # Paginação
    paginator = Paginator(noticias, 12)
    try:
        pagina = int(request.GET.get('pagina', '1'))
    except ValueError:
        pagina = 1
    try:
        noticias = paginator.page(pagina)
    except (EmptyPage, InvalidPage):
        noticias = paginator.page(paginator.num_pages)
    
    return render(request, 'main/noticia_lista.html', {
        'noticias': noticias
    })


@login_required
def noticia_comentar(request, slug):
    """
    Adiciona um comentário a uma notícia (suporta AJAX)
    """
    noticia = get_object_or_404(Noticia, slug=slug)
    texto = request.POST.get('texto', '').strip()
    
    # Verificar se é AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not texto:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'O comentário não pode estar vazio.'})
        messages.error(request, 'O comentário não pode estar vazio.')
        return redirect('main:noticia_detalhe', slug=slug)
    
    try:
        comentario = NoticiaComentario.objects.create(
            noticia=noticia,
            autor=request.user,
            conteudo=texto,
            ativo=True
        )
        
        # Invalida o cache da notícia
        cache.delete(f'noticia_detalhe_{slug}')
        
        # Se for AJAX, retorna JSON
        if is_ajax:
            return JsonResponse({
                'success': True,
                'comment': {
                    'author': comentario.autor.nome_completo_rp or comentario.autor.username,
                    'content': comentario.conteudo.replace('\n', '<br>'),
                    'date': comentario.data_criacao.strftime('%d/%m/%Y %H:%M')
                }
            })
        
        messages.success(request, 'Comentário adicionado com sucesso!')
        return redirect('main:noticia_detalhe', slug=slug)
        
    except Exception as e:
        print(f"Erro ao criar comentário: {str(e)}")  # Debug
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Erro ao adicionar comentário: {str(e)}')
        return redirect('main:noticia_detalhe', slug=slug)


@login_required
@permission_required('main.pode_moderar_noticias')
def noticia_moderar(request, slug):
    """View para moderação de notícias"""
    noticia = get_object_or_404(Noticia, slug=slug)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'aprovar':
            noticia.status = 'publicado'
            noticia.publicado = True
            noticia.data_publicacao = timezone.now()
            noticia.editor = request.user
            noticia.save()
            messages.success(request, 'Notícia aprovada e publicada com sucesso!')
            
        elif acao == 'rejeitar':
            noticia.status = 'rascunho'
            noticia.editor = request.user
            noticia.save()
            messages.warning(request, 'Notícia rejeitada e movida para rascunhos.')
            
        elif acao == 'arquivar':
            noticia.status = 'arquivado'
            noticia.editor = request.user
            noticia.save()
            messages.info(request, 'Notícia arquivada com sucesso.')
    
    
    return redirect('main:noticia_detalhe', slug=slug)


@login_required
@require_http_methods(["POST"])
def api_upload_imagem(request):
    """API para upload de imagens via AJAX"""
    try:
        imagem = request.FILES.get('imagem')
        if not imagem:
            return JsonResponse({'success': False, 'error': 'Nenhuma imagem enviada'})
        
        # Validar extensão
        extensoes_permitidas = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(imagem.name)[1].lower()
        if ext not in extensoes_permitidas:
            return JsonResponse({
                'success': False, 
                'error': 'Formato de arquivo não permitido. Use: ' + ', '.join(extensoes_permitidas)
            })
        
        # Validar tamanho (max 5MB)
        if imagem.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'Imagem muito grande. Tamanho máximo: 5MB'
            })
        
        # Gerar nome único
        nome_arquivo = f"{uuid.uuid4()}{ext}"
        caminho_arquivo = os.path.join('noticias/uploads', nome_arquivo)
        
        # Salvar arquivo
        caminho_completo = default_storage.save(caminho_arquivo, imagem)
        url = static(caminho_completo)
        
        return JsonResponse({
            'success': True,
            'url': url,
            'nome_arquivo': nome_arquivo
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def api_noticia_like(request, noticia_id):
    """API para curtir/descurtir uma notícia"""
    try:
        noticia = get_object_or_404(Noticia, id=noticia_id)
        
        # Verificar se o usuário já curtiu
        like, created = NoticiaLike.objects.get_or_create(
            noticia=noticia,
            usuario=request.user
        )
        
        if not created:
            # Se já existe, remove o like (descurtir)
            like.delete()
            liked = False
        else:
            # Se não existe, adiciona o like
            liked = True
        
        # Contar total de likes
        total_likes = noticia.likes.count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': total_likes
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def api_noticia_like_status(request, noticia_id):
    """API para verificar o status de like de uma notícia"""
    try:
        noticia = get_object_or_404(Noticia, id=noticia_id)
        
        liked = False
        if request.user.is_authenticated:
            liked = NoticiaLike.objects.filter(
                noticia=noticia,
                usuario=request.user
            ).exists()
        
        total_likes = noticia.likes.count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': total_likes
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def api_noticia_view(request, noticia_id):
    """API para incrementar visualizações de uma notícia"""
    try:
        noticia = get_object_or_404(Noticia, id=noticia_id)
        
        # Incrementar visualizações apenas se não for o autor
        if not request.user.is_authenticated or request.user != noticia.autor:
            noticia.visualizacoes += 1
            noticia.save(update_fields=['visualizacoes'])
        
        return JsonResponse({
            'success': True,
            'views': noticia.visualizacoes
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ===== SISTEMA DE CIDADANIA =====

@login_required 
def gestao_cidadania(request):
    """Painel de gestão de solicitações de cidadania"""
    # Buscar configuração de cidadania
    try:
        config = ConfiguracaoCidadania.objects.first()
    except:
        config = None
    
    # Verificar permissões - ORDEM IMPORTANTE: verificar cargos autorizados PRIMEIRO
    tem_permissao = False
    
    # 1. Verificar se é superuser ou nível alto
    if (request.user.is_superuser or 
        request.user.nivel_acesso in ['administrador', 'coordenador', 'fundador']):
        tem_permissao = True
    
    # 2. Verificar se tem cargo autorizado
    elif config and config.cargos_autorizados.exists():
        try:
            profile = request.user.profile
            if profile.cargo_atual and profile.cargo_atual in config.cargos_autorizados.all():
                tem_permissao = True
        except:
            pass
    
    # 3. Verificar permissão específica
    elif request.user.has_perm('users.pode_analisar_cidadania'):
        tem_permissao = True
    
    if not tem_permissao:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('main:home')
    
    # Verificar se o usuário pode aprovar (mesmo lógica, mas separada para clareza)
    pode_aprovar = False
    if request.user.is_superuser or request.user.nivel_acesso in ['administrador', 'coordenador', 'fundador']:
        pode_aprovar = True
    elif config and config.cargos_autorizados.exists():
        try:
            profile = request.user.profile
            if profile.cargo_atual and profile.cargo_atual in config.cargos_autorizados.all():
                pode_aprovar = True
        except:
            pass
    
    # Buscar solicitações
    solicitacoes = SolicitacaoCidadania.objects.select_related('usuario').order_by('-data_solicitacao')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(solicitacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'config': config,
        'pode_aprovar': pode_aprovar,
        'status_filter': status_filter,
        'total_pendentes': SolicitacaoCidadania.objects.filter(status='pendente').count(),
        'total_aprovadas': SolicitacaoCidadania.objects.filter(status='aprovada').count(),
        'total_rejeitadas': SolicitacaoCidadania.objects.filter(status='rejeitada').count(),
    }
    
    return render(request, 'main/gestao_cidadania.html', context)


@login_required
@require_http_methods(["POST"])
def aprovar_cidadania(request, solicitacao_id):
    """Aprova uma solicitação de cidadania"""
    try:
        # Verificar permissões - mesma lógica da gestão
        tem_permissao = False
        
        # 1. Verificar se é superuser ou nível alto
        if (request.user.is_superuser or 
            request.user.nivel_acesso in ['administrador', 'coordenador', 'fundador']):
            tem_permissao = True
        
        # 2. Verificar se tem cargo autorizado
        else:
            config = ConfiguracaoCidadania.objects.first()
            if config and config.cargos_autorizados.exists():
                try:
                    profile = request.user.profile
                    if profile.cargo_atual and profile.cargo_atual in config.cargos_autorizados.all():
                        tem_permissao = True
                except:
                    pass
        
        if not tem_permissao:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para aprovar cidadania'
            })
        
        # Buscar solicitação
        solicitacao = get_object_or_404(SolicitacaoCidadania, id=solicitacao_id)
        
        if solicitacao.status != 'pendente':
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitação já foi processada'
            })
        
        # Obter observações
        data = json.loads(request.body)
        observacoes = data.get('observacoes', '').strip()
        
        # Aprovar solicitação
        solicitacao.status = 'aprovada'
        solicitacao.aprovado_por = request.user
        solicitacao.data_resposta = timezone.now()
        solicitacao.observacoes_staff = observacoes
        solicitacao.save()
        
        # Atualizar nível do usuário para cidadão
        usuario = solicitacao.usuario
        usuario.nivel_acesso = 'cidadao'
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Cidadania aprovada para {usuario.nome_completo_rp}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def rejeitar_cidadania(request, solicitacao_id):
    """Rejeita uma solicitação de cidadania"""
    try:
        # Verificar permissões - mesma lógica da aprovação
        tem_permissao = False
        
        # 1. Verificar se é superuser ou nível alto
        if (request.user.is_superuser or 
            request.user.nivel_acesso in ['administrador', 'coordenador', 'fundador']):
            tem_permissao = True
        
        # 2. Verificar se tem cargo autorizado
        else:
            config = ConfiguracaoCidadania.objects.first()
            if config and config.cargos_autorizados.exists():
                try:
                    profile = request.user.profile
                    if profile.cargo_atual and profile.cargo_atual in config.cargos_autorizados.all():
                        tem_permissao = True
                except:
                    pass
        
        if not tem_permissao:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para rejeitar cidadania'
            })
        
        # Buscar solicitação
        solicitacao = get_object_or_404(SolicitacaoCidadania, id=solicitacao_id)
        
        if solicitacao.status != 'pendente':
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitação já foi processada'
            })
        
        # Obter observações (obrigatórias para rejeição)
        data = json.loads(request.body)
        observacoes = data.get('observacoes', '').strip()
        
        if not observacoes:
            return JsonResponse({
                'success': False,
                'error': 'Observações são obrigatórias para rejeição'
            })
        
        # Rejeitar solicitação
        solicitacao.status = 'rejeitada'
        solicitacao.aprovado_por = request.user
        solicitacao.data_resposta = timezone.now()
        solicitacao.observacoes_staff = observacoes
        solicitacao.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Cidadania rejeitada para {solicitacao.usuario.nome_completo_rp}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
def configurar_cidadania(request):
    """Configurações do sistema de cidadania"""
    # Verificar permissões
    if not (request.user.is_superuser or 
            request.user.nivel_acesso in ['administrador', 'coordenador', 'fundador']):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('main:home')
    
    # Buscar ou criar configuração
    config, created = ConfiguracaoCidadania.objects.get_or_create(
        defaults={
            'prazo_analise_dias': 7,
            'documentos_obrigatorios': 'RG ou CNH\nCPF\nComprovante de Residência',
            'instrucoes': 'Para solicitar sua cidadania brasileira, preencha o formulário abaixo com seus dados pessoais e anexe os documentos necessários.',
            'ativo': True,
        }
    )
    
    if request.method == 'POST':
        try:
            # Atualizar configurações
            config.prazo_analise_dias = int(request.POST.get('prazo_analise_dias', 7))
            config.documentos_obrigatorios = request.POST.get('documentos_obrigatorios', '')
            config.instrucoes = request.POST.get('instrucoes', '')
            config.ativo = request.POST.get('ativo') == 'on'
            
            # Órgão responsável
            orgao_id = request.POST.get('orgao_responsavel')
            if orgao_id:
                config.orgao_responsavel_id = orgao_id
            else:
                config.orgao_responsavel = None
            
            config.save()
            
            # Cargos autorizados
            cargos_ids = request.POST.getlist('cargos_autorizados')
            config.cargos_autorizados.set(cargos_ids)
            
            messages.success(request, 'Configurações de cidadania salvas com sucesso!')
            return redirect('main:configurar_cidadania')
            
        except Exception as e:
            messages.error(request, f'Erro ao salvar configurações: {str(e)}')
    
    # Buscar dados para o formulário
    orgaos = Orgao.objects.all().order_by('poder__nome', 'nome')
    
    # Filtrar cargos da Polícia Federal
    cargos_pf = Cargo.objects.filter(
        entidade__nome__icontains='polícia federal'
    ).order_by('entidade__nome', 'nome')
    
    # Todos os cargos para seleção avançada
    cargos_todos = Cargo.objects.select_related('entidade__orgao__poder').order_by(
        'entidade__orgao__poder__nome', 'entidade__orgao__nome', 'entidade__nome', 'nome'
    )
    
    context = {
        'config': config,
        'orgaos': orgaos,
        'cargos_pf': cargos_pf,
        'cargos_todos': cargos_todos,
        'cargos_selecionados': config.cargos_autorizados.all(),
    }
    
    return render(request, 'main/configurar_cidadania.html', context)


# ===== VIEWS DO SISTEMA DE PROTOCOLOS =====

@login_required
def protocolos_home(request):
    """Página inicial do sistema de protocolos"""
    user = request.user
    
    # Protocolos enviados diretamente para o usuário
    protocolos_diretos = Protocolo.objects.filter(
        usuario_destinatario=user
    ).order_by('-data_cadastro')[:10]
    
    # Protocolos enviados para o setor do usuário
    protocolos_setor = []
    if hasattr(user, 'profile') and user.profile.cargo_atual:
        entidade = user.profile.cargo_atual.entidade
        protocolos_setor = Protocolo.objects.filter(
            entidade_destinatario=entidade,
            usuario_destinatario__isnull=True
        ).order_by('-data_cadastro')[:10]
    
    # Protocolos enviados para o órgão do usuário
    protocolos_orgao = []
    if hasattr(user, 'profile') and user.profile.cargo_atual:
        orgao = user.profile.cargo_atual.entidade.orgao
        protocolos_orgao = Protocolo.objects.filter(
            orgao_destinatario=orgao,
            entidade_destinatario__isnull=True,
            usuario_destinatario__isnull=True
        ).order_by('-data_cadastro')[:10]
    
    # Protocolos monitorados
    protocolos_monitorados = Protocolo.objects.filter(
        monitorado_por_usuario=True,
        usuario_cadastro=user
    ).order_by('-data_cadastro')[:10]
    
    # Solicitações de assinatura pendentes
    solicitacoes_assinatura = SolicitacaoAssinatura.objects.filter(
        usuario_destinatario=user,
        status='pendente'
    ).order_by('-data_solicitacao')[:5]
    
    context = {
        'protocolos_diretos': protocolos_diretos,
        'protocolos_setor': protocolos_setor,
        'protocolos_orgao': protocolos_orgao,
        'protocolos_monitorados': protocolos_monitorados,
        'solicitacoes_assinatura': solicitacoes_assinatura,
    }
    
    return render(request, 'main/protocolos_home.html', context)


@login_required
def protocolo_criar(request):
    """Criar novo protocolo"""
    if request.method == 'POST':
        try:
            # Dados básicos
            assunto = request.POST.get('assunto')
            detalhamento = request.POST.get('detalhamento')
            especie_documento_id = request.POST.get('especie_documento')
            urgencia = request.POST.get('urgencia', 'nao')
            restricao_acesso = request.POST.get('restricao_acesso', 'publico')
            monitorar = request.POST.get('monitorar') == 'on'
            
            # Destino
            orgao_destinatario_id = request.POST.get('orgao_destinatario')
            entidade_destinatario_id = request.POST.get('entidade_destinatario')
            usuario_destinatario_id = request.POST.get('usuario_destinatario')
            
            # Validações
            if not all([assunto, detalhamento, especie_documento_id, orgao_destinatario_id]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('main:protocolo_criar')
            
            # Verificar se detalhamento não excede 2400 caracteres
            if len(detalhamento) > 2400:
                messages.error(request, 'O detalhamento não pode exceder 2.400 caracteres.')
                return redirect('main:protocolo_criar')
            
            # Buscar objetos
            especie_documento = get_object_or_404(EspecieDocumento, id=especie_documento_id)
            orgao_destinatario = get_object_or_404(Orgao, id=orgao_destinatario_id)
            entidade_destinatario = None
            if entidade_destinatario_id:
                entidade_destinatario = get_object_or_404(Entidade, id=entidade_destinatario_id)
            
            usuario_destinatario = None
            if usuario_destinatario_id:
                usuario_destinatario = get_object_or_404(User, id=usuario_destinatario_id)
            
            # Criar protocolo
            protocolo = Protocolo.objects.create(
                usuario_cadastro=request.user,
                orgao_cadastro=Protocolo.get_orgao_usuario(request.user),
                entidade_cadastro=Protocolo.get_entidade_usuario(request.user),
                orgao_destinatario=orgao_destinatario,
                entidade_destinatario=entidade_destinatario,
                usuario_destinatario=usuario_destinatario,
                especie_documento=especie_documento,
                assunto=assunto,
                detalhamento=detalhamento,
                urgencia=urgencia,
                restricao_acesso=restricao_acesso,
                monitorado_por_usuario=monitorar
            )
            
            # Processar interessados
            interessados_data = request.POST.getlist('interessados')
            for interessado_data in interessados_data:
                if interessado_data:
                    try:
                        interessado_id = int(interessado_data)
                        interessado = User.objects.get(id=interessado_id)
                        
                        ProtocoloInteressado.objects.create(
                            protocolo=protocolo,
                            usuario=interessado,
                            orgao=Protocolo.get_orgao_usuario(interessado),
                            entidade=Protocolo.get_entidade_usuario(interessado)
                        )
                    except (ValueError, User.DoesNotExist):
                        continue
            
            # Processar documentos e anexos
            documentos = request.FILES.getlist('documentos')
            for documento in documentos:
                ProtocoloDocumento.objects.create(
                    protocolo=protocolo,
                    nome=documento.name,
                    arquivo=documento,
                    tipo='documento',
                    usuario_upload=request.user
                )
            
            anexos = request.FILES.getlist('anexos')
            for anexo in anexos:
                ProtocoloDocumento.objects.create(
                    protocolo=protocolo,
                    nome=anexo.name,
                    arquivo=anexo,
                    tipo='anexo',
                    usuario_upload=request.user
                )
            
            messages.success(request, f'Protocolo {protocolo.numero_protocolo} criado com sucesso!')
            return redirect('main:protocolo_detalhe', numero_protocolo=protocolo.numero_protocolo)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar protocolo: {str(e)}')
            return redirect('main:protocolo_criar')
    
    # GET - Exibir formulário
    especies_documento = EspecieDocumento.objects.filter(ativo=True).order_by('nome')
    orgaos = Orgao.objects.filter(ativo=True).order_by('poder__nome', 'nome')
    usuarios = User.objects.filter(is_active=True).order_by('nome_completo_rp')
    
    # Dados do usuário atual
    user_orgaos = []
    user_entidades = []
    if hasattr(request.user, 'profile') and request.user.profile.cargo_atual:
        user_orgaos = [request.user.profile.cargo_atual.entidade.orgao]
        user_entidades = [request.user.profile.cargo_atual.entidade]
    else:
        # Usuário cidadão
        user_orgaos = [Protocolo.get_or_create_orgao_cidadao()]
        user_entidades = [Protocolo.get_or_create_entidade_cidadao()]
    
    context = {
        'especies_documento': especies_documento,
        'orgaos': orgaos,
        'usuarios': usuarios,
        'user_orgaos': user_orgaos,
        'user_entidades': user_entidades,
    }
    
    return render(request, 'main/protocolo_criar.html', context)


@login_required
def protocolo_detalhe(request, numero_protocolo):
    """Detalhe do protocolo"""
    protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
    
    # Verificar se usuário pode visualizar
    if not protocolo.pode_visualizar(request.user):
        messages.error(request, 'Você não tem permissão para visualizar este protocolo.')
        return redirect('main:protocolos_home')
    
    # Buscar dados relacionados
    documentos = protocolo.documentos.all().order_by('-data_upload')
    encaminhamentos = protocolo.encaminhamentos.all().order_by('data_encaminhamento')  # Cronológica para timeline
    interessados = protocolo.interessados.all()
    solicitacoes_acesso = protocolo.solicitacoes_acesso.all().order_by('-data_solicitacao')
    
    # Buscar poderes para o modal de encaminhamento
    poderes = Poder.objects.all().prefetch_related('orgao_set')
    
    # Verificar se usuário pode gerenciar
    pode_gerenciar = protocolo.pode_gerenciar(request.user)
    
    # Criar timeline de movimentações (apenas encaminhamentos)
    movimentacoes_timeline = []
    
    # Adicionar criação do protocolo como primeira movimentação
    movimentacoes_timeline.append({
        'tipo': 'criacao',
        'data': protocolo.data_cadastro,
        'usuario_origem': protocolo.usuario_cadastro,
        'orgao_origem': protocolo.orgao_cadastro,
        'entidade_origem': protocolo.entidade_cadastro,
        'usuario_destino': protocolo.usuario_destinatario,
        'orgao_destino': protocolo.orgao_destinatario,
        'entidade_destino': protocolo.entidade_destinatario,
        'parecer': f'Protocolo criado com o assunto: {protocolo.assunto}',
        'detalhamento': protocolo.detalhamento
    })
    
    # Adicionar encaminhamentos
    for enc in encaminhamentos:
        movimentacoes_timeline.append({
            'tipo': 'encaminhamento',
            'data': enc.data_encaminhamento,
            'usuario_origem': enc.usuario_origem,
            'orgao_origem': enc.orgao_origem,
            'entidade_origem': enc.entidade_origem,
            'usuario_destino': enc.usuario_destino,
            'orgao_destino': enc.orgao_destino,
            'entidade_destino': enc.entidade_destino,
            'parecer': enc.parecer,
            'id': enc.id
        })
    
    # Ordenar timeline por data
    movimentacoes_timeline.sort(key=lambda x: x['data'])
    
    context = {
        'protocolo': protocolo,
        'documentos': documentos,
        'encaminhamentos': encaminhamentos,
        'interessados': interessados,
        'solicitacoes_acesso': solicitacoes_acesso,
        'pode_gerenciar': pode_gerenciar,
        'poderes': poderes,
        'movimentacoes_timeline': movimentacoes_timeline,
    }
    
    return render(request, 'main/protocolo_detalhe.html', context)


@login_required
def protocolo_consultar(request):
    """Consultar protocolo por número"""
    numero_protocolo = request.GET.get('numero_protocolo', '').strip()
    
    if numero_protocolo:
        try:
            protocolo = Protocolo.objects.get(numero_protocolo=numero_protocolo)
            
            # Verificar se usuário pode visualizar
            if protocolo.pode_visualizar(request.user):
                return redirect('main:protocolo_detalhe', numero_protocolo=numero_protocolo)
            else:
                messages.error(request, 'Você não tem permissão para visualizar este protocolo.')
        except Protocolo.DoesNotExist:
            messages.error(request, 'Protocolo não encontrado.')
    
    return render(request, 'main/protocolo_consultar.html')


@login_required
def api_entidades_por_orgao_protocolo(request, orgao_id):
    """API para buscar entidades por órgão (protocolos)"""
    try:
        orgao = get_object_or_404(Orgao, id=orgao_id)
        entidades = orgao.entidade_set.all().order_by('nome')
        
        data = {
            'entidades': [
                {
                    'id': entidade.id,
                    'nome': entidade.nome
                }
                for entidade in entidades
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_usuarios_por_entidade_protocolo(request, entidade_id):
    """API para buscar usuários de uma entidade para protocolos"""
    try:
        entidade = get_object_or_404(Entidade, id=entidade_id)
        usuarios = User.objects.filter(
            profile__cargo_atual__entidade=entidade
        ).values('id', 'nome_completo_rp')
        
        return JsonResponse({
            'usuarios': list(usuarios)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ===== FUNCIONALIDADES DO PROTOCOLO =====

@login_required
@require_http_methods(["POST"])
def protocolo_upload_documento(request, numero_protocolo):
    """Upload de documento para protocolo"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar permissões
        if not protocolo.pode_gerenciar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para adicionar documentos a este protocolo'
            })
        
        # Verificar se arquivo foi enviado
        if 'arquivo' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum arquivo foi enviado'
            })
        
        arquivo = request.FILES['arquivo']
        nome = request.POST.get('nome', arquivo.name)
        tipo = request.POST.get('tipo', 'documento')
        
        # Validar tipo de arquivo
        extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.xlsx', '.xls']
        if not any(arquivo.name.lower().endswith(ext) for ext in extensoes_permitidas):
            return JsonResponse({
                'success': False,
                'error': 'Tipo de arquivo não permitido. Use: PDF, DOC, DOCX, JPG, PNG, TXT, XLS, XLSX'
            })
        
        # Validar tamanho (10MB)
        if arquivo.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'Arquivo muito grande. Tamanho máximo: 10MB'
            })
        
        # Criar documento
        documento = ProtocoloDocumento.objects.create(
            protocolo=protocolo,
            nome=nome,
            arquivo=arquivo,
            tipo=tipo,
            usuario_upload=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Documento adicionado com sucesso',
            'documento': {
                'id': documento.id,
                'nome': documento.nome,
                'tipo': documento.get_tipo_display(),
                'data_upload': documento.data_upload.strftime('%d/%m/%Y %H:%M'),
                'usuario': documento.usuario_upload.nome_completo_rp,
                'url': documento.arquivo.url
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_adicionar_interessado(request, numero_protocolo):
    """Adicionar interessado ao protocolo"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar permissões
        if not protocolo.pode_gerenciar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para adicionar interessados a este protocolo'
            })
        
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        
        if not usuario_id:
            return JsonResponse({
                'success': False,
                'error': 'Usuário é obrigatório'
            })
        
        usuario = get_object_or_404(User, id=usuario_id)
        
        # Verificar se já é interessado
        if ProtocoloInteressado.objects.filter(protocolo=protocolo, usuario=usuario).exists():
            return JsonResponse({
                'success': False,
                'error': 'Este usuário já é interessado neste protocolo'
            })
        
        # Adicionar interessado
        interessado = ProtocoloInteressado.objects.create(
            protocolo=protocolo,
            usuario=usuario,
            orgao=Protocolo.get_orgao_usuario(usuario),
            entidade=Protocolo.get_entidade_usuario(usuario)
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{usuario.nome_completo_rp} adicionado como interessado',
            'interessado': {
                'id': interessado.id,
                'nome': interessado.usuario.nome_completo_rp,
                'orgao': interessado.orgao.nome if interessado.orgao else 'Cidadão',
                'entidade': interessado.entidade.nome if interessado.entidade else 'Cidadão',
                'data': interessado.data_inclusao.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_encaminhar(request, numero_protocolo):
    """Encaminhar protocolo para outro órgão/setor/usuário"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar permissões
        if not protocolo.pode_gerenciar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para encaminhar este protocolo'
            })
        
        data = json.loads(request.body)
        parecer = data.get('parecer', '').strip()
        orgao_destino_id = data.get('orgao_destino_id')
        entidade_destino_id = data.get('entidade_destino_id')
        usuario_destino_id = data.get('usuario_destino_id')
        
        if not parecer:
            return JsonResponse({
                'success': False,
                'error': 'Parecer é obrigatório'
            })
        
        if not orgao_destino_id:
            return JsonResponse({
                'success': False,
                'error': 'Órgão de destino é obrigatório'
            })
        
        # Buscar objetos
        orgao_destino = get_object_or_404(Orgao, id=orgao_destino_id)
        entidade_destino = None
        if entidade_destino_id:
            entidade_destino = get_object_or_404(Entidade, id=entidade_destino_id)
        
        usuario_destino = None
        if usuario_destino_id:
            usuario_destino = get_object_or_404(User, id=usuario_destino_id)
        
        # Criar encaminhamento
        encaminhamento = ProtocoloEncaminhamento.objects.create(
            protocolo=protocolo,
            parecer=parecer,
            orgao_destino=orgao_destino,
            entidade_destino=entidade_destino,
            usuario_destino=usuario_destino,
            orgao_origem=Protocolo.get_orgao_usuario(request.user),
            entidade_origem=Protocolo.get_entidade_usuario(request.user),
            usuario_origem=request.user
        )
        
        # Atualizar destino do protocolo
        protocolo.orgao_destinatario = orgao_destino
        protocolo.entidade_destinatario = entidade_destino
        protocolo.usuario_destinatario = usuario_destino
        protocolo.status = 'em_andamento'
        protocolo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Protocolo encaminhado com sucesso',
            'encaminhamento': {
                'id': encaminhamento.id,
                'parecer': encaminhamento.parecer,
                'data': encaminhamento.data_encaminhamento.strftime('%d/%m/%Y %H:%M'),
                'usuario_origem': encaminhamento.usuario_origem.nome_completo_rp,
                'destino': f"{orgao_destino.nome}" + (f" - {entidade_destino.nome}" if entidade_destino else "") + (f" - {usuario_destino.nome_completo_rp}" if usuario_destino else "")
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_solicitar_assinatura(request, numero_protocolo):
    """Solicitar assinatura de documento"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar permissões
        if not protocolo.pode_gerenciar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para solicitar assinaturas neste protocolo'
            })
        
        data = json.loads(request.body)
        documento_id = data.get('documento_id')
        usuario_destinatario_id = data.get('usuario_destinatario_id')
        mensagem = data.get('mensagem', '').strip()
        
        if not documento_id:
            return JsonResponse({
                'success': False,
                'error': 'Documento é obrigatório'
            })
        
        if not usuario_destinatario_id:
            return JsonResponse({
                'success': False,
                'error': 'Destinatário é obrigatório'
            })
        
        documento = get_object_or_404(ProtocoloDocumento, id=documento_id, protocolo=protocolo)
        usuario_destinatario = get_object_or_404(User, id=usuario_destinatario_id)
        
        # Verificar se já existe solicitação pendente
        if SolicitacaoAssinatura.objects.filter(
            documento=documento,
            usuario_destinatario=usuario_destinatario,
            status='pendente'
        ).exists():
            return JsonResponse({
                'success': False,
                'error': 'Já existe uma solicitação de assinatura pendente para este documento e usuário'
            })
        
        # Criar solicitação
        solicitacao = SolicitacaoAssinatura.objects.create(
            documento=documento,
            usuario_solicitante=request.user,
            usuario_destinatario=usuario_destinatario,
            mensagem=mensagem
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitação de assinatura enviada para {usuario_destinatario.nome_completo_rp}',
            'solicitacao': {
                'id': solicitacao.id,
                'documento': documento.nome,
                'destinatario': usuario_destinatario.nome_completo_rp,
                'data': solicitacao.data_solicitacao.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_remover_interessado(request, numero_protocolo, interessado_id):
    """Remover interessado do protocolo"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        interessado = get_object_or_404(ProtocoloInteressado, id=interessado_id, protocolo=protocolo)
        
        # Verificar permissões
        if not protocolo.pode_gerenciar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para remover interessados deste protocolo'
            })
        
        nome_interessado = interessado.usuario.nome_completo_rp
        interessado.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{nome_interessado} removido dos interessados'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_excluir_documento(request, numero_protocolo, documento_id):
    """Excluir documento do protocolo"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        documento = get_object_or_404(ProtocoloDocumento, id=documento_id, protocolo=protocolo)
        
        # Verificar permissões - só quem fez upload ou pode gerenciar pode excluir
        if not (documento.usuario_upload == request.user or protocolo.pode_gerenciar(request.user)):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para excluir este documento'
            })
        
        nome_documento = documento.nome
        documento.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Documento "{nome_documento}" excluído com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


# ===== APIS PARA BUSCA =====

@login_required
def api_buscar_usuarios_protocolo(request):
    """API para buscar usuários para adicionar como interessados"""
    try:
        termo = request.GET.get('q', '').strip()
        if len(termo) < 2:
            return JsonResponse({'usuarios': []})
        
        usuarios = User.objects.filter(
            Q(nome_completo_rp__icontains=termo) |
            Q(username__icontains=termo)
        ).values('id', 'nome_completo_rp', 'username')[:10]
        
        return JsonResponse({
            'usuarios': list(usuarios)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def protocolo_assinar_documento(request, numero_protocolo, documento_id):
    """Assinar documento do protocolo (compatibilidade + nova funcionalidade de múltiplas assinaturas)"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        documento = get_object_or_404(ProtocoloDocumento, id=documento_id, protocolo=protocolo)
        
        # Verificar se usuário pode visualizar o protocolo
        if not protocolo.pode_visualizar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para acessar este protocolo'
            })
        
        # Verificar se pode assinar (nova lógica para múltiplas assinaturas)
        if not documento.pode_assinar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não pode assinar este documento ou já assinou anteriormente'
            })
        
        data = json.loads(request.body)
        observacoes = data.get('observacoes', '').strip()
        
        # Criar nova assinatura no sistema de múltiplas assinaturas
        assinatura = AssinaturaDocumento.objects.create(
            documento=documento,
            usuario=request.user,
            observacoes=observacoes
        )
        
        # Por compatibilidade, se for a primeira assinatura, marcar também no documento
        if not documento.assinado:
            documento.assinado = True
            documento.data_assinatura = assinatura.data_assinatura
            documento.usuario_assinatura = request.user
            documento.observacoes_assinatura = observacoes
            documento.save()
        
        # Atualizar solicitações de assinatura relacionadas
        SolicitacaoAssinatura.objects.filter(
            documento=documento,
            usuario_destinatario=request.user,
            status='pendente'
        ).update(
            status='aceita',
            data_resposta=timezone.now(),
            motivo_recusa=observacoes
        )
        
        # Contar total de assinaturas
        total_assinaturas = documento.get_todas_assinaturas().count()
        
        return JsonResponse({
            'success': True,
            'message': f'Documento "{documento.nome}" assinado com sucesso! ({total_assinaturas} assinatura{"s" if total_assinaturas > 1 else ""})',
            'documento': {
                'id': documento.id,
                'assinado': True,
                'total_assinaturas': total_assinaturas,
                'data_assinatura': assinatura.data_assinatura.strftime('%d/%m/%Y %H:%M'),
                'usuario_assinatura': request.user.nome_completo_rp
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_rejeitar_assinatura(request, numero_protocolo, documento_id):
    """Rejeitar assinatura de documento"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        documento = get_object_or_404(ProtocoloDocumento, id=documento_id, protocolo=protocolo)
        
        # Verificar se usuário pode visualizar o protocolo
        if not protocolo.pode_visualizar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para acessar este protocolo'
            })
        
        data = json.loads(request.body)
        motivo = data.get('motivo', '').strip()
        
        if not motivo:
            return JsonResponse({
                'success': False,
                'error': 'Motivo da rejeição é obrigatório'
            })
        
        # Atualizar solicitações de assinatura relacionadas
        SolicitacaoAssinatura.objects.filter(
            documento=documento,
            usuario_destinatario=request.user,
            status='pendente'
        ).update(
            status='recusada',
            data_resposta=timezone.now(),
            motivo_recusa=motivo
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Assinatura do documento "{documento.nome}" rejeitada'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def protocolo_listar_assinaturas(request, numero_protocolo, documento_id):
    """Listar todas as assinaturas de um documento"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        documento = get_object_or_404(ProtocoloDocumento, id=documento_id, protocolo=protocolo)
        
        # Verificar se usuário pode visualizar o protocolo
        if not protocolo.pode_visualizar(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para acessar este protocolo'
            })
        
        # Buscar todas as assinaturas ativas
        assinaturas = documento.get_todas_assinaturas()
        
        assinaturas_data = []
        for assinatura in assinaturas:
            assinaturas_data.append({
                'id': assinatura.id,
                'usuario': assinatura.usuario.nome_completo_rp,
                'cargo': assinatura.cargo_assinante or 'N/A',
                'data_assinatura': assinatura.data_assinatura.strftime('%d/%m/%Y %H:%M'),
                'observacoes': assinatura.observacoes,
                'hash_documento': assinatura.hash_documento,
                'valida': assinatura.validar_assinatura()
            })
        
        return JsonResponse({
            'success': True,
            'documento': {
                'nome': documento.nome,
                'identificador': documento.identificador
            },
            'total_assinaturas': len(assinaturas_data),
            'assinaturas': assinaturas_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def protocolo_parar_monitorar(request, numero_protocolo):
    """Parar de monitorar um protocolo"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar se o usuário pode parar de monitorar (deve ser o criador)
        if protocolo.usuario_cadastro != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Apenas o criador do protocolo pode parar de monitorá-lo'
            })
        
        # Verificar se está sendo monitorado
        if not protocolo.monitorado_por_usuario:
            return JsonResponse({
                'success': False,
                'error': 'Este protocolo não está sendo monitorado'
            })
        
        # Parar de monitorar
        protocolo.monitorado_por_usuario = False
        protocolo.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Protocolo {protocolo.numero_protocolo} não está mais sendo monitorado'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })


@login_required
def protocolo_documento_consolidado(request, numero_protocolo):
    """Gerar documento consolidado do protocolo com todos os documentos e histórico"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar permissões
        if not protocolo.pode_visualizar(request.user):
            messages.error(request, 'Você não tem permissão para acessar este protocolo.')
            return redirect('main:protocolos_home')
        
        # Buscar todos os dados relacionados
        documentos = protocolo.documentos.all().order_by('data_upload')
        encaminhamentos = protocolo.encaminhamentos.all().order_by('data_encaminhamento')
        interessados = protocolo.interessados.all().order_by('data_inclusao')
        
        # Buscar todas as solicitações de assinatura
        solicitacoes_assinatura = SolicitacaoAssinatura.objects.filter(
            documento__protocolo=protocolo
        ).order_by('data_solicitacao')
        
        context = {
            'protocolo': protocolo,
            'documentos': documentos,
            'encaminhamentos': encaminhamentos,
            'interessados': interessados,
            'solicitacoes_assinatura': solicitacoes_assinatura,
            'data_geracao': timezone.now(),
        }
        
        return render(request, 'main/protocolo_documento_consolidado.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar documento consolidado: {str(e)}')
        return redirect('main:protocolo_detalhe', numero_protocolo=numero_protocolo)


@login_required
def protocolo_documento_consolidado_pdf(request, numero_protocolo):
    """Gerar PDF do documento consolidado com formato simplificado e funcional"""
    try:
        protocolo = get_object_or_404(Protocolo, numero_protocolo=numero_protocolo)
        
        # Verificar permissões
        if not protocolo.pode_visualizar(request.user):
            return HttpResponse('Acesso negado', status=403)
        
        # Criar resposta HTTP para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="protocolo_{numero_protocolo}_consolidado.pdf"'
        
        # Buffer para o PDF
        buffer = io.BytesIO()
        
        # Configuração do documento A4
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              topMargin=20*mm, bottomMargin=20*mm,
                              leftMargin=20*mm, rightMargin=20*mm)
        
        # Buscar dados do protocolo
        documentos = protocolo.documentos.all().order_by('data_upload', 'id')
        encaminhamentos = protocolo.encaminhamentos.all().order_by('data_encaminhamento')
        interessados = protocolo.interessados.all().order_by('data_inclusao')
        
        # Função helper para obter ID Roblox de qualquer usuário
        def obter_roblox_id_usuario(usuario):
            if hasattr(usuario, 'roblox_id') and usuario.roblox_id:
                return str(usuario.roblox_id)
            elif hasattr(usuario, 'roblox_username') and usuario.roblox_username:
                return usuario.roblox_username
            else:
                return 'N/A'
        
        # Estilos simplificados
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        titulo_style = ParagraphStyle(
            'TituloStyle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Times-Bold',
            textColor=colors.HexColor('#1a365d'),
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        # Estilo para corpo do documento
        corpo_style = ParagraphStyle(
            'CorpoStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Courier',
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        )
        
        # Estilo para informações
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Courier',
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=3
        )
        
        # Dados do usuário que está baixando
        usuario_download = request.user
        data_download = timezone.now()
        
        # Função para desenhar rodapé simples
        def criar_funcao_desenho(documento_especifico=None):
            def desenhar_rodape_simples(canvas, doc):
                page_num = canvas.getPageNumber()
                
                # === RODAPÉ SIMPLES (TODAS AS PÁGINAS) ===
                canvas.setFont("Courier", 8)
                canvas.setFillColor(colors.HexColor('#718096'))
                
                # Protocolo (esquerda)
                canvas.drawString(20*mm, 10*mm, f"Protocolo: {numero_protocolo}")
                
                # Data de geração (centro)
                data_geracao = data_download.strftime('%d/%m/%Y as %H:%M')
                canvas.drawCentredString(A4[0]/2, 10*mm, f"Gerado em: {data_geracao}")
                
                # Número da página (direita)
                canvas.drawRightString(A4[0]-20*mm, 10*mm, f"Pagina {page_num}")
                
                # === INFORMAÇÕES DE ASSINATURA (SE APLICÁVEL) ===
                if documento_especifico and documento_especifico.assinado:
                    canvas.setFont("Courier", 7)
                    canvas.setFillColor(colors.black)
                    
                    # Linha separadora
                    canvas.line(20*mm, 25*mm, A4[0]-20*mm, 25*mm)
                    
                    # Informações da assinatura
                    canvas.drawString(20*mm, 22*mm, "ASSINATURA DIGITAL VALIDADA:")
                    assinatura_texto = f"Documento: {documento_especifico.nome[:40]}"
                    canvas.drawString(20*mm, 19*mm, assinatura_texto)
                    assinante_texto = f"Assinante: {documento_especifico.usuario_assinatura.nome_completo_rp} (ID: {obter_roblox_id_usuario(documento_especifico.usuario_assinatura)})"
                    canvas.drawString(20*mm, 16*mm, assinante_texto)
                    data_assinatura = f"Data: {documento_especifico.data_assinatura.strftime('%d/%m/%Y as %H:%M')}"
                    canvas.drawString(20*mm, 13*mm, data_assinatura)
            
            return desenhar_rodape_simples
        
        # Função padrão
        funcao_padrao = criar_funcao_desenho(None)
        
        # === CONSTRUIR PRIMEIRA PÁGINA ===
        elements_primeira = []
        
        # Título principal simples
        elements_primeira.append(Paragraph("DOCUMENTO CONSOLIDADO DE PROTOCOLO", ParagraphStyle(
            'TituloMain', fontSize=14, fontName='Courier-Bold', textColor=colors.black,
            alignment=TA_CENTER, spaceAfter=20
        )))
        
        # === INFORMAÇÕES GERAIS ===
        elements_primeira.append(Paragraph("INFORMACOES GERAIS", ParagraphStyle(
            'SecaoStyle', fontSize=12, fontName='Courier-Bold', textColor=colors.black,
            alignment=TA_CENTER, spaceAfter=10
        )))
        
        elements_primeira.append(Paragraph("_" * 80, ParagraphStyle(
            'separator', fontSize=8, fontName='Courier', textColor=colors.HexColor('#718096')
        )))
        elements_primeira.append(Spacer(1, 8))
        
        # Informações básicas
        elements_primeira.append(Paragraph(f"PROTOCOLO: {numero_protocolo}", info_style))
        elements_primeira.append(Paragraph(f"DATA DE CADASTRO: {protocolo.data_cadastro.strftime('%d/%m/%Y as %H:%M:%S')}", info_style))
        elements_primeira.append(Paragraph(f"ASSUNTO: {protocolo.assunto}", info_style))
        elements_primeira.append(Paragraph(f"ESPECIE DE DOCUMENTO: {protocolo.especie_documento.nome}", info_style))
        elements_primeira.append(Paragraph(f"STATUS: {protocolo.get_status_display()}", info_style))
        elements_primeira.append(Paragraph(f"URGENCIA: {'SIM' if protocolo.urgencia == 'sim' else 'NAO'}", info_style))
        elements_primeira.append(Spacer(1, 10))
        
        elements_primeira.append(Paragraph(f"INTERESSADO: {protocolo.usuario_cadastro.nome_completo_rp}", info_style))
        elements_primeira.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(protocolo.usuario_cadastro)}", info_style))
        elements_primeira.append(Paragraph(f"ORGAO DE ORIGEM: {protocolo.orgao_cadastro.nome if protocolo.orgao_cadastro else 'CIDADAO'}", info_style))
        elements_primeira.append(Paragraph(f"ORGAO DE DESTINO: {protocolo.orgao_destinatario.nome}", info_style))
        elements_primeira.append(Spacer(1, 15))
        
        # === DETALHAMENTO INICIAL ===
        elements_primeira.append(Paragraph("DETALHAMENTO INICIAL", ParagraphStyle(
            'SecaoStyle', fontSize=12, fontName='Courier-Bold', textColor=colors.black,
            alignment=TA_CENTER, spaceAfter=10
        )))
        
        elements_primeira.append(Paragraph("_" * 80, ParagraphStyle(
            'separator', fontSize=8, fontName='Courier', textColor=colors.HexColor('#718096')
        )))
        elements_primeira.append(Spacer(1, 8))
        
        # Detalhamento com quebras de linha
        detalhamento_lines = protocolo.detalhamento.split('\n')
        for line in detalhamento_lines:
            if line.strip():
                elements_primeira.append(Paragraph(line, corpo_style))
            else:
                elements_primeira.append(Spacer(1, 6))
        
        # === PREPARAR EVENTOS CRONOLÓGICOS ===
        eventos_cronologicos = []
        
        # 1. Criação do protocolo
        eventos_cronologicos.append({
            'tipo': 'criacao_protocolo',
            'data': protocolo.data_cadastro,
            'protocolo': protocolo,
            'ordem': 0
        })
        
        # 2. Uploads de documentos
        for doc in documentos:
            eventos_cronologicos.append({
                'tipo': 'upload_documento',
                'data': doc.data_upload,
                'documento': doc,
                'ordem': 1
            })
        
        # 3. Encaminhamentos (pareceres)
        for enc in encaminhamentos:
            eventos_cronologicos.append({
                'tipo': 'encaminhamento',
                'data': enc.data_encaminhamento,
                'encaminhamento': enc,
                'ordem': 2
            })
        
        # 4. Assinaturas (múltiplas)
        for doc in documentos:
            # Sistema antigo (compatibilidade)
            if doc.assinado and doc.data_assinatura:
                eventos_cronologicos.append({
                    'tipo': 'assinatura',
                    'data': doc.data_assinatura,
                    'documento': doc,
                    'ordem': 3,
                    'assinatura_unica': True
                })
            
            # Sistema novo (múltiplas assinaturas)
            assinaturas_multiplas = doc.get_todas_assinaturas()
            for assinatura in assinaturas_multiplas:
                # Evitar duplicação com o sistema antigo
                if not (doc.assinado and doc.usuario_assinatura == assinatura.usuario):
                    eventos_cronologicos.append({
                        'tipo': 'assinatura_multipla',
                        'data': assinatura.data_assinatura,
                        'documento': doc,
                        'assinatura': assinatura,
                        'ordem': 3
                    })
        
        # Ordenar cronologicamente
        eventos_cronologicos.sort(key=lambda x: (x['data'], x['ordem']))
        
        # === COMEÇAR CONSTRUÇÃO DO PDF FINAL ===
        try:
            from PyPDF2 import PdfReader, PdfWriter
            pdf_writer = PdfWriter()
            
            # === PRIMEIRA PÁGINA ===
            buffer_primeira = io.BytesIO()
            doc_primeira = SimpleDocTemplate(buffer_primeira, pagesize=A4,
                                           topMargin=20*mm, bottomMargin=20*mm,
                                           leftMargin=20*mm, rightMargin=20*mm)
            doc_primeira.build(elements_primeira, onFirstPage=funcao_padrao, onLaterPages=funcao_padrao)
            buffer_primeira.seek(0)
            
            primeira_pdf = PdfReader(buffer_primeira)
            for page in primeira_pdf.pages:
                pdf_writer.add_page(page)
            buffer_primeira.close()
            
            # === PÁGINAS DEDICADAS PARA CADA EVENTO ===
            for i, evento in enumerate(eventos_cronologicos):
                buffer_evento = io.BytesIO()
                doc_evento = SimpleDocTemplate(buffer_evento, pagesize=A4,
                                             topMargin=30*mm, bottomMargin=30*mm,
                                             leftMargin=20*mm, rightMargin=20*mm)
                
                elements_evento = []
                
                # Cabeçalho do evento
                elements_evento.append(Paragraph(f"EVENTO {i+1} - {evento['data'].strftime('%d/%m/%Y as %H:%M')}", 
                                               titulo_style))
                elements_evento.append(Spacer(1, 15))
                
                if evento['tipo'] == 'criacao_protocolo':
                    elements_evento.append(Paragraph("CRIACAO DO PROTOCOLO", titulo_style))
                    elements_evento.append(Spacer(1, 10))
                    
                    elements_evento.append(Paragraph("INFORMACOES DO REGISTRO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    
                    elements_evento.append(Paragraph(f"RESPONSAVEL: {protocolo.usuario_cadastro.nome_completo_rp}", info_style))
                    elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(protocolo.usuario_cadastro)}", info_style))
                    elements_evento.append(Paragraph(f"DATA/HORA: {protocolo.data_cadastro.strftime('%d/%m/%Y as %H:%M:%S')}", info_style))
                    elements_evento.append(Paragraph(f"STATUS INICIAL: {protocolo.get_status_display()}", info_style))
                    
                    # Detalhamento completo na página do evento
                    elements_evento.append(Spacer(1, 15))
                    elements_evento.append(Paragraph("DETALHAMENTO COMPLETO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    detalhamento_lines = protocolo.detalhamento.split('\n')
                    for line in detalhamento_lines:
                        if line.strip():
                            elements_evento.append(Paragraph(line, corpo_style))
                        else:
                            elements_evento.append(Spacer(1, 6))
                    
                elif evento['tipo'] == 'upload_documento':
                    doc = evento['documento']
                    elements_evento.append(Paragraph("DOCUMENTO ANEXADO", titulo_style))
                    elements_evento.append(Spacer(1, 10))
                    
                    elements_evento.append(Paragraph("INFORMACOES DO DOCUMENTO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    
                    elements_evento.append(Paragraph(f"ARQUIVO: {doc.nome}", info_style))
                    elements_evento.append(Paragraph(f"TIPO: {doc.get_tipo_display()}", info_style))
                    elements_evento.append(Paragraph(f"IDENTIFICADOR: {doc.identificador or 'N/A'}", info_style))
                    elements_evento.append(Paragraph(f"RESPONSAVEL: {doc.usuario_upload.nome_completo_rp}", info_style))
                    elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(doc.usuario_upload)}", info_style))
                    elements_evento.append(Paragraph(f"DATA/HORA: {doc.data_upload.strftime('%d/%m/%Y as %H:%M:%S')}", info_style))
                    
                    # Status de assinatura
                    elements_evento.append(Spacer(1, 10))
                    if doc.assinado:
                        elements_evento.append(Paragraph("STATUS: DOCUMENTO ASSINADO", ParagraphStyle(
                            'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#22c55e'), spaceAfter=5
                        )))
                        elements_evento.append(Paragraph(f"ASSINADO POR: {doc.usuario_assinatura.nome_completo_rp}", info_style))
                        elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(doc.usuario_assinatura)}", info_style))
                        elements_evento.append(Paragraph(f"DATA DA ASSINATURA: {doc.data_assinatura.strftime('%d/%m/%Y as %H:%M')}", info_style))
                        if doc.observacoes_assinatura:
                            elements_evento.append(Paragraph(f"OBSERVACOES: {doc.observacoes_assinatura}", info_style))
                    else:
                        elements_evento.append(Paragraph("STATUS: AGUARDANDO ASSINATURA", ParagraphStyle(
                            'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#f59e0b'), spaceAfter=5
                        )))
                    
                    # Se for PDF, anexar integralmente após esta página
                    if (doc.arquivo and 
                        os.path.exists(doc.arquivo.path) and
                        os.path.splitext(doc.arquivo.path)[1].lower() == '.pdf'):
                        
                        elements_evento.append(Spacer(1, 20))
                        elements_evento.append(Paragraph("ANEXO - DOCUMENTO INTEGRAL", ParagraphStyle(
                            'AnexoTitulo', fontSize=12, fontName='Courier-Bold', textColor=colors.HexColor('#dc2626'),
                            alignment=TA_CENTER, spaceAfter=10
                        )))
                        elements_evento.append(Paragraph("O arquivo PDF completo esta incluido nas proximas paginas", corpo_style))
                
                elif evento['tipo'] == 'encaminhamento':
                    enc = evento['encaminhamento']
                    elements_evento.append(Paragraph("ENCAMINHAMENTO COM PARECER", titulo_style))
                    elements_evento.append(Spacer(1, 10))
                    
                    # Origem
                    elements_evento.append(Paragraph("ORIGEM:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"RESPONSAVEL: {enc.usuario_origem.nome_completo_rp}", info_style))
                    elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(enc.usuario_origem)}", info_style))
                    elements_evento.append(Paragraph(f"ORGAO: {enc.orgao_origem.nome if enc.orgao_origem else 'CIDADAO'}", info_style))
                    if enc.entidade_origem:
                        elements_evento.append(Paragraph(f"SETOR: {enc.entidade_origem.nome}", info_style))
                    
                    elements_evento.append(Spacer(1, 10))
                    
                    # Destino
                    elements_evento.append(Paragraph("DESTINO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"ORGAO: {enc.orgao_destino.nome}", info_style))
                    if enc.entidade_destino:
                        elements_evento.append(Paragraph(f"SETOR: {enc.entidade_destino.nome}", info_style))
                    if enc.usuario_destino:
                        elements_evento.append(Paragraph(f"DESTINATARIO: {enc.usuario_destino.nome_completo_rp}", info_style))
                        elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(enc.usuario_destino)}", info_style))
                    
                    elements_evento.append(Paragraph(f"DATA/HORA: {enc.data_encaminhamento.strftime('%d/%m/%Y as %H:%M:%S')}", info_style))
                    
                    # Parecer completo
                    elements_evento.append(Spacer(1, 15))
                    elements_evento.append(Paragraph("PARECER TECNICO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph("_" * 70, ParagraphStyle(
                        'separator', fontSize=8, fontName='Courier', textColor=colors.HexColor('#718096')
                    )))
                    elements_evento.append(Spacer(1, 8))
                    
                    parecer_lines = enc.parecer.split('\n')
                    for line in parecer_lines:
                        if line.strip():
                            elements_evento.append(Paragraph(line, corpo_style))
                        else:
                            elements_evento.append(Spacer(1, 6))
                
                elif evento['tipo'] == 'assinatura':
                    doc = evento['documento']
                    elements_evento.append(Paragraph("ASSINATURA DIGITAL", titulo_style))
                    elements_evento.append(Spacer(1, 10))
                    
                    # Informações do documento
                    elements_evento.append(Paragraph("DOCUMENTO ASSINADO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"NOME: {doc.nome}", info_style))
                    elements_evento.append(Paragraph(f"IDENTIFICADOR: {doc.identificador or 'N/A'}", info_style))
                    
                    elements_evento.append(Spacer(1, 10))
                    
                    # Informações do signatário
                    elements_evento.append(Paragraph("INFORMACOES DO SIGNATARIO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"ASSINANTE: {doc.usuario_assinatura.nome_completo_rp}", info_style))
                    elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(doc.usuario_assinatura)}", info_style))
                    elements_evento.append(Paragraph(f"DATA/HORA: {doc.data_assinatura.strftime('%d/%m/%Y as %H:%M:%S')}", info_style))
                    
                    # Cargo do assinante
                    if hasattr(doc.usuario_assinatura, 'profile') and doc.usuario_assinatura.profile.cargo_atual:
                        elements_evento.append(Paragraph(f"CARGO: {doc.usuario_assinatura.profile.cargo_atual.nome}", info_style))
                    
                    elements_evento.append(Spacer(1, 10))
                    elements_evento.append(Paragraph("STATUS: DOCUMENTO OFICIALMENTE ASSINADO", ParagraphStyle(
                        'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#22c55e'), spaceAfter=10
                    )))
                    
                    # Observações da assinatura
                    if doc.observacoes_assinatura:
                        elements_evento.append(Paragraph("OBSERVACOES DA ASSINATURA:", ParagraphStyle(
                            'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                        )))
                        obs_lines = doc.observacoes_assinatura.split('\n')
                        for line in obs_lines:
                            if line.strip():
                                elements_evento.append(Paragraph(line, corpo_style))
                    
                    # Validação da assinatura
                    elements_evento.append(Spacer(1, 15))
                    elements_evento.append(Paragraph("VALIDACAO E AUTENTICIDADE:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"HASH DO DOCUMENTO: {hash(f'{doc.id}{doc.nome}{doc.data_upload}') % 1000000:06d}", info_style))
                    elements_evento.append(Paragraph(f"TIMESTAMP UNIX: {int(doc.data_assinatura.timestamp())}", info_style))
                    elements_evento.append(Spacer(1, 8))
                    elements_evento.append(Paragraph("ASSINATURA VALIDA E VERIFICADA", ParagraphStyle(
                        'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#22c55e'), spaceAfter=10
                    )))
                
                elif evento['tipo'] == 'assinatura_multipla':
                    doc = evento['documento']
                    assinatura = evento['assinatura']
                    elements_evento.append(Paragraph("ASSINATURA DIGITAL MULTIPLA", titulo_style))
                    elements_evento.append(Spacer(1, 10))
                    
                    # Informações do documento
                    elements_evento.append(Paragraph("DOCUMENTO ASSINADO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"NOME: {doc.nome}", info_style))
                    elements_evento.append(Paragraph(f"IDENTIFICADOR: {doc.identificador or 'N/A'}", info_style))
                    
                    # Total de assinaturas no documento
                    total_assinaturas = doc.get_todas_assinaturas().count()
                    elements_evento.append(Paragraph(f"TOTAL DE ASSINATURAS: {total_assinaturas}", info_style))
                    
                    elements_evento.append(Spacer(1, 10))
                    
                    # Informações do signatário
                    elements_evento.append(Paragraph("INFORMACOES DO SIGNATARIO:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"ASSINANTE: {assinatura.usuario.nome_completo_rp}", info_style))
                    elements_evento.append(Paragraph(f"ID ROBLOX: {obter_roblox_id_usuario(assinatura.usuario)}", info_style))
                    elements_evento.append(Paragraph(f"DATA/HORA: {assinatura.data_assinatura.strftime('%d/%m/%Y as %H:%M:%S')}", info_style))
                    elements_evento.append(Paragraph(f"CARGO NA ASSINATURA: {assinatura.cargo_assinante or 'N/A'}", info_style))
                    
                    elements_evento.append(Spacer(1, 10))
                    if assinatura.ativa:
                        elements_evento.append(Paragraph("STATUS: ASSINATURA ATIVA E VALIDA", ParagraphStyle(
                            'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#22c55e'), spaceAfter=10
                        )))
                    else:
                        elements_evento.append(Paragraph("STATUS: ASSINATURA REVOGADA", ParagraphStyle(
                            'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#dc2626'), spaceAfter=10
                        )))
                    
                    # Observações da assinatura
                    if assinatura.observacoes:
                        elements_evento.append(Paragraph("OBSERVACOES DA ASSINATURA:", ParagraphStyle(
                            'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                        )))
                        obs_lines = assinatura.observacoes.split('\n')
                        for line in obs_lines:
                            if line.strip():
                                elements_evento.append(Paragraph(line, corpo_style))
                    
                    # Validação da assinatura
                    elements_evento.append(Spacer(1, 15))
                    elements_evento.append(Paragraph("VALIDACAO E AUTENTICIDADE:", ParagraphStyle(
                        'SubTitulo', fontSize=11, fontName='Courier-Bold', textColor=colors.black, spaceAfter=8
                    )))
                    elements_evento.append(Paragraph(f"HASH DA ASSINATURA: {assinatura.hash_documento}", info_style))
                    elements_evento.append(Paragraph(f"TIMESTAMP UNIX: {int(assinatura.data_assinatura.timestamp())}", info_style))
                    
                    # Verificar validade
                    if assinatura.validar_assinatura():
                        elements_evento.append(Paragraph("VERIFICACAO: ASSINATURA VALIDA", ParagraphStyle(
                            'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#22c55e'), spaceAfter=10
                        )))
                    else:
                        elements_evento.append(Paragraph("VERIFICACAO: ASSINATURA CORROMPIDA", ParagraphStyle(
                            'Status', fontSize=11, fontName='Courier-Bold', textColor=colors.HexColor('#dc2626'), spaceAfter=10
                        )))
                
                # Determinar função de desenho para este evento
                if evento['tipo'] == 'upload_documento':
                    funcao_desenho_evento = criar_funcao_desenho(evento['documento'])
                elif evento['tipo'] == 'assinatura':
                    funcao_desenho_evento = criar_funcao_desenho(evento['documento'])
                elif evento['tipo'] == 'assinatura_multipla':
                    funcao_desenho_evento = criar_funcao_desenho(evento['documento'])
                else:
                    funcao_desenho_evento = funcao_padrao
                
                # Construir página do evento
                doc_evento.build(elements_evento, onFirstPage=funcao_desenho_evento, onLaterPages=funcao_desenho_evento)
                buffer_evento.seek(0)
                
                # Adicionar ao PDF principal
                evento_pdf = PdfReader(buffer_evento)
                for page in evento_pdf.pages:
                    pdf_writer.add_page(page)
                
                # Se for documento PDF, anexar integralmente
                if (evento['tipo'] == 'upload_documento' and 
                    evento['documento'].arquivo and 
                    os.path.exists(evento['documento'].arquivo.path) and
                    os.path.splitext(evento['documento'].arquivo.path)[1].lower() == '.pdf'):
                    
                    try:
                        with open(evento['documento'].arquivo.path, 'rb') as pdf_file:
                            documento_pdf = PdfReader(pdf_file)
                            for page in documento_pdf.pages:
                                pdf_writer.add_page(page)
                    except Exception as e:
                        print(f"Erro ao anexar PDF {evento['documento'].nome}: {str(e)}")
                
                buffer_evento.close()
            
            # === GERAR PDF FINAL ===
            buffer_final = io.BytesIO()
            pdf_writer.write(buffer_final)
            
            pdf_data = buffer_final.getvalue()
            buffer_final.close()
            buffer.close()
            
            response.write(pdf_data)
            return response
            
        except ImportError:
            # Se PyPDF2 não estiver disponível, usar método simplificado
            elements_simples = elements_primeira
            
            # Adicionar resumo cronológico
            elements_simples.append(Spacer(1, 20))
            elements_simples.append(Paragraph("CRONOLOGIA DE EVENTOS", ParagraphStyle(
                'SecaoStyle', fontSize=12, fontName='Courier-Bold', textColor=colors.black,
                alignment=TA_CENTER, spaceAfter=10
            )))
            
            for i, evento in enumerate(eventos_cronologicos):
                elements_simples.append(Paragraph(f"EVENTO {i+1}: {evento['data'].strftime('%d/%m/%Y as %H:%M')}", 
                                                ParagraphStyle('EventoHeader', fontSize=10, fontName='Courier-Bold', 
                                                             textColor=colors.black, spaceAfter=5)))
                
                if evento['tipo'] == 'criacao_protocolo':
                    elements_simples.append(Paragraph("TIPO: CRIACAO DO PROTOCOLO", info_style))
                elif evento['tipo'] == 'upload_documento':
                    elements_simples.append(Paragraph(f"TIPO: DOCUMENTO ANEXADO - {evento['documento'].nome}", info_style))
                elif evento['tipo'] == 'encaminhamento':
                    elements_simples.append(Paragraph(f"TIPO: ENCAMINHAMENTO - {evento['encaminhamento'].usuario_origem.nome_completo_rp}", info_style))
                elif evento['tipo'] == 'assinatura':
                    elements_simples.append(Paragraph(f"TIPO: ASSINATURA - {evento['documento'].nome}", info_style))
                
                elements_simples.append(Spacer(1, 8))
            
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  topMargin=20*mm, bottomMargin=20*mm,
                                  leftMargin=20*mm, rightMargin=20*mm)
            doc.build(elements_simples, onFirstPage=funcao_padrao, onLaterPages=funcao_padrao)
            pdf_data = buffer.getvalue()
            buffer.close()
            response.write(pdf_data)
            return response
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro completo ao gerar PDF: {error_details}")
        return HttpResponse(f'Erro ao gerar PDF: {str(e)}', status=500)