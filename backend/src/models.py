from pathlib import Path
import tinydb
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import logging
from functools import cmp_to_key

from formvalidators import FormValidators
from filesystem import FileSystemHandler

@dataclass
class Book:
    uuid: str
    author: str
    title: str
    added: datetime
    tags: List[str] = field(default_factory=list)
    filename: str = ""
    other_formats: List[str] = field(default_factory=list)
    series: Optional[str] = None
    num_series: Optional[float] = None
    description: Optional[str] = None
    read: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Book':
        logger = logging.getLogger(__name__)
        added_str = data['added']
        added = None
        try:
            # Attempt to parse ISO 8601 format directly
            added = datetime.fromisoformat(added_str)
            if added.tzinfo is None:
                added = added.replace(tzinfo=datetime.now().astimezone().tzinfo)
        except ValueError:
            # Fallback to other formats if ISO parsing fails
            for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
                try:
                    # Strip sub-second precision if not supported by format
                    added_str_to_parse = added_str
                    if "%f" not in fmt and "." in added_str_to_parse:
                        added_str_to_parse = added_str_to_parse.split('.')[0]

                    added = datetime.strptime(added_str_to_parse, fmt)
                    if added.tzinfo is None: # Make naive datetime aware
                        added = added.replace(tzinfo=datetime.now().astimezone().tzinfo)
                    break
                except ValueError:
                    continue
            if added is None: # If all parsing attempts fail
                logger.error(f"Error parsing 'added' date '{added_str}'. Using current UTC time.")
                added = datetime.now(timezone.utc)


        read_value = None
        read_data = data.get('read')
        if read_data and isinstance(read_data, str) and read_data.strip():
            read_str = str(read_data)
            try:
                read_value = datetime.fromisoformat(read_str)
                if read_value.tzinfo is None:
                    read_value = read_value.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except ValueError:
                try:
                    read_value = datetime.strptime(read_str, "%Y-%m-%d %H:%M")
                    if read_value.tzinfo is None: # Make naive datetime aware
                        read_value = read_value.replace(tzinfo=datetime.now().astimezone().tzinfo)
                except ValueError as e:
                    logger.warning(f"Error parsing 'read' date '{read_str}': {e}. Setting to None.")
                    read_value = None

        return cls(
            uuid=data['uuid'],
            author=data['author'],
            title=data['title'],
            added=added,
            tags=data.get('tags', []),
            filename=data.get('filename', ''),
            other_formats=data.get('other_formats', []),
            series=data.get('series'),
            num_series=data.get('num_series'),
            description=data.get('description'),
            read=read_value
        )

    def to_dict(self) -> Dict:
        # Ensure 'added' is always a datetime object before calling isoformat
        if not isinstance(self.added, datetime):
            # This case should ideally not happen if from_dict is correct
            # and added is always initialized properly.
            # For robustness, convert to datetime if it's a string, or handle error
            logger = logging.getLogger(__name__)
            logger.error(f"Book.added is not a datetime object: {self.added}. Attempting conversion or defaulting.")
            # Attempt to parse if string, otherwise, this indicates a deeper issue
            if isinstance(self.added, str):
                try:
                    self.added = datetime.fromisoformat(self.added)
                    if self.added.tzinfo is None:
                         self.added = self.added.replace(tzinfo=datetime.now().astimezone().tzinfo)
                except ValueError:
                    self.added = datetime.now(timezone.utc) # Fallback
            else: # Not a string, not a datetime - critical issue
                 self.added = datetime.now(timezone.utc)


        added_iso = self.added.isoformat()
        read_iso = None
        if self.read is not None:
            if isinstance(self.read, datetime):
                read_iso = self.read.isoformat()
            else:
                # This case implies self.read was not converted to datetime correctly
                # or was set to a non-datetime, non-None value.
                logger = logging.getLogger(__name__)
                logger.warning(f"Book.read is not a datetime object: {self.read}. Storing as None.")
                read_iso = None # Or handle as an error case

        return {
            'uuid': self.uuid,
            'author': self.author,
            'title': self.title,
            'added': added_iso,
            'tags': self.tags,
            'filename': self.filename,
            'other_formats': self.other_formats,
            'series': self.series,
            'num_series': self.num_series,
            'description': self.description,
            'read': read_iso
        }

    @property
    def formatted_date(self) -> str:
        """Formats the date for display, excluding microseconds."""
        # Ensure self.added is a datetime object before formatting
        if isinstance(self.added, datetime):
            return self.added.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # This case should ideally not happen. Log an error or return a default.
            logger = logging.getLogger(__name__)
            logger.error(f"Book.added is not a datetime object: {self.added} in formatted_date. Returning empty string.")
            return "" # Or raise an error, or return a sensible default

    @classmethod
    def parse_ui_date(cls, date_str: str) -> datetime:
        """Converts a date string from UI format (Y-m-d H:M) to a timezone-aware datetime object."""
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=datetime.now().astimezone().tzinfo)

