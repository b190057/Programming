import os
import time

from scraper import logger
import pandas as pd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from constants import DATA_PATH


def get_final_df_box(driver) -> pd.DataFrame:
    """
    This function extract the title, gross, genre and weeks of the box office

    @param driver: Driver of the webpage of box office
    @return: A Dataframe containing the title, gross, genre and weeks of the box office
    """
    box_office_usa = None
    try:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get box office USA
        box_office_name = "Box Office USA"
        box_office_header = soup.find_all(class_="header")
        for item in box_office_header:
            if item.text.strip().startswith(box_office_name):
                box_office_usa = item.parent
                break

    except Exception as e:
        logger.error(f"Could not extract the producer or the time {e}")

    if not box_office_usa:
        raise Exception('Could not get into the box office USA')

    # Get header and body of the target table
    thead = box_office_usa.find('thead')
    tbody = box_office_usa.find('tbody')

    if not thead or not tbody:
        raise Exception('Could not get the header or body of the table')

    # Get column headers
    df_columns = list()
    for item in thead.find_all('th'):
        df_columns.append(item.text)

    df_box_office = pd.DataFrame(columns=df_columns)
    for row in tbody.find_all('tr'):
        items = row.find_all('td')
        if len(items) != len(df_columns):
            logger.error("There are more elements in the row than in the table's header")

        item_list = list()
        for item in items:
            item_list.append(item.text)

        # Add new row to the df
        new_row = dict(zip(df_columns, item_list))
        df_box_office.loc[len(df_box_office)] = new_row

    return df_box_office


def get_box_office_page(driver) -> None:
    """
    This function gets into the box office page

    @param driver: Driver of the main page
    @return: None
    """

    try:
        # Go to the box office page
        page_find = "Box office"
        element_find = "FA Rankings"  # Locate this element to scroll and see the top 1000 FA button
        fa_rankings = driver.find_element(By.XPATH, f"//*[contains(text(), '{element_find}')]")
        boxWeb = driver.find_element(By.XPATH, f"//*[contains(text(), '{page_find}')]")
        if not fa_rankings.is_displayed():
            raise Exception()

        # Scroll to see the box office button
        fa_rankings.location_once_scrolled_into_view
        time.sleep(1)
        boxWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the box office webpage:  {e}")
        raise Exception(e)


def get_data(driver) -> tuple[str, str]:
    """
    This function extract the producers and time of a given film.

    @param driver: Driver of the webpage of a film
    @return: the producers and the time of the movie
    """
    producers = None
    duration = None
    try:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')  # Get all the names and url of the movies

        # Get producers
        producers = soup.find(class_="card-producer").text

    except Exception as e:
        logger.error(f"Could not extract the producers {e}")

    try:
        # Get duration
        dt_duration = driver.find_element(By.XPATH, "//dt[contains(text(), 'Running time')]")
        dd_duration = dt_duration.find_element(By.XPATH, "following-sibling::dd")
        duration = dd_duration.text

    except Exception as e:
        logger.error(f"Could not extract the time {e}")

    finally:
        return producers, duration


def get_final_df(driver, title_list) -> pd.DataFrame:
    """
    Extract the information of every movie from their own page

    @param driver: Driver of the new releases
    @param title_list: List containing the title and url of each movie
    @return: A Pandas Dataframe that contains the title, the producers and the duration of new releases
    """
    df = pd.DataFrame(columns=['Title', 'Producers', 'Duration'])
    for movie_title, movie_url in title_list:
        try:
            driver.get(movie_url)
            time.sleep(0.5)
            producers, duration = get_data(driver)
            # Get movie data
            new_row = {'Title': movie_title,
                       'Producers': producers,
                       'Duration': duration}
            df.loc[len(df)] = new_row
        except Exception as e:
            logger.error(f'Error extracting data from the film {movie_title.upper()}: {e}')

    return df


def get_urls(driver) -> list[tuple[str, str]]:
    """
    Obtain all names and urls of the new released movies

    @param driver: Driver of the new releases movies
    @return: a list of tuples where the left side is the movie name, and the right side is the url
    """
    # Get all the names and url of the movies
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # get all the movie titles
    release_movies_html = soup.find_all(class_="movie-title")

    if not release_movies_html:
        logger.error("Could not get the information of the url from the html")
        raise Exception("Could not get the information of the url from the html")

    # Get all the found elements
    title_list = list()
    for element in release_movies_html:
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


def get_releases_page(driver) -> None:
    """
    This function gets into the new releases

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
        raise Exception(e)

    time.sleep(3)

    try:
        # Go to the releases page
        page_find = "US releases"
        releasesWeb = driver.find_element(By.XPATH, f"//*[contains(text(), '{page_find}')]")
        if not releasesWeb.is_displayed():
            raise Exception()

        releasesWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the releases webpage:  {e}")
        raise Exception(e)


def start_scrapper() -> None:
    """
    Web scraper for the releases and the box office

    @return:
    """
    # Add options and initialize the webdriver
    options = webdriver.FirefoxOptions()
    options.add_argument("--disable-cookies")
    driver = webdriver.Firefox(options=options)

    # Get into the main webpage
    driver.get("https://www.filmaffinity.com/us/main.html")
    time.sleep(3)

    # Go into releases page
    get_releases_page(driver)
    time.sleep(3)

    # Scroll to the bottom and get all the URL
    title_list = get_urls(driver)

    # Get and save the data from the releases
    df = get_final_df(driver, title_list)
    df.to_csv(os.path.join(DATA_PATH, 'releases.csv'), index=False)

    # Get the box office
    get_box_office_page(driver)

    # Get and save the data from the box office
    df_box = get_final_df_box(driver)
    df_box.to_csv(os.path.join(DATA_PATH, 'box_office.csv'), index=False)

    driver.quit()
    logger.info("Everything worked fine for the new releases scraper")
