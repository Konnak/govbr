from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.exceptions import ValidationError
import requests
import json
import re

from .models import User, SolicitacaoAlteracaoNome, SolicitacaoCidadania, LogAcesso


def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_roblox_user_info(roblox_id, size="420x420"):
    """Obtém informações do usuário do Roblox via API"""
    try:
        # API para obter informações básicas do usuário
        response = requests.get(f'https://users.roblox.com/v1/users/{roblox_id}')
        if response.status_code == 200:
            user_data = response.json()
            
            # API para obter avatar
            avatar_response = requests.get(f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size={size}&format=Png&isCircular=false')
            avatar_url = ''
            if avatar_response.status_code == 200:
                avatar_data = avatar_response.json()
                if avatar_data.get('data') and len(avatar_data['data']) > 0:
                    avatar_url = avatar_data['data'][0].get('imageUrl', '')
            
            return {
                'id': user_data.get('id'),
                'username': user_data.get('name'),
                'display_name': user_data.get('displayName'),
                'description': user_data.get('description', ''),
                'avatar_url': avatar_url,
                'created': user_data.get('created'),
                'is_banned': user_data.get('isBanned', False)
            }
    except Exception as e:
        print(f"Erro ao obter dados do Roblox: {e}")
    
    return None


def verificar_codigo_perfil_roblox(roblox_id, codigo):
    """Verifica se o código está na descrição do perfil do Roblox"""
    try:
        user_info = get_roblox_user_info(roblox_id)
        if user_info and user_info.get('description'):
            return codigo in user_info['description']
    except Exception as e:
        print(f"Erro ao verificar código no perfil: {e}")
    
    return False


@require_http_methods(["POST"])
def registro_step1(request):
    """Primeiro passo do registro - dados básicos"""
    try:
        data = json.loads(request.body)
        nome_completo = data.get('nome_completo', '').strip()
        roblox_id = data.get('roblox_id', '').strip()
        
        # Validações
        if not nome_completo or len(nome_completo) < 3:
            return JsonResponse({
                'success': False, 
                'error': 'Nome completo deve ter pelo menos 3 caracteres'
            })
        
        if not roblox_id or not roblox_id.isdigit():
            return JsonResponse({
                'success': False, 
                'error': 'ID do Roblox deve ser um número válido'
            })
        
        roblox_id = int(roblox_id)
        
        # Verificar se o ID do Roblox já está em uso
        if User.objects.filter(roblox_id=roblox_id).exists():
            return JsonResponse({
                'success': False, 
                'error': 'Este ID do Roblox já está cadastrado'
            })
        
        # Obter dados do Roblox
        roblox_data = get_roblox_user_info(roblox_id)
        if not roblox_data:
            return JsonResponse({
                'success': False, 
                'error': 'ID do Roblox não encontrado ou inválido'
            })
        
        if roblox_data.get('is_banned'):
            return JsonResponse({
                'success': False, 
                'error': 'Esta conta do Roblox está banida'
            })
        
        # Salvar dados na sessão
        request.session['registro_data'] = {
            'nome_completo': nome_completo,
            'roblox_id': roblox_id,
            'roblox_username': roblox_data.get('username'),
            'avatar_url': roblox_data.get('avatar_url', '')
        }
        
        return JsonResponse({
            'success': True,
            'roblox_username': roblox_data.get('username'),
            'avatar_url': roblox_data.get('avatar_url', ''),
            'next_step': 'verification'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@require_http_methods(["POST"])
def registro_step2(request):
    """Segundo passo - gerar código de verificação"""
    try:
        registro_data = request.session.get('registro_data')
        if not registro_data:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        # Gerar código de verificação
        import secrets
        import string
        codigo = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # Salvar código na sessão
        request.session['codigo_verificacao'] = codigo
        
        return JsonResponse({
            'success': True,
            'codigo': codigo,
            'roblox_username': registro_data.get('roblox_username'),
            'instrucoes': f'Adicione o código "{codigo}" na descrição do seu perfil do Roblox e clique em "Verificar Código"'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@require_http_methods(["POST"])
def verificar_codigo_roblox(request):
    """Verificar se o código está no perfil do Roblox"""
    try:
        registro_data = request.session.get('registro_data')
        codigo = request.session.get('codigo_verificacao')
        
        if not registro_data or not codigo:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        roblox_id = registro_data.get('roblox_id')
        
        # Verificar código no perfil
        if verificar_codigo_perfil_roblox(roblox_id, codigo):
            return JsonResponse({
                'success': True,
                'message': 'Código verificado com sucesso! Agora você pode criar sua senha.',
                'next_step': 'password'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Código não encontrado na descrição do seu perfil. Certifique-se de que adicionou o código corretamente.'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@require_http_methods(["POST"])
def registro_step3(request):
    """Terceiro passo - criar senha e finalizar registro"""
    try:
        data = json.loads(request.body)
        password = data.get('password', '').strip()
        password_confirm = data.get('password_confirm', '').strip()
        
        registro_data = request.session.get('registro_data')
        codigo = request.session.get('codigo_verificacao')
        
        if not registro_data or not codigo:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        # Validar senhas
        if not password or len(password) < 8:
            return JsonResponse({'success': False, 'error': 'A senha deve ter pelo menos 8 caracteres'})
        
        if password != password_confirm:
            return JsonResponse({'success': False, 'error': 'As senhas não coincidem'})
        
        # Verificar novamente o código (segurança)
        roblox_id = registro_data.get('roblox_id')
        if not verificar_codigo_perfil_roblox(roblox_id, codigo):
            return JsonResponse({'success': False, 'error': 'Código de verificação não encontrado'})
        
        # Criar usuário
        username = f"user_{roblox_id}"  # Username único baseado no ID
        
        user = User.objects.create_user(
            username=username,
            password=password,
            nome_completo_rp=registro_data.get('nome_completo'),
            roblox_id=roblox_id,
            roblox_username=registro_data.get('roblox_username'),
            avatar_url=registro_data.get('avatar_url', ''),
            verificado=True,
            data_verificacao=timezone.now()
        )
        
        # Limpar sessão
        if 'registro_data' in request.session:
            del request.session['registro_data']
        if 'codigo_verificacao' in request.session:
            del request.session['codigo_verificacao']
        
        # Log de acesso
        LogAcesso.objects.create(
            usuario=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            sucesso=True
        )
        
        # Fazer login automático
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Conta criada com sucesso! Bem-vindo ao GovBR Roleplay!',
            'redirect': '/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@require_http_methods(["POST"])
def login_view(request):
    """View para login via API - suporta username, Roblox ID ou Roblox username"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Usuário e senha são obrigatórios'
            })
        
        logger.info(f"Tentativa de login com: '{username}'")
        
        user = None
        user_obj = None
        
        # MÉTODO 1: Tenta autenticar primeiro com o username direto (Django)
        user = authenticate(request, username=username, password=password)
        if user:
            logger.info(f"Login bem-sucedido via username Django: {username}")
        
        # MÉTODO 2: Se não encontrou e o valor é numérico, tenta buscar por Roblox ID
        if user is None and username.isdigit():
            try:
                roblox_id = int(username)
                user_obj = User.objects.get(roblox_id=roblox_id)
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    logger.info(f"Login bem-sucedido via Roblox ID: {roblox_id} -> {user_obj.username}")
            except (User.DoesNotExist, ValueError) as e:
                logger.info(f"Usuário não encontrado com Roblox ID: {username} - {e}")
        
        # MÉTODO 3: Se ainda não encontrou, tenta buscar por Roblox username (case-insensitive)
        if user is None:
            try:
                # Busca case-insensitive e garante que o campo não está vazio
                user_obj = User.objects.filter(
                    roblox_username__iexact=username,
                    roblox_username__isnull=False
                ).exclude(roblox_username='').get()
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    logger.info(f"Login bem-sucedido via Roblox username: {username} -> {user_obj.username}")
            except User.DoesNotExist:
                logger.info(f"Usuário não encontrado com Roblox username: {username}")
            except User.MultipleObjectsReturned:
                logger.warning(f"Múltiplos usuários encontrados com Roblox username: {username}")
                # Em caso de múltiplos usuários, pega o primeiro ativo
                try:
                    user_obj = User.objects.filter(
                        roblox_username__iexact=username,
                        roblox_username__isnull=False,
                        is_active=True
                    ).exclude(roblox_username='').first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                        if user:
                            logger.info(f"Login bem-sucedido via Roblox username (múltiplos): {username} -> {user_obj.username}")
                except Exception as e:
                    logger.error(f"Erro ao lidar com múltiplos usuários: {e}")
        
        # MÉTODO 4: Se ainda não encontrou, tenta buscar por username case-insensitive
        if user is None:
            try:
                user_obj = User.objects.get(username__iexact=username)
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    logger.info(f"Login bem-sucedido via username case-insensitive: {username} -> {user_obj.username}")
            except User.DoesNotExist:
                logger.info(f"Usuário não encontrado com username case-insensitive: {username}")
        
        # Verificar se o login foi bem-sucedido
        if user is not None and user.is_active:
            # Fazer login
            login(request, user)
            
            # Atualizar último login
            user.data_ultimo_login = timezone.now()
            user.save(update_fields=['data_ultimo_login'])
            
            # Registrar log de acesso com sucesso
            LogAcesso.objects.create(
                usuario=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                sucesso=True
            )
            
            logger.info(f"Login realizado com sucesso para: {user.username} ({user.nome_completo_rp})")
            messages.success(request, 'Login realizado com sucesso!')
            
            return JsonResponse({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': '/'
            })
        else:
            # Registrar tentativa de login mal-sucedida
            if user_obj:
                LogAcesso.objects.create(
                    usuario=user_obj,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    sucesso=False
                )
            
            logger.warning(f"Tentativa de login falhada para: {username}")
            
            # Mensagem de erro mais específica baseada no que foi encontrado
            if user_obj and not user:
                error_msg = 'Senha incorreta. Verifique sua senha e tente novamente.'
            elif user and not user.is_active:
                error_msg = 'Conta desativada. Entre em contato com o suporte.'
            else:
                error_msg = 'Credenciais inválidas. Verifique seu usuário/ID/username do Roblox e senha.'
            
            return JsonResponse({
                'success': False,
                'error': error_msg
            })
            
    except json.JSONDecodeError:
        logger.error("Dados JSON inválidos na tentativa de login")
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        logger.error(f"Erro interno na tentativa de login: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


def logout_view(request):
    """View para logout"""
    messages.success(request, 'Logout realizado com sucesso!')
    logout(request)
    return redirect('main:home')


@login_required
def perfil_view(request):
    """View para exibir perfil do usuário"""
    context = {
        'user': request.user,
        'solicitacoes_nome': SolicitacaoAlteracaoNome.objects.filter(usuario=request.user),
        'solicitacao_cidadania': SolicitacaoCidadania.objects.filter(usuario=request.user).first(),
        'logs_acesso': LogAcesso.objects.filter(usuario=request.user)[:10]
    }
    return render(request, 'users/perfil.html', context)


@login_required
@require_http_methods(["POST"])
def alterar_senha(request):
    """Altera a senha do usuário"""
    try:
        data = json.loads(request.body)
        senha_atual = data.get('senha_atual', '').strip()
        nova_senha = data.get('nova_senha', '').strip()
        confirmar_senha = data.get('confirmar_senha', '').strip()
        
        # Validações
        if not senha_atual or not nova_senha or not confirmar_senha:
            return JsonResponse({
                'success': False,
                'error': 'Todos os campos são obrigatórios'
            })
            
        if nova_senha != confirmar_senha:
            return JsonResponse({
                'success': False,
                'error': 'As senhas não coincidem'
            })
            
        if len(nova_senha) < 8:
            return JsonResponse({
                'success': False,
                'error': 'A senha deve ter pelo menos 8 caracteres'
            })
            
        # Verificar senha atual
        if not request.user.check_password(senha_atual):
            return JsonResponse({
                'success': False,
                'error': 'Senha atual incorreta'
            })
            
        # Alterar senha
        request.user.set_password(nova_senha)
        request.user.save()
        
        # Fazer login novamente com a nova senha
        login(request, request.user)
        
        messages.success(request, 'Senha alterada com sucesso!')
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def solicitar_alteracao_nome(request):
    """Solicita alteração de nome"""
    try:
        data = json.loads(request.body)
        novo_nome = data.get('novo_nome', '').strip()
        motivo = data.get('motivo', '').strip()
        
        # Validações
        if not novo_nome or len(novo_nome) < 3:
            return JsonResponse({
                'success': False,
                'error': 'O novo nome deve ter pelo menos 3 caracteres'
            })
            
        if not motivo or len(motivo) < 10:
            return JsonResponse({
                'success': False,
                'error': 'O motivo deve ter pelo menos 10 caracteres'
            })
            
        # Verificar se já existe solicitação pendente
        if SolicitacaoAlteracaoNome.objects.filter(
            usuario=request.user,
            status='pendente'
        ).exists():
            return JsonResponse({
                'success': False,
                'error': 'Você já possui uma solicitação pendente'
            })
            
        # Criar solicitação
        SolicitacaoAlteracaoNome.objects.create(
            usuario=request.user,
            novo_nome=novo_nome,
            motivo=motivo
        )
        
        messages.success(request, 'Solicitação de alteração de nome enviada com sucesso!')
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def solicitar_cidadania(request):
    """Solicita cidadania brasileira"""
    try:
        data = json.loads(request.body)
        motivo = data.get('motivo', '').strip()
        
        # Validação básica
        if not motivo or len(motivo) < 50:
            return JsonResponse({
                'success': False,
                'error': 'O motivo deve ter pelo menos 50 caracteres'
            })
            
        # Verificar se já é cidadão
        if request.user.is_cidadao:
            return JsonResponse({
                'success': False,
                'error': 'Você já é cidadão brasileiro'
            })
            
        # Verificar se já existe solicitação pendente
        if SolicitacaoCidadania.objects.filter(
            usuario=request.user,
            status__in=['pendente', 'em_analise', 'documentos_pendentes']
        ).exists():
            return JsonResponse({
                'success': False,
                'error': 'Você já possui uma solicitação em andamento'
            })
            
        # Verificar se tem solicitação aprovada (não pode solicitar mais)
        if SolicitacaoCidadania.objects.filter(
            usuario=request.user,
            status='aprovada'
        ).exists():
            return JsonResponse({
                'success': False,
                'error': 'Você já teve uma solicitação de cidadania aprovada'
            })
            
        # Verificar se o sistema está ativo
        from main.models import ConfiguracaoCidadania
        config = ConfiguracaoCidadania.objects.first()
        if config and not config.ativo:
            return JsonResponse({
                'success': False,
                'error': 'O sistema de cidadania está temporariamente desabilitado'
            })
            
        # Criar solicitação com dados básicos (campos opcionais ficam em branco)
        solicitacao = SolicitacaoCidadania.objects.create(
            usuario=request.user,
            nome_completo=request.user.nome_completo_rp,  # Usar nome do RP como padrão
            nome_rp=request.user.nome_completo_rp,
            email=request.user.email or '',  # Email do usuário ou vazio
            motivo=motivo
        )
        
        messages.success(request, f'Solicitação de cidadania enviada com sucesso! Protocolo: {solicitacao.numero_protocolo}')
        return JsonResponse({
            'success': True,
            'protocolo': solicitacao.numero_protocolo
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


@login_required
def iniciar_vinculacao_discord(request):
    """Inicia o processo de vinculação com o Discord"""
    try:
        # Gerar URL de autorização do Discord
        from .discord_service import get_discord_auth_url
        auth_url = get_discord_auth_url()
        
        messages.info(request, 'Redirecionando para autenticação do Discord...')
        return JsonResponse({'success': True, 'url': auth_url})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


def discord_callback(request):
    """Callback do OAuth do Discord"""
    try:
        from .discord_service import (
            get_discord_tokens,
            get_discord_user,
            save_discord_info
        )
        
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'Código de autorização não fornecido')
            return redirect('users:perfil')
            
        # Obter tokens do Discord
        tokens = get_discord_tokens(code)
        if not tokens:
            messages.error(request, 'Erro ao obter tokens do Discord')
            return redirect('users:perfil')
            
        # Obter informações do usuário
        user_info = get_discord_user(tokens['access_token'])
        if not user_info:
            messages.error(request, 'Erro ao obter informações do Discord')
            return redirect('users:perfil')
            
        # Salvar informações do Discord
        save_discord_info(request.user, tokens, user_info)
        
        messages.success(request, 'Conta do Discord vinculada com sucesso!')
        return redirect('users:perfil')
        
    except Exception as e:
        messages.error(request, f'Erro ao vincular conta do Discord: {str(e)}')
        return redirect('users:perfil')


@login_required
@require_http_methods(["POST"])
def desvincular_discord(request):
    """Desvincula a conta do Discord"""
    try:
        if not request.user.discord_id:
            return JsonResponse({
                'success': False,
                'error': 'Você não possui uma conta do Discord vinculada'
            })
            
        # Limpar informações do Discord
        request.user.discord_id = None
        request.user.discord_username = None
        request.user.discord_avatar = None
        request.user.discord_access_token = None
        request.user.discord_refresh_token = None
        request.user.discord_token_expires_at = None
        request.user.save()
        
        messages.success(request, 'Conta do Discord desvinculada com sucesso!')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})


# Manter função antiga para compatibilidade (será removida depois)
@login_required
@require_http_methods(["POST"])
def vincular_discord(request):
    """Redireciona para nova implementação OAuth"""
    return iniciar_vinculacao_discord(request)


# Views AJAX para seleção hierárquica de cargos no admin
from django.contrib.admin.views.decorators import staff_member_required
from main.models import Poder, Orgao, Entidade, Cargo


@staff_member_required
@require_http_methods(["POST"])
def ajax_orgaos(request):
    """Retorna órgãos baseado no poder selecionado"""
    try:
        data = json.loads(request.body)
        poder_id = data.get('poder_id')
        
        if not poder_id:
            return JsonResponse({'orgaos': []})
        
        orgaos = Orgao.objects.filter(poder_id=poder_id).values('id', 'nome').order_by('nome')
        
        return JsonResponse({
            'success': True,
            'orgaos': list(orgaos)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'orgaos': []
        })


@staff_member_required
@require_http_methods(["POST"])
def ajax_entidades(request):
    """Retorna entidades baseado no órgão selecionado"""
    try:
        data = json.loads(request.body)
        orgao_id = data.get('orgao_id')
        
        if not orgao_id:
            return JsonResponse({'entidades': []})
        
        entidades = Entidade.objects.filter(orgao_id=orgao_id).values('id', 'nome').order_by('nome')
        
        return JsonResponse({
            'success': True,
            'entidades': list(entidades)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'entidades': []
        })


@staff_member_required
@require_http_methods(["POST"])
def ajax_cargos(request):
    """Retorna cargos baseado na entidade selecionada"""
    try:
        data = json.loads(request.body)
        entidade_id = data.get('entidade_id')
        
        if not entidade_id:
            return JsonResponse({'cargos': []})
        
        cargos = Cargo.objects.filter(entidade_id=entidade_id).values('id', 'nome', 'simbolo_gestao').order_by('nome')
        
        # Adicionar informação do símbolo para exibição
        cargos_list = []
        for cargo in cargos:
            simbolo_display = dict(Cargo.SIMBOLO_CHOICES).get(cargo['simbolo_gestao'], '')
            cargos_list.append({
                'id': cargo['id'],
                'nome': f"{cargo['nome']} ({simbolo_display})" if simbolo_display != 'Nenhum' else cargo['nome']
            })
        
        return JsonResponse({
            'success': True,
            'cargos': cargos_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'cargos': []
        })
