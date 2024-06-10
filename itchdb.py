import sqlite3
import os
import argparse
import itchylog as log

def create_db(db_file='itch.db', table_name='Game'):
    log.info(f"Creating database and table '{table_name}' if they don't exist...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    Title TEXT,
                    Developer TEXT,
                    ImageURL TEXT,
                    HomePage TEXT,
                    Key TEXT,
                    DLPage TEXT,
                    FileCount TEXT,
                    Platforms TEXT,
                    Description TEXT,
                    Download TEXT,
                    Stars TEXT,
                    RatingCount TEXT,
                    Author TEXT,
                    Genre TEXT,
                    AverageSession TEXT,
                    Languages TEXT,
                    Updated TEXT,
                    Published TEXT,
                    Status TEXT,
                    Inputs TEXT,
                    Accessibility TEXT,
                    Tags TEXT,
                    ReleaseDate TEXT,
                    Other TEXT
                )''')
    conn.commit()
    conn.close()
    log.info("Database and table created.")

def insert_game(game_data, db_file='itch.db', table_name='Game'):
    log.info(f"Inserting game '{game_data['Title']}' into table '{table_name}'...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(f'''INSERT INTO {table_name} (
                            Title, Developer, ImageURL, HomePage, Key, DLPage, FileCount, Platforms, Description, Download,
                            Stars, RatingCount, Author, Genre, AverageSession, Languages, Updated, Published, Status,
                            Inputs, Accessibility, Tags, ReleaseDate, Other)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (game_data['Title'], game_data['Developer'], game_data['ImageURL'], game_data['HomePage'], game_data['Key'],
                           game_data['DLPage'], game_data['FileCount'], game_data['Platforms'], game_data['Description'], game_data['Download'],
                           game_data.get('Stars', ''), game_data.get('RatingCount', ''), game_data.get('Author', ''),
                           game_data.get('Genre', ''), game_data.get('AverageSession', ''), game_data.get('Languages', ''),
                           game_data.get('Updated', ''), game_data.get('Published', ''), game_data.get('Status', ''),
                           game_data.get('Inputs', ''), game_data.get('Accessibility', ''), game_data.get('Tags', ''),
                           game_data.get('ReleaseDate', ''), game_data.get('Other', '')))
        conn.commit()
        log.info("Game data inserted successfully.")
    except sqlite3.Error as e:
        log.error(f"Failed to insert game data: {e}")
    finally:
        conn.close()

def count_rows(db_file='itch.db', table_name='Game'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    row_count = cursor.fetchone()[0]
    conn.close()
    log.info(f"Total number of rows in the {table_name} table: {row_count}")
    return row_count

def get_game_by_title(title, db_file='itch.db', table_name='Game'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM {table_name} WHERE Title = ?', (title,))
    game = cursor.fetchone()
    conn.close()
    if game:
        log.info("Game found in database.")
        keys = ['id', 'Title', 'Developer', 'ImageURL', 'HomePage', 'Key', 'DLPage', 'FileCount', 'Platforms', 'Description', 'Download',
                'Stars', 'RatingCount', 'Author', 'Genre', 'AverageSession', 'Languages', 'Updated', 'Published', 'Status',
                'Inputs', 'Accessibility', 'Tags', 'ReleaseDate', 'Other']
        return dict(zip(keys, game))
    else:
        log.info("Game not found in database.")
        return None

def db_file_exists(db_file='itch.db'):
    exists = os.path.isfile(db_file)
    log.info(f"Database file '{db_file}' exists: {exists}")
    return exists

def table_exists(db_file='itch.db', table_name='Game'):
    log.info(f"Checking if table '{table_name}' exists in database '{db_file}'...")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    table_exists = c.fetchone() is not None
    conn.close()
    log.info(f"Table '{table_name}' exists: {table_exists}")
    return table_exists

def clean_database(db_file='itch.db', table_name='Game'):
    if db_file_exists(db_file):
        row_count = count_rows(db_file, table_name)
        print(f"Database '{db_file}' exists with {row_count} rows in table '{table_name}'. Deleting database.")
        os.remove(db_file)
        log.info(f"Database '{db_file}' deleted successfully.")
    else:
        print(f"Database '{db_file}' does not exist.")
        log.warning(f"No database file '{db_file}' to delete.")

def main():
    parser = argparse.ArgumentParser(description="Manage the itch.io game database.")
    parser.add_argument('--init', action='store_true', help="Initialize the database (delete if exists and start from scratch)")
    parser.add_argument('--db', type=str, default='itch.db', help="Specify the database file")
    parser.add_argument('--table', type=str, default='Game', help="Specify the table name")
    parser.add_argument('--clean', action='store_true', help="Check database existence, print row count and delete the database.")
    args = parser.parse_args()

    db_file = args.db
    table_name = args.table

    if args.init:
        clean_database(db_file, table_name)
        create_db(db_file, table_name)
    else:
        if not db_file_exists(db_file) or not table_exists(db_file, table_name):
            clean_database(db_file, table_name)
            create_db(db_file, table_name)

if __name__ == "__main__":
    main()
