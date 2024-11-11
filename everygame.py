import os
import re
import logging
import requests
import unicodedata
import time
import random
from bs4 import BeautifulSoup
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "https://tinfoil.io/Title/"
API_URL = "https://tinfoil.media/Title/ApiJson/?rating_content=&language=&category=&region=us&rating=0"
HTML_FILE_TEMPLATE = "tinfoil_page_{}.html"
OUTPUT_FOLDER = "cheat_code"

# Function to sanitize folder and file names
def sanitize_name(name, for_folder=False):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'^[^a-zA-Z]+', '', name)

    if for_folder:
        sanitized_name = re.sub(r'[^\w\s-]', '', name).strip()
    else:
        sanitized_name = re.sub(r'[^\w\s\-\[\]]', '', name).strip()

    if sanitized_name.count('[') != sanitized_name.count(']'):
        sanitized_name = sanitized_name.rstrip(']')

    return sanitized_name

# Function to fetch all game IDs using the API
def fetch_all_game_ids():
    logging.info(f"Fetching all game IDs from API: {API_URL}")
    response = requests.get(API_URL)
    if response.status_code != 200:
        logging.error(f"Failed to fetch game IDs. Status code: {response.status_code}")
        return []

    try:
        data = response.json().get('data', [])
        game_ids = [(item['id'], re.sub(r'<.*?>', '', item['name'])) for item in data if 'id' in item and 'name' in item]
        logging.info(f"Found {len(game_ids)} game IDs.")
        return game_ids
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return []

# Function to check if a game has cheats
def has_cheats(game_id):
    url = f"{BASE_URL}{game_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cheats_section = soup.find('h4', string=re.compile("Cheats"))
    return bool(cheats_section)

# Function to process a single game ID
def process_game(game_id, game_name):
    url = f"{BASE_URL}{game_id}"
    html_file = HTML_FILE_TEMPLATE.format(game_id)

    # Download HTML content
    logging.info(f"Downloading HTML content from {url}")
    response = requests.get(url)
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(response.text)
    logging.info(f"Downloaded HTML content to {html_file}")

    # Parse the HTML content
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Sanitize game name
    game_title = sanitize_name(game_name, for_folder=True)
    logging.debug(f"Game title extracted: {game_title}")

    # Extract build IDs and cheats
    build_ids_with_cheats = {}
    build_table = soup.find('table', class_='fixed table')
    if build_table:
        rows = build_table.find_all('tr')[1:]
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 2:
                build_id = columns[0].get_text(strip=True)[:16]
                version = columns[1].get_text(strip=True)
                build_ids_with_cheats[build_id] = {'version': version, 'cheats': []}
                logging.debug(f"Build ID extracted: {build_id} (Version: {version})")
    else:
        logging.error("Build ID section not found.")

    # Extract cheats and associate them with build IDs
    cheats_section = soup.find('h4', string=re.compile("Cheats"))
    if cheats_section:
        cheat_table = cheats_section.find_next('table', class_='table')
        cheat_rows = cheat_table.find('tbody').find_all('tr')
        for cheat_row in cheat_rows:
            columns = cheat_row.find_all('td')
            if len(columns) >= 4:
                cheat_name = sanitize_name(columns[0].get_text(strip=True))
                cheat_folder_name = sanitize_name(columns[0].get_text(strip=True), for_folder=True)
                patch_version = columns[1].get_text(strip=True)
                source_elements = columns[3].find_all('li')
                cheat_details = "\n".join([item.get_text(strip=True) for item in source_elements])

                # Only add cheats to matching build ID versions
                for build_id, build_info in build_ids_with_cheats.items():
                    if build_info['version'] == patch_version:
                        build_info['cheats'].append({
                            'name': cheat_name,
                            'folder_name': cheat_folder_name,
                            'details': cheat_details
                        })
                        logging.debug(f"Cheat added for Build ID {build_id}: {cheat_name}")
    else:
        logging.error("Cheat section not found.")

    # Create directory structure and save cheats only for build IDs that have cheats
    base_dir = os.path.join(os.getcwd(), OUTPUT_FOLDER, game_title)
    os.makedirs(base_dir, exist_ok=True)

    for build_id, build_info in build_ids_with_cheats.items():
        if build_info['cheats']:  # Only create folders for build IDs with cheats
            build_dir = os.path.join(base_dir, build_id)
            os.makedirs(build_dir, exist_ok=True)
            logging.info(f"Build directory created: {build_dir}")

            for cheat in build_info['cheats']:
                cheat_dir = os.path.join(build_dir, cheat['folder_name'])
                os.makedirs(cheat_dir, exist_ok=True)
                logging.info(f"Cheat directory created: {cheat_dir}")

                cheats_folder = os.path.join(cheat_dir, 'cheats')
                os.makedirs(cheats_folder, exist_ok=True)

                cheat_file_path = os.path.join(cheats_folder, f"{build_id}.txt")
                try:
                    with open(cheat_file_path, 'w') as cheat_file:
                        cheat_file.write(f"[{cheat['name']}]\n")
                        cheat_file.write(cheat['details'])
                        logging.info(f"Cheat file written: {cheat_file_path}")
                except Exception as e:
                    logging.error(f"Failed to write cheat file: {cheat_file_path}, Error: {e}")

    # Cleanup HTML file
    try:
        os.remove(html_file)
        logging.info(f"Deleted temporary file: {html_file}")
    except Exception as e:
        logging.error(f"Failed to delete file: {html_file}, Error: {e}")

    logging.info(f"Processing for game ID {game_id} completed successfully.")

# Main function
if __name__ == "__main__":
    game_ids = fetch_all_game_ids()
    
    if not game_ids:
        logging.error("No game IDs found.")
        sys.exit(1)

    for game_id, game_name in game_ids:
        logging.info(f"Checking for cheats in game ID: {game_id} ({game_name})")
        if has_cheats(game_id):
            logging.info(f"Cheats found for game ID: {game_id}. Processing...")
            process_game(game_id, game_name)

            # Random delay between 10 to 30 seconds
            delay = random.randint(10, 30)
            logging.info(f"Waiting for {delay} seconds before processing the next game.")
            time.sleep(delay)
        else:
            logging.info(f"No cheats found for game ID: {game_id}. Skipping...")

    print("All games with cheats processed successfully.")
