import logging
import colorlog

def setup_logging():
    if not logging.getLogger().handlers:
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
        formatter.log_colors = log_colors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.setLevel(logging.INFO)
        uvicorn_logger.addHandler(console_handler)

        for lib_name in ['fastapi']:
            logging.getLogger(lib_name).setLevel(logging.WARNING)

setup_logging()

# Use a named logger in your app
logger = logging.getLogger('yuqin_manage')

try:
    pass
except Exception as e:
    logger.error("An error occurred", exc_info=True)
