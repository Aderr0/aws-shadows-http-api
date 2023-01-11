
# Externals modules
import logging, sys

__app_name = sys.argv[0]

# log with low level will be ignore : notset < debug < info < warning < error < critical
__logger: logging.Logger

__logger = logging.getLogger(__app_name)
formatter = logging.Formatter(fmt="|%(levelname)s| %(message)s")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
__logger.addHandler(handler)

def set_log_level(is_log_level_debug=False):
    log_level = logging.DEBUG if is_log_level_debug else logging.INFO
    __logger.setLevel(log_level)

def log_debug(message: str):
    __logger.debug(message)

def log_info(message: str):
    __logger.info(message)

def log_warning(message: str):
    __logger.warning(message)

def log_error(message: str):
    __logger.error(message)

def log_critical(message: str):
    __logger.critical(message)