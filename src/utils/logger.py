"""
Utilitário para configuração de logging
"""

import logging
import os
from datetime import datetime

from .descriptions import SOLUTION_NAME

# from pathlib import Path

# from dotenv import load_dotenv

# Carrega o arquivo .env da pasta env/
# env_path = Path("env/descriptions.env")
# load_dotenv(env_path)

# SOLUTION_NAME: str = os.getenv("SOLUTION_NAME", "SOLUTION_NAME")


class MeuLogger:
    """
    Classe utilitária para configuração de logging
    """

    @staticmethod
    def setup_logger(log_folder) -> logging.Logger:
        """
        Configura e retorna um logger para a aplicação

        Args:
            log_folder: Pasta onde os logs serão salvos

        Returns:
            Logger configurado
        """
        try:
            project_root = os.path.dirname(__file__)
        except NameError:
            project_root = os.getcwd()

        # Pasta que usamos como delimitador
        project_root = project_root.split("src")[0].rstrip(os.path.sep)

        log_folder = os.path.join(project_root, log_folder)
        # Cria pasta de logs se não existir
        os.makedirs(log_folder, exist_ok=True)

        # Nome do arquivo de log com timestamp
        log_filename = os.path.join(log_folder, f"{SOLUTION_NAME.lower()}_{datetime.now().strftime('%Y%m%d')}.log")

        # Configuração do logger
        logger = logging.getLogger(SOLUTION_NAME)
        logger.setLevel(logging.INFO)

        # Remove handlers existentes para evitar duplicação
        if logger.handlers:
            logger.handlers.clear()

        # Handler para arquivo
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formato do log
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger
