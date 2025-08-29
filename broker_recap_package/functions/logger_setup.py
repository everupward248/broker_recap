import logging 
from pathlib import Path

DEFAULT_LOG_PATH = Path(r"C:\Users\johnj\OneDrive\Documents\programming\projects\polar_star\broker_recap\broker_recap_package\logs")

def get_logger(name: str=__name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        file_name = name.replace("_", "")

        #this line of code is determining if the script will be run as package or directly as a script. "broker_recap_package" - to be removed to run as script
        handler = logging.FileHandler(DEFAULT_LOG_PATH / f"validation_log_{file_name}.log", mode="w")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger