import os
import time

from scraper import logger
import pandas as pd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from constants import DATA_PATH


def get_releases_data(driver) -> list[dict]:
    """
    This function extract the title, origin country, genre and release date of every film

    @param driver: Driver of the webpage of new Netflix releases
    @return: List of rows to be added to the Dataframe
    """
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    several_films = soup.find_all("div", id="main-wrapper-rdcat")

    new_rows = list()
    for films in several_films:
        # Get release date
        date_release_html = films.find(class_="rdate-cat rdate-cat-first")
        date_release = None
        if date_release_html:
            date_release = date_release_html.text.strip()
        elif films.find(class_="rdate-cat"):
            date_release = films.find(class_="rdate-cat").text.strip()
        else:
            logger.error("Couldn't get the release date")

        for film in films.find_all(class_="top-movie"):
            # Get countries
            country_html = film.find_all('img', class_='nflag')
            countries = list()
            if country_html:
                for country in country_html:
                    countries.append(country['alt'])
            else:
                logger.error("Could not find country")

            # Get genres
            genres_html = film.find(class_='types-wrapper')
            genres = list()
            if genres_html:
                for genre in genres_html.find_all(class_="type"):
                    genres.append(genre.text)
            elif film.find_all('a', class_='genre'):
                for genre in film.find_all('a', class_='genre'):
                    genres.append(genre.text)
            else:
                logger.error('Could not get genres')

            # Get title
            title_html = film.find("a", title=True)
            title = None
            if title_html:
                title = title_html['title'].strip()
            else:
                logger.error('Could not get the title')

            # Add new row
            new_row = {'Title': title,
                       'Origin_country': str(countries)[1:-1].replace('\'', ''),
                       'genres': str(genres)[1:-1].replace('\'', ''),
                       'Release_date': date_release}
            new_rows.append(new_row)

    return new_rows


def get_releases_df(driver) -> pd.DataFrame:
    """
    Extract the information of the new releases

    @param driver: Driver of the new Netflix releases
    @return: A Pandas Dataframe that contains the title, origin country, genre and release date
    """
    df = pd.DataFrame(columns=['Title', 'Origin_country', 'genres', 'Release_date'])

    rows_list = get_releases_data(driver)
    for new_row in rows_list:
        df.loc[len(df)] = new_row

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    button_name = "button-np-cat next-date-cat"
    while soup.find(class_=button_name):
        netflixWeb = driver.find_element(By.CSS_SELECTOR, ".next-date-cat")
        if not netflixWeb.is_displayed():
            raise Exception()

        # Get into the next webpage
        netflixWeb.location_once_scrolled_into_view
        time.sleep(3)
        netflixWeb.click()
        time.sleep(5)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add the information to the dataframe
        rows_list = get_releases_data(driver)
        for new_row in rows_list:
            df.loc[len(df)] = new_row

    return df


def get_netflix_page(driver) -> None:
    """
    This function gets into the new Netflix releases

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
        # Go to the Netflix releases page
        page_find = "Netflix (coming soon)"
        netflixWeb = driver.find_element(By.XPATH, f"//*[contains(text(), '{page_find}')]")
        if not netflixWeb.is_displayed():
            raise Exception()

        netflixWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the Netflix webpage:  {e}")
        raise Exception("Could not get into the Netflix webpage")


def get_netflix_voted_page(driver) -> None:
    """
    This function gets into the netflix most voted content

    @param driver: Driver of the main page
    @return: None
    """
    try:
        # Go to the Netflix releases page
        page_find = "Netflix"
        netflixWeb = driver.find_element(By.XPATH, f"//*[contains(text(), '{page_find}')]")
        if not netflixWeb.is_displayed():
            raise Exception()

        netflixWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the Netflix webpage:  {e}")
        raise Exception("Could not get into the Netflix webpage")

    try:
        # Go to the Netflix releases page
        page_find = "Popularity"
        netflixWeb = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{page_find}')]"))
        )
        if not netflixWeb.is_displayed():
            raise Exception()

        netflixWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the popularity Netflix webpage:  {e}")
        raise Exception("Could not get into the popularity Netflix webpage")


def get_voted_df(driver) -> pd.DataFrame:
    """
    Extract the information of the most voted content

    @param driver: Driver of the Netflix's most voted content
    @return: A Pandas Dataframe that contains the title, origin country, genres, release date, number of votes and rating
    """
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    several_films = soup.find_all("div", class_="top-movie")

    df = pd.DataFrame(columns=['Title', 'Origin_country', 'Genres', 'Release_date', 'n_votes', 'rating'])

    for film in several_films:

        # Get release year
        release_year = None
        release_year_html = film.find("span", class_="date")
        if release_year_html:
            release_year = release_year_html.text.strip()

        countries_html = film.find("div", class_="mc-data")
        countries = list()
        if countries_html and countries_html.find("div", class_=False):
            countries_html = countries_html.find("div", class_=False).find_all('img', class_='nflag')
            try:
                # Get Country
                for country in countries_html:
                    countries.append(country['alt'])
            except Exception as e:
                logger.error(f"Couldn't get the country{e}")

        # Get genres
        genres_html = film.find(class_='types-wrapper')
        genres = list()
        if genres_html:
            for genre in genres_html.find_all(class_="type"):
                genres.append(genre.text)
        elif film.find_all('a', class_='genre'):
            for genre in film.find_all('a', class_='genre'):
                genres.append(genre.text)
        else:
            logger.error('Could not get genres')

        # Get title
        title_html = film.find("a", title=True)
        title = None
        if title_html:
            title = title_html['title'].strip()
        else:
            logger.error('Could not get the title')

        # Get number of votes
        votes_html = film.find(class_="rat-count countcat")
        votes = None
        if votes_html:
            votes = votes_html.text.strip()

        # Get rating
        rating_html = film.find(class_="avg-rating")
        rating = None
        if rating_html:
            rating = rating_html.text.strip()

        # Add new row
        new_row = {'Title': title,
                   'Origin_country': str(countries)[1:-1].replace('\'', ''),
                   'Genres': str(genres)[1:-1].replace('\'', ''),
                   'Release_date': release_year,
                   'n_votes': votes,
                   'rating': rating}
        df.loc[len(df)] = new_row

    return df


def get_netflix_best_page(driver) -> None:
    """
    This function gets into the new Netflix best content

    @param driver: Driver of the main page
    @return: None
    """
    try:
        # Go to the Netflix releases page
        page_find = "Netflix"
        netflixWeb = driver.find_element(By.XPATH, f"//*[contains(text(), '{page_find}')]")
        if not netflixWeb.is_displayed():
            raise Exception()

        netflixWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the Netflix webpage:  {e}")
        raise Exception("Could not get into the Netflix webpage")

    try:
        # Go to the Netflix releases page
        page_find = "Rating"
        netflixWeb = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{page_find}')]"))
        )
        if not netflixWeb.is_displayed():
            raise Exception()

        netflixWeb.click()
    except Exception as e:
        logger.error(f"Could not get into the best rated Netflix webpage:  {e}")
        raise Exception("Could not get into the best rated Netflix webpage")


def get_best_df(driver) -> pd.DataFrame:
    """
    Extract the information of the best Netflix content

    @param driver: Driver of the best Netflix content
    @return: A Pandas Dataframe that contains the title, origin country, genres, release date, number of votes and rating
    """
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    several_films = soup.find_all("div", class_="top-movie")

    df = pd.DataFrame(columns=['Title', 'Origin_country', 'Genres', 'Release_date', 'n_votes', 'rating'])

    for film in several_films:

        # Get release year
        release_year = None
        release_year_html = film.find("span", class_="date")
        if release_year_html:
            release_year = release_year_html.text.strip()

        countries_html = film.find("div", class_="mc-data")
        countries = list()
        if countries_html and countries_html.find("div", class_=False):
            countries_html = countries_html.find("div", class_=False).find_all('img', class_='nflag')
            try:
                # Get Country
                for country in countries_html:
                    countries.append(country['alt'])
            except Exception as e:
                logger.error(f"Couldn't get the country{e}")

        # Get genres
        genres_html = film.find(class_='types-wrapper')
        genres = list()
        if genres_html:
            for genre in genres_html.find_all(class_="type"):
                genres.append(genre.text)
        elif film.find_all('a', class_='genre'):
            for genre in film.find_all('a', class_='genre'):
                genres.append(genre.text)
        else:
            logger.error('Could not get genres')

        # Get title
        title_html = film.find("a", title=True)
        title = None
        if title_html:
            title = title_html['title'].strip()
        else:
            logger.error('Could not get the title')

        # Get number of votes
        votes_html = film.find(class_="rat-count")
        votes = None
        if votes_html:
            votes = votes_html.text.strip()

        # Get rating
        rating_html = film.find(class_="avg-rating")
        rating = None
        if rating_html:
            rating = rating_html.text.strip()

        # Add new row
        new_row = {'Title': title,
                   'Origin_country': str(countries)[1:-1].replace('\'', ''),
                   'Genres': str(genres)[1:-1].replace('\'', ''),
                   'Release_date': release_year,
                   'n_votes': votes,
                   'rating': rating}
        df.loc[len(df)] = new_row

    return df


def start_scrapper() -> None:
    """
    Web scraper for the new Netflix releases

        @return:
    """
    # Add options and initialize the webdriver
    options = webdriver.FirefoxOptions()
    options.add_argument("--disable-cookies")
    driver = webdriver.Firefox(options=options)

    # Get into the main webpage
    driver.get("https://www.filmaffinity.com/us/main.html")
    time.sleep(3)

    # Go into the new Netflix releases webpage
    get_netflix_page(driver)
    time.sleep(3)

    # Get and save the data containing the films
    df = get_releases_df(driver)
    df.to_csv(os.path.join(DATA_PATH, 'netflix_releases.csv'), index=False)
    logger.info("Netflix new releases data correctly extracted")

    # Go to the most voted netflix
    driver.get("https://www.filmaffinity.com/us/main.html")
    time.sleep(3)
    get_netflix_voted_page(driver)
    time.sleep(3)

    # Get and save the data containing the films
    df = get_voted_df(driver)
    df.to_csv(os.path.join(DATA_PATH, 'netflix_most_voted.csv'), index=False)
    logger.info("Netflix most voted content data correctly extracted")

    # Go to the most voted netflix
    driver.get("https://www.filmaffinity.com/us/main.html")
    time.sleep(3)
    get_netflix_best_page(driver)
    time.sleep(3)

    # Get and save the data containing the films
    df = get_best_df(driver)
    df.to_csv(os.path.join(DATA_PATH, 'netflix_best.csv'), index=False)
    logger.info("Netflix best content data correctly extracted")

    driver.quit()

