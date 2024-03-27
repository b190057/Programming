# Assigment
Assignment for PROGRAMMING FOR DATA SCIENCE
Student names:
* Álvaro Alonso Lancho
* Alberto González Ruíz
* Adrian Retes
* Pablo Torija Martínez
* Raúl Moldes del Castillo


# IMPORTANT
To interact with the program, linux or Windows OS must be needed (for logging)

## Structure of the project

The project has the following structure:

```
📦Programming
 ┣ 📂data
 ┃ ┣ 📜box_office.csv
 ┃ ┣ 📜netflix_best.csv
 ┃ ┣ 📜netflix_most_voted.csv
 ┃ ┣ 📜netflix_releases.csv
 ┃ ┣ 📜releases.csv
 ┃ ┗ 📜top_films.csv
 ┣ 📂images
 ┃ ┣ 📜box_office.png
 ┃ ┣ 📜collaboration_directors_actors.png
 ┃ ┣ 📜combined_plot.png
 ┃ ┣ 📜netflix_releases2024_April.png
 ┃ ┣ 📜netflix_releases2024_June.png
 ┃ ┣ 📜netflix_releases2024_March.png
 ┃ ┣ 📜netflix_releases2024_May.png
 ┃ ┣ 📜netflix_votes_rating.png
 ┃ ┗ 📜top_producers.png
 ┣ 📂log
 ┃ ┣ 📜scraper.log
 ┃ ┗ 📂config
 ┃   ┣ 📜logger_linux.yml
 ┃   ┗ 📜logger_windows.yml
 ┣ 📂scraper
 ┃ ┣ 📜main_scraper.py
 ┃ ┣ 📜netflix.py
 ┃ ┣ 📜releases.py
 ┃ ┗ 📜top_films.py
 ┣ 📂visualization
 ┃ ┣ 📜main_visualization.py
 ┃ ┣ 📜netflix_visualization.py
 ┃ ┣ 📜releases_visualization.py
 ┃ ┣ 📜top_films_visualization.py
 ┃ ┗ 📂utils
 ┃   ┗ 📜calendar.py
 ┣ 📜constants.py
 ┣ 📜main.py
 ┣ 📜README.md
 ┗ 📜requirements.txt
```

There are five folders that stores the following information:
* `data` this folder contains all the files in csv format extracted by the different scrappers
* `images` this folder contains all the png generated for visualization showing the data obtained in the `data` folder
* `log` this folder contains all the configuration for the personalized logging
* `scraper` this folder contains all the logic for the scrapers, lunched by a main scraper. The data is stored in the `data` folder
* `visualization` this folder contains all the logic for the data visualization, launched by a main visualization. The visualizations are stored in the `images` folder

## How to install the dependencies

First, a virtual environment must be created

After that, install the `requirements.txt` file which contains all the necessary dependencies with the specific versions used.

```sh
pip install -r requirements.txt
```

## How to interact with the program

You just need to execute `main.py` by staying this file in the root of the project

```sh
python main.py
```

## Description of folders and files
### scraper:
#### main_scraper.py: this file just execute the three scrapers presented as follows
#### netflix.py: this file generates the 3 different csv, 
COMPLETAR