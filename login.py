import requests
from bs4 import BeautifulSoup
import base64
import json
from datetime import datetime
import pytz
import sys
import argparse
from cred_store import store_credentials, fetch_credentials
import itchylog as log

def get_csrf_token(session, url):
    """Fetch CSRF token from the login page."""
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('meta', {'name': 'csrf_token'})['value']

def decode_csrf_token(csrf_token):
    """Decode CSRF token and return its components."""
    token_parts = csrf_token.split('.')
    encoded_data = token_parts[0]
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    parsed_data = json.loads(decoded_data)
    return parsed_data[0], parsed_data[1], parsed_data[2], token_parts[1]

def prepare_login_headers():
    """Prepare headers required for login."""
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://itch.io",
        "Pragma": "no-cache",
        "Referer": "https://itch.io/login",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android"
    }

def get_timezone_offset():
    """Calculate local timezone offset in minutes from UTC."""
    local_zone = datetime.now().astimezone().tzinfo
    return int(datetime.now(local_zone).utcoffset().total_seconds() / 60)

def perform_login(session, url, username, password, csrf_token, offset_minutes):
    """Perform the login operation and handle the response."""
    headers = prepare_login_headers()
    login_data = {
        "csrf_token": csrf_token,
        "tz": str(offset_minutes),
        "username": username,
        "password": password
    }
    response = session.post(url, data=login_data, headers=headers)
    response.raise_for_status()
    return response

def main(username, password):
    login_url = "https://itch.io/login"
    session = requests.Session()

    try:
        csrf_token = get_csrf_token(session, login_url)
        log.debug(f"CSRF Token: {csrf_token}")

        nonce_id, timestamp, hash_code, padding = decode_csrf_token(csrf_token)
        timestamp_readable = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        log.debug(f"Segments:\nNonce/ID: {nonce_id}\nTimestamp: {timestamp} ({timestamp_readable})\nHashCode: {hash_code}\nPadding: {padding}")

        offset_minutes = get_timezone_offset()
        log.debug(f"Timezone Offset: {offset_minutes}")

        response = perform_login(session, login_url, username, password, csrf_token, offset_minutes)

        if "dashboard" in response.text:
            log.info("Login successful!")
            handle_successful_login(session, response)
        else:
            log.error(f"Login failed. Status code: {response.status_code}")
            log.error(response.text)
    except requests.exceptions.RequestException as e:
        log.critical(f"An error occurred: {e}")
        sys.exit(1)

def handle_successful_login(session, response):
    """Handle tasks following a successful login, such as storing and fetching credentials."""
    cookies = session.cookies.get_dict()
    log.debug(f"Cookies from session: {cookies}")

    expires_str = [s.split('=')[1] for s in response.headers.get('Set-Cookie', '').split(';') if 'Expires' in s][0]
    expires_gmt = datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S GMT")
    local_zone = datetime.now().astimezone().tzinfo
    expires_local = pytz.timezone('GMT').localize(expires_gmt).astimezone(local_zone)

    log.info(f"Cookie Tokens Expire At (Local Time): {expires_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    store_credentials(cookies)

    fetched_headers = fetch_credentials()
    log.debug(f"Fetched Credentials: {fetched_headers}")
    validate_stored_credentials(fetched_headers)

def validate_stored_credentials(headers):
    """Validate the integrity of stored credentials."""
    if headers.get('Cookie') and 'itchio_token=' in headers['Cookie'] and 'itchio=' in headers['Cookie']:
        log.info("Credentials stored and fetched correctly.")
    else:
        log.error("Credentials were not stored/fetched correctly.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Login to Itch.io and store credentials securely.")
    parser.add_argument('--username', required=True, help='Your Itch.io username.')
    parser.add_argument('--password', required=True, help='Your Itch.io password.')

    args = parser.parse_args()
    main(args.username, args.password)
