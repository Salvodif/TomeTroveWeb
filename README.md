# TomeTroveWeb

## Simplified Development Setup

This project includes a convenience script `start_dev.sh` to simplify the development setup process by starting both the backend and frontend servers concurrently.

### Purpose

The `start_dev.sh` script automates the following:
- Starting the Python backend server.
- Starting the Node.js frontend development server.
- Creation of Python virtual environment and installation of backend dependencies if not already set up.
- Installation of frontend Node modules if not already set up.

### Prerequisites

Before running the script, ensure you have the following installed:
- Python 3 (python3)
- Node.js
- npm (usually comes with Node.js) or yarn
- `concurrently`: This is a Node.js package used to run multiple commands concurrently. If `concurrently` is not installed globally, the script will detect this and provide instructions on how to install it (e.g., `npm install -g concurrently` or `yarn global add concurrently`).

### How to Run

1. Open your terminal.
2. Navigate to the root directory of the project.
3. Make the script executable (if you haven't already):
   ```bash
   chmod +x start_dev.sh
   ```
4. Run the script:
   ```bash
   ./start_dev.sh
   ```
This will start both the backend and frontend development servers. You should see output from both servers in your terminal.