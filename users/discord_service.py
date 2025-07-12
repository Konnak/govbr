import requests
import secrets
import urllib.parse
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class DiscordOAuthService:
    """Serviço para integração com Discord OAuth2"""
    
    def __init__(self):
        self.client_id = settings.DISCORD_CLIENT_ID
        self.client_secret = settings.DISCORD_CLIENT_SECRET
        self.redirect_uri = settings.DISCORD_REDIRECT_URI
        self.api_endpoint = settings.DISCORD_API_ENDPOINT
        self.auth_url = settings.DISCORD_AUTHORIZATION_BASE_URL
        self.token_url = settings.DISCORD_TOKEN_URL
    
    def generate_auth_url(self, user_id):
        """Gera URL de autorização do Discord"""
        state = secrets.token_urlsafe(32)
        
        # Armazenar state no cache por 10 minutos
        cache.set(f'discord_state_{state}', user_id, 600)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'identify email',
            'state': state,
            'prompt': 'consent'
        }
        
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"
    
    def validate_state(self, state):
        """Valida o state e retorna o user_id"""
        user_id = cache.get(f'discord_state_{state}')
        if user_id:
            cache.delete(f'discord_state_{state}')
            return user_id
        return None
    
    def exchange_code_for_token(self, code):
        """Troca o código de autorização por tokens de acesso"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao trocar código por token: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Obtém informações do usuário do Discord"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f'{self.api_endpoint}/users/@me', headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao obter informações do usuário: {e}")
            return None
    
    def refresh_access_token(self, refresh_token):
        """Renova o token de acesso usando o refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao renovar token: {e}")
            return None
    
    def revoke_token(self, access_token):
        """Revoga o token de acesso"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'token': access_token,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(f'{self.api_endpoint}/oauth2/token/revoke', data=data, headers=headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Erro ao revogar token: {e}")
            return False
    
    def link_discord_account(self, user, discord_data, tokens):
        """Vincula conta do Discord ao usuário"""
        try:
            # Verificar se o Discord ID já está vinculado a outro usuário
            from .models import User
            existing_user = User.objects.filter(
                discord_id=discord_data['id']
            ).exclude(id=user.id).first()
            
            if existing_user:
                return {
                    'success': False,
                    'error': 'Esta conta do Discord já está vinculada a outro usuário.'
                }
            
            # Vincular dados do Discord
            user.discord_id = discord_data['id']
            user.discord_username = discord_data['username']
            user.discord_display_name = discord_data.get('global_name') or discord_data.get('display_name', '')
            user.discord_avatar = discord_data.get('avatar', '')
            user.discord_email = discord_data.get('email', '')
            user.discord_access_token = tokens['access_token']
            user.discord_refresh_token = tokens.get('refresh_token', '')
            user.discord_vinculado = True
            user.discord_data_vinculacao = timezone.now()
            user.save()
            
            logger.info(f"Discord vinculado com sucesso para usuário {user.username}")
            
            return {
                'success': True,
                'message': 'Discord vinculado com sucesso!',
                'discord_data': {
                    'id': discord_data['id'],
                    'username': discord_data['username'],
                    'display_name': user.discord_display_name,
                    'avatar_url': user.get_discord_avatar_url()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao vincular Discord: {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor. Tente novamente.'
            }
    
    def unlink_discord_account(self, user):
        """Desvincula conta do Discord do usuário"""
        try:
            # Revogar token se existir
            if user.discord_access_token:
                self.revoke_token(user.discord_access_token)
            
            # Limpar dados do Discord
            user.desvincular_discord()
            
            logger.info(f"Discord desvinculado com sucesso para usuário {user.username}")
            
            return {
                'success': True,
                'message': 'Discord desvinculado com sucesso!'
            }
            
        except Exception as e:
            logger.error(f"Erro ao desvincular Discord: {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor. Tente novamente.'
            } 