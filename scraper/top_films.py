import os
import time

from scraper import logger
import pandas as pd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from log.config.msg import DATA_PATH


def get_data(driver) -> tuple[list[str], list[str], list[str]]:
    """
    This function extract the director, the genres and the actor of a given film.

    @param driver: Driver of the webpage of a film
    @return: three lists, the directors, the genres and the actors.
    """
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')  # Get all the names and url of the movies

    # Get directors
    directors = soup.find(class_="directors")
    directors_list = list()
    if directors:
        for director in directors.find_all('a'):
            directors_list.append(director.text)

    # Get genres
    genres = soup.find(class_="card-genres")
    genres_list = list()
    if genres:
        for genre in genres.find_all('a'):
            genres_list.append(genre.text)

    # Get actors
    actors = soup.find(class_="card-cast-debug")
    actors_list = list()
    if actors:
        for actor in actors.find_all('a'):
            actors_list.append(actor.text)
    else:
        actors = soup.find(class_="card-cast")
        if actors:
            for actor in actors.find_all('a'):
                actors_list.append(actor.text)
        else:
            logger.error("Could not extract the actors")


    if len(actors_list) > 1:
        actors_list = actors_list[:-1]

    return directors_list, genres_list, actors_list


def get_final_df(driver, title_list) -> pd.DataFrame:
    """
    Extract the information of every movie from their own page

    @param driver: Driver of the top 1000 FA
    @param title_list: List containing the title and url of each movie
    @return: A Pandas Dataframe that contains the title, the directors, the genres and the actors of all 1000 movies
    """
    df = pd.DataFrame(columns=['Title', 'Directors', 'genres', 'Actors'])
    for movie_title, movie_url in title_list:
        try:
            driver.get(movie_url)
            time.sleep(0.5)
            directors_list, genres_list, actors_list = get_data(driver)
            # Get movie data
            new_row = {'Title': movie_title,
                       'Directors': str(directors_list)[1:-1].replace('\'', ''),
                       'genres': str(genres_list)[1:-1].replace('\'', ''),
                       'Actors': str(actors_list)[1:-1].replace('\'', '')}
            df.loc[len(df)] = new_row
        except Exception as e:
            logger.error(f'Error extracting data from the film {movie_title.upper()}: {e}')

    return df


def get_urls(driver) -> list[tuple[str, str]]:
    """
    Obtain all names and urls of the 1000 films from the top 1000 FA

    @param driver: Driver of the top 1000 FA
    @return: a list of tuples where the left side is the movie name, and the right side is the url
    """
    while True:
        try:
            time.sleep(1)

            # Wait until the show-more button is visible
            driver.find_element(By.CLASS_NAME, "show-more")
            show_more_button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "show-more"))
            )

            # Click in the "show-more" button if displayed
            if not show_more_button.is_displayed():
                break
            show_more_button.location_once_scrolled_into_view
            time.sleep(0.5)
            show_more_button.click()
        except Exception as e:
            # If the button is not found, then we extract the information of the movies
            logger.info(f"There is no more 'show-more' button: {e}")
            break

    # Get all the names and url of the movies
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # get all the movie titles
    top_movies_html = soup.find_all(class_="mc-title")

    if not top_movies_html:
        logger.error("Could not get the information of the url from the html")

    # Get all the found elements
    title_list = list()
    for element in top_movies_html:
        link = None
        name = None
        try:
            link = element.find('a')['href']
            name = element.text.strip()
            title_list.append((name, link))
        except Exception as e:
            if link:
                logger.error(f'Could not get the name of the movie: {e}')
                title_list.append((name, link))
            else:
                logger.error(f'Could not get the link of the movie: {e}')
                title_list.append((name, link))

    return title_list


def get_top_page(driver) -> None:
    """
    This function gets into the top 1000 FA page

    @param driver: Driver of the main page
    @return: None
    """
    try:
        # Disagree cookies filmaffinity
        text_to_find = "DISAGREE"
        configCookies = driver.find_element(By.XPATH, f"//*[contains(text(), '{text_to_find}')]")
        configCookies.click()
    except Exception as e:
        logger.error(f"Cookies could not been rejected: {e}")
        raise Exception("Cookies could not been rejected:")

    time.sleep(3)

    try:
        # Go to the top 1000 films
        page_find = "Top 1000 FA"
        element_find = "FA Rankings"  # Locate this element to scroll and see the top 1000 FA button
        fa_rankings = driver.find_element(By.XPATH, f"//*[contains(text(), '{element_find}')]")
        topWeb = driver.find_element(By.XPATH, f"//*[contains(text(), '{page_find}')]")
        if not fa_rankings.is_displayed():
            raise Exception()

        # Scroll to see the Top 1000 FA ranking
        fa_rankings.location_once_scrolled_into_view
        time.sleep(1)
        topWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the top webpage:  {e}")
        raise Exception("Could not get into the top webpage")


def start_scrapper() -> None:
    """
    Web scraper for the top 1000 FA

        @return:
    """
    # Add options and initialize the webdriver
    options = webdriver.FirefoxOptions()
    options.add_argument("--disable-cookies")
    driver = webdriver.Firefox(options=options)

    # Get into the main webpage
    driver.get("https://www.filmaffinity.com/us/main.html")
    time.sleep(3)

    # Go into the top 1000 FA
    get_top_page(driver)
    time.sleep(3)

    # Scroll to the bottom and get all the URL
    title_list = get_urls(driver)

    # Get and save the data containing the films
    df = get_final_df(driver, title_list)
    df.to_csv(os.path.join(DATA_PATH, 'top_films.csv'), index=False)

    driver.quit()

    logger.info("Everything worked fine for the new top films scraper")
