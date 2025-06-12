import os
import json
from pathlib import Path

# Assuming 'tometrove_backend.src' is in PYTHONPATH or installed
# If running directly from 'tometrove_backend' directory, adjust imports if necessary
# For direct script run from 'tometrove_backend/', Python might not find 'src' easily
# One way is to add 'src' to sys.path:
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from configmanager import ConfigManager
from models import LibraryManager
from tools.logger import AppLogger # Assuming AppLogger is in src/tools/

def main():
    backend_root = Path(__file__).parent
    config_file = backend_root / 'config.json'
    template_config_file = backend_root / 'config.json.template'

    # Check if config.json exists, if not, guide user
    if not config_file.exists():
        if template_config_file.exists():
            print(f"Configuration file '{config_file}' not found.")
            print(f"Please copy '{template_config_file}' to '{config_file}' and customize it.")
            # Create a dummy config.json from template for the example to run partially
            try:
                with open(template_config_file, 'r') as f_template:
                    template_data = json.load(f_template)

                # IMPORTANT: Modify paths for a *dummy* run, especially tinydb_path
                # to be inside the project for this example if it's not already.
                # The user's actual library_root_path will be external.
                template_data["paths"]["tinydb_path"] = "data/example_library.json"
                # Ensure data directory exists for the example db
                (backend_root / "data").mkdir(exist_ok=True)

                with open(config_file, 'w') as f_config:
                    json.dump(template_data, f_config, indent=2)
                print(f"Created a temporary '{config_file}' from template for this example run.")
                print(f"Using DB at: {template_data['paths']['tinydb_path']}")
                print(f"Ensure 'library_root_path' in '{config_file}' points to your actual book collection for full functionality.")
            except Exception as e:
                print(f"Could not create temporary config.json: {e}")
                return
        else:
            print(f"Configuration file '{config_file}' and template '{template_config_file}' not found. Cannot run example.")
            return

    try:
        print(f"Loading configuration from: {config_file}")
        config_manager = ConfigManager(config_path=str(config_file))
    except RuntimeError as e:
        print(f"Error loading configuration: {e}")
        return

    # Initialize logger (optional, but good practice)
    try:
        app_logger = AppLogger(config_manager)
        logger = app_logger.logger # Use the configured logger instance
        logger.info("Backend example script started.")
    except Exception as e:
        print(f"Error initializing logger: {e}")
        # Continue without logger if it fails for the example
        logger = print

    # Initialize LibraryManager
    db_path_str = config_manager.paths.get('tinydb_path')
    library_root_str = config_manager.paths.get('library_root_path')

    if not db_path_str or not library_root_str:
        logger("Error: 'tinydb_path' or 'library_root_path' not found in config.")
        return

    # Resolve db_path: if relative, make it relative to backend_root
    db_path = Path(db_path_str)
    if not db_path.is_absolute():
        db_path = (backend_root / db_path).resolve()

    # Ensure parent directory for db_path exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger(f"Initializing LibraryManager with DB: '{db_path}' and Library Root: '{library_root_str}'")

    try:
        library_manager = LibraryManager(
            library_root_path=library_root_str,
            db_path=str(db_path)
        )
    except Exception as e:
        logger(f"Error initializing LibraryManager: {e}")
        return

    logger("LibraryManager initialized successfully.")

    # Example usage: List all books (or count them)
    try:
        all_books = library_manager.books.get_all_books()
        logger(f"Total books in the library: {len(all_books)}")

        if all_books:
            logger("First 3 books (if any):")
            for i, book in enumerate(all_books[:3]):
                logger(f"  {i+1}. {book.title} by {book.author} (UUID: {book.uuid})")
        else:
            logger("The library is currently empty.")

        # Example: List all tags
        all_tags = library_manager.tags.get_all_tag_names()
        logger(f"Available tags: {all_tags}")

    except Exception as e:
        logger(f"Error during LibraryManager usage: {e}")
    finally:
        logger("Closing LibraryManager.")
        library_manager.close()
        logger("Backend example script finished.")

if __name__ == "__main__":
    main()
