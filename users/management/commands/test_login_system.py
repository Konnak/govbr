from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from users.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Testa o sistema de login com ID Roblox e username Roblox'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-user',
            action='store_true',
            help='Cria um usuário de teste para demonstração',
        )
        parser.add_argument(
            '--test-login',
            type=str,
            help='Testa login com o valor fornecido (ID ou username)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Sistema de Login com ID/Username Roblox - Teste')
        )
        self.stdout.write('=' * 50)

        if options['create_test_user']:
            self.create_test_user()

        if options['test_login']:
            self.test_login_methods(options['test_login'])

        # Mostrar estatísticas dos usuários
        self.show_user_stats()

    def create_test_user(self):
        """Cria um usuário de teste"""
        self.stdout.write('\n📝 Criando usuário de teste...')
        
        # Dados de teste
        test_data = {
            'username': 'test_user_12345',
            'nome_completo_rp': 'João Silva Test',
            'roblox_id': 12345678901,
            'roblox_username': 'TestUser123',
            'password': 'senha123456',
            'nivel_acesso': 'cidadao',
            'verificado': True,
            'data_verificacao': timezone.now(),
        }
        
        # Verificar se já existe
        if User.objects.filter(roblox_id=test_data['roblox_id']).exists():
            self.stdout.write(
                self.style.WARNING('⚠️  Usuário de teste já existe!')
            )
            user = User.objects.get(roblox_id=test_data['roblox_id'])
        else:
            # Criar usuário
            user = User.objects.create_user(**test_data)
            self.stdout.write(
                self.style.SUCCESS('✅ Usuário de teste criado com sucesso!')
            )
        
        # Mostrar dados do usuário criado
        self.stdout.write(f'👤 Username: {user.username}')
        self.stdout.write(f'🆔 Roblox ID: {user.roblox_id}')
        self.stdout.write(f'👤 Roblox Username: {user.roblox_username}')
        self.stdout.write(f'🔑 Senha de teste: senha123456')

    def test_login_methods(self, login_value):
        """Testa diferentes métodos de login"""
        self.stdout.write(f'\n🔍 Testando login com: "{login_value}"')
        self.stdout.write('-' * 30)

        # Método 1: Username direto
        user = self.find_user_by_username(login_value)
        if user:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Encontrado por username: {user.username}')
            )

        # Método 2: Roblox ID (se for numérico)
        if login_value.isdigit():
            user = self.find_user_by_roblox_id(login_value)
            if user:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Encontrado por Roblox ID: {user.roblox_id} -> {user.username}')
                )

        # Método 3: Roblox Username
        user = self.find_user_by_roblox_username(login_value)
        if user:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Encontrado por Roblox username: {user.roblox_username} -> {user.username}')
            )

        # Método 4: Username case-insensitive
        user = self.find_user_by_username_icase(login_value)
        if user:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Encontrado por username (case-insensitive): {user.username}')
            )

        # Se nenhum método encontrou
        if not any([
            self.find_user_by_username(login_value),
            self.find_user_by_roblox_id(login_value) if login_value.isdigit() else None,
            self.find_user_by_roblox_username(login_value),
            self.find_user_by_username_icase(login_value)
        ]):
            self.stdout.write(
                self.style.ERROR(f'❌ Nenhum usuário encontrado com: "{login_value}"')
            )

    def find_user_by_username(self, username):
        """Busca por username exato"""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def find_user_by_roblox_id(self, roblox_id):
        """Busca por Roblox ID"""
        try:
            return User.objects.get(roblox_id=int(roblox_id))
        except (User.DoesNotExist, ValueError):
            return None

    def find_user_by_roblox_username(self, roblox_username):
        """Busca por Roblox username (case-insensitive)"""
        try:
            return User.objects.filter(
                roblox_username__iexact=roblox_username,
                roblox_username__isnull=False
            ).exclude(roblox_username='').get()
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def find_user_by_username_icase(self, username):
        """Busca por username case-insensitive"""
        try:
            return User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return None

    def show_user_stats(self):
        """Mostra estatísticas dos usuários"""
        self.stdout.write('\n📊 Estatísticas do Sistema')
        self.stdout.write('-' * 30)
        
        total_users = User.objects.count()
        users_with_roblox_username = User.objects.exclude(
            roblox_username__isnull=True
        ).exclude(roblox_username='').count()
        verified_users = User.objects.filter(verificado=True).count()
        
        self.stdout.write(f'👥 Total de usuários: {total_users}')
        self.stdout.write(f'🎮 Usuários com Roblox username: {users_with_roblox_username}')
        self.stdout.write(f'✅ Usuários verificados: {verified_users}')
        
        if total_users > 0:
            self.stdout.write('\n🔍 Exemplos de teste:')
            self.stdout.write('python manage.py test_login_system --create-test-user')
            self.stdout.write('python manage.py test_login_system --test-login 12345678901')
            self.stdout.write('python manage.py test_login_system --test-login TestUser123')
            self.stdout.write('python manage.py test_login_system --test-login test_user_12345')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS('✅ Sistema de login suporta:')
        )
        self.stdout.write('• Username do sistema (ex: user_123456789)')
        self.stdout.write('• ID do Roblox (ex: 123456789)')
        self.stdout.write('• Username do Roblox (ex: MeuUsuario)')
        self.stdout.write('• Busca case-insensitive para usernames')
        self.stdout.write('• Logs detalhados para debug') 