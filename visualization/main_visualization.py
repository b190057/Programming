from visualization.netflix_visualization import start_visualization as netflix_visualization
from visualization.releases_visualization import start_visualization as releases_visualization
from visualization.top_films_visualization import start_visualization as top_films_visualization

import logging


def main() -> None:
    """
    This function initialize the visualization of all data obtained

    @return: Show all the data located in the several csv located in the data folder
    """
    logger = logging.getLogger("visualization")
    # execute visualizations
    netflix_visualization()
    releases_visualization()
    top_films_visualization()
