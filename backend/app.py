import os
import json
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add src to sys.path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from configmanager import ConfigManager
from models import LibraryManager, Book # Import Book for type hinting and creating new books

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing frontend requests

# --- Configuration ---
backend_root = Path(__file__).parent
config_file = backend_root / 'config.json'
template_config_file = backend_root / 'config.json.template'
library_manager = None # Global LibraryManager instance

def init_library_manager():
    global library_manager
    if not config_file.exists():
        if template_config_file.exists():
            try:
                with open(template_config_file, 'r') as f_template:
                    template_data = json.load(f_template)

                # Use relative path for the example DB if not absolute
                db_path_str = template_data["paths"]["tinydb_file"]
                db_path = Path(db_path_str)
                if not db_path.is_absolute():
                    template_data["paths"]["tinydb_file"] = str((backend_root / db_path_str).resolve())

                # Ensure data directory exists for the example db
                db_dir = (backend_root / Path(db_path_str).parent)
                db_dir.mkdir(parents=True, exist_ok=True)

                with open(config_file, 'w') as f_config:
                    json.dump(template_data, f_config, indent=2)
                print(f"Created a temporary '{config_file}' from template.")
            except Exception as e:
                print(f"Could not create temporary config.json: {e}")
                # Decide if app should exit or run with limited functionality
                raise RuntimeError(f"Could not create temporary config.json: {e}")
        else:
            raise RuntimeError(f"Configuration file '{config_file}' and template '{template_config_file}' not found.")

    try:
        config_manager = ConfigManager(config_path=str(config_file))
        db_path_str = config_manager.paths.get('tinydb_file')
        library_root_str = config_manager.paths.get('library_path')

        if not db_path_str or not library_root_str:
            raise RuntimeError("'tinydb_file' or 'library_path' not found in config.")

        db_path = Path(db_path_str)
        if not db_path.is_absolute():
            db_path = (backend_root / db_path).resolve()

        db_path.parent.mkdir(parents=True, exist_ok=True)

        library_manager = LibraryManager(
            library_root_path=library_root_str,
            db_path=str(db_path)
        )
        print("LibraryManager initialized successfully.")
    except Exception as e:
        print(f"Error initializing LibraryManager: {e}")
        # Decide if app should exit or run with limited functionality
        raise RuntimeError(f"Error initializing LibraryManager: {e}")

# Initialize LibraryManager when the app starts
try:
    init_library_manager()
except RuntimeError as e:
    # If init fails, the app might not be usable.
    # Log this and decide on behavior (e.g., exit, or run with endpoints that return errors).
    print(f"FATAL: LibraryManager could not be initialized: {e}")
    # For now, we'll let it run and endpoints will likely fail if library_manager is None.
    # A more robust solution would be to have health check endpoints or prevent app from starting.

# --- Helper Functions ---
def book_to_dict(book_obj):
    """Converts a Book object to a dictionary suitable for JSON serialization,
       handling the 'read' status and 'uuid' to 'id' mapping.
    """
    if not book_obj:
        return None

    book_dict = book_obj.to_dict() # Uses the existing method in Book class
    book_dict['id'] = book_dict.pop('uuid') # Rename uuid to id for frontend

    # Convert 'read' (datetime or None) to boolean 'is_read'
    book_dict['is_read'] = book_obj.read is not None
    # Keep 'read' as ISO string if needed, or remove if 'is_read' is sufficient
    # book_dict['read_timestamp'] = book_obj.read.isoformat() if book_obj.read else None
    return book_dict

