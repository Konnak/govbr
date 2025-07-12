from django.core.management.base import BaseCommand
from main.models import ProtocoloDocumento, Protocolo


class Command(BaseCommand):
    help = 'Atualiza identificadores dos documentos existentes'

    def handle(self, *args, **options):
        self.stdout.write('Atualizando identificadores dos documentos...')
        
        # Buscar todos os protocolos
        protocolos = Protocolo.objects.all()
        total_documentos = 0
        
        for protocolo in protocolos:
            # Buscar documentos do protocolo sem identificador
            documentos = ProtocoloDocumento.objects.filter(
                protocolo=protocolo,
                identificador=''
            ).order_by('data_upload')
            
            for idx, documento in enumerate(documentos, 1):
                documento.identificador = f"DOC-{idx:03d}"
                documento.save()
                total_documentos += 1
                
                self.stdout.write(f'  {protocolo.numero_protocolo}: {documento.nome} → {documento.identificador}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Identificadores atualizados para {total_documentos} documentos!')
        ) 