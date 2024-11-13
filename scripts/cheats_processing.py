# scripts/cheats_processing.py

import requests
import logging
from scripts.constants import CHEATSLIPS_API_TOKEN

def get_cheats_from_cheatslips(game_id, build_id):
    if not CHEATSLIPS_API_TOKEN.value:
        logging.info("No API key provided. Skipping fetching cheats from cheatslips.com.")
        return []

    url = f"https://www.cheatslips.com/api/v1/cheats/{game_id}/{build_id}"
    headers = {
        "accept": "application/json",
        "X-API-TOKEN": CHEATSLIPS_API_TOKEN.value
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            # No cheats available for this build ID
            return []
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching cheats from cheatslips.com for game ID {game_id}, build ID {build_id}: {e}")
        return []

    data = response.json()

    cheats = []
    # The 'cheats' key contains a list of cheats
    for cheat_entry in data.get('cheats', []):
        content = cheat_entry.get('content', '')
        # Parse the content to extract individual cheats
        parsed_cheats = parse_cheat_content(content)
        # Add source to each cheat
        for cheat in parsed_cheats:
            cheat['source'] = 'cheatslips'
        cheats.extend(parsed_cheats)

    return cheats

def parse_cheat_content(content):
    cheats = []
    lines = content.split('\n')
    current_cheat = None

    for line in lines:
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            # This is a cheat name
            cheat_name = line[1:-1].strip()
            if cheat_name.startswith('--'):
                # Ignore section headers
                continue
            if current_cheat:
                # Save the previous cheat
                cheats.append(current_cheat)
            current_cheat = {
                'name': cheat_name,
                'codes': []
            }
        elif line and current_cheat:
            # This is a code line
            current_cheat['codes'].append(line)
    if current_cheat:
        # Add the last cheat
        cheats.append(current_cheat)

    return cheats
