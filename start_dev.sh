#!/bin/bash

# Check if concurrently is installed
if ! command -v concurrently &> /dev/null
then
    echo "concurrently could not be found. Please install it globally:"
    echo "npm install -g concurrently"
    echo "or"
    echo "yarn global add concurrently"
    exit
fi

echo "Starting backend and frontend concurrently..."

concurrently \
  "cd backend && (if [ ! -d 'venv' ]; then python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt; else source venv/bin/activate; fi) && python app.py" \
  "cd frontend && (if [ ! -d 'node_modules' ]; then npm install; fi) && npm run dev"
