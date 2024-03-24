from log.config import config_logging
from scraper.main_scraper import main as main_scraper
from visualization.main_visualization import main as main_visualization

if __name__ == '__main__':
    config_logging()
    main_scraper()
    main_visualization()
