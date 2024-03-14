from log.config import config_logging
from scraper.main_scraper import main as main_scraper

if __name__ == '__main__':
    config_logging()
    main_scraper()
