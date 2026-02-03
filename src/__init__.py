"""
Arquivo __init__ para tornar src um pacote Python
"""

import sys
from pathlib import Path

# Adiciona raiz do projeto ao PYTHONPATH automaticamente
# Isso permite usar importações absolutas: from src.utils.logger import MeuLogger
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
