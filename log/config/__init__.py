import logging.config
from pathlib import Path
import yaml
import platform
import struct


def config_logging() -> None:
    os = (platform.system().lower(), struct.calcsize('P') * 8)[0]
    with open(Path(__file__).parent.joinpath(f'logger_{os}.yml'), 'r') as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)
