import React, { useState } from 'react';
import { BookTable } from './components/BookTable';
import { AddBookModal } from './components/AddBookModal';
import { mockBooks } from './data/mockBooks';
import { Book } from './types/Book';
import { Library, Github, Link } from 'lucide-react';

function App() {
  const [books, setBooks] = useState<Book[]>(mockBooks);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const handleToggleRead = (id: string) => {
    setBooks(books.map(book => 
      book.id === id ? { ...book, read: !book.read } : book
    ));
  };

  const handleAddBook = (bookData: Omit<Book, 'id'>) => {
    const newBook: Book = {
      ...bookData,
      id: Date.now().toString()
    };
    setBooks([newBook, ...books]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
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
                <span>Pronto per l'integrazione Python</span>
              </div>
              <a
                href="https://github.com"
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <BookTable
          books={books}
          onToggleRead={handleToggleRead}
          onAddBook={() => setIsAddModalOpen(true)}
        />
      </main>

      {/* Add Book Modal */}
      <AddBookModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAddBook={handleAddBook}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500">
            <p className="text-sm">
              Sistema di gestione biblioteca • Pronto per l'integrazione con le tue classi Python
            </p>
            <p className="text-xs mt-2">
              Aggiungi le tue API Python per sincronizzare automaticamente i dati
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;