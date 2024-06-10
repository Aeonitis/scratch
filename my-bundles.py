import requests
from bs4 import BeautifulSoup
from cred_store import fetch_credentials
import itchdb  # Import the itchdb module
from game_page_info import fetch_additional_game_info 
import itchylog as log 

headers = fetch_credentials()

def fetch_html(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'  # Explicitly setting encoding to 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    else:
        log.error(f"Failed to retrieve the page {url}. Status code: {response.status_code}")
        return None

def extract_bundles(soup):
    bundles = []
    bundle_elements = soup.select('.bundle_keys ul li a')
    for element in bundle_elements:
        name = element.text.strip()
        url = element['href']
        time_info = element.find_next_sibling('abbr').get('title', 'No time info available')
        bundles.append({
            'name': name,
            'url': f"https://itch.io{url}",
            'time': time_info
        })
    return bundles

def get_total_pages(soup):
    pager_label = soup.select_one('.pager_label')
    if pager_label:
        total_pages = pager_label.text.split()[-1]  # Extracting the total number of pages from the string 'Page 1 of 13'
        return int(total_pages)
    return 0

def extract_game_info(soup):
    games = {}
    game_rows = soup.select('.game_row')
    print(f"{len(game_rows)} games in current batch...")
    
    for game in game_rows:
        title = game.select_one('.game_title a').text.strip()
        dev_name = game.select_one('.game_author a').text.strip()
        dl_page = game.select_one('.game_title a')['href']  # Extracting game link
        img_url = game.select_one('.game_thumb').get('data-background_image', 'No image available')

        file_count = game.select_one('.file_count').text.split()[0] if game.select_one('.file_count') else 'No files'
        description = game.select_one('.game_short_text').text.strip() if game.select_one('.game_short_text') else 'No description'

        platforms = []
        # Check for operating system availability indicators
        for span in game.select('.meta_row span'):
            if 'title' in span.attrs:
                platform = span['title'].replace('Available for ', '')
                platforms.append(platform)

        # Robust check for "Play in browser" option
        button_row = game.select_one('.button_row')
        if button_row:
            play_in_browser = any(link for link in button_row.select('a') if 'play' in link.text.lower() and 'browser' in link.text.lower())
            if play_in_browser:
                platforms.append('Browser')

        # Extracting download URL
        download_btn = game.select_one('a.game_download_btn')
        # Default values
        game_key = download_url = 'UNCLAIMED'
        home_page = None
        
        if download_btn:
            download_url = download_btn['href']
            if 'download' in download_url:
                home_page, game_key = download_url.split('/download/')
        else:
            form_btn = game.select_one('form button[name="action"][value="claim"]')
            download_url = 'UNCLAIMED' if form_btn else 'No download URL'

        # Fetch additional game info from game page
        additional_game_info = fetch_additional_game_info(home_page if home_page else dl_page)

        # Ensure dl_page is 'UNCLAIMED' if game_key is 'UNCLAIMED', then update homepage
        if game_key == 'UNCLAIMED':
            home_page = dl_page
            dl_page = 'UNCLAIMED'      

        print(f"\nMapping: {title}")
        # print(f"\n--------  MAPPINGS --------")
        # print(f"\ndownload_url: {download_url}")
        # print(f"\ndl_page: {dl_page}")
        # print(f"\ngame_key: {game_key}")
        # print(f"\nhome_page: {home_page}")
        # print(f"\n------------------------------")
        games[title] = {
            'Title': title,
            'Developer': dev_name,
            'ImageURL': img_url,
            'HomePage': home_page if home_page else dl_page,
            'Key': game_key,
            'DLPage': dl_page,
            'FileCount': file_count,
            'Platforms': ', '.join(platforms),
            'Description': description,
            'Download': download_url,
            'Stars': additional_game_info.get('Stars', ''),
            'RatingCount': additional_game_info.get('RatingCount', ''),
            'Author': additional_game_info.get('Author', ''),
            'Genre': additional_game_info.get('Genre', ''),
            'AverageSession': additional_game_info.get('AverageSession', ''),
            'Languages': additional_game_info.get('Languages', ''),
            'Updated': additional_game_info.get('Updated', ''),
            'Published': additional_game_info.get('Published', ''),
            'Status': additional_game_info.get('Status', ''),
            'Inputs': additional_game_info.get('Inputs', ''),
            'Accessibility': additional_game_info.get('Accessibility', ''),
            'Tags': additional_game_info.get('Tags', ''),
            'ReleaseDate': additional_game_info.get('ReleaseDate', ''),  # Added ReleaseDate field
            'Other': ', '.join(additional_game_info.get('Other', [])) if isinstance(additional_game_info.get('Other', []), list) else additional_game_info.get('Other', '')
        }

    return games

def find_next_page(soup):
    next_page_link = soup.select_one('.next_page')
    return next_page_link['href'] if next_page_link else None

def main():
    log.info("Starting main process...")
    # Ensure the database and table are created if they don't exist
    if not itchdb.db_file_exists():
        log.info("Scratching up a database...")
        itchdb.create_db()
    elif not itchdb.table_exists():
        log.info("Game table not found, creating db...")
        itchdb.create_db()

    # Counting the number of rows in the Game table
    row_count = itchdb.count_rows()
    log.info(f"Total number of rows in the Game table: {row_count}")
    
    # Exit the main function if the row count is more than 0
    if row_count > 0:
        log.info("Trying a test query for a title...")
        game = itchdb.get_game_by_title('A Short Hike')
        log.info(f"Game retrieved: {game}")
        log.info(f"DB Already exists and has {row_count} rows (>0 rows).")
        return
    else:
        log.info("Creating the database and table...")
        itchdb.create_db()
    
    bundles_page_url = 'https://itch.io/my-purchases/bundles'
    bundles_soup = fetch_html(bundles_page_url, headers)

    if bundles_soup:
        bundles = extract_bundles(bundles_soup)
        log.info(f"Found {len(bundles)} bundles:")
        for bundle in bundles:
            log.info(f"Name: {bundle['name']}, URL: {bundle['url']}, Time: {bundle['time']}")

        total_games = 0

        # Fetch games from each bundle
        for bundle in bundles:
            log.info(f"Fetching games from bundle: {bundle['name']}")
            current_page_url = bundle['url']
            bundle_games_count = 0

            while current_page_url:
                log.info(f"Fetching data from: {current_page_url}")
                soup = fetch_html(current_page_url, headers)
                if soup:
                    games = extract_game_info(soup)
                    bundle_games_count += len(games)
                    total_games += len(games)
                    for title, game in games.items():
                        log.info(f"Inserting[{total_games}]: '{title}' intoDATAABASSe!!")
                        itchdb.insert_game(game)  # Insert game data into the database
                    next_page_path = find_next_page(soup)
                    current_page_url = f"{bundle['url']}{next_page_path}" if next_page_path else None
                else:
                    log.error("Failed to fetch the page.")
                    break


            print("---------------------------------------------------------------")
            print(f"Total games in bundle '{bundle['name']}': {bundle_games_count}")
            print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        log.info(f"Total games processed from all bundles: {total_games}")
        log.info(f"Total games in the database: {itchdb.count_rows()}")
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

    else:
        log.error("Failed to fetch the bundles page.")

if __name__ == "__main__":
    main()
