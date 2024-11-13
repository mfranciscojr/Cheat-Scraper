# main.py

import argparse
import getpass
import logging
import sys
from scripts.fetch_game_data import fetch_game_data
from scripts.utils import setup_logging
from scripts.constants import CHEATSLIPS_API_TOKEN

def main():
    parser = argparse.ArgumentParser(description='Fetch cheats for Switch games and generate HTML files.')
    parser.add_argument('-g', '--gameid', help='Specify a comma-separated list of game IDs to process.')
    parser.add_argument('-t', '--title', help='Specify a comma-separated list of game titles or partial titles to search for.')
    parser.add_argument('-b', '--buildid', nargs='?', const=True, help='Specify a semicolon-separated list of titleid,buildid pairs (e.g., "titleid,buildid;titleid,buildid"). Best for cheatslips.com due to API count limitation.')
    parser.add_argument('-a', '--all', action='store_true', help='Process all games.')
    parser.add_argument('-k', '--apikey', help='Provide the cheatslips.com API key.')
    args = parser.parse_args()

    if not args.gameid and not args.title and not args.all and not args.buildid:
        parser.print_help()
        sys.exit(1)

    if sum(bool(x) for x in [args.gameid, args.title, args.all, args.buildid]) > 1:
        print("Please specify only one of -g/--gameid, -t/--title, -b/--buildid, or -a/--all.")
        sys.exit(1)

    setup_logging()

    if args.apikey:
        CHEATSLIPS_API_TOKEN.value = args.apikey.strip()
    else:
        # Prompt the user for the API key, hiding input
        CHEATSLIPS_API_TOKEN.value = getpass.getpass(prompt="Please enter your cheatslips.com API key (leave blank to skip): ").strip()
        if not CHEATSLIPS_API_TOKEN.value:
            CHEATSLIPS_API_TOKEN.value = None
            logging.info("No API key provided. The script will only scrape from tinfoil.io and not from cheatslips.com.")
            logging.info("You can get an API key by registering at https://www.cheatslips.com/ and generating an API key at https://www.cheatslips.com/profile/api")

    specific_game_ids = None
    title_queries = None
    buildid_list = None

    if args.buildid is not None:
        if args.buildid is True:
            # Prompt the user for TitleID and BuildID
            titleid = input("Please enter the TitleID: ").strip()
            # Fetch game title
            from scripts.fetch_game_data import get_game_title_by_id
            game_title = get_game_title_by_id(titleid)
            if game_title:
                print(f"You are getting cheats for: {game_title}")
            else:
                print(f"No game found with TitleID: {titleid}")
                sys.exit(1)
            buildid = input("Please enter the BuildID: ").strip()
            buildid_list = [f"{titleid},{buildid}"]
        else:
            # Split the buildid pairs by semicolons
            buildid_list = [pair.strip() for pair in args.buildid.split(';') if pair.strip()]
    elif args.gameid:
        # Split the game IDs by commas
        specific_game_ids = [gid.strip() for gid in args.gameid.split(',')]
    elif args.title:
        # Split the title queries by commas
        title_queries = [t.strip() for t in args.title.split(',')]

    fetch_game_data(specific_game_ids=specific_game_ids, process_all=args.all, title_queries=title_queries, buildid_list=buildid_list)

if __name__ == "__main__":
    main()
