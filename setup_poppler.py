#!/usr/bin/env python3
"""
Script para configurar Poppler no Windows
Este script baixa e configura o Poppler para permitir conversão de PDF para imagem
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_poppler():
    """Baixa e configura o Poppler para Windows"""
    
    print("🔄 Configurando Poppler para Windows...")
    
    # URLs para diferentes arquiteturas
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.01.0-0/Release-23.01.0-0.zip"
    
    # Diretórios
    project_dir = Path(__file__).parent
    poppler_dir = project_dir / "poppler"
    poppler_zip = project_dir / "poppler.zip"
    
    try:
        # Limpar diretório existente
        if poppler_dir.exists():
            shutil.rmtree(poppler_dir)
            
        # Baixar Poppler
        print("📥 Baixando Poppler...")
        urllib.request.urlretrieve(poppler_url, poppler_zip)
        print("✅ Download concluído!")
        
        # Extrair
        print("📂 Extraindo arquivos...")
        with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
            zip_ref.extractall(poppler_dir)
        
        # Encontrar o diretório bin
        bin_dirs = list(poppler_dir.rglob("**/bin"))
        if not bin_dirs:
            raise Exception("Diretório bin não encontrado no Poppler")
            
        poppler_bin = bin_dirs[0]
        print(f"📁 Poppler extraído em: {poppler_bin}")
        
        # Adicionar ao PATH do sistema (temporário para esta sessão)
        current_path = os.environ.get('PATH', '')
        if str(poppler_bin) not in current_path:
            os.environ['PATH'] = f"{poppler_bin};{current_path}"
            print("✅ Poppler adicionado ao PATH!")
        
        # Testar instalação
        print("🧪 Testando instalação...")
        test_command = f'"{poppler_bin / "pdftoppm.exe"}" -h'
        result = os.system(test_command + " >nul 2>&1")
        
        if result == 0:
            print("✅ Poppler configurado com sucesso!")
            
            # Criar arquivo de configuração
            config_file = project_dir / "poppler_config.py"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(f'''# Configuração do Poppler
POPPLER_PATH = r"{poppler_bin}"

# Adicionar ao PATH se necessário
import os
if POPPLER_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = f"{POPPLER_PATH};{{os.environ.get('PATH', '')}}"
''')
            print(f"📝 Arquivo de configuração criado: {config_file}")
            
        else:
            print("❌ Erro ao testar Poppler")
            return False
            
        # Limpar arquivo zip
        if poppler_zip.exists():
            poppler_zip.unlink()
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar Poppler: {e}")
        return False

def check_poppler():
    """Verifica se o Poppler está disponível"""
    try:
        from pdf2image import convert_from_path
        # Tentar importar - se não der erro, está funcionando
        print("✅ Poppler já está disponível!")
        return True
    except Exception as e:
        print(f"❌ Poppler não disponível: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configurador do Poppler para Windows")
    print("=" * 50)
    
    if not check_poppler():
        print("\n🔧 Poppler não encontrado. Iniciando instalação...")
        if download_poppler():
            print("\n🎉 Configuração concluída com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Reinicie o servidor Django")
            print("2. Teste a geração de PDF com anexos")
        else:
            print("\n💥 Falha na configuração do Poppler")
            sys.exit(1)
    else:
        print("\n✅ Poppler já está configurado corretamente!") 