from visualization.releases_visualization import start_visualization as releases_visualization

import logging


def main() -> None:
    """
    This function initialize the visualization of all data obtained

    @return: Show all the data located in the several csv located in the data folder
    """
    logger = logging.getLogger("visualization")
    # Execute scrappers
    releases_visualization()
