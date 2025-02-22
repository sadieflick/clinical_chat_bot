#!/bin/bash

cd src

# Check if json_vector_db directory exists
if [ -d "../json_vector_db" ]; then
    echo "Found json vector db folder!"
    python3 run.py

else
    echo "Didn't find json vector db folder"
    echo "Creating json vectordb"
    python3 run.py --populate
fi

# Start uvicorn server for running fastAPI and Chainlit
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# start FastAPI / mount chainlit
python3 main.py
