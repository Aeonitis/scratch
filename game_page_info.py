import requests
from bs4 import BeautifulSoup
import re
import itchylog as log

def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'utf-8'  # Explicitly setting encoding to 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")
        return None

def extract_game_page_info(soup):
    info_panel = soup.select_one('.info_panel_wrapper')
    if not info_panel:
        print("No info panel found.")
        return None

    game_info = {}
    other_info = []
    mentions = []
    rows = info_panel.select('table tbody tr')

    for row in rows:
        cells = row.find_all('td')
        key = cells[0].get_text(strip=True)
        value = cells[1].get_text(strip=True)

        if key == 'Rating':
            rating_match = re.search(r'Rated ([\d\.]+) out of 5 stars', value)
            rating_count_element = cells[1].find('span', {'itemprop': 'ratingCount'})
            rating_count = rating_count_element['content'] if rating_count_element else ''
            game_info['Stars'] = rating_match.group(1) if rating_match else ''
            game_info['RatingCount'] = rating_count
        elif key == 'Genre':
            game_info['Genre'] = value
        elif key == 'Average session':
            game_info['AverageSession'] = value
        elif key == 'Languages':
            game_info['Languages'] = value
        elif key == 'Updated':
            game_info['Updated'] = value
        elif key == 'Published':
            game_info['Published'] = value
        elif key == 'Status':
            game_info['Status'] = value
        elif key == 'Inputs':
            game_info['Inputs'] = value
        elif key == 'Accessibility':
            game_info['Accessibility'] = value
        elif key == 'Author':
            game_info['Author'] = value
        elif key == 'Tags':
            game_info['Tags'] = value
        elif key == 'Release date':
            game_info['ReleaseDate'] = value
        elif key == 'Links':
            links = [a['href'] for a in cells[1].find_all('a', href=True)]
            game_info['Links'] = links
            log.debug(f"Links: {game_info['Links']}")
        elif key == 'Mentions':
            mentions = [a['href'] for a in cells[1].find_all('a', href=True)]
        else:
            other_info.append(f"{key}={value}")

    if mentions:
        other_info.append(f"Mentions={', '.join(mentions)}")
    game_info['Other'] = "; ".join(other_info)
    log.debug(f"Concatenated 'Other' field: {game_info['Other']}")
    return game_info

def fetch_additional_game_info(url):
    soup = fetch_html(url)
    if not soup:
        return {}
    game_page_info = extract_game_page_info(soup)
    if game_page_info:
        return game_page_info
    else:
        print("No game information found.")
        return {}
