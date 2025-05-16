from logging import getLogger
from logging.config import dictConfig

from app.settings import log_config

logger = getLogger()
dictConfig(log_config)
