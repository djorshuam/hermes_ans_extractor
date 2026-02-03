"""
CLI - Interface de Linha de Comando para a solução
"""

import sys
from typing import Callable, TypedDict

from src.utils.descriptions import SOLUTION_DESCRIPTION, SOLUTION_NAME
from src.utils.extract_pbi import ExtratorPBI as extrator_pbi
from src.utils.extract_pentaho import df_vidas_operadora
from src.utils.logger import MeuLogger
from start_sync_service import start_sync_service

# Configura logger
logger = MeuLogger.setup_logger()


class MenuOption(TypedDict):
    """Estrutura de uma opção de menu no CLI"""

    title: str
    exec: Callable


def print_header():
    """Imprime cabeçalho do CLI"""
    print()
    print("=" * 80)
    print(f"{'-' * 32}{' ' * 5}{SOLUTION_NAME}{' ' * 5}{'-' * 32}")
    print(f"{SOLUTION_DESCRIPTION}")
    print("=" * 80)
    print()


def print_menu():
    """Imprime menu principal"""
    print("MENU PRINCIPAL:")
    print("-" * 80)
    for i, option in enumerate(MENU, 1):
        print(f"  {i}. {option['title']}")
    print("-" * 80)


MENU: list[MenuOption] = [
    {
        "title": "Iniciar serviço de sincronização automática (agendado)",
        "exec": start_sync_service,
    },
    {
        "title": "Extrair Dados PBI - Data",
        "exec": lambda: extrator_pbi(logger).data_atualizacao(),
    },
    {
        "title": "Extrair Dados PBI - IGR",
        "exec": lambda: extrator_pbi(logger).dados_IGR(),
    },
    {
        "title": "Extrair Dados Pentaho - Vidas Operadora",
        "exec": lambda: df_vidas_operadora(["368253"]),
    },
    {
        "title": "Sair",
        "exec": lambda: (print("\n👋 Encerrando CLI. Até logo!\n"), sys.exit(0)),
    },
]


def main():
    """Função principal do CLI"""
    print_header()

    while True:
        try:
            print_menu()
            choice = input("\nSelecione uma opção: ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(MENU):
                MENU[int(choice) - 1]["exec"]()
            else:
                print("\n⚠️  Opção inválida. Tente novamente.")

            input("\nPressione ENTER para continuar...")
            print("\n" * 2)

        except KeyboardInterrupt:
            print("\n\n👋 CLI encerrado pelo usuário. Até logo!\n")
            return
        except Exception as error:
            print(f"\n❌ Erro inesperado: {error}")
            logger.error("Erro inesperado no CLI: %s", error, exc_info=True)
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
