import logging
import sys
from logtail import LogtailHandler
from src.config import config

def setup_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG) 

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.propagate = False

    # reduce noise (important)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    # betterstack_handler = LogtailHandler(source_token=config.BetterStack)

    stream_handler.setLevel(logging.INFO)    
    file_handler.setLevel(logging.DEBUG)     
    # betterstack_handler.setLevel(logging.DEBUG)  

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # betterstack_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    # logger.addHandler(betterstack_handler)

    return logger

logger = setup_logger()