import os
import sys
import io
import logging
from datetime import datetime

# Verificar que sys.stdout y sys.stderr no sean None antes de redirigirlos
if getattr(sys, 'stdout', None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if getattr(sys, 'stderr', None):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Determinar el directorio base en AppData para evitar problemas de permisos
def get_log_directory():
    if sys.platform == "win32":
        return os.path.join(os.getenv("APPDATA"), "SubtitlesExtractor", "logs")
    else:
        return os.path.join(os.path.expanduser("~"), ".SubtitlesExtractor", "logs")

LOG_DIR = get_log_directory()
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app_log.log")
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Iniciando aplicación...")
logger.debug("Versión de Python: %s", sys.version)
logger.debug("Sistema operativo: %s", os.name)
