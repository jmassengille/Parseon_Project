#!/bin/bash

# Start frontend
cd frontend && npm run dev &

# Start backend
cd backend && uvicorn main:app --reload --port 8000 &

# Wait for any process to exit
wait -n

# Kill all processes when one dies
pkill -P $$