import sqlite3
import argparse
import itchylog as log

def get_game_by_title(title, db_file='itch.db'):
    """
    Retrieves game information by title from the database, ignoring case.
    """
    
    log.info(f"Querying the database for the game titled '{title}'.")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        # Use LOWER() to make the search case-insensitive
        cursor.execute("SELECT * FROM Game WHERE LOWER(Title) = LOWER(?)", (title,))
        game = cursor.fetchone()
        if game:
            keys = ['id', 'Title', 'Developer', 'ImageURL', 'HomePage', 'Key', 'DLPage', 'FileCount', 'Platforms', 'Description', 'Download',
                    'Stars', 'RatingCount', 'Author', 'Genre', 'AverageSession', 'Languages', 'Updated', 'Published', 'Status',
                    'Inputs', 'Accessibility', 'Tags', 'ReleaseDate', 'Other']
            result = dict(zip(keys, game))
            log.info("Game successfully retrieved from the database.")
            return result
        else:
            log.warning("Game not found in the database.")
            return None
    except sqlite3.Error as e:
        log.error(f"Database error: {e}")
        return None
    finally:
        conn.close()


def get_games_by_genre(genre, db_file='itch.db'):
    """
    Searches for all games in the database that include a specified genre.
    """
    log.info(f"Searching for games with genre containing '{genre}'.")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT * FROM Game WHERE Genre LIKE ?''', (f"%{genre}%",))
        games = cursor.fetchall()
        if games:
            log.info(f"Found {len(games)} games with genre containing '{genre}'.")
            return games
        else:
            log.warning("No games found with the specified genre.")
            return []
    except sqlite3.Error as e:
        log.error(f"Database error: {e}")
        return []
    finally:
        conn.close()


def execute_custom_sql(sql_query, db_file='itch.db'):
    log.info(f"Executing custom SQL query: {sql_query}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if results:
            log.info("Custom SQL query executed successfully. Results found.")
            return results
        else:
            log.warning("No results found for the custom SQL query.")
            log.warning(f"Executed SQL: {sql_query}")  # For debugging
            return []
    except sqlite3.Error as e:
        log.error(f"Database error during custom SQL execution: {e}")
        return []
    finally:
        conn.close()

        

def count_rows(db_file='itch.db', table_name='Game'):
    """
    Counts the number of rows in the specified table.
    """
    log.info(f"Counting rows in the table '{table_name}'.")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    log.info(f"Total rows in '{table_name}': {count}")
    return count

def main():
    parser = argparse.ArgumentParser(description="Query the itch.io game database using various parameters. See docstring for examples.")
    parser.add_argument('--title', help="Query game by title.")
    parser.add_argument('--genre', help="Query games by genre containing the specified substring.")
    parser.add_argument('--sql', help="Execute a custom SQL query.")
    parser.add_argument('--rows', action='store_true', help="Count the number of rows in the Game table.")
    args = parser.parse_args()

    if args.title:
        game = get_game_by_title(args.title)
        if game:
            print("Game found:")
            for key, value in game.items():
                print(f"{key}: {value}")
        else:
            print("Game not found.")
    elif args.genre:
        games = get_games_by_genre(args.genre)
        if games:
            print(f"Found {len(games)} games with genre containing '{args.genre}':")
            for game in games:
                print(game)
        else:
            print("No games found with the specified genre.")
    elif args.sql:
        results = execute_custom_sql(args.sql)
        if results:
            print("Results from custom SQL query:")
            for result in results:
                print(result)
        else:
            print("No results found for the custom SQL query.")
    elif args.rows:
        row_count = count_rows()
        print(f"Total number of rows in the Game table: {row_count}")
    else:
        print("No valid arguments provided. Use --help for options.")

if __name__ == "__main__":
    main()