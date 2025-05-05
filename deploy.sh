#!/bin/bash
set -e  # Exit on error

echo "========================================"
echo "Parseon Deployment Preparation"
echo "========================================"

# Make sure we're in the project root
cd "$(dirname "$0")"

echo "Preparing backend for deployment..."

# Make sure scripts are executable
chmod +x backend/prestart.sh
chmod +x backend/build.sh
[ -f backend/deploy_hooks.sh ] && chmod +x backend/deploy_hooks.sh

# Make sure railway.toml is using the right configuration
echo "Checking Railway configuration..."
if [ ! -f backend/railway.toml ]; then
  echo "ERROR: railway.toml not found in backend directory!"
  exit 1
fi

echo "Deployment configuration verified"

echo ""
echo "=== DEPLOYMENT OPTIONS ==="
echo ""
echo "Option 1: Deploy to Railway directly from GitHub"
echo "------------------------------------------------"
echo "1. Go to Railway dashboard and create a new project"
echo "2. Select 'Deploy from GitHub repo'"
echo "3. Connect your GitHub repository"
echo "4. Select the 'backend' directory as your source directory"
echo "5. Set environment variables:"
echo "   - OPENAI_API_KEY: Your OpenAI API key"
echo "   - SECRET_KEY: A secure random string for JWT"
echo "   - ENVIRONMENT: 'production'"
echo "   - BACKEND_CORS_ORIGINS: Include your Vercel frontend URL (comma-separated)"
echo "6. Add a PostgreSQL plugin to your Railway project"
echo ""
echo "Option 2: Deploy with Docker (locally or to any platform)"
echo "-------------------------------------------------------"
echo "1. Build the Docker image:"
echo "   docker build -t parseon-backend ./backend"
echo ""
echo "2. Run the container:"
echo "   docker run -p 8000:8000 -e OPENAI_API_KEY=your_key -e ENVIRONMENT=production parseon-backend"
echo ""
echo "Option 3: Manual deployment"
echo "-------------------------"
echo "1. Create and activate a Python virtual environment"
echo "2. cd backend"
echo "3. pip install -r requirements.txt"
echo "4. bash prestart.sh"
echo "5. uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "For all options, after deployment check the health endpoint:"
echo "http://localhost:8000/health (local) or https://your-project-name.railway.app/health (Railway)"
echo ""
echo "Preparation complete! You can now deploy using any of the options above." 