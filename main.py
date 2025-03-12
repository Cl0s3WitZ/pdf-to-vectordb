import os
from config import Config
from function_and_class.display import display_banner
from enum import Enum, auto
from function_and_class.utils import load_existing_database, create_new_database, run_benchmark


######################################
# FUNCTION AND CLASS FOR MENU ACTION #
######################################


class MenuAction(Enum):
    CREATE_DB = auto()
    LOAD_DB = auto()
    RUN_BENCHMARK = auto()
    DEDUPLICATE_DB = auto()
    DISPLAY_CHUNKS = auto()
    QUIT = auto()

def get_menu_choice() -> MenuAction:
    print("\n=== Main Menu ===")
    print("1. Create new database")
    print("2. Load existing database")
    print("3. Run benchmark")
    print("4. Deduplicate existing database")
    print("5. Display all chunks")
    print("6. Quit")
    
    choice = input("\nSelect an option (1-6): ")
    
    match choice:
        case "1": return MenuAction.CREATE_DB
        case "2": return MenuAction.LOAD_DB
        case "3": return MenuAction.RUN_BENCHMARK
        case "4": return MenuAction.DEDUPLICATE_DB
        case "5": return MenuAction.DISPLAY_CHUNKS
        case "6": return MenuAction.QUIT
        case _: return None

#################
# MAIN FUNCTION #
#################

def main():
    db = None
    display_banner()
    while True:
        action = get_menu_choice()
        
        match action:
            case MenuAction.CREATE_DB:
                db = create_new_database()
            case MenuAction.LOAD_DB:
                db = load_existing_database()
            case MenuAction.RUN_BENCHMARK:
                run_benchmark()
            case MenuAction.DEDUPLICATE_DB:
                print("\nLoading database for deduplication...")
                db = load_existing_database()
                if db is not None:
                    confirmation = input("\nDo you want to deduplicate the database? (y/n): ")
                    if confirmation.lower() == 'y':
                        db.deduplicate_existing_database()
            case MenuAction.DISPLAY_CHUNKS:
                if db is not None:
                    db.display_all_chunks()
                else:
                    print("\nNo database loaded!")
            case MenuAction.QUIT:
                print("Goodbye!")
                break
            case None:
                print("Invalid option. Please try again.")
                continue
        
        if db is not None:
            # Search loop
            while True:
                query = input("\nEnter your search query (or 'q' to return to menu): ")
                if query.lower() == 'q':
                    break
                    
                results = db.search(query)
                print("\nSearch results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Similarity score: {result['similarity_score']:.2f}")
                    print(f"PDF: {os.path.basename(result['pdf_path'])}")
                    print(f"Page: {result['page']}")
                    print(f"Excerpt: {result['text'][:Config.MAX_DISPLAY_CHARS]}...")

if __name__ == "__main__":
    main()
