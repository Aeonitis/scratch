import os
import glob
import sys
import argparse
import subprocess
import itchylog as log
import sqlite3

cred_file_path = 'itch.cred'

def check_files():
    db_files = glob.glob("*.db")
    cred_files = glob.glob("*.cred")
    db_available = len(db_files) > 0
    cred_available = len(cred_files) > 0
    return db_available, cred_available

def ask_user(options):
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    choice = input("Select an option: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(options):
            return choice
        else:
            print("Invalid choice. Please try again.")
            return ask_user(options)
    except ValueError:
        print("Invalid choice. Please try again.")
        return ask_user(options)

def count_rows(db_file='itch.db', table_name='Game'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def is_database_initialized(db_file='itch.db', table_name='Game'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    table_exists = cursor.fetchone() is not None
    conn.close()
    if table_exists:
        log.info(f"Just pinging table '{table_name}'...")
        return count_rows(db_file, table_name) >= 0
    return False

def run_database_initialization(db_file='itch.db', table_name='Game', init=False):
    args = ['python', 'itchdb.py', '--db', db_file, '--table', table_name]
    if init:
        args.append('--init')
    subprocess.run(args, check=True)
    return is_database_initialized(db_file, table_name)

def run_insert_bundles():
    subprocess.run(['python', 'my-bundles.py'], check=True)

def validate_directory(directory):
    if not os.path.isdir(directory):
        log.error(f"The directory '{directory}' does not exist.")
        print(f"Error: The directory '{directory}' does not exist.")
        sys.exit(1)
    
def run_login_script(username, password):
    # Build the command with necessary arguments
    args = ['python', 'login.py', '--username', username, '--password', password]
    subprocess.run(args, check=True)
    
def cred_exists():
    if os.path.exists(cred_file_path):
        log.info(f"Credentials -> {cred_file_path}")
    else:
        log.warning("Credential file does not exist")


def main():
    parser = argparse.ArgumentParser(description='Process some usernames and passwords.')
    parser.add_argument('--username', required=True, help='Your username')
    parser.add_argument('--password', required=True, help='Your password')
    args = parser.parse_args()

    db_available, cred_available = check_files()

    if not db_available or not cred_available or not is_database_initialized():
        options = ["Initialize database and credentials", "Exit"]
        choice = ask_user(options)

        if choice == 1:
            if run_database_initialization(init=True):
                log.info("Database initialization complete.")
                run_login_script(args.username, args.password)
                cred_exists()
                run_insert_bundles()
                log.info("Database is populated.")
            else:
                log.error("Database initialization failed or no data was inserted.")
        elif choice == 2:
            print("Exiting.")
            sys.exit(0)
    else:
        log.info("Both database and credentials files are available.")
        # run_login_script(args.username, args.password, os.getcwd())  # Assuming the current directory needs authentication

        options = ["Check game info", "Reinitialize the CLI (warns it may take a few minutes)", "Exit"]
        choice = ask_user(options)

        if choice == 1:
            subprocess.run(['python', 'usage.py'])
        elif choice == 2:
            print("Warning: Reinitializing may take a few minutes.")
            if input("Are you sure you want to continue? (y/n): ").lower() == 'y':
                if run_database_initialization(init=True):
                    log.info("Database re-initialization complete.")
                    cred_exists()
                    run_insert_bundles()
                    log.info("Database is populated.")
                else:
                    log.error("Database re-initialization failed or no data was inserted.")
            else:
                print("Operation cancelled.")
        elif choice == 3:
            print("Exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