# --- API Endpoints ---
@app.route('/api/books', methods=['GET'])
def get_books():
    if not library_manager:
        return jsonify({"error": "LibraryManager not initialized"}), 500
    try:
        books_list = library_manager.books.get_all_books()
        # Sort books by 'added' date by default (newest first) as per models.BookManager.sort_books
        sorted_books = library_manager.books.sort_books(field='added', reverse=True) # Assuming 'added' is a valid sort field
        return jsonify([book_to_dict(b) for b in sorted_books])
    except Exception as e:
        print(f"Error in get_books: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book():
    if not library_manager:
        return jsonify({"error": "LibraryManager not initialized"}), 500
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        # Basic validation (can be expanded)
        required_fields = ['title', 'author']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Create a new Book object - adapting frontend fields to backend model
        # Frontend sends 'id', 'dateAdded', 'tags' (list of strings), 'read' (boolean)
        # Backend 'Book' needs 'uuid', 'added' (datetime), 'tags' (list of strings)

        from datetime import datetime, timezone
        import uuid

        new_book_data = {
            "uuid": str(uuid.uuid4()),
            "title": data["title"],
            "author": data["author"],
            "added": datetime.now(timezone.utc), # Or parse from data if 'dateAdded' is provided
            "tags": data.get("tags", []),
            "filename": data.get("filename", ""), # Optional
            "series": data.get("series"), # Optional
            "num_series": data.get("num_series"), # Optional
            "description": data.get("description"), # Optional
            # 'read' status (boolean from frontend) needs to be handled.
            # If frontend sends 'read' as boolean, convert to datetime for backend if it's read.
        }
        if data.get('read', False): # Assuming frontend sends 'read' as boolean
             new_book_data['read'] = datetime.now(timezone.utc)
        else:
            new_book_data['read'] = None

        book_obj = Book(**new_book_data)
        library_manager.books.add_book(book_obj)
        return jsonify(book_to_dict(book_obj)), 201

    except Exception as e:
        print(f"Error in add_book: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    if not library_manager:
        return jsonify({"error": "LibraryManager not initialized"}), 500
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid data"}), 400

        # Fetch the existing book
        book_obj = library_manager.books.get_book(book_id) # Changed from get_book_by_uuid
        if not book_obj:
            return jsonify({"error": "Book not found"}), 404

        # Update fields - map frontend 'id' to backend 'uuid' if necessary (already done by book_id)
        # Map frontend 'read' (boolean) to backend 'read' (datetime)
        update_payload = {}
        for key, value in data.items():
            if key == "read": # Frontend sends 'read' as boolean
                if value: # if true (book is read)
                    update_payload['read'] = book_obj.read or datetime.now(timezone.utc)
                else: # if false (book is not read)
                    update_payload['read'] = None
            elif key not in ["id", "uuid"]: # Avoid trying to update 'id' or 'uuid' directly
                 update_payload[key] = value

        if not update_payload:
             return jsonify({"message": "No update data provided"}), 200 # Or 400 if some change is expected

        library_manager.books.update_book(book_id, update_payload)
        updated_book_obj = library_manager.books.get_book(book_id) # Re-fetch to get the updated state
        return jsonify(book_to_dict(updated_book_obj))

    except Exception as e:
        print(f"Error in update_book (ID: {book_id}): {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if not library_manager:
        return jsonify({"error": "LibraryManager not initialized"}), 500
    try:
        book_obj = library_manager.books.get_book(book_id) # Changed from get_book_by_uuid
        if not book_obj:
            return jsonify({"error": "Book not found"}), 404

        library_manager.books.remove_book(book_id)
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        print(f"Error in delete_book (ID: {book_id}): {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags', methods=['GET'])
def get_tags():
    if not library_manager:
        return jsonify({"error": "LibraryManager not initialized"}), 500
    try:
        tags = library_manager.tags.get_all_tag_names() # Assuming this returns a list of strings
        return jsonify(tags)
    except Exception as e:
        print(f"Error in get_tags: {e}")
        return jsonify({"error": str(e)}), 500

# --- Main Execution ---
if __name__ == '__main__':
    # Note: For production, use a WSGI server like Gunicorn or Waitress
    app.run(debug=True, port=5001) # Running on a different port than default 5000 for Vite
