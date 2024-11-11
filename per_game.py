import os
import re
import logging
import requests
import unicodedata
from bs4 import BeautifulSoup
import argparse
import sys
import glob

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "https://tinfoil.io/Title/"
HTML_FILE_TEMPLATE = "tinfoil_page_{}.html"
CHEAT_CODE_DIR = "cheat_code"

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

# Function to process a single game ID
def process_game(game_id):
    url = f"{BASE_URL}{game_id}"

    # Ensure the cheat_code directory exists
    os.makedirs(CHEAT_CODE_DIR, exist_ok=True)

    # Adjust html_file path to be inside cheat_code directory
    html_file = os.path.join(CHEAT_CODE_DIR, HTML_FILE_TEMPLATE.format(game_id))

    # Download HTML content
    logging.info(f"Downloading HTML content from {url}")
    response = requests.get(url)
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(response.text)
    logging.info(f"Downloaded HTML content to {html_file}")

    # Parse the HTML content
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Extract game title
    game_title_element = soup.find('h1')
    if not game_title_element:
        logging.error("Game title not found.")
        return
    game_title = game_title_element.get_text(strip=True)
    game_title = sanitize_name(game_title, for_folder=True)
    logging.debug(f"Game title extracted: {game_title}")

    # Extract build IDs
    build_ids = []
    build_table = soup.find('table', class_='fixed table')
    if build_table:
        rows = build_table.find_all('tr')[1:]
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 2:
                build_id = columns[0].get_text(strip=True)[:16]
                version = columns[1].get_text(strip=True)
                build_ids.append((build_id, version))
                logging.debug(f"Build ID extracted: {build_id} (Version: {version})")
    else:
        logging.error("Build ID section not found.")

    if not build_ids:
        logging.error("No build IDs extracted.")
        return

    # Extract cheats
    cheats = []
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

                logging.debug(f"Cheat extracted: {cheat_name} (Patch: {patch_version})")
                cheats.append({
                    'name': cheat_name,
                    'folder_name': cheat_folder_name,
                    'patch': patch_version,
                    'details': cheat_details
                })
    else:
        logging.error("Cheat section not found.")

    if not cheats:
        logging.error("No cheats extracted.")
        return

    # Create a set of versions that have cheats
    cheat_versions = set(cheat['patch'] for cheat in cheats)
    logging.debug(f"Versions with cheats: {cheat_versions}")

    # Create directory structure and save cheats
    base_dir = os.path.join(os.getcwd(), CHEAT_CODE_DIR, game_title)
    os.makedirs(base_dir, exist_ok=True)

    for build_id, version in build_ids:
        if version not in cheat_versions:
            logging.info(f"No cheats for version {version} (Build ID: {build_id}). Skipping.")
            continue  # Skip this build ID if no cheats for this version

        build_dir = os.path.join(base_dir, build_id)
        os.makedirs(build_dir, exist_ok=True)
        logging.info(f"Build directory created: {build_dir}")

        for cheat in cheats:
            if cheat['patch'] == version:
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

    logging.info(f"Processing for game ID {game_id} completed successfully.")

# Cleanup function to delete all downloaded HTML files
def cleanup_html_files():
    html_files = glob.glob(os.path.join(CHEAT_CODE_DIR, "tinfoil_page_*.html"))
    for html_file in html_files:
        try:
            os.remove(html_file)
            logging.info(f"Deleted temporary file: {html_file}")
        except Exception as e:
            logging.error(f"Failed to delete file: {html_file}, Error: {e}")

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape cheats for multiple game IDs from tinfoil.io.")
    parser.add_argument('-g', '--gameids', type=str, help="Comma-separated list of game IDs")
    parser.add_argument('-t', '--textfile', type=str, help="Text file containing game IDs (one per line)")
    args = parser.parse_args()

    game_ids = []
    if args.gameids:
        game_ids.extend(args.gameids.split(','))

    if args.textfile:
        try:
            with open(args.textfile, 'r') as file:
                game_ids.extend([line.strip() for line in file if line.strip()])
        except FileNotFoundError:
            logging.error(f"Text file '{args.textfile}' not found.")
            sys.exit(1)

    if not game_ids:
        parser.print_help()
        sys.exit(1)

    for game_id in game_ids:
        game_id = game_id.strip()
        if game_id:
            logging.info(f"Processing game ID: {game_id}")
            process_game(game_id)

    # Cleanup HTML files
    cleanup_html_files()
    print("All game IDs processed successfully. Temporary HTML files have been deleted.")
