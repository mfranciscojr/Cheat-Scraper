# Cheat Scraper

This Python script scrapes cheat codes for multiple game IDs, it extracts cheats and organizes the output in a structured directory format.

## Features

- Extracts the game title, build IDs, and available cheats for each game.
- Saves cheats in a folder structure organized by game title, build ID, and cheat name.


## Requirements

- Python 3.x
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (`pip install beautifulsoup4`)
- [Requests](https://docs.python-requests.org/) (`pip install requests`)

## How To

- Clone this repository
- Install the needed python library
  ``` bash
  pip install -r requirements.txt

## Usage

The script can process a list of game IDs provided either directly as command-line arguments or via a text file.

### Command-Line Arguments

- `-g, --gameids`: Comma-separated list of game IDs (e.g., `01008B900DC0A000,01008B900DC0A001`).
- `-t, --textfile`: Text file containing game IDs, one per line.

### Example Commands

```bash
# Example: Using a comma-separated list of game IDs
python per_game.py -g 01008B900DC0A000,01008B900DC0A001

# Example: Using a text file containing game IDs
python per_game.py -t game_ids.txt

# Scrape Everything
python everygame.py