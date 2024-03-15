from scraper.top_films import start_scrapper as top_scrapper
from scraper.releases import start_scrapper as releases_scrapper

import logging


def main() -> None:
    """
    This function initialize the scraper log and calls all scrapers

    @return:Save all the data extracted into several csv located in the data folder
    """
    logger = logging.getLogger("scraper")
    # Execute scrappers
    top_scrapper()
    releases_scrapper()
