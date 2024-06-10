def print_usage():
    print("=======================================")
    print("           The SCRATCH |\/\'anual      ")
    print("=======================================")
    
    print("---------------------------------------")
    print("Setup Utility for your Game Database")
    print("---------------------------------------")
    print("\nUsage for _setup.py:")
    print("  py _setup.py --username USERNAME --password 'PASSWORD'")
    
    
    print("---------------------------------------")
    print("Query Utility for Itch.io Game Database")
    print("---------------------------------------")
    print("\nUsage for _query.py:")
    print("  python _query.py [OPTIONS]")
    print("  Query the itch.io game database using various parameters.")
    
    print("\nOptional Arguments:")
    print("  -h, --help       Show this help message and exit")
    print("  --title TITLE    Query game by title")
    print("  --genre GENRE    Query games by genre containing the specified substring")
    print("  --sql SQL        Execute a custom SQL query")
    print("  --rows           Count the number of rows in the Game table")
    
    print("\nSample SQL Usage Examples:")
    print("  python _query.py --sql \"SELECT Title, Developer FROM Game WHERE Stars > '4.5'\"")
    print("  python _query.py --sql \"SELECT Title, RatingCount FROM Game WHERE RatingCount > '100'\"")
    print("  python _query.py --sql \"SELECT * FROM Game WHERE Tags LIKE '%multiplayer%'\"")
    print("\n> Note: 'Stars' and 'RatingCount' are stored as strings, so comparisons should be done cautiously.")
    
    print("\nDO NOT WORK, THIS IS ON THE TODO LIST, WORK IN PROGRESS!!! =================")
    print("  python _query.py --sql \"SELECT * FROM Game WHERE date(Published) > date('2018-01-01')\"")
    print("  python _query.py --sql \"SELECT * FROM Game WHERE Published > '2020'\"")
    print("  python _query.py --sql \"SELECT * FROM Game WHERE Genre LIKE '%Sci-Fi%'\"")
    print("DO NOT WORK=======================================")
    
    print("\nTable Columns for Manual SQL Usage:")
    print("  id, Title, Developer, ImageURL, HomePage, Key, DLPage, FileCount, Platforms, Description,")
    print("  Download, Stars, RatingCount, Author, Genre, AverageSession, Languages, Updated, Published,")
    print("  Status, Inputs, Accessibility, Tags, ReleaseDate, Other")
    
    print("\nTo output to a text file:")
    print("  python _query.py --sql \"SELECT * FROM Game WHERE Genre LIKE '%RPG%'\" > RPG.txt")
    print("\n")
    
    print("---------------------------------------")
    print("       Scratch Store File Manager      ")
    print("---------------------------------------")
    print("\nUsage for _scratch.py:")
    print("  python _scratch.py --dir '/path/to/directory'")
    print("  Allows you to run queries and download games from itch.io.")
    print("\nOptional Arguments:")
    print("  -h, --help      Show this help message and exit")
    print("  --title TITLE   Specify the title of the game to query")
    print("  --dir DIR       Specify the directory for downloads")
    print("\nSample Scratch by Title Usage Example:")
    print("  python _scratch.py --dir '/Users/aeonitis/temp'")
    print("=======================================\n")
    
if __name__ == "__main__":
    print_usage()
