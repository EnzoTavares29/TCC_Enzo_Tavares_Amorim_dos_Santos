# utils/path_utils.py

import os

def project_root():
    """
    Retorna o diretório raiz do projeto (onde está o main.py)
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def asset_path(*paths):
    """
    Monta caminho absoluto para arquivos em assets/
    """
    return os.path.join(project_root(), "assets", *paths)
