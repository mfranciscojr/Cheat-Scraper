# scripts/fetch_game_data.py

import requests
import logging
import sys
import time
from bs4 import BeautifulSoup
from scripts.cheats_processing import get_cheats_from_cheatslips
from scripts.html_generation import generate_html_per_game, generate_main_index_html
from scripts.utils import sanitize_filename
from scripts.constants import CHEATSLIPS_API_TOKEN
from colorama import Fore
import os
import zipfile
import questionary

def fetch_game_data(specific_game_ids=None, process_all=False, title_queries=None, buildid_list=None):
    # Fetch game data and process according to the provided options
    url = "https://tinfoil.media/Title/ApiJson/"

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(Fore.YELLOW + f"Error fetching game data: {e}")
        sys.exit(1)

    # Parse the JSON content
    data = response.json()

    # Ensure 'data' key is present
    if 'data' not in data:
        logging.error(Fore.YELLOW + "No 'data' key found in the JSON response.")
        sys.exit(1)

    games_to_process = []

    # Map to quickly find games by ID
    game_map = {item['id']: item for item in data['data']}

    # Determine which games to process
    if buildid_list:
        # Process specific titleid,buildid pairs
        for pair in buildid_list:
            if ',' not in pair:
                logging.error(Fore.RED + f"Invalid format for buildid option: '{pair}'. Expected format is 'titleid,buildid'.")
                continue
            titleid, buildid = pair.split(',', 1)
            titleid = titleid.strip()
            buildid = buildid.strip()

            game = game_map.get(titleid)
            if not game:
                logging.error(Fore.RED + f"No game found with title ID {titleid}")
                continue

            # Extract the title from the 'name' field using BeautifulSoup
            name_field = game.get('name')
            if not name_field:
                logging.warning(Fore.YELLOW + f"No 'name' found for game ID {titleid}")
                continue

            soup = BeautifulSoup(name_field, 'html.parser')
            title = soup.get_text()

            logging.info(f"Processing game '{title}' (Title ID: {titleid}, Build ID: {buildid})")

            # Get Build IDs and Cheats for the current game
            build_ids = get_build_ids_and_cheats(titleid, title, specific_build_ids=[buildid])

            # Exclude build IDs with zero cheats
            build_ids_with_cheats = [build for build in build_ids if len(build.get('cheats', [])) > 0]

            # Check if any cheats are available for the game
            has_cheats = len(build_ids_with_cheats) > 0

            if has_cheats:
                # Prepare the game data
                game_data = {
                    'id': titleid,
                    'title': title,
                    'release_date': game.get('release_date'),
                    'size': game.get('size'),
                    'publisher': game.get('publisher'),
                    'build_ids': build_ids_with_cheats  # Use filtered build IDs
                }

                games_to_process.append(game_data)

                # Generate HTML per game
                generate_html_per_game(game_data)

                # Optional: Sleep to be respectful to the server
                time.sleep(0.1)  # Adjust the sleep time as needed
            else:
                logging.info(Fore.RED + f"No cheats available for game '{title}' with Build ID '{buildid}'. Skipping...")

    elif specific_game_ids:
        # Process specific game IDs
        for game_id in specific_game_ids:
            game = game_map.get(game_id)
            if not game:
                logging.error(Fore.RED + f"No game found with ID {game_id}")
                continue

            # Extract the title from the 'name' field using BeautifulSoup
            name_field = game.get('name')
            if not name_field:
                logging.warning(Fore.YELLOW + f"No 'name' found for game ID {game_id}")
                continue

            soup = BeautifulSoup(name_field, 'html.parser')
            title = soup.get_text()

            logging.info(f"Processing game '{title}' (Game ID: {game_id})")

            # Get Build IDs and Cheats for the current game
            build_ids = get_build_ids_and_cheats(game_id, title)

            # Exclude build IDs with zero cheats
            build_ids_with_cheats = [build for build in build_ids if len(build.get('cheats', [])) > 0]

            # Check if any cheats are available for the game
            has_cheats = len(build_ids_with_cheats) > 0

            if has_cheats:
                # Prepare the game data
                game_data = {
                    'id': game_id,
                    'title': title,
                    'release_date': game.get('release_date'),
                    'size': game.get('size'),
                    'publisher': game.get('publisher'),
                    'build_ids': build_ids_with_cheats  # Use filtered build IDs
                }

                games_to_process.append(game_data)

                # Generate HTML per game
                generate_html_per_game(game_data)

                # Optional: Sleep to be respectful to the server
                time.sleep(0.1)  # Adjust the sleep time as needed
            else:
                logging.info(Fore.RED + f"No cheats available for game '{title}'. Skipping...")

    elif title_queries:
        # Process games matching title queries
        for query in title_queries:
            query = query.strip().lower()
            matching_games = []
            for item in data['data']:
                name_field = item.get('name')
                if not name_field:
                    continue
                soup = BeautifulSoup(name_field, 'html.parser')
                title = soup.get_text()
                if query in title.lower():
                    matching_games.append(item)
            if not matching_games:
                logging.error(Fore.RED + f"No games found matching title '{query}'")
                continue
            elif len(matching_games) == 1:
                # Only one match, proceed
                games_to_process.append(matching_games[0])
            else:
                # Multiple matches, present selection
                choices = [
                    f"{item.get('id')} - {BeautifulSoup(item.get('name'), 'html.parser').get_text()}"
                    for item in matching_games
                ]
                selected_games = questionary.checkbox(
                    f"Multiple games found matching '{query}'. Please select one or more:",
                    choices=choices
                ).ask()
                if not selected_games:
                    logging.error(Fore.RED + f"No games selected for query '{query}'. Skipping...")
                    continue
                # Find the selected games
                selected_ids = [sel.split(' - ')[0] for sel in selected_games]
                selected_items = [item for item in matching_games if item.get('id') in selected_ids]
                games_to_process.extend(selected_items)

        # Process the selected games
        for game in games_to_process:
            game_id = game.get('id')
            name_field = game.get('name')
            if not name_field:
                logging.warning(Fore.YELLOW + f"No 'name' found for game ID {game_id}")
                continue

            soup = BeautifulSoup(name_field, 'html.parser')
            title = soup.get_text()

            logging.info(f"Processing game '{title}' (Game ID: {game_id})")

            # Get Build IDs and Cheats for the current game
            build_ids = get_build_ids_and_cheats(game_id, title)

            # Exclude build IDs with zero cheats
            build_ids_with_cheats = [build for build in build_ids if len(build.get('cheats', [])) > 0]

            # Check if any cheats are available for the game
            has_cheats = len(build_ids_with_cheats) > 0

            if has_cheats:
                # Prepare the game data
                game_data = {
                    'id': game_id,
                    'title': title,
                    'release_date': game.get('release_date'),
                    'size': game.get('size'),
                    'publisher': game.get('publisher'),
                    'build_ids': build_ids_with_cheats  # Use filtered build IDs
                }

                # Update the game data in the list
                games_to_process[games_to_process.index(game)] = game_data

                # Generate HTML per game
                generate_html_per_game(game_data)

                # Optional: Sleep to be respectful to the server
                time.sleep(0.1)  # Adjust the sleep time as needed
            else:
                logging.info(Fore.RED + f"No cheats available for game '{title}'. Skipping...")

    elif process_all:
        # Process all games
        for index, item in enumerate(data['data']):
            game_id = item.get('id')
            if not game_id:
                logging.warning(Fore.YELLOW + f"No 'id' found for item at index {index}")
                continue

            # Extract the title from the 'name' field using BeautifulSoup
            name_field = item.get('name')
            if not name_field:
                logging.warning(Fore.YELLOW + f"No 'name' found for game ID {game_id}")
                continue

            soup = BeautifulSoup(name_field, 'html.parser')
            title = soup.get_text()

            logging.info(f"Processing {index + 1}/{len(data['data'])}: {title}")

            # Get Build IDs and Cheats for the current game
            build_ids = get_build_ids_and_cheats(game_id, title)

            # Exclude build IDs with zero cheats
            build_ids_with_cheats = [build for build in build_ids if len(build.get('cheats', [])) > 0]

            # Check if any cheats are available for the game
            has_cheats = len(build_ids_with_cheats) > 0

            if has_cheats:
                # Prepare the game data
                game_data = {
                    'id': game_id,
                    'title': title,
                    'release_date': item.get('release_date'),
                    'size': item.get('size'),
                    'publisher': item.get('publisher'),
                    'build_ids': build_ids_with_cheats  # Use filtered build IDs
                }

                games_to_process.append(game_data)

                # Generate HTML per game
                generate_html_per_game(game_data)

                # Optional: Sleep to be respectful to the server
                time.sleep(0.1)  # Adjust the sleep time as needed
            else:
                logging.info(Fore.RED + f"No cheats available for game '{title}'. Skipping...")

    else:
        print("Please specify a game ID with -g or --gameid, use -t or --title to search by title, use -b or --buildid to specify titleid and buildid pairs, or use -a/--all to process all games.")
        sys.exit(1)

    if games_to_process:
        # Generate main index.html
        generate_main_index_html(games_to_process)

def get_build_ids_and_cheats(game_id, title, specific_build_ids=None):
    # (Include the full function code from your original script)
    # Ensure that all necessary imports and references are correctly adjusted.

    url = f"https://tinfoil.io/Title/{game_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(Fore.YELLOW + f"Error fetching data for game '{title}' (game ID {game_id}): {e}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')

    build_ids = []

    # Extract Build IDs
    build_header = soup.find('h2', string="Build ID's")
    if build_header:
        table_div = build_header.find_next_sibling('div')
        if table_div:
            table = table_div.find('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            full_build_id = cols[0].get_text(strip=True)
                            version = cols[1].get_text(strip=True)
                            build_id = full_build_id[:16]
                            # Initialize 'cheats' list and 'sources' list for each build ID
                            build_ids.append({
                                'build_id': build_id,
                                'version': version,
                                'cheats': [],
                                'sources': []
                            })

    # If specific_build_ids is provided, filter the build_ids
    if specific_build_ids:
        build_ids = [build for build in build_ids if build['build_id'] in specific_build_ids]
        if not build_ids:
            logging.warning(Fore.YELLOW + f"No matching build IDs found for game '{title}' (game ID {game_id})")
            return []

    # Create a mapping from version to build IDs
    version_to_build = {build['version']: build for build in build_ids}

    # Extract Cheats from tinfoil.io
    cheats_found = False  # Flag to check if any cheats are found

    cheats_header = soup.find('h4', string="Cheats")
    if cheats_header:
        table_div = cheats_header.find_next_sibling('div')
        if table_div:
            table = table_div.find('table', class_='table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            cheat_name = cols[0].get_text(strip=True)
                            # Remove brackets if present
                            if cheat_name.startswith('[') and cheat_name.endswith(']'):
                                cheat_name = cheat_name[1:-1].strip()
                            patch_version = cols[1].get_text(strip=True)
                            date_added = cols[2].get_text(strip=True)
                            source_ul = cols[3].find('ul', class_='cheat')
                            cheat_codes = []
                            if source_ul:
                                for li in source_ul.find_all('li'):
                                    code_line = li.get_text(strip=True)
                                    cheat_codes.append(code_line)
                            cheat = {
                                'name': cheat_name,
                                'date_added': date_added,
                                'codes': cheat_codes,
                                'source': 'tinfoil'
                            }
                            # Associate the cheat with the corresponding build ID based on version
                            build = version_to_build.get(patch_version)
                            if build:
                                build['cheats'].append(cheat)
                                if 'tinfoil' not in build['sources']:
                                    logging.info(Fore.LIGHTBLUE_EX + f"Cheats found on tinfoil.io for '{title}' on Build ID {build['build_id']}")
                                    build['sources'].append('tinfoil')
                                cheats_found = True
                            else:
                                logging.warning(Fore.YELLOW + f"No build ID found for version {patch_version} in game '{title}' (game ID {game_id})")
    else:
        logging.info(Fore.RED + f"No cheats found on tinfoil.io for '{title}' (game ID {game_id})")

    # Now, for each build ID, fetch cheats from cheatslips.com if API key is provided
    if CHEATSLIPS_API_TOKEN.value:
        for build in build_ids:
            cheats_from_cheatslips = get_cheats_from_cheatslips(game_id, build['build_id'])
            if cheats_from_cheatslips:
                if 'cheatslips' not in build['sources']:
                    logging.info(Fore.LIGHTBLUE_EX + f"Cheats found on cheatslips.com for '{title}' on Build ID {build['build_id']}")
                    build['sources'].append('cheatslips')
                build['cheats'].extend(cheats_from_cheatslips)
                cheats_found = True
            else:
                logging.info(Fore.RED + f"No cheats found on cheatslips.com for '{title}' with game ID {game_id} on build ID {build['build_id']}")
    else:
        logging.info(Fore.YELLOW + "No API key provided. Skipping fetching cheats from cheatslips.com.")

    if not cheats_found:
        logging.info(Fore.RED + f"No cheats found for game '{title}' (game ID {game_id}) on tinfoil.io or cheatslips.com")

    # Now, for each build_id, save the cheats and zip the directory if cheats are present
    for build in build_ids:
        if build.get('cheats'):
            # Save all cheats for this build_id
            build_id_dir = save_cheat_files(title, build['build_id'], build['cheats'])

            # Zip the build_id directory
            zip_filename = f"{title} - {build['build_id']}.zip"
            safe_zip_filename = sanitize_filename(zip_filename)
            zip_filepath = os.path.join(build_id_dir, safe_zip_filename)
            try:
                with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(build_id_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, build_id_dir)
                            zipf.write(file_path, arcname)
                logging.info(Fore.GREEN + f"Created zip file: {zip_filepath}")
            except Exception as e:
                logging.error(Fore.YELLOW + f"Error creating zip file '{zip_filepath}': {e}")

            # Update the build dictionary with the paths
            build['cheat_directory'] = build_id_dir
            build['zip_file'] = zip_filepath

    return build_ids

def save_cheat_files(title, build_id, cheats):
    # Sanitize the title and build_id for use in file paths
    from scripts.utils import sanitize_filename
    safe_title = sanitize_filename(title)
    safe_build_id = sanitize_filename(build_id)

    build_id_dir = os.path.join('cheat_code', safe_title, safe_build_id)

    for cheat in cheats:
        cheat_name = cheat['name']
        safe_cheat_name = sanitize_filename(cheat_name)

        # Construct the directory path
        dir_path = os.path.join(build_id_dir, safe_cheat_name, 'cheats')

        # Create directories if they don't exist
        os.makedirs(dir_path, exist_ok=True)

        # Construct the file path
        file_path = os.path.join(dir_path, f"{safe_build_id}.txt")

        # Prepare the content
        content = f"[{cheat_name}]\n"
        content += '\n'.join(cheat['codes'])

        # Write the content to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(Fore.GREEN + f"Saved cheat file for '{title}', cheat '{cheat_name}': {file_path}")
        except IOError as e:
            logging.error(Fore.YELLOW + f"Error writing cheat file '{file_path}': {e}")

    return build_id_dir  # Return the build ID directory path

def get_game_title_by_id(titleid):
    # Fetch game title using tinfoil API
    url = "https://tinfoil.media/Title/ApiJson/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data.get('data', []):
            if item.get('id') == titleid:
                name_field = item.get('name')
                if name_field:
                    soup = BeautifulSoup(name_field, 'html.parser')
                    title = soup.get_text()
                    return title
        return None
    except requests.exceptions.RequestException as e:
        logging.error(Fore.YELLOW + f"Error fetching game data: {e}")
        return None
