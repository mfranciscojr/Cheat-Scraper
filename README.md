# Switch Cheats Scraper

This project is a Python script that fetches cheat codes for Switch games from **tinfoil.io** and **cheatslips.com**. It generates organized cheat files and HTML pages for easy browsing and downloading. The script can process specific games by Title ID, search by game titles, process all available games, or work with specific TitleID and BuildID pairs.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Options](#options)
  - [Examples](#examples)
- [Directory Structure](#directory-structure)
- [Notes](#notes)
- [License](#license)

## Features

- Fetch cheat codes from **tinfoil.io** and **cheatslips.com**.
- Supports fetching cheats for:
  - Specific game IDs (Title IDs).
  - Games matching specific titles or partial titles.
  - Specific TitleID and BuildID pairs.
  - All available games.
- Generates organized cheat files in the appropriate directory structure.
- Creates HTML pages for each game with searchable and sortable tables.
- Generates a main index HTML page listing all processed games.
- Optional integration with **cheatslips.com** API for additional cheats (requires API key).

## Prerequisites

- Python 3.6 or higher.
- Internet connection to access **tinfoil.io** and **cheatslips.com** APIs.

## Installation

1. **Clone the repository or download the script files** to your local machine.

   ```bash
   git clone https://github.com/mfranciscojr/Cheat-Scraper
   ```

2. **Navigate to the project directory**.

   ```bash
   cd Cheat-Scraper
   ```

3. **Install the required packages** using `pip`.

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` includes:

   ```
    attrs==24.2.0
    beautifulsoup4==4.12.3
    certifi==2024.8.30
    charset-normalizer==3.4.0
    colorama==0.4.6
    h11==0.14.0
    idna==3.10
    outcome==1.3.0.post0
    prompt-toolkit==3.0.36
    PySocks==1.7.1
    questionary==2.0.1
    requests==2.32.3
    selenium==4.26.1
    sniffio==1.3.1
    sortedcontainers==2.4.0
    soupsieve==2.6
    trio==0.27.0
    trio-websocket==0.11.1
    typing_extensions==4.12.2
    urllib3==2.2.3
    wcwidth==0.2.13
    websocket-client==1.8.0
    wsproto==1.2.0
   ```

## Usage

The main script to run is `main.py`. You can execute it with different options depending on your needs.

### Options

- `-g`, `--gameid`: Specify a comma-separated list of game IDs (Title IDs) to process.
- `-t`, `--title`: Specify a comma-separated list of game titles or partial titles to search for.
- `-b`, `--buildid`: Specify a semicolon-separated list of `titleid,buildid` pairs. If used without arguments, the script will prompt for input.
- `-a`, `--all`: Process all available games (may take a long time).
- `-k`, `--apikey`: Provide your **cheatslips.com** API key. If not provided, you'll be prompted to enter it.

**Note:** Please specify only one of `-g`, `-t`, `-b`, or `-a` per execution.

### Examples

#### 1. Fetch Cheats by Game ID (Title ID)

```bash
python main.py -g 01001B300B9BE000
```

This command fetches cheats for the game with the specified Title ID.

#### 2. Search for Games by Title

```bash
python main.py -t 'diablo'
```

This command searches for games with titles containing 'diablo'. If multiple games match, you'll be prompted to select one or more.

#### 3. Fetch Cheats by TitleID and BuildID Pair

```bash
python main.py -b '01001B300B9BE000,2607A74F5DF7754C'
```

This command fetches cheats for the specified TitleID and BuildID pair.

You can also provide multiple pairs:

```bash
python main.py -b 'titleid1,buildid1;titleid2,buildid2'
```

#### 4. Process All Games
**Warning:**  Don't provide cheatslip API for this, cheatslip limits their API to 3 BuildID's only.
```bash
python main.py -a
```

**Warning:** Processing all games may take a significant amount of time and may hit API rate limits.

#### 5. Provide **cheatslips.com** API Key

You can provide your **cheatslips.com** API key using the `-k` option:

```bash
python main.py -g 01001B300B9BE000 -k YOUR_API_KEY_HERE
```

If you don't provide the API key as an argument, the script will prompt you to enter it. You can leave it blank to skip fetching from **cheatslips.com**.

### Outputs

- **Cheat Files**: Saved in the `cheat_code` directory, organized by game title and build ID.
- **HTML Pages**:
  - Individual game pages: Located in `cheat_code/<Game Title>/index.html`.
  - Main index page: Located at `cheat_code/index.html`.
- **ZIP Files**: Each build ID directory is zipped for easy download.

### Navigating the HTML Pages

- The HTML pages include searchable and sortable tables.
- Use the dropdown filters at the top of each column to filter data.
- Click on column headers to sort the data.

## Directory Structure

After running the script, your directory structure will look like this:

```
.
├── cheat_code
│   ├── index.html                # Main index page listing all games
│   ├── <Game Title 1>
│   │   ├── index.html            # Game-specific page
│   │   └── <Build ID 1>
│       ├── <Cheat Name 1>
│       │   └── cheats
│       │       └── <Build ID>.txt
│       ├── <Cheat Name 2>
│       │   └── cheats
│       │       └── <Build ID>.txt
│       └── <Game Title> - <Build ID>.zip   # Zipped cheat files
│   └── <Game Title 2>
│       └── ...
├── main.py
├── requirements.txt
└── scripts
    ├── __init__.py
    ├── cheats_processing.py
    ├── constants.py
    ├── fetch_game_data.py
    ├── html_generation.py
    └── utils.py
```

## Notes

- **API Key for cheatslips.com**:
  - You can get an API key by registering at [cheatslips.com](https://www.cheatslips.com/) and generating an API key in your profile settings.
  - Providing an API key allows the script to fetch additional cheats from **cheatslips.com**.
  - If no API key is provided, the script will only fetch cheats from **tinfoil.io**.
- **Respect API Rate Limits**:
  - Be cautious when using the `-a` option to process all games, as it may hit API rate limits.
  - Consider adding delays or processing games in batches if necessary.
- **Dependencies**:
  - Ensure all dependencies in `requirements.txt` are installed.
  - Use a virtual environment to avoid conflicts with other Python packages.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer**: This script is intended for educational and personal use only. Please respect the terms of service of **tinfoil.io** and **cheatslips.com** when using their APIs.

