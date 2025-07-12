from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import NoticiaCategoria, NoticiaTag, Poder

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura dados básicos para o sistema de notícias'

    def handle(self, *args, **options):
        self.stdout.write('Configurando sistema de notícias...')
        
        # Criar poder Imprensa se não existir
        imprensa, created = Poder.objects.get_or_create(nome='Imprensa')
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Poder "Imprensa" criado com sucesso')
            )
        else:
            self.stdout.write(f'• Poder "Imprensa" já existe')
        
        # Criar categorias padrão
        categorias_padrao = [
            {
                'nome': 'Política',
                'icone': 'fas fa-landmark',
                'cor': '#dc3545'
            },
            {
                'nome': 'Economia',
                'icone': 'fas fa-chart-line',
                'cor': '#28a745'
            },
            {
                'nome': 'Segurança',
                'icone': 'fas fa-shield-alt',
                'cor': '#007bff'
            },
            {
                'nome': 'Educação',
                'icone': 'fas fa-graduation-cap',
                'cor': '#6f42c1'
            },
            {
                'nome': 'Saúde',
                'icone': 'fas fa-heartbeat',
                'cor': '#e83e8c'
            },
            {
                'nome': 'Tecnologia',
                'icone': 'fas fa-microchip',
                'cor': '#17a2b8'
            },
            {
                'nome': 'Esportes',
                'icone': 'fas fa-futbol',
                'cor': '#fd7e14'
            },
            {
                'nome': 'Cultura',
                'icone': 'fas fa-theater-masks',
                'cor': '#6610f2'
            }
        ]
        
        for categoria_data in categorias_padrao:
            categoria, created = NoticiaCategoria.objects.get_or_create(
                nome=categoria_data['nome'],
                defaults={
                    'icone': categoria_data['icone'],
                    'cor': categoria_data['cor'],
                    'descricao': f'Notícias relacionadas a {categoria_data["nome"].lower()}'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Categoria "{categoria.nome}" criada')
                )
            else:
                self.stdout.write(f'• Categoria "{categoria.nome}" já existe')
        
        # Criar tags padrão
        tags_padrao = [
            'governo', 'brasil', 'roblox', 'roleplay', 'política', 'economia',
            'segurança', 'educação', 'saúde', 'tecnologia', 'esportes', 'cultura',
            'notícia', 'comunicado', 'anúncio', 'decreto', 'lei', 'portaria'
        ]
        
        for tag_nome in tags_padrao:
            tag, created = NoticiaTag.objects.get_or_create(nome=tag_nome)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Tag "{tag.nome}" criada')
                )
            else:
                self.stdout.write(f'• Tag "{tag.nome}" já existe')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Sistema de notícias configurado com sucesso!')
        )
        self.stdout.write('\nPróximos passos:')
        self.stdout.write('1. Crie um usuário com cargo na Imprensa para poder criar notícias')
        self.stdout.write('2. Acesse /noticias/criar/ para criar sua primeira notícia')
        self.stdout.write('3. Configure permissões adicionais no Django Admin se necessário') 