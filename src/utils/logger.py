import logging
import os

def get_logger(name: str = "app_logger", log_file: str = "logs/app.log", level: int = logging.INFO) -> logging.Logger:
    """
    Retorna um logger configurado que grava mensagens em um arquivo.

    :param name: Nome do logger.
    :param log_file: Caminho do arquivo de log.
    :param level: Nível mínimo de logging (ex: logging.INFO, logging.DEBUG).
    :return: Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger
