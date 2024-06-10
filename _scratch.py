import argparse
import webbrowser
import subprocess
from _query import get_game_by_title
from get_downloads import main as download_main

def query_and_download():
    parser = argparse.ArgumentParser(description="Query and download games from itch.io.")
    parser.add_argument('--title', help="The title of the game to query.")
    parser.add_argument('--dir', required=True, help="The directory where files will be downloaded.")
    args = parser.parse_args()

    if args.title:
        game = get_game_by_title(args.title)
        if not game:
            print("Game not found.")
            return

        print("Game found:")
        for key, value in game.items():
            print(f"{key}: {value}")

        if game.get('DLPage', 'UNCLAIMED') == 'UNCLAIMED':
            print("This game is unclaimed and does not have a download page.")
            choice = input("Do you want to: \n1. Go to the home page to claim it\n2. Go to itch.io to buy more games\n3. Nah, scratch that I'll pass, thanks!\nEnter your choice (1, 2, 3): ")
            if choice == '1':
                if game.get('HomePage'):
                    webbrowser.open(game['HomePage'])
                    print(f"Opening {game['HomePage']}")
                else:
                    print("No home page available for this game.")
            elif choice == '2':
                webbrowser.open("https://itch.io")
                print("Opening https://itch.io")
            elif choice == '3':
                print("Exiting the script.")
            else:
                print("Invalid option selected. Exiting.")
            return

        # Ask user if they want to download all files or select a specific one
        user_choice = input("Do you want to download all files or select a specific one? (a(all) or s(select): ").strip().lower()
        if user_choice in ['a', 'all']:
            download_main(game['DLPage'], args.dir, game.get('Key'), True, None)
        elif user_choice in ['s', 'select']:
            download_main(game['DLPage'], args.dir, game.get('Key'), False, None)
        else:
            print("Invalid option provided.")
    else:
        subprocess.run(['python', 'usage.py'])

if __name__ == "__main__":
    query_and_download()
    # subprocess.run(['python', 'usage.py'])
