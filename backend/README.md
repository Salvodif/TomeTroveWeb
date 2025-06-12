# TomeTroveBackend

This is the backend server for the TomeTrove personal library management application. It's built with Python, Flask, and uses TinyDB for data storage.

## Features

*   Provides API endpoints for managing books and tags.
*   Handles data persistence using TinyDB.
*   Basic configuration management for database paths.

## Project Structure

```
backend/
├── app.py                # Main Flask application, API endpoints
├── config.json.template  # Template for configuration
├── config.json           # Actual configuration (created on first run or manually)
├── requirements.txt      # Python dependencies
├── library_files/        # Example directory for storing book files (if feature is used)
└── src/
    ├── __init__.py
    ├── configmanager.py  # Handles configuration loading
    ├── filesystem.py     # Filesystem utilities
    ├── formvalidators.py # Form validation utilities
    ├── models.py         # Core data models (Book, LibraryManager, etc.)
    └── tools/
        └── logger.py     # Logging utility
```

## Setup and Running

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configuration (`config.json`):**
    The application uses a `config.json` file for settings, primarily the path to the TinyDB database file and the root directory for library files.
    *   If `config.json` does not exist, the application will attempt to create one from `config.json.template` on the first run.
    *   The default template sets up `tinydb_path` as `data/library.json` (relative to the `backend` directory) and `library_root_path` as `library_files/`.
    *   Ensure the directory for `tinydb_path` (e.g., `data/`) can be created or exists, and `library_files/` exists if you plan to use file-based features (currently minimal in the API).

6.  **Run the Flask development server:**
    ```bash
    python app.py
    ```
    The server will start, typically on `http://localhost:5001`.

## API Endpoints

The backend provides the following API endpoints:

*   **Books**
    *   `GET /api/books`: Retrieves a list of all books.
    *   `POST /api/books`: Adds a new book.
        *   Payload (JSON): `{ "title": "...", "author": "...", "tags": ["...", "..."], "series": "...", "num_series": 1, "description": "...", "filename": "...", "read": false }`
        *   `title` and `author` are required. Other fields are optional.
        *   `read` is a boolean; backend converts to datetime if true.
    *   `PUT /api/books/<book_id>`: Updates an existing book.
        *   Payload (JSON): Can include any fields from the book model to be updated, e.g., `{ "read": true }` or `{ "title": "New Title" }`.
    *   `DELETE /api/books/<book_id>`: Deletes a book by its ID.

*   **Tags**
    *   `GET /api/tags`: Retrieves a list of all unique tag names.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all routes, allowing requests from any origin. This is configured in `app.py` using `Flask-CORS`.

## Dependencies

*   Flask
*   Flask-CORS
*   TinyDB
*   (Any other dependencies listed in `requirements.txt`)
```
