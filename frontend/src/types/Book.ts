export interface Book {
  id: string;
  title: string;
  author: string;
  dateAdded: string; // Corresponds to 'added' in backend (ISO string from book_to_dict)
  tags: string[];
  series?: string;
  seriesNumber?: number; // Corresponds to 'num_series' in backend
  rating?: number; // This field is frontend-specific, backend doesn't have it
  read: boolean; // Corresponds to 'is_read' from backend (boolean from book_to_dict)
  filename?: string;
  description?: string;
}