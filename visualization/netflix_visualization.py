import os
import re

import matplotlib.pyplot as plt

from visualization.utils.calendar import MplCalendar

import pandas as pd
import numpy as np

from visualization import logger
from constants import DATA_PATH, IMAGES_PATH, MONTH_NAMES


def visualization_popular_best(df_best: pd.DataFrame, df_votes: pd.DataFrame) -> None:
    """
    A plot that shows the box office information of the best/most voted releases

    @param df_best: Dataframe with the processed data of the best releases
    @param df_votes: Dataframe with the processed data of the most voted releases
    @return: A plot that shows the box office information of the best/most voted releases
    """

    # convert n_votes to int
    df_best['n_votes'] = df_best['n_votes'].astype(int)
    df_votes['n_votes'] = df_votes['n_votes'].astype(int)

    # group votes by the number indicated by the variable n_votes
    n_votes = 1000
    df_best['n_votes_grouped'] = (df_best['n_votes'] / n_votes).apply(np.ceil).astype(int)
    df_votes['n_votes_grouped'] = (df_votes['n_votes'] / n_votes).apply(np.ceil).astype(int)

    # add column to indicate type
    df_best['Type'] = 'Best'
    df_votes['Type'] = 'More popular'

    # combine both dataframes
    df_combined = pd.concat([df_best, df_votes], ignore_index=True)

    # order dataframe by rating
    df_combined = df_combined.sort_values(by='rating', ascending=True)

    # create scatter plot
    plt.figure(figsize=(14, 8))

    # color data
    best = 'blue'
    more_popular = 'red'

    # plot data
    plt.scatter(df_combined['n_votes_grouped'], df_combined['rating'],
                c=df_combined['Type'].map({'Best': best, 'More popular': more_popular}), alpha=0.5, s=50)

    # add labels and title
    plt.xlabel(f'Number of votes (for each {str(n_votes)})')
    plt.ylabel('Rating')
    plt.title('Relationships between the best and more popular series')

    # adjust x axis limits
    plt.xlim(df_combined['n_votes_grouped'].min() - 1, df_combined['n_votes_grouped'].max() + 1)

    # rotate labels to be legible
    plt.xticks(np.unique(df_combined['n_votes_grouped']), [f"{x}k" for x in np.unique(df_combined['n_votes_grouped'])],
               rotation=45)

    # create legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=best, markersize=10, label='Best'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=more_popular, markersize=10, label='More popular')]

    # add legend
    plt.legend(handles=legend_elements, title='Type', loc='best')

    # save the plot
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_PATH, 'netflix_votes_rating.png'))


def divide_string_length(string, length=35):
    return '\n'.join(string[i:i + length] for i in range(0, len(string), length))


def visualization_next_release(df_releases: pd.DataFrame) -> None:
    """
    A calendar plot that shows the next netflix releases with the origin country and genre

    @param df_releases: Dataframe with information of the next netflix releases
    @return: A plot that shows the next netflix releases
    """

    # get the data divided in year, month and day, then the info is saved in a list
    data = {}
    for index, row in df_releases.iterrows():
        year = row['Release_date'].year
        month = row['Release_date'].month
        day = row['Release_date'].day
        genres = str(row['genres'])[1:-1].replace("'", "")
        origin_country = row['Origin_country']
        title = row['Title']
        if year not in data.keys():
            data[year] = {}
        if month not in data[year].keys():
            data[year][month] = {}
        if day not in data[year][month].keys():
            data[year][month][day] = []

        data[year][month][day].append({
            'title': title,
            'genres': genres,
            'country': origin_country
        })

    get_year_month = list()
    for key in data.keys():
        for key2 in data[key].keys():
            get_year_month.append((key, key2))

    create_calendars = list()
    for year, month in get_year_month:
        cal = MplCalendar(year, month)
        for day in data[year][month].keys():
            for film in data[year][month][day]:
                title = divide_string_length(film['title'])
                genres = divide_string_length(film['genres'])
                country = divide_string_length(film['country'])
                cal.add_event(day, f"""title: {title}\ngenre(s): {genres}\ncountry: {country}\n""")
        create_calendars.append(cal)

    logger.info(f"There are {str(len(create_calendars))} months to plot netflix next releases")

    for cal in create_calendars:
        cal.save(os.path.join(IMAGES_PATH, f"netflix_releases{cal.year}_{MONTH_NAMES[cal.month - 1]}.png"))


def data_cleaning() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Extract and clean the data to be used in the different visualizations

    @return: 2 different df that will be used for the data visualization
    """
    # load csv
    df_best = pd.read_csv(os.path.join(DATA_PATH, 'netflix_best.csv'))
    df_votes = pd.read_csv(os.path.join(DATA_PATH, 'netflix_most_voted.csv'))
    df_releases = pd.read_csv(os.path.join(DATA_PATH, 'netflix_releases.csv'))

    # rename "Genres" to "genres"
    df_best = df_best.rename(columns={'Genres': 'genres'})
    df_votes = df_votes.rename(columns={'Genres': 'genres'})

    # Check null values
    if df_best.isnull().any()['Title'] or df_votes.isnull().any()['Title'] or df_releases.isnull().any()['Title']:
        logger.error("There are films with no titles!!")
        df_releases.dropna(subset=['Title'])
        df_votes.dropna(subset=['Title'])
        df_best.dropna(subset=['Title'])

    if df_releases.isnull().any().any():
        logger.error("There are null values in the netflix releases csv")
        # check the null values
        print(df_releases[df_releases.isnull().any(axis=1)])

    if df_best.isnull().any().any():
        logger.error("There are null values in the best netflix csv")
        # check the null values
        print(df_best[df_best.isnull().any(axis=1)])

    if df_votes.isnull().any().any():
        logger.error("There are null values in the most voted netflix csv")
        # check the null values
        print(df_votes[df_votes.isnull().any(axis=1)])

    # clean the number of votes
    regex = r'\d{1,3}(?:,\d{3})*'
    df_best['n_votes'] = df_best['n_votes'].apply(
        lambda x: re.search(regex, x).group().replace(',', '') if x and re.search(regex, x) else None)
    df_votes['n_votes'] = df_votes['n_votes'].apply(
        lambda x: re.search(regex, x).group().replace(',', '') if x and re.search(regex, x) else None)

    # clean rating to get an over 100 rating
    regex = r'\d{1,2}(?:.\d{1,2})*'
    df_best['rating'] = df_best['rating'].apply(
        lambda x: re.search(regex, str(x)).group().replace('.', '') if x and re.search(regex, str(x)) else None)
    df_votes['rating'] = df_votes['rating'].apply(
        lambda x: re.search(regex, str(x)).group().replace('.', '') if x and re.search(regex, str(x)) else None)

    # clean genres
    df_releases['genres'] = df_releases['genres'].apply(lambda x: str(x).split(', ') if str(x).split(',') else None)
    df_votes['genres'] = df_votes['genres'].apply(lambda x: str(x).split(', ') if str(x).split(',') else None)
    df_best['genres'] = df_best['genres'].apply(lambda x: str(x).split(', ') if str(x).split(',') else None)

    # clean dates
    df_releases['Release_date'] = pd.to_datetime(df_releases['Release_date'])

    return df_releases, df_best, df_votes


def start_visualization() -> None:
    df_releases, df_best, df_votes = data_cleaning()

    # start visualizations
    visualization_next_release(df_releases)
    logger.info("Visualization for netflix next releases succeed")

    visualization_popular_best(df_best, df_votes)
    logger.info("Visualization of the popular/best netflix content succeed")
