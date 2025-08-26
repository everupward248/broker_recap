import logging 

def get_logger(name: str=__name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        file_name = name.replace("_", "")

        handler = logging.FileHandler(f"logs/validation_log_{file_name}.log", mode="w")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger