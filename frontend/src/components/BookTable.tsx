// frontend/src/components/BookTable.tsx

// Ensure Lucide icons are imported
import React, { useState, useMemo } from 'react';
import { Book } from '../types/Book';
// Make sure Trash2 is imported
import { CheckCircle, Circle, Search, Plus, BookOpen, Tag, Calendar, Trash2 } from 'lucide-react';


interface BookTableProps {
  books: Book[];
  onToggleRead: (id: string) => void;
  onAddBook: () => void;
  onDeleteBook: (id: string) => void; // Added this prop
}

export const BookTable: React.FC<BookTableProps> = ({ books, onToggleRead, onAddBook, onDeleteBook }) => {
  const [searchTerm, setSearchTerm] = useState('');
  // Ensure sortBy can handle all relevant Book keys, especially if new ones are added or names change.
  // For now, 'dateAdded', 'title', 'author', 'read', 'series' are primary.
  const [sortBy, setSortBy] = useState<keyof Book | 'actions'>('dateAdded');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const filteredAndSortedBooks = useMemo(() => {
    let filtered = books.filter(book =>
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (book.tags && book.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))) || // check if tags exist
      (book.series && book.series.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    if (sortBy !== 'actions') { // Prevent sorting by 'actions' column
        return filtered.sort((a, b) => {
        let aValue = a[sortBy as keyof Book]; // Type assertion
        let bValue = b[sortBy as keyof Book]; // Type assertion

        if (sortBy === 'dateAdded') {
            aValue = new Date(aValue as string).getTime();
            bValue = new Date(bValue as string).getTime();
        } else if (typeof aValue === 'string' && typeof bValue === 'string') {
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
        } else if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
            // no change needed for boolean
        }


        if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
        return 0;
        });
    }
    return filtered; // Return unsorted if sortBy is 'actions' or an invalid key
  }, [books, searchTerm, sortBy, sortOrder]);

  const handleSort = (column: keyof Book | 'actions') => { // Allow 'actions' but don't sort by it
    if (column === 'actions') return; // Do nothing if actions column header is clicked

    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column as keyof Book); // Ensure it's a valid Book key
      setSortOrder('asc');
    }
  };

  const formatDate = (dateString: string) => {
    try {
        return new Date(dateString).toLocaleDateString('it-IT');
    } catch (e) {
        return "Invalid date";
    }
  };

  const getTagColor = (tag: string) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-green-100 text-green-800',
      'bg-purple-100 text-purple-800',
      'bg-orange-100 text-orange-800',
      'bg-pink-100 text-pink-800',
      'bg-indigo-100 text-indigo-800'
    ];
    if (!tag) return colors[0];
    const hash = tag.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  return (
    <div className="space-y-6">
      {/* Header with search and add button - unchanged */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Cerca per titolo, autore, tag o serie..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          />
        </div>
        <button
          onClick={onAddBook}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 font-medium"
        >
          <Plus className="w-4 h-4" />
          Aggiungi Libro
        </button>
      </div>

      {/* Stats - unchanged */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <div>
              <div className="text-2xl font-bold text-gray-900">{books.length}</div>
              <div className="text-sm text-gray-500">Libri Totali</div>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div>
              <div className="text-2xl font-bold text-gray-900">{books.filter(b => b.read).length}</div>
              <div className="text-sm text-gray-500">Libri Letti</div>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <Circle className="w-8 h-8 text-orange-600" />
            <div>
              <div className="text-2xl font-bold text-gray-900">{books.filter(b => !b.read).length}</div>
              <div className="text-sm text-gray-500">Da Leggere</div>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left">
                  <button
                    onClick={() => handleSort('read')}
                    className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
                  >
                    Stato
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button
                    onClick={() => handleSort('title')}
                    className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
                  >
                    Titolo
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button
                    onClick={() => handleSort('author')}
                    className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
                  >
                    Autore
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button
                    onClick={() => handleSort('dateAdded')}
                    className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
                  >
                    <Calendar className="w-3 h-3" />
                    Data Aggiunta
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <Tag className="w-3 h-3" />
                    Tags
                  </span>
                </th>
                <th className="px-6 py-4 text-left">
                  <button
                    onClick={() => handleSort('series')}
                    className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
                  >
                    Serie
                  </button>
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Azioni
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredAndSortedBooks.map((book) => (
                <tr key={book.id} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-6 py-4">
                    <button
                      onClick={() => onToggleRead(book.id)}
                      className="transition-transform duration-200 hover:scale-110"
                    >
                      {book.read ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-400 hover:text-gray-600" />
                      )}
                    </button>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{book.title}</div>
                    {book.rating !== undefined && book.rating > 0 && ( // Check if rating exists and is positive
                      <div className="text-sm text-gray-500 mt-1">
                        {'★'.repeat(book.rating)}{'☆'.repeat(5 - book.rating)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{book.author}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(book.dateAdded)}</td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {book.tags && book.tags.map((tag) => ( // check if tags exist
                        <span
                          key={tag}
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTagColor(tag)}`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {book.series && (
                      <div>
                        <div className="font-medium">{book.series}</div>
                        {book.seriesNumber !== undefined && ( // check if seriesNumber exists
                          <div className="text-xs text-gray-500">Libro #{book.seriesNumber}</div>
                        )}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => onDeleteBook(book.id)}
                      className="text-red-500 hover:text-red-700 transition-colors p-1"
                      aria-label={`Delete ${book.title}`}
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredAndSortedBooks.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Nessun libro trovato</p>
            <p className="text-gray-400 text-sm">Prova a modificare i termini di ricerca o aggiungi un nuovo libro.</p>
          </div>
        )}
      </div>
    </div>
  );
};