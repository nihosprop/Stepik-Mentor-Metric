import logging.config
import os

from main_config import main_config


def setup_logging() -> None:
    """
    Setup logging
    Returns: None
    """
    config: dict = main_config.logs.dict_config

    handlers = config.get('handlers', {})
    for handler in handlers.values():
        if 'filename' in handler:
            log_dir = os.path.dirname(handler['filename'])
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

    logging.config.dictConfig(config)
