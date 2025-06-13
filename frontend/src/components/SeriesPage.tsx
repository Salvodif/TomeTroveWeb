import React, { useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Book } from '../types/Book';
import { CheckCircle, Circle, ArrowLeft, BookOpen, Calendar, Star } from 'lucide-react';

interface SeriesPageProps {
  books: Book[];
  onToggleRead: (id: string) => void;
}

export const SeriesPage: React.FC<SeriesPageProps> = ({ books, onToggleRead }) => {
  const { seriesName } = useParams<{ seriesName: string }>();
  
  const seriesBooks = useMemo(() => {
    if (!seriesName) return [];
    
    const decodedSeriesName = decodeURIComponent(seriesName);
    return books
      .filter(book => book.series === decodedSeriesName)
      .sort((a, b) => {
        if (a.seriesNumber && b.seriesNumber) {
          return a.seriesNumber - b.seriesNumber;
        }
        if (a.seriesNumber) return -1;
        if (b.seriesNumber) return 1;
        return a.title.localeCompare(b.title);
      });
  }, [books, seriesName]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT');
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
    const hash = tag.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  const readBooks = seriesBooks.filter(book => book.read).length;
  const totalBooks = seriesBooks.length;
  const averageRating = seriesBooks
    .filter(book => book.rating)
    .reduce((sum, book) => sum + (book.rating || 0), 0) / 
    seriesBooks.filter(book => book.rating).length;

  if (!seriesName) {
    return <div>Serie non trovata</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/"
          className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Torna alla biblioteca
        </Link>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {decodeURIComponent(seriesName)}
            </h1>
            <p className="text-gray-600">
              Serie completa con {totalBooks} {totalBooks === 1 ? 'libro' : 'libri'}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">
              {readBooks}/{totalBooks}
            </div>
            <div className="text-sm text-gray-500">Libri letti</div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-blue-600" />
              <div>
                <div className="text-lg font-semibold text-gray-900">{totalBooks}</div>
                <div className="text-sm text-gray-500">Libri Totali</div>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <div>
                <div className="text-lg font-semibold text-gray-900">{readBooks}</div>
                <div className="text-sm text-gray-500">Libri Letti</div>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center gap-3">
              <Star className="w-6 h-6 text-yellow-600" />
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  {averageRating ? averageRating.toFixed(1) : 'N/A'}
                </div>
                <div className="text-sm text-gray-500">Valutazione Media</div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progresso di lettura</span>
            <span>{Math.round((readBooks / totalBooks) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(readBooks / totalBooks) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Books List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Libri della Serie</h2>
        </div>
        
        <div className="divide-y divide-gray-200">
          {seriesBooks.map((book) => (
            <div key={book.id} className="p-6 hover:bg-gray-50 transition-colors duration-150">
              <div className="flex items-start gap-4">
                <button
                  onClick={() => onToggleRead(book.id)}
                  className="mt-1 transition-transform duration-200 hover:scale-110"
                >
                  {book.read ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : (
                    <Circle className="w-6 h-6 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {book.seriesNumber && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Libro #{book.seriesNumber}
                          </span>
                        )}
                        <h3 className="text-lg font-semibold text-gray-900">{book.title}</h3>
                      </div>
                      
                      <p className="text-gray-600 mb-2">di {book.author}</p>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {formatDate(book.dateAdded)}
                        </div>
                        {book.rating && (
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 text-yellow-500" />
                            <span>{'★'.repeat(book.rating)}{'☆'.repeat(5 - book.rating)}</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-wrap gap-1">
                        {book.tags.map((tag) => (
                          <span
                            key={tag}
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTagColor(tag)}`}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                      
                      {book.notes && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-700">{book.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {seriesBooks.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Nessun libro trovato per questa serie</p>
          </div>
        )}
      </div>
    </div>
  );
};