// frontend/src/App.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { BookTable } from './components/BookTable';
import { AddBookModal } from './components/AddBookModal';
import { Book } from './types/Book';
import { Library, Github, Link } from 'lucide-react';

const API_URL = '/api'; // Backend API URL

function App() {
  const [books, setBooks] = useState<Book[]>([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBooks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/books`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({})); // Try to parse error, default to empty obj
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBooks(data.map((b: any) => ({
        ...b, // Spread all fields from backend response (id, title, author, tags, series, num_series, filename, description)
        dateAdded: b.added, // Map 'added' to 'dateAdded'
        read: b.is_read,     // Map 'is_read' to 'read'
        seriesNumber: b.num_series, // Map 'num_series' to 'seriesNumber'
      })));
    } catch (e: any) {
      setError(e.message || 'Failed to fetch books');
      console.error("Failed to fetch books:", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  const handleToggleRead = async (bookId: string) => {
    const book = books.find(b => b.id === bookId);
    if (!book) return;

    // Optimistic update
    const originalBooks = [...books];
    setBooks(books.map(b => b.id === bookId ? { ...b, read: !b.read } : b));

    try {
      const response = await fetch(`${API_URL}/books/${bookId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ read: !book.read }), // Send the new read state
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const returnedBook = await response.json();
      // Update with data from server to ensure consistency
      setBooks(originalBooks.map(b => // Use originalBooks to map over the state before optimistic update
        b.id === bookId ? {
            ...b, // Keep original fields not returned by this specific PUT or map them if they are
            id: returnedBook.id,
            title: returnedBook.title,
            author: returnedBook.author,
            tags: returnedBook.tags,
            series: returnedBook.series,
            seriesNumber: returnedBook.num_series,
            description: returnedBook.description,
            filename: returnedBook.filename,
            dateAdded: returnedBook.added,
            read: returnedBook.is_read,
        } : b
      ));
    } catch (e: any) {
      setError(e.message || 'Failed to update book');
      console.error("Failed to update book:", e);
      setBooks(originalBooks); // Revert on error
    }
  };

  const handleAddBook = async (bookData: Omit<Book, 'id' | 'dateAdded' | 'read'> & { dateAdded?: string, read?: boolean }) => {
    const newBookRequestData = {
      title: bookData.title,
      author: bookData.author,
      tags: bookData.tags || [],
      series: bookData.series,
      num_series: bookData.seriesNumber,
      description: bookData.description,
      filename: bookData.filename,
      read: bookData.read || false,
    };

    try {
      const response = await fetch(`${API_URL}/books`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newBookRequestData),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const addedBookFromApi = await response.json();

      const newBook: Book = {
        // Map all fields from the API response to the Book type
        id: addedBookFromApi.id,
        title: addedBookFromApi.title,
        author: addedBookFromApi.author,
        dateAdded: addedBookFromApi.added,
        tags: addedBookFromApi.tags || [],
        series: addedBookFromApi.series,
        seriesNumber: addedBookFromApi.num_series,
        description: addedBookFromApi.description,
        filename: addedBookFromApi.filename,
        read: addedBookFromApi.is_read,
        // rating is frontend only, so it won't be in addedBookFromApi
      };
      setBooks([newBook, ...books]); // Add to start of list
      setIsAddModalOpen(false);
    } catch (e: any) {
      setError(e.message || 'Failed to add book');
      console.error("Failed to add book:", e);
    }
  };

  const handleDeleteBook = async (bookId: string) => {
    const originalBooks = [...books];
    setBooks(books.filter(b => b.id !== bookId)); // Optimistic update

    try {
      const response = await fetch(`${API_URL}/books/${bookId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to delete book');
      console.error("Failed to delete book:", e);
      setBooks(originalBooks); // Revert on error
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-xl text-gray-500">Loading books...</p>
      </div>
    );
  }

  if (error && books.length === 0) {
    return (
      <div className="min-h-screen bg-red-50 flex flex-col items-center justify-center p-4">
        <h2 className="text-2xl font-bold text-red-700 mb-4">Error</h2>
        <p className="text-red-600 mb-2">{error}</p>
        <button
          onClick={() => { setError(null); fetchBooks(); }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

   const transientErrorDisplay = error && books.length > 0 ? (
    <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
      <p className="font-bold">Operation Failed</p>
      <p>{error}. Please try again. <button onClick={() => setError(null)} className="underline">Dismiss</button></p>
    </div>
  ) : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Library className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Biblioteca Personale</h1>
                <p className="text-sm text-gray-500">Gestione della tua collezione di libri</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 text-sm text-gray-500">
                <Link className="w-4 h-4" />
                <span>Connesso al Backend Python</span>
              </div>
              <a
                href="https://github.com/google/generative-ai-docs/tree/main/examples/walkthroughs/node/noop-code-agent" // Example Repo Link
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {transientErrorDisplay}
        <BookTable
          books={books}
          onToggleRead={handleToggleRead}
          onAddBook={() => setIsAddModalOpen(true)}
          onDeleteBook={handleDeleteBook}
        />
      </main>

      <AddBookModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAddBook={handleAddBook}
      />

      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500">
            <p className="text-sm">
              Sistema di gestione biblioteca • Connesso al backend Python
            </p>
            <p className="text-xs mt-2">
              I dati sono sincronizzati automaticamente con il database.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;