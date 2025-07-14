import logging 

def get_logger(name: str=__name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.FileHandler("validation_log.log", mode="w")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger