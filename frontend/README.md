# TomeTrove Frontend

This is the frontend for the TomeTrove personal library management application. It's built with React, TypeScript, Vite, and Tailwind CSS.

## Features

*   Displays a list of books from the backend.
*   Allows adding, deleting, and updating the read status of books.
*   Search and sort functionality for the book list.
*   User-friendly interface for managing a personal book collection.
*   Communicates with the TomeTrove backend for data persistence.

## Project Structure

```
frontend/
├── index.html            # Entry point for the application
├── package.json          # Project dependencies and scripts
├── vite.config.ts        # Vite configuration (including dev server proxy)
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
├── tsconfig.json         # TypeScript configuration
└── src/
    ├── App.tsx             # Main application component, state management
    ├── main.tsx            # Renders the React application
    ├── index.css           # Global styles (Tailwind base, etc.)
    ├── components/         # Reusable UI components
    │   ├── AddBookModal.tsx  # Modal for adding new books
    │   └── BookTable.tsx     # Table for displaying books
    ├── types/
    │   └── Book.ts         # TypeScript interface for Book objects
    └── vite-env.d.ts       # Vite environment types
```

## Setup and Running

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    # or
    # yarn install
    ```

3.  **Backend Connection:**
    This frontend application expects the TomeTrove backend server to be running. By default, it assumes the backend is available at `http://localhost:5001`.
    The Vite development server is configured to proxy requests from `/api` to `http://localhost:5001/api`. Ensure the backend is running before starting the frontend.

4.  **Run the Vite development server:**
    ```bash
    npm run dev
    # or
    # yarn dev
    ```
    The application will typically start on `http://localhost:3000` (or another port if 3000 is busy, as specified in `vite.config.ts` or by Vite).

## Building for Production

To create a production build:

```bash
npm run build
# or
# yarn build
```
The production-ready static assets will be placed in the `dist/` directory.

## Key Dependencies

*   React
*   TypeScript
*   Vite
*   Tailwind CSS
*   Lucide React (for icons)

## Development Notes

*   **API Proxy:** The Vite development server (`vite.config.ts`) is configured to proxy API requests from the frontend's `/api` path to the backend server (defaulting to `http://localhost:5001`). This means frontend code can make requests to `/api/books` instead of `http://localhost:5001/api/books`.
*   **Styling:** Tailwind CSS is used for styling. Utility classes are preferred. Global styles are in `src/index.css`.
*   **Linting and Formatting:** ESLint is configured for linting. Consider adding Prettier for code formatting if not already integrated.
```
