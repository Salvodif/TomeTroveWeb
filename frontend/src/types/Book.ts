export interface Book {
  id: string;
  title: string;
  author: string;
  dateAdded: string;
  tags: string[];
  series?: string;
  seriesNumber?: number;
  read: boolean;
  rating?: number;
  notes?: string;
}