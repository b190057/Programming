import os

import pandas as pd

import matplotlib.pyplot as plt
import networkx as nx

from visualization import logger
from constants import DATA_PATH
from constants import IMAGES_PATH


def convert_to_list(string: str) -> list:
    """
    Auxiliar function to convert a string to a list (necessary to load the info of the df)

    @param string: string to be converted to list
    @return:  the string split as list
    """

    # eliminate the brackets and quotes and split the string by commas
    if string:
        return string.strip('][').replace("'", "").split(', ')
    else:
        return []


def visualization_collaboration(df_directors_actors: pd.DataFrame) -> None:
    """
    A plot that shows the collaboration between directors and actors

    @param df_directors_actors: Dataframe with no missing director or actor
    @return: A plot that shows the collaboration between directors and actors
    """

    # convert strings to a real list
    df_directors_actors['Directors'] = df_directors_actors['Directors'].apply(convert_to_list)
    df_directors_actors['Actors'] = df_directors_actors['Actors'].apply(convert_to_list)

    # create new column to combine actors and directors to a list for every film
    df_directors_actors['Collaboration'] = df_directors_actors.apply(
        lambda row: [(direct, act) for direct in row['Directors'] for act in row['Actors']], axis=1)

    # convert the collaborations list into a serie to count the frequencies
    collaborations_series = df_directors_actors['Collaboration'].explode().value_counts()

    # get the actors, directors and number of collaborations of all films
    top_collaborations = list()
    actors = set()
    directors = set()
    # change the number to add more collaborations
    n_collaborations = 12
    for (director, actor), count in collaborations_series.items():
        if actor != director:
            if n_collaborations == 0:
                break
            n_collaborations -= 1
            top_collaborations.append((director, actor, count))
            actors.add(actor)
            directors.add(director)

    # define colors
    director_color = 'lightblue'
    actor_color = 'lightgreen'
    edge_color = 'gray'
    weight_color = 'red'

    # create graph
    G = nx.Graph()

    # add nodes, edges and weights to the graph
    for actor in actors:
        G.add_node(actor, color=actor_color)
    for director in directors:
        G.add_node(director, color=director_color)
    for director, actor, count in top_collaborations:
        G.add_edge(director, actor, weight=count)

    # create figure
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=2, seed=42)

    # obtain colors
    node_colors = [data['color'] for _, data in G.nodes(data=True)]

    # reformat graph info
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color=node_colors, font_size=8, font_weight='bold',
            edge_color=edge_color, width=2, alpha=0.8)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color=weight_color)

    # create legend in the top right corner
    plt.legend(handles=[plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=director_color, markersize=10,
                                   label='Directors'),
                        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=actor_color, markersize=10,
                                   label='Actors')],
               loc='upper right')

    # add info of the plot
    plt.title(f'Top {str(n_collaborations)} Collaborations between Directors and Actors')
    plt.tight_layout()
    plt.axis('off')

    # save the plot
    plt.savefig(os.path.join(IMAGES_PATH, 'collaboration_directors_actors.png'))


def visualization_frequency_actors_directors_genres(df_genres_actors_directors: pd.DataFrame) -> None:
    """
    Saves a plot that shows the top 20 genres,20 directors and 20 actors in the top 1000 films

    @param df_genres_actors_directors: Dataframe with no missing genres, actors or directors in the same row
    @return: A dictionary containing the number of appearance of each genre
    """
    # count genres
    counting_genres = {}
    df_genres_actors_directors['genres'].apply(
        lambda genres: [counting_genres.update({genre.strip(): counting_genres.get(genre.strip(), 0) + 1}) for genre in
                        str(genres).split(',') if isinstance(genres, str) and not pd.isnull(genres)])

    # count directors
    counting_directors = {}
    df_genres_actors_directors['Directors'].apply(lambda directors: [
        counting_directors.update({director.strip(): counting_directors.get(director.strip(), 0) + 1}) for director in
        str(directors).split(',') if isinstance(directors, str) and not pd.isnull(directors)])

    # count actors
    counting_actors = {}
    df_genres_actors_directors['Actors'].apply(
        lambda actors: [counting_actors.update({actor.strip(): counting_actors.get(actor.strip(), 0) + 1}) for actor in
                        str(actors).split(',') if isinstance(actors, str) and not pd.isnull(actors)])

    # order the data
    counting_genres_sorted = dict(sorted(counting_genres.items(), key=lambda item: item[1], reverse=True))
    counting_directors_sorted = dict(sorted(counting_directors.items(), key=lambda item: item[1], reverse=True))
    counting_actors_sorted = dict(sorted(counting_actors.items(), key=lambda item: item[1], reverse=True))

    top_n = 20
    top_20_genres = dict(list(counting_genres_sorted.items())[:top_n])
    top_20_directors = dict(list(counting_directors_sorted.items())[:top_n])
    top_20_actors = dict(list(counting_actors_sorted.items())[:top_n])

    # create figure with 3 plots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    # graph for genres
    bars_genres = ax1.barh(list(top_20_genres.keys()), list(top_20_genres.values()), color='skyblue')
    ax1.set_title('Top 20 genre distribution', fontweight='bold')
    ax1.set_xlabel('Frequency')
    ax1.set_ylabel('Genre')

    # add the number of appearances of each genre
    for bar, count in zip(bars_genres, top_20_genres.values()):
        ax1.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{count}', ha='left', va='center')

    # graph for directors
    bars_directors = ax2.barh(list(top_20_directors.keys()), list(top_20_directors.values()), color='lightgreen')
    ax2.set_title('Top 20 directors distribution', fontweight='bold')
    ax2.set_xlabel('Frequency')
    ax2.set_ylabel('Director')

    # add the number of appearances of each director
    for bar, count in zip(bars_directors, top_20_directors.values()):
        ax2.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{count}', ha='left', va='center')

    # graph for actors
    bars_actors = ax3.barh(list(top_20_actors.keys()), list(top_20_actors.values()), color='salmon')
    ax3.set_title('Top 20 actors distribution', fontweight='bold')
    ax3.set_xlabel('Frequency')
    ax3.set_ylabel('Actor')

    # add the number of appearances of each actor
    for bar, count in zip(bars_actors, top_20_actors.values()):
        ax3.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{count}', ha='left', va='center')

    # save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_PATH, 'combined_plot.png'))


def data_cleaning() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract and clean the data to be used in the different visualizations

    @return: 2 different df that will be used for the data visualization
    """
    df = pd.read_csv(os.path.join(DATA_PATH, 'top_films.csv'))

    # Check if all films have title
    films_no_title = list(df[df['Title'].isnull()].index)
    if films_no_title:
        logger.info(f"There are {len(films_no_title)} that doesn't have title")
        # Drop films with no title
        df = df.dropna(subset=['Title'])

    # df to return
    df_directors_actors = df.copy()
    df_genres_actors_directors = df.copy()

    # check if all films have director
    df_directors_actors = df_directors_actors.dropna(subset=['Directors'])

    # check if all films have actor
    df_directors_actors = df_directors_actors.dropna(subset=['Actors'])

    # check if all films have genre, actor or director
    rows_with_missing_data = df[df[['Directors', 'genres', 'Actors']].isna().all(axis=1)]
    if len(rows_with_missing_data) > 0:
        logger.error("There are films with all missing data")
        print(rows_with_missing_data)
        raise Exception("There are films with all missing data")

    # Drop the unnecessary columns
    df_directors_actors = df_directors_actors.drop('genres', axis=1)
    df_directors_actors = df_directors_actors.drop('Title', axis=1)

    df_genres_actors_directors = df_genres_actors_directors.drop('Title', axis=1)

    return df_genres_actors_directors, df_directors_actors


def start_visualization() -> None:
    """
    Data visualization for the top 1000 FA films

    @return: Shows all the plots and save them into the folder images
    """
    df_genres_actors_directors, df_directors_actors = data_cleaning()

    visualization_frequency_actors_directors_genres(df_genres_actors_directors)
    logger.info("Visualization for most appeared frequency succeed")

    visualization_collaboration(df_directors_actors)
    logger.info("Visualization of collaborations succeed")
