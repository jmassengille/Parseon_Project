#!/bin/bash
# Railway Deployment Readiness Check Script for Parseon
# This script performs a full health check of the application
# and ensures it's ready for deployment to Railway.
#
# Usage:
#   ./check_deployment_readiness.sh [--check-openai] [--host localhost] [--port 8000]

set -e  # Exit on error

# Default values
HOST="localhost"
PORT_VALUE="8000"  # Renamed to avoid conflict with env var
CHECK_OPENAI=""
RETRIES="3"
TIMEOUT="5"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --check-openai)
      CHECK_OPENAI="--check-openai"
      shift
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT_VALUE="$2"
      shift 2
      ;;
    --retries)
      RETRIES="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set environment variables if not already set
if [ -z "$ENVIRONMENT" ]; then
  export ENVIRONMENT="production"
  echo "Setting ENVIRONMENT=production"
fi

if [ -z "$PORT" ]; then
  export PORT=$PORT_VALUE
  echo "Setting PORT=$PORT_VALUE"
fi

echo "=================================================="
echo "PARSEON RAILWAY DEPLOYMENT READINESS CHECK"
echo "Checking application health and configuration..."
echo "=================================================="

# Check if the server is running
SERVER_RUNNING=false
if curl -s "http://${HOST}:${PORT_VALUE}/health" > /dev/null 2>&1; then
  echo "✅ Server is running at http://${HOST}:${PORT_VALUE}"
  SERVER_RUNNING=true
else
  echo "❌ Server is not running at http://${HOST}:${PORT_VALUE}"
  echo "Please start the server first with:"
  echo "  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT_VALUE"
  echo ""
  echo "To continue with other checks without checking the API, use:"
  echo "  python health_check.py --skip-health"
  exit 1
fi

# Run the health check with all checks enabled
echo "Running full health check..."
python health_check.py --host "$HOST" --port "$PORT_VALUE" --retries "$RETRIES" --timeout "$TIMEOUT" $CHECK_OPENAI

# Script exit code will be based on the health check exit code 