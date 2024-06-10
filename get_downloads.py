import os
import requests
from bs4 import BeautifulSoup
from cred_store import fetch_credentials
import argparse
from urllib.parse import urlparse
import itchylog as log

# Fetch headers for the request
headers = fetch_credentials()

def fetch_html(url, headers):
    try:
        response = requests.get(url, headers=headers)
        log.info(f"Fetching HTML content from {url}")
        response.raise_for_status()
        response.encoding = 'utf-8'  # Explicitly setting encoding to 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching HTML content: {e}")
        return None

def extract_download_info(html_content):
    if html_content is None:
        return []

    download_data = []
    for upload in html_content.find_all('div', class_='upload'):
        link_tag = upload.find('a', class_='button download_btn')
        if link_tag and 'data-upload_id' in link_tag.attrs:
            upload_id = link_tag['data-upload_id']
            upload_name_tag = upload.find('strong', class_='name')
            file_size_tag = upload.find('span', class_='file_size').find('span')

            download_data.append({
                'upload_id': upload_id,
                'title': upload_name_tag['title'] if upload_name_tag else 'Unknown',
                'file_size': file_size_tag.text if file_size_tag else 'Unknown',
                'source': 'game_download',
                'key': None  # Key will be dynamically set later
            })
    return download_data

def construct_download_url(base_url, upload_id, source, key):
    return f"{base_url}/file/{upload_id}?source={source}&key={key}"

def get_file_name(html_content, upload_id):
    # Find the file name based on the upload_id
    upload_div = html_content.find('a', {'data-upload_id': upload_id})
    if upload_div:
        name_tag = upload_div.find_next('strong', class_='name')
        if name_tag and 'title' in name_tag.attrs:
            return name_tag['title']
    return f"file_{upload_id}.zip"

def follow_redirect_and_download(url, file_name, dest_folder, headers):
    local_filename = os.path.join(dest_folder, file_name)
    try:
        print(f"Attempting Download of '{file_name}'")
        log.info(f"Initiating download request to {url}")
        with requests.post(url, headers=headers) as response:
            log.debug(f"Initial response status code: {response.status_code}")
            log.debug(f"Initial response headers: {response.headers}")
            response.raise_for_status()
            json_data = response.json()
            if 'url' in json_data:
                download_url = json_data['url']
                log.info(f"Following redirect to {download_url}")
                with requests.get(download_url, headers=headers, stream=True) as download_response:
                    log.debug(f"Download response status code: {download_response.status_code}")
                    log.debug(f"Download response headers: {download_response.headers}")
                    download_response.raise_for_status()
                    with open(local_filename, 'wb') as file:
                        for chunk in download_response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    print(f"Downloaded: {local_filename}")
            else:
                log.error(f"No download URL found in response JSON: {json_data}")
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to download {url}: {e}")



def main(url, dest_folder, key, download_all, specific_file):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{parsed_url.path.split('/')[1]}"
    
    # Extract key from URL if not provided
    if not key:
        key = url.split('/')[-1]
    
    # Log the key being used
    log.info(f"Using key: {key}")

    # Check if URL contains '/download/'
    if '/download/' not in url:
        log.warning("\n" + "="*60)
        log.warning("WARNING: The URL does not contain '/download/'. This may not work correctly.")
        log.warning("="*60 + "\n")

    # Check if URL ends with the provided key
    if key and not url.endswith(key):
        log.warning("\n" + "="*60)
        log.warning(f"WARNING: The URL does not end with the key '{key}'. This may not work correctly.")
        log.warning("="*60 + "\n")
    
    html_content = fetch_html(url, headers)
    if html_content:
        download_data = extract_download_info(html_content)
        if download_data:
            for data in download_data:
                data['key'] = key
            print("Download links found:")
            for index, data in enumerate(download_data, start=1):
                print(f"{index}. Title: {data['title']}, File Size: {data['file_size']}, Link: {construct_download_url(base_url, data['upload_id'], data['source'], data['key'])}")

            if specific_file:
                file_found = False
                for data in download_data:
                    if data['title'] == specific_file:
                        download_url = construct_download_url(base_url, data['upload_id'], data['source'], data['key'])
                        file_name = get_file_name(html_content, data['upload_id'])
                        follow_redirect_and_download(download_url, file_name, dest_folder, headers)
                        file_found = True
                        break
                if not file_found:
                    log.error(f"File '{specific_file}' not found in the available downloads.")
            elif download_all:
                for data in download_data:
                    download_url = construct_download_url(base_url, data['upload_id'], data['source'], data['key'])
                    file_name = get_file_name(html_content, data['upload_id'])
                    follow_redirect_and_download(download_url, file_name, dest_folder, headers)
            else:
                choice = input("Enter the number of the file you want to download, or type 'all' to download all files: ").strip()
                if choice.lower() in ['a', 'all']:
                    for data in download_data:
                        download_url = construct_download_url(base_url, data['upload_id'], data['source'], data['key'])
                        file_name = get_file_name(html_content, data['upload_id'])
                        follow_redirect_and_download(download_url, file_name, dest_folder, headers)
                else:
                    try:
                        choice_index = int(choice) - 1
                        if 0 <= choice_index < len(download_data):
                            data = download_data[choice_index]
                            download_url = construct_download_url(base_url, data['upload_id'], data['source'], data['key'])
                            file_name = get_file_name(html_content, data['upload_id'])
                            follow_redirect_and_download(download_url, file_name, dest_folder, headers)
                        else:
                            log.error("Invalid choice.")
                    except ValueError:
                        log.error("Invalid input. Please enter a valid number or 'all'.")
        else:
            log.error("No download links found.")
    else:
        log.error("Failed to fetch HTML content.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from Itch.io game download page.")
    parser.add_argument('--url', required=True, help='The URL of the Itch.io download page.')
    parser.add_argument('--dest', required=True, help='The destination folder for downloads.')
    parser.add_argument('--key', help='The key for the download. If not provided, it will be extracted from the URL.')
    parser.add_argument('--all', action='store_true', help='Download all available files.')
    parser.add_argument('--file', help='Download a specific file by name.')

    args = parser.parse_args()

    main(args.url, args.dest, args.key, args.all, args.file)
