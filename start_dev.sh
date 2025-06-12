#!/bin/bash

# Check if concurrently is installed
if ! command -v concurrently &> /dev/null
then
    echo "concurrently could not be found. Please install it globally:"
    echo "npm install -g concurrently"
    echo "or"
    echo "yarn global add concurrently"
    echo "Alternatively, install it as a dev dependency in your project's root: npm install --save-dev concurrently"
    echo "If installed as a dev dependency, you might need to run this script using 'npx ./start_dev.sh' or adjust the 'concurrently' command to 'npx concurrently'"
    exit
fi

echo "Starting backend and frontend concurrently..."

concurrently \
  "cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt && ./venv/bin/python app.py" \
  "cd frontend && (if [ ! -d 'node_modules' ]; then npm install; fi) && npm run dev"
