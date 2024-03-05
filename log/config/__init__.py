import logging.config
from pathlib import Path
import yaml

def config_logging():
    with open(Path(__file__).parent.joinpath(f'logger_windows.yml'), 'r') as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)
