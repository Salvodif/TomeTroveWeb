import { Book } from '../types/Book';

export const mockBooks: Book[] = [
  {
    id: '1',
    title: 'Il Nome della Rosa',
    author: 'Umberto Eco',
    dateAdded: '2024-01-15',
    tags: ['Mistero', 'Storico', 'Filosofia'],
    series: undefined,
    read: true,
    rating: 5,
    notes: 'Capolavoro assoluto'
  },
  {
    id: '2',
    title: 'Fondazione',
    author: 'Isaac Asimov',
    dateAdded: '2024-02-03',
    tags: ['Fantascienza', 'Serie'],
    series: 'Ciclo delle Fondazioni',
    seriesNumber: 1,
    read: true,
    rating: 5
  },
  {
    id: '3',
    title: 'Fondazione e Impero',
    author: 'Isaac Asimov',
    dateAdded: '2024-02-10',
    tags: ['Fantascienza', 'Serie'],
    series: 'Ciclo delle Fondazioni',
    seriesNumber: 2,
    read: false
  },
  {
    id: '4',
    title: 'Cent\'anni di solitudine',
    author: 'Gabriel García Márquez',
    dateAdded: '2024-01-28',
    tags: ['Realismo Magico', 'Classico'],
    series: undefined,
    read: true,
    rating: 4
  },
  {
    id: '5',
    title: 'Il Trono di Spade',
    author: 'George R.R. Martin',
    dateAdded: '2024-03-05',
    tags: ['Fantasy', 'Epico', 'Serie'],
    series: 'Cronache del Ghiaccio e del Fuoco',
    seriesNumber: 1,
    read: false
  },
  {
    id: '6',
    title: 'Neuromante',
    author: 'William Gibson',
    dateAdded: '2024-02-20',
    tags: ['Cyberpunk', 'Fantascienza'],
    series: undefined,
    read: true,
    rating: 4
  },
  {
    id: '7',
    title: 'L\'Eleganza del Riccio',
    author: 'Muriel Barbery',
    dateAdded: '2024-01-10',
    tags: ['Drammatico', 'Filosofia'],
    series: undefined,
    read: false
  },
  {
    id: '8',
    title: 'Dune',
    author: 'Frank Herbert',
    dateAdded: '2024-02-28',
    tags: ['Fantascienza', 'Epico', 'Serie'],
    series: 'Ciclo di Dune',
    seriesNumber: 1,
    read: true,
    rating: 5
  }
];