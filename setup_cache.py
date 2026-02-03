"""
Script de configuração de cache Python centralizado
Configura PYTHONPYCACHEPREFIX para centralizar __pycache__ em .cache/
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def limpar_tela():
    """Limpa a tela do terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def configurar_cache_windows():
    """Configura cache no Windows via setx."""
    # Cache dentro da pasta hermes
    hermes_path = Path(__file__).parent
    cache_path = hermes_path / ".cache"
    cache_path_str = str(cache_path.absolute())

    print("\n" + "=" * 50)
    print("  CONFIGURANDO CACHE PYTHON - WINDOWS")
    print("=" * 50)
    print(f"\nProjeto Hermes: {hermes_path}")
    print(f"Caminho do cache: {cache_path_str}\n")  # Define para a sessão atual
    os.environ["PYTHONPYCACHEPREFIX"] = cache_path_str
    print("✓ Variável definida para sessão atual")

    # Define permanentemente
    try:
        resultado = subprocess.run(
            ["setx", "PYTHONPYCACHEPREFIX", cache_path_str], capture_output=True, text=True, check=False
        )

        if resultado.returncode == 0:
            print("✓ Variável definida permanentemente")
            print("\n⚠ IMPORTANTE:")
            print("  - Feche e reabra o VS Code completamente")
            print("  - Novos terminais usarão a configuração")
        else:
            print("⚠ Não foi possível definir permanentemente")
            print("  Execute como Administrador se necessário")

    except Exception as e:
        print(f"⚠ Erro ao configurar permanentemente: {e}")

    # Verifica se está funcionando
    print("\n" + "-" * 50)
    print("Verificando configuração...")
    print(f"sys.pycache_prefix = {sys.pycache_prefix}")

    if sys.pycache_prefix:
        print("\n✓ Configuração aplicada com sucesso!")
    else:
        print("\n⚠ Cache ainda não está ativo nesta sessão")
        print("  Reinicie o terminal para ativar")

    print("=" * 50 + "\n")


def configurar_cache_unix():
    """Configura cache no Linux/Mac via arquivo de perfil."""
    cache_path = Path(__file__).parent / ".cache"
    cache_path_str = str(cache_path.absolute())

    print("\n" + "=" * 50)
    print("  CONFIGURANDO CACHE PYTHON - UNIX")
    print("=" * 50)
    print(f"\nCaminho do cache: {cache_path_str}\n")

    # Define para a sessão atual
    os.environ["PYTHONPYCACHEPREFIX"] = cache_path_str
    print("✓ Variável definida para sessão atual")

    # Adiciona ao perfil do shell
    shell_config = Path.home() / ".bashrc"
    if not shell_config.exists():
        shell_config = Path.home() / ".zshrc"

    config_line = f'\nexport PYTHONPYCACHEPREFIX="{cache_path_str}"\n'

    try:
        with open(shell_config, "a", encoding="utf-8") as f:
            f.write(config_line)

        print(f"✓ Configuração adicionada a {shell_config}")
        print("\n⚠ IMPORTANTE:")
        print("  - Reinicie o terminal ou execute:")
        print(f"    source {shell_config}")

    except Exception as e:
        print(f"⚠ Erro ao configurar: {e}")

    print("=" * 50 + "\n")


def limpar_cache_antigo():
    """Remove pastas __pycache__ antigas."""
    print("\n" + "=" * 50)
    print("  LIMPEZA DE CACHE ANTIGO")
    print("=" * 50 + "\n")

    resposta = input("Deseja remover pastas __pycache__ antigas? (s/N): ").strip().lower()

    if resposta == "s":
        hermes_path = Path(__file__).parent
        count = 0
        errors = []

        print("\nProcurando pastas __pycache__...")

        for pycache in hermes_path.rglob("__pycache__"):
            if pycache.is_dir():
                try:

                    # Tenta remover atributos de somente leitura antes
                    for root, dirs, files in os.walk(pycache):
                        for d in dirs:
                            os.chmod(os.path.join(root, d), 0o777)
                        for f in files:
                            file_path = os.path.join(root, f)
                            os.chmod(file_path, 0o777)

                    shutil.rmtree(pycache)
                    print(f"  ✓ Removido: {pycache.relative_to(hermes_path)}")
                    count += 1
                except PermissionError:
                    error_msg = f"{pycache.relative_to(hermes_path)} - Arquivo em uso"
                    errors.append(error_msg)
                    print(f"  ✗ {error_msg}")
                except Exception as e:
                    error_msg = f"{pycache.relative_to(hermes_path)} - {str(e)}"
                    errors.append(error_msg)
                    print(f"  ✗ {error_msg}")

        print("\n" + "-" * 50)
        if count > 0:
            print(f"✓ {count} pasta(s) __pycache__ removida(s)")
        if errors:
            print(f"⚠ {len(errors)} pasta(s) não puderam ser removidas")
            print("\nDica: Feche o VS Code e Python, então execute novamente")
        if count == 0 and not errors:
            print("✓ Nenhuma pasta __pycache__ encontrada")
    else:
        print("\n✓ Limpeza cancelada")

    print("=" * 50 + "\n")


def main():
    """Função principal."""
    limpar_tela()

    print("\n")
    print("=" * 50)
    print("  CONFIGURAÇÃO DE CACHE PYTHON CENTRALIZADO")
    print("  Projeto: Hermes")
    print("=" * 50)
    print("\nEste script centraliza todos os arquivos __pycache__")
    print("em uma única pasta .cache/ no projeto Hermes")
    print("=" * 50)

    if os.name == "nt":
        configurar_cache_windows()
    else:
        configurar_cache_unix()

    limpar_cache_antigo()

    input("\nPressione Enter para sair...")


if __name__ == "__main__":
    main()
