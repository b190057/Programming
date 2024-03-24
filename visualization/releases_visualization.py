import os
import re

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import pandas as pd

from visualization import logger
from constants import DATA_PATH
from constants import IMAGES_PATH


def visualization_box_office(df_join: pd.DataFrame) -> None:
    """
    A plot that shows the box office information of the current releases

    @param df_join: Dataframe with the processed data
    @return: A plot that shows the most frequency apparition of the 1000 films
    """

    # get the data
    df_join = df_join.sort_values(by='Duration', ascending=False)
    normalization_index = 42000

    # parse data to list
    title_list = df_join['Title'].to_list()
    weekend_gross_list = [int(size_str) / normalization_index for size_str in df_join['Weekend Gross'].to_list()]
    total_gross_list = [int(size_str) / normalization_index for size_str in df_join['Total Gross'].to_list()]
    weeks_list = df_join['Weeks'].to_list()
    duration_list = df_join['Duration'].to_list()
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'magenta']

    # start the plot
    fig, axs = plt.subplots(1, 2, figsize=(14, 7))

    # Trazar los datos en el primer subgráfico
    axs[0].scatter(weeks_list, duration_list, s=total_gross_list, c=colors)
    axs[0].set_title('Box office total gross', weight='bold')
    axs[0].set_xlabel('Weeks')
    axs[0].set_ylabel('Duration (minutes)')
    axs[0].grid(True)

    # Crear una leyenda para el primer subgráfico
    handles = [mpatches.Patch(color=color, label=label) for label, color in zip(title_list, colors)]
    axs[0].legend(handles=handles, loc='upper right', frameon=True)

    # Trazar los datos en el segundo subgráfico (igual al primero)
    axs[1].scatter(weeks_list, duration_list, s=weekend_gross_list, c=colors)
    axs[1].set_title('Box office weekend gross', weight='bold')
    axs[1].set_xlabel('Weeks')
    axs[1].set_ylabel('Duration (minutes)')
    axs[1].grid(True)

    # Crear una leyenda para el segundo subgráfico (igual al primero)
    axs[1].legend(handles=handles, loc='upper right', frameon=True)

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_PATH, 'box_office.png'))
    plt.show()


def visualization_producers(df_releases: pd.DataFrame) -> None:
    """
    A plot that shows the most frequent producers of the released films

    @param df_releases: Dataframe with no missing actor
    @return: A plot that shows the most frequent producers of the released films
    """

    # Count the participating of each actor
    counting_producers = {}
    df_releases['Producers'].apply(
        lambda producers: [
            counting_producers.update({producer.strip(): counting_producers.get(producer.strip(), 0) + 1}) for producer
            in producers])

    # Represent actors that have done more than 8 films
    producer_names = list(counting_producers.keys())
    producer_frequencies = list(counting_producers.values())
    filtered_producers = [(name, frequency) for name, frequency in zip(producer_names, producer_frequencies) if
                          frequency >= 2]

    # create pie chart
    names, values = zip(*filtered_producers)

    plt.title('Top producers of the current releases', fontsize=20, weight='bold')
    plt.pie(values, labels=names, autopct='%1.1f%%')

    plt.savefig(os.path.join(IMAGES_PATH, 'top_producers.png'))
    plt.show()


def data_cleaning() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract and clean the data to be used in the different visualizations

    @return: 2 different df that will be used for the data visualization
    """
    # load csv
    df_box_office = pd.read_csv(os.path.join(DATA_PATH, 'box_office.csv'))
    df_releases = pd.read_csv(os.path.join(DATA_PATH, 'releases.csv'))

    # clean columns
    df_box_office = df_box_office.drop(columns=['#', 'Genre'])

    # Check null values
    if df_box_office.isnull().any()['Title'] or df_releases.isnull().any()['Title']:
        logger.error("There are films with no titles!!")
        df_releases.dropna(subset=['Title'])
        df_box_office.dropna(subset=['Title'])

    df_releases_aux = df_releases.copy()

    if df_releases.isnull().any().any():
        logger.error("There are null values in the releases csv")
        # check the null values
        print(df_releases[df_releases.isnull().any(axis=1)])

    if df_box_office.isnull().any().any():
        logger.error("There are null values in the box office csv")
        # check the null values
        print(df_box_office[df_box_office.isnull().any(axis=1)])

    # clean the title name
    df_box_office['Title'] = df_box_office['Title'].apply(lambda x: x.strip())

    # clean the gross with regex
    regex = r'\d{1,3}(?:,\d{3})*'
    df_box_office['Total Gross'] = df_box_office['Total Gross'].apply(
        lambda x: re.search(regex, x).group().replace(',', '') if x and re.search(regex, x) else None)
    df_box_office['Weekend Gross'] = df_box_office['Weekend Gross'].apply(
        lambda x: re.search(regex, x).group().replace(',', '') if x and re.search(regex, x) else None)

    # clean the duration
    regex = r'\b\d+\b'

    df_releases_aux = df_releases_aux.dropna(subset=['Duration'])
    df_releases_aux['Duration'] = df_releases_aux['Duration'].apply(
        lambda x: re.search(regex, x).group() if x and re.search(regex, str(x)) else None)

    # join the 2 dataframes by the colum 'Title'
    df_join = pd.merge(df_releases_aux, df_box_office, on='Title')

    # clean the producers
    df_releases = df_releases.dropna(subset=['Producers'])
    df_releases['Producers'] = df_releases['Producers'].apply(
        lambda x: str(x).split('Distributor')[0].strip().replace('.', '').split(', ') if str(x).split(
            'Distributor') else None)
    logger.info("Data preprocessed correctly")

    return df_join, df_releases


def start_visualization() -> None:
    df_join, df_releases = data_cleaning()

    # start visualizations
    visualization_producers(df_releases)
    logger.info("Visualization producers succeed")

    visualization_box_office(df_join)
    logger.info("Visualization of box office succeed")
