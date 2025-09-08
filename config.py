import os

from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Directus
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://your-directus-instance.com")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "your-directus-token")

# Diretórios do projeto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# Comentário: OUTPUTS_DIR removido - usando apenas RESULTS_DIR
DOCUMENTOS_DIR = os.path.join(PROJECT_ROOT, "documentos")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")

# Configurações da aplicação
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")  # Atualizado para usar results
LUA_FILTER_PATH = os.getenv("LUA_FILTER_PATH", "comments_html_filter_direct.lua")

# Garantir que os diretórios existam
for directory in [DOCUMENTOS_DIR, TESTS_DIR, RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configurações do Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Configurações de segurança
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default
ALLOWED_EXTENSIONS = {"docx"}
