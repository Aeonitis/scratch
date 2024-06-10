import os
import json
from cryptography.fernet import Fernet
import argparse
import itchylog as log

key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
cipher_suite = Fernet(key)
cred_file_path = 'itch.cred'

def store_credentials(cookies):
    log.info("Cookies received for storage")
    log.debug(f"Cookies: {cookies}")

    data_to_store = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Cookie": f"itchio_token={cookies.get('itchio_token', '')}; itchio={cookies.get('itchio', '')}",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
    }

    log.info("Data to be stored")
    log.debug(f"Data: {data_to_store}")

    data_json = json.dumps(data_to_store)
    encrypted_data = cipher_suite.encrypt(data_json.encode())

    with open(cred_file_path, 'wb') as cred_file:
        cred_file.write(encrypted_data)

    log.info("Tokens have been successfully stored in itch.cred")

def fetch_credentials():
    if not os.path.exists(cred_file_path):
        log.error("Credential file not found")
        return None

    with open(cred_file_path, 'rb') as cred_file:
        encrypted_data = cred_file.read()

    decrypted_data = cipher_suite.decrypt(encrypted_data)
    data_to_store = json.loads(decrypted_data.decode())

    log.info("Decrypted data fetched")
    log.debug(f"Decrypted data: {data_to_store}")

    return data_to_store

def clear_credentials():
    if os.path.exists(cred_file_path):
        os.remove(cred_file_path)
        print("Your credentials have been successfully been deleted.")
        log.info("Credentials have been cleared")
    else:
        log.warning("Credential file does not exist")

def main():
    parser = argparse.ArgumentParser(description="Manage credentials for Itch.io")
    parser.add_argument('--store', help='Store credentials provided as JSON string')
    parser.add_argument('--fetch', action='store_true', help='Fetch and display stored credentials')
    parser.add_argument('--clear', action='store_true', help='Clear stored credentials')

    args = parser.parse_args()

    if args.store:
        try:
            response_headers = json.loads(args.store)
            store_credentials(response_headers)
        except json.JSONDecodeError:
            log.error("Invalid JSON string provided for --store")
    elif args.fetch:
        credentials = fetch_credentials()
        if credentials:
            print(json.dumps(credentials, indent=2))
    elif args.clear:
        clear_credentials()
    else:
        log.info("No valid argument provided. Use --store, --fetch, or --clear")

if __name__ == "__main__":
    main()
