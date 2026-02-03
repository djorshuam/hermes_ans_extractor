"""
Script principal para sincronização de dados Salesforce para Data Lake Oracle

Executa sincronização de hora em hora das tabelas configuradas
"""

import os
import sys
import time
from pathlib import Path

import schedule
from dotenv import load_dotenv
from src.run_sync import run_sync
from src.utils.logger import MeuLogger

# Configura logger
logger = MeuLogger.setup_logger()

# Carrega o arquivo .env da pasta env/
env_path = Path("env/credentials.env")
load_dotenv(env_path)


def start_sync_service():
    """Função principal - executa sincronização em modo agendado"""
    try:
        # Intervalo de sincronização (em minutos)
        sync_interval = int(os.getenv("SYNC_INTERVAL_MINUTES", "10"))

        logger.info("%s", "=" * 80)
        logger.info("SINCRONIZAÇÃO AGENDADA INICIADA")
        logger.info("%s", "=" * 80)
        logger.info("Intervalo de sincronização: %s minuto(s)", sync_interval)
        logger.info("%s", "=" * 80)

        # Executa primeira sincronização imediatamente
        logger.info("Executando primeira sincronização...")
        # run_sync(logger)

        # Agenda sincronizações periódicas
        schedule.every(sync_interval).minutes.do(run_sync, logger=logger)

        logger.info("Aguardando próxima execução (a cada %s minuto(s))...", sync_interval)
        logger.info("Pressione Ctrl+C para interromper")

        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto

    except KeyboardInterrupt:
        logger.info("\n\nSincronização interrompida pelo usuário")
        sys.exit(0)

    except Exception as error:
        logger.error("Erro fatal: %s", error, exc_info=True)
        sys.exit(1)


if __name__ == "__start_sync_service__":
    start_sync_service()