######################################################################################################
#
#                   TagsManager
#
######################################################################################################
class TagsManager:
    """Manages tags in the TinyDB database."""
    def __init__(self, db_path: str):
        self.db = tinydb.TinyDB(db_path)
        self.tags_table = self.db.table('tags')
        self._cache = None
        self._dirty = True

    def _ensure_cache(self):
        """Loads the cache if it's outdated or doesn't exist."""
        if self._dirty or self._cache is None:
            self._cache = {tag.doc_id: tag for tag in self.tags_table.all()}
            self._dirty = False

    def get_all_tags(self) -> Dict[int, Dict[str, Any]]:
        """Gets all tags from the cache."""
        self._ensure_cache()
        return self._cache.copy()

    def get_all_tag_names(self) -> List[str]:
        """Gets a list of unique and sorted tag names."""
        self._ensure_cache()
        if not self._cache:
            return []
        return sorted(list(set(tag_data['name'] for tag_data in self._cache.values() if 'name' in tag_data)))

    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Gets a specific tag by name."""
        self._ensure_cache()
        for tag in self._cache.values():
            if tag['name'] == name:
                return tag
        return None

    def add_tag(self, name: str, icon: str) -> int:
        """Adds a new tag."""
        tag_id = self.tags_table.insert({'name': name, 'icon': icon})
        self._dirty = True
        return tag_id

    def update_tag(self, tag_id: int, new_data: Dict[str, Any]):
        """Updates an existing tag."""
        self.tags_table.update(new_data, doc_ids=[tag_id])
        self._dirty = True

    def remove_tag(self, tag_id: int):
        """Removes a tag."""
        self.tags_table.remove(doc_ids=[tag_id])
        self._dirty = True

    def close(self):
        """Closes the database connection and clears the cache."""
        self.db.close()
        self._cache = None
        self._dirty = True

#####################################################################################################
#                                       BookManager
#                    Manages interaction with the TinyDB database for books.
#####################################################################################################
class BookManager:
    """Manages books in the TinyDB database."""
    def __init__(self, library_root_path: str, db_path: str, tags_manager: Optional[TagsManager] = None): # Made Optional explicit
        self.db = tinydb.TinyDB(db_path)
        self.books_table = self.db.table('books')
        self._cache = None
        self._dirty = True
        self._library_root = library_root_path
        self.tags_manager = tags_manager

    @property
    def library_root(self) -> str:
        return self._library_root

    def _ensure_cache(self):
        """Loads the cache if it's outdated or doesn't exist."""
        if self._dirty or self._cache is None:
            self._cache = {book['uuid']: Book.from_dict(book)
                          for book in self.books_table.all()}
            self._dirty = False

    def add_book(self, book: Book):
        # Validate author name
        is_valid, fs_name = FormValidators.validate_author_name(book.author)
        if not is_valid:
            raise ValueError(f"Invalid author name: {fs_name}")

        """Adds a book to the database and invalidates the cache."""
        self.books_table.insert(book.to_dict())
        self._dirty = True

    def get_book_path(self, book: Book) -> str:
        """Returns the full path of the book file."""
        logger = logging.getLogger(__name__) # Ensure logger is available
        if not book.filename or not book.filename.strip():
            logger.warning(f"Book '{book.title}' (UUID: {book.uuid}) has no filename; cannot determine path.")
            raise ValueError("Book has no associated filename to construct a path.")

        directory_name_fs = ""
        # Check if it's a series book (series name exists and num_series is present)
        if book.series and book.series.strip() and book.num_series is not None:
            directory_name_fs = FormValidators.series_to_fsname(book.series)
            if not directory_name_fs:
                logger.error(f"Failed to generate series directory for book '{book.title}' (UUID: {book.uuid}) with series '{book.series}'. Defaulting to author directory.")
                directory_name_fs = FormValidators.author_to_fsname(book.author)
                if not directory_name_fs:
                     logger.error(f"Author name also problematic for book '{book.title}' (UUID: {book.uuid}). Using '.' as directory.")
                     directory_name_fs = "."
        else:
            # Not a series book, or series information is incomplete
            directory_name_fs = FormValidators.author_to_fsname(book.author)
            if not directory_name_fs:
                logger.error(f"Failed to generate author directory for book '{book.title}' (UUID: {book.uuid}). Using '.' as directory.")
                directory_name_fs = "."

        return str(Path(self.library_root) / directory_name_fs / book.filename)

    def ensure_directory(self, author: str) -> str:
        """Creates the author's directory if it doesn't exist."""
        author_dir = FormValidators.author_to_fsname(author)
        author_path = Path(self.library_root) / author_dir
        return FileSystemHandler.ensure_directory_exists(str(author_path))


################### UPDATE BOOK ###########################
    def update_book(self, uuid: str, new_data: Dict):
        """Updates an existing book and invalidates the cache."""
        logger = logging.getLogger(__name__)
        logger.debug(f"BookManager.update_book - Attempting to update book with UUID: {uuid}. Incoming data: {new_data}")
        q = tinydb.Query()

        # Get old book object before updating
        old_book_obj = self.get_book(uuid) # Changed from get_book_by_uuid
        if not old_book_obj:
            logger.error(f"BookManager.update_book - Book with UUID {uuid} not found. Cannot update.")
            raise ValueError(f"Book with UUID {uuid} not found.")

        # old_book_data variable is removed as old_book_obj is now the Book instance
        try:
            old_file_path = self.get_book_path(old_book_obj)
            logger.debug(f"BookManager.update_book - Old file path: {old_file_path}")
        except ValueError as e:
            # This can happen if the book has no filename, which is possible.
            old_file_path = None
            logger.warning(f"BookManager.update_book - Could not determine old file path for book {uuid}: {e}")

        # Process 'added' field
        if 'added' in new_data:
            if isinstance(new_data['added'], datetime):
                new_data['added'] = new_data['added'].isoformat()
            elif isinstance(new_data['added'], str):
                # Attempt to parse if it's a string, assuming ISO 8601 or fallback
                try:
                    dt = datetime.fromisoformat(new_data['added'])
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                    new_data['added'] = dt.isoformat()
                except ValueError:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Invalid date string for 'added' in update_book: {new_data['added']}. Keeping original or consider error handling.")
                    # Decide on error handling: raise error, log and skip, or try other parsing
            # If it's neither datetime nor string, it might be an issue depending on input types

        # Process 'read' field
        if 'read' in new_data:
            if isinstance(new_data['read'], datetime):
                new_data['read'] = new_data['read'].isoformat()
            elif isinstance(new_data['read'], str):
                if not new_data['read'].strip(): # Empty string
                    new_data['read'] = None
                else:
                    # Attempt to parse if it's a non-empty string
                    try:
                        # Try ISO format first
                        dt = datetime.fromisoformat(new_data['read'])
                        if dt.tzinfo is None:
                             dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                        new_data['read'] = dt.isoformat()
                    except ValueError:
                        # Fallback to UI format if ISO fails
                        try:
                            dt = Book.parse_ui_date(new_data['read']) # Uses the class method
                            new_data['read'] = dt.isoformat()
                        except ValueError:
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Invalid date string for 'read' in update_book: {new_data['read']}. Setting to None.")
                            new_data['read'] = None
            elif new_data['read'] is None:
                pass # Already None, which is the desired state for storage
            else: # Not datetime, not string, not None
                logger = logging.getLogger(__name__)
                logger.warning(f"Unexpected type for 'read' in update_book: {type(new_data['read'])}. Setting to None.")
                new_data['read'] = None

        # Granular logging for 'filename' field processing
        if 'filename' in new_data:
            logger.debug(f"BookManager.update_book - Filename field present. Type before conversion check: {type(new_data['filename'])}, Value: {repr(new_data['filename'])}")
            if isinstance(new_data['filename'], Path):
                logger.debug(f"BookManager.update_book - Attempting to convert filename from Path object.")
                new_data['filename'] = str(new_data['filename'])
                logger.debug(f"BookManager.update_book - Filename field converted. Type after conversion: {type(new_data['filename'])}, Value: {repr(new_data['filename'])}")
            else:
                logger.debug(f"BookManager.update_book - Filename field is present but not a Path object. Type: {type(new_data['filename'])}, Value: {repr(new_data['filename'])}")
        else:
            logger.debug("BookManager.update_book - Filename field not in new_data.")

        logger.debug(f"BookManager.update_book - Data before TinyDB update operation: {new_data}")
        self.books_table.update(new_data, q.uuid == uuid)
        self._dirty = True

        # After updating, check if title, author, series, or num_series changed to rename file/path
        new_title = new_data.get('title', old_book_obj.title)
        new_author = new_data.get('author', old_book_obj.author)
        new_series = new_data.get('series', old_book_obj.series) # May be None or empty string
        new_num_series_val = new_data.get('num_series', old_book_obj.num_series) # May be None

        new_num_series = None
        if new_num_series_val is not None:
            if isinstance(new_num_series_val, str):
                try:
                    new_num_series = float(new_num_series_val) if new_num_series_val.strip() else None
                except ValueError:
                    logger.warning(f"Could not parse num_series string '{new_num_series_val}' to float for book {uuid}. Treating as None.")
                    new_num_series = None # Explicitly None if parsing fails
            elif isinstance(new_num_series_val, (int, float)):
                new_num_series = float(new_num_series_val)
            else:
                logger.warning(f"Invalid type for num_series '{new_num_series_val}' for book {uuid}. Treating as None.")
                new_num_series = None


        title_changed = new_title != old_book_obj.title
        author_changed = new_author != old_book_obj.author
        series_changed = (new_series or "").strip() != (old_book_obj.series or "").strip() # Compare stripped series

        old_num_series_float = None
        if old_book_obj.num_series is not None:
            try: old_num_series_float = float(old_book_obj.num_series)
            except: pass

        num_series_changed = new_num_series != old_num_series_float

        metadata_changed_for_path = title_changed or author_changed or series_changed or num_series_changed
        logger.debug(f"Book {uuid}: title_changed={title_changed}, author_changed={author_changed}, series_changed={series_changed}, num_series_changed={num_series_changed}")


        if metadata_changed_for_path:
            logger.info(f"BookManager.update_book - Metadata changed for book {uuid}. Evaluating path and filename.")

            actual_old_file_path = None
            old_filename_from_db = old_book_obj.filename

            if old_filename_from_db and old_filename_from_db.strip():
                # Candidate 1: Old Author directory (Non-series path)
                old_author_fs_c1 = FormValidators.author_to_fsname(old_book_obj.author)
                path_c1 = Path(self.library_root) / old_author_fs_c1 / old_filename_from_db
                if path_c1.exists():
                    actual_old_file_path = str(path_c1)
                    logger.debug(f"Found old file at author path: {actual_old_file_path}")

                # Candidate 2: Incorrect previous series path (Author - Series)
                if not actual_old_file_path and old_book_obj.series and old_book_obj.series.strip():
                    old_author_fs_c2 = FormValidators.author_to_fsname(old_book_obj.author)
                    old_series_fs_c2 = FormValidators.series_to_fsname(old_book_obj.series)
                    old_incorrect_series_dir = f"{old_author_fs_c2} - {old_series_fs_c2}"
                    path_c2 = Path(self.library_root) / old_incorrect_series_dir / old_filename_from_db
                    if path_c2.exists():
                        actual_old_file_path = str(path_c2)
                        logger.debug(f"Found old file at 'Author - Series' path: {actual_old_file_path}")

                # Candidate 3: Current series path (SeriesName/) - in case only filename changes
                if not actual_old_file_path and old_book_obj.series and old_book_obj.series.strip() and old_book_obj.num_series is not None:
                    old_series_fs_c3 = FormValidators.series_to_fsname(old_book_obj.series)
                    path_c3 = Path(self.library_root) / old_series_fs_c3 / old_filename_from_db
                    if path_c3.exists():
                        actual_old_file_path = str(path_c3)
                        logger.debug(f"Found old file at new series path type: {actual_old_file_path}")


                if not actual_old_file_path:
                    logger.warning(f"Old file '{old_filename_from_db}' for book {uuid} not found at any expected legacy locations.")

            # Generate new filename
            file_extension = ""
            if old_filename_from_db and old_filename_from_db.strip():
                file_extension = Path(old_filename_from_db).suffix
            elif 'file_extension' in new_data and new_data['file_extension'].startswith('.'):
                file_extension = new_data['file_extension']
            else:
                file_extension = '.epub' # Default if no old filename and no specific new extension
                logger.debug(f"Defaulting to file extension '{file_extension}' for book {uuid}")

            new_author_fs = FormValidators.author_to_fsname(new_author)
            new_title_fs = FormValidators.title_to_fsname(new_title)
            new_filename_stem = ""

            is_new_series_book = new_series and new_series.strip() and new_num_series is not None

            if is_new_series_book:
                try:
                    new_filename_stem = f"{int(new_num_series):02d} - {new_author_fs} - {new_title_fs}"
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid num_series '{new_num_series}' for book {uuid} filename formatting: {e}. Falling back.")
                    # Fallback for series book filename if num_series is problematic
                    new_filename_stem = f"{new_author_fs} - {new_title_fs}"
            else: # Not a series book
                # NON-SERIES book: Filename should be "Author - Title"
                new_filename_stem = f"{new_author_fs} - {new_title_fs}" # CORRECTED LOGIC FOR NON-SERIES

            new_filename = f"{new_filename_stem}{file_extension}"
            logger.debug(f"Generated new filename for book {uuid}: {new_filename}")

            # Generate new parent directory path
            new_parent_dir_path_obj = None
            if is_new_series_book:
                new_series_fs = FormValidators.series_to_fsname(new_series)
                if not new_series_fs: # Should not happen if series name is valid
                    logger.error(f"Problem generating series dir name for '{new_series}'. Using author dir for book {uuid}.")
                    new_parent_dir_path_obj = Path(self.library_root) / new_author_fs
                else:
                    new_parent_dir_path_obj = Path(self.library_root) / new_series_fs
            else: # Non-series book
                new_parent_dir_path_obj = Path(self.library_root) / new_author_fs

            if not new_parent_dir_path_obj: # Ultimate fallback, should be extremely rare
                 logger.error(f"Could not determine parent directory for book {uuid}. Defaulting to library root.")
                 new_parent_dir_path_obj = Path(self.library_root)


            logger.debug(f"Ensuring new directory exists: {new_parent_dir_path_obj}")
            FileSystemHandler.ensure_directory_exists(str(new_parent_dir_path_obj))
            new_file_path = str(new_parent_dir_path_obj / new_filename)
            logger.debug(f"New full file path for book {uuid}: {new_file_path}")

            if actual_old_file_path:
                if actual_old_file_path != new_file_path:
                    try:
                        FileSystemHandler.rename_file(actual_old_file_path, new_file_path)
                        logger.info(f"File for book {uuid} MOVED from {actual_old_file_path} to {new_file_path}")
                    except Exception as e:
                        logger.error(f"Error moving file for book {uuid} from {actual_old_file_path} to {new_file_path}: {e}")
                else:
                    logger.info(f"File for book {uuid} is already at the correct path and name: {new_file_path}. No move needed.")

            # Update filename in DB if it has changed or if it was empty and is now set
            if old_filename_from_db != new_filename or (not old_filename_from_db and new_filename):
                self.books_table.update({'filename': new_filename}, q.uuid == uuid)
                logger.info(f"Filename for book {uuid} updated in DB to: {new_filename}")
            else:
                logger.debug(f"Filename for book {uuid} ('{new_filename}') unchanged in DB.")

        else: # No metadata changed that affects path, but check if filename was passed in new_data
            if 'filename' in new_data and new_data['filename'] != old_book_obj.filename:
                 # This case is if filename is directly edited by user, not via metadata change.
                 # The current self.get_book_path(old_book_obj) would use the *old* metadata for directory.
                 # This specific scenario might need more thought if direct filename edits are allowed
                 # and should also trigger directory re-evaluation based on *current* metadata.
                 # For now, we assume filename changes are driven by metadata changes above.
                 logger.info(f"Book {uuid}: Metadata affecting path did not change, but 'filename' might have been in new_data. Current logic prioritizes metadata-driven filename/path.")
                 # If only the filename string changed in new_data, but not the components (author, title, series),
                 # the DB has already been updated. We might need to ensure consistency if this happens.
                 # For now, this path is less critical as changes are expected via metadata.

#################################################################

################### REMOVE BOOK ###########################
    def remove_book(self, uuid: str):
        """Removes a book from the database and invalidates the cache."""
        BookQuery = tinydb.Query()
        self.books_table.remove(BookQuery.uuid == uuid)
        self._dirty = True

    def get_book(self, uuid: str) -> Optional[Book]:
        """Gets a specific book by UUID from the cache."""
        self._ensure_cache()
        return self._cache.get(uuid)

    def get_all_books(self) -> List[Book]:
        """Gets all books from the cache."""
        self._ensure_cache()
        return list(self._cache.values())

    def get_all_author_names(self) -> List[str]:
        """Gets a list of unique and sorted author names."""
        self._ensure_cache()
        if not self._cache:
            return []
        return sorted(list(set(book.author for book in self._cache.values() if book.author)))

    def get_all_series_names(self) -> List[str]:
        """Gets a list of unique and sorted series names."""
        self._ensure_cache()
        if not self._cache:
            return []

        series_names = set()
        for book in self._cache.values():
            if book.series and book.series.strip():
                series_names.add(book.series)
        return sorted(list(series_names))

    def get_books_by_series(self, series_name: str) -> List[Book]:
        """Gets a list of books belonging to a specific series."""
        self._ensure_cache()
        if not self._cache:
            return []

        return [book for book in self._cache.values() if book.series == series_name]

    def search_books_by_text(self, text: str) -> List[Book]:
        """Searches books by text in title or author."""
        if not text:
            return self.get_all_books()

        self._ensure_cache()
        text_lower = text.lower()

        return [
            book for book in self._cache.values()
            if (book.title and text_lower in book.title.lower()) or
               (book.author and text_lower in book.author.lower())
        ]

################### SORT BOOKS ###########################
    def sort_books(self, field: str, reverse: bool = None) -> List[Book]:
        books = self.get_all_books()
        if not books:
            return []

        logger = logging.getLogger(__name__)

        if field == 'added':

            def compare_books(book1: Book, book2: Book):
                # 1. Sort by 'added' (descending)
                # Ensure 'added' is datetime, handle if not (though from_dict should ensure this)
                b1_added = book1.added if isinstance(book1.added, datetime) else datetime.min.replace(tzinfo=timezone.utc)
                b2_added = book2.added if isinstance(book2.added, datetime) else datetime.min.replace(tzinfo=timezone.utc)

                # Ensure timezone awareness for comparison if one is aware and other is naive (should not happen with current from_dict)
                if (b1_added.tzinfo is None and b2_added.tzinfo is not None):
                    b1_added = b1_added.replace(tzinfo=timezone.utc) # Assuming UTC for safety
                if (b2_added.tzinfo is None and b1_added.tzinfo is not None):
                    b2_added = b2_added.replace(tzinfo=timezone.utc)


                if b1_added < b2_added: return 1
                if b1_added > b2_added: return -1

                # At this point, book1.added == book2.added
                is_series1 = bool(book1.series and book1.series.strip() and book1.num_series is not None)
                is_series2 = bool(book2.series and book2.series.strip() and book2.num_series is not None)

                if is_series1 and is_series2:
                    # Both are series books
                    # 2a. Sort by num_series (ascending)
                    # Ensure num_series are float for comparison
                    try:
                        num1 = float(book1.num_series)
                        num2 = float(book2.num_series)
                        if num1 < num2: return -1
                        if num1 > num2: return 1
                    except (ValueError, TypeError):
                        # Handle cases where num_series might not be a valid number
                        # This case implies data inconsistency. Sort non-numeric num_series last.
                        if isinstance(book1.num_series, (int, float)) and not isinstance(book2.num_series, (int, float)): return -1
                        if not isinstance(book1.num_series, (int, float)) and isinstance(book2.num_series, (int, float)): return 1
                        # If both are non-numeric or conversion failed for both, proceed to next criteria


                    # 2b. Sort by series name (ascending, case-insensitive)
                    series1_lower = (book1.series or "").lower()
                    series2_lower = (book2.series or "").lower()
                    if series1_lower < series2_lower: return -1
                    if series1_lower > series2_lower: return 1

                    # 2c. Sort by title (ascending, case-insensitive)
                    title1_lower = (book1.title or "").lower()
                    title2_lower = (book2.title or "").lower()
                    if title1_lower < title2_lower: return -1
                    if title1_lower > title2_lower: return 1
                    return 0

                elif is_series1: # book1 is series, book2 is not
                    return -1 # Series books come before non-series books

                elif is_series2: # book2 is series, book1 is not
                    return 1  # Non-series books come after series books

                else: # Both are non-series books
                    # 2d. Sort by title (ascending, case-insensitive)
                    title1_lower = (book1.title or "").lower()
                    title2_lower = (book2.title or "").lower()
                    if title1_lower < title2_lower: return -1
                    if title1_lower > title2_lower: return 1
                    return 0

            # For 'added' field, the problem implies reverse is True by default (newest first)
            # The compare_books function is already set for descending on 'added'.
            # If `reverse` parameter is explicitly False for 'added', we would need to invert the compare_books logic or results.
            # However, the original logic for `reverse is None` was `True` for 'added'.
            # So, if `reverse` is True or None, use compare_books as is. If `reverse` is False, we need to sort ascending.

            # The custom compare_books function sorts 'added' descending.
            # If reverse=False (meaning ascending for 'added'), we need to flip the result of compare_books.
            if reverse is False: # Explicit request for ascending 'added'
                 books.sort(key=cmp_to_key(lambda b1, b2: -1 * compare_books(b1, b2)))
            else: # Default (reverse=True or None) for 'added' means descending
                 books.sort(key=cmp_to_key(compare_books))


        elif hasattr(books[0], field) if books else False:
            actual_reverse = reverse if reverse is not None else False # Default to ascending for other fields

            def get_sort_key(b: Book):
                val = getattr(b, field, None)
                is_first_book_attr_str = isinstance(getattr(books[0], field, None), str) if books else False

                if isinstance(val, str):
                    return (val or "").lower()
                if val is None:
                    if is_first_book_attr_str: # If the attribute type is generally string
                        return "" # Sort None strings as empty strings
                    # For non-string types, place Nones consistently
                    # To sort Nones last in ascending: return a type-appropriate max value or tuple
                    # To sort Nones first in ascending: return a type-appropriate min value or tuple
                    # Current logic: sort Nones first for non-str types in ascending if not handled explicitly
                    # Let's refine to sort Nones last for numeric/datetime
                    if isinstance(getattr(books[0], field, None), (int, float)):
                         return float('inf') if not actual_reverse else float('-inf')
                    if isinstance(getattr(books[0], field, None), datetime):
                         return datetime.max.replace(tzinfo=timezone.utc) if not actual_reverse else datetime.min.replace(tzinfo=timezone.utc)
                    return None # Python's default None handling (usually sorts them first)
                return val

            try:
                books.sort(key=get_sort_key, reverse=actual_reverse)
            except TypeError as e:
                logger.error(f"TypeError during sorting by field '{field}': {e}. List may be partially sorted or unsorted. Attempting naive sort for '{field}'.")
                try:
                    # Fallback to direct attribute access, hoping Python handles mixed types or Nones more gracefully (or fails similarly)
                    books.sort(key=lambda x: getattr(x, field, None), reverse=actual_reverse)
                except Exception as e_naive:
                    logger.error(f"Naive sort also failed for field '{field}': {e_naive}")
        else:
            logger.warning(f"Sort field '{field}' not found on Book objects or book list is empty. Returning unsorted list.")

        return books

    def close(self):
        """Closes the database connection and clears the cache."""
        self.db.close()
        self._cache = None
        self._dirty = True

######################################################################
#
#       LibraryManager
#
######################################################################
class LibraryManager:
    """Container for BookManager and TagsManager."""

    def __init__(self, library_root_path: str, db_path: str):
        self._library_root_path = library_root_path
        self._db_path = db_path
        self.__book_manager: Optional[BookManager] = None
        self.__tags_manager: Optional[TagsManager] = None

    @property
    def books(self) -> BookManager:
        """Access to the BookManager instance."""
        if self.__book_manager is None:
            # Ensure TagsManager is initialized first if needed by BookManager
            self.__book_manager = BookManager(
                library_root_path=self._library_root_path,
                db_path=self._db_path,
                tags_manager=self.tags # Pass the TagsManager instance
            )
        return self.__book_manager

    @property
    def tags(self) -> TagsManager:
        """Access to the TagsManager instance."""
        if self.__tags_manager is None:
            self.__tags_manager = TagsManager(db_path=self._db_path)
        return self.__tags_manager

    def close(self):
        """Closes all manager connections."""
        if self.__book_manager:
            self.__book_manager.close()
        if self.__tags_manager:
            self.__tags_manager.close()