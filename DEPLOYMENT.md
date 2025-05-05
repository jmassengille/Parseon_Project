# Parseon Deployment Guide

This guide outlines the steps required to deploy Parseon to production environments using Vercel (frontend) and Railway (backend).

## Prerequisites

- A Vercel account
- A Railway account
- An OpenAI API key

## Frontend Deployment (Vercel)

1. **Prepare your repository**
   - Ensure your codebase is in a Git repository (GitHub, GitLab, or Bitbucket)
   - Make sure the frontend's `package.json` and `vercel.json` are correctly configured

2. **Set up environment variables in Vercel**
   - `NEXT_PUBLIC_API_URL`: The URL of your Railway backend (e.g., https://parseon-backend.railway.app)
   - `NEXT_PUBLIC_ENABLE_MOCK_API`: Set to "false" for production, or "true" for testing without a backend
   - `NEXT_PUBLIC_ENABLE_TEST_MODE`: Set to "false" for production

3. **Deploy to Vercel**
   - Connect your Git repository to Vercel
   - Configure the build settings:
     - Framework preset: Next.js
     - Root directory: frontend/
     - Build command: npm run build
     - Output directory: .next
   - Deploy!

## Backend Deployment (Railway)

1. **Prepare your backend code**
   - Ensure your `railway.toml` is correctly configured with:
     ```toml
     [build]
     builder = "nixpacks"
     buildCommand = "pip install -r requirements.txt && chmod +x prestart.sh"

     [deploy]
     startCommand = "bash -c './prestart.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT'"
     healthcheckPath = "/health"
     healthcheckTimeout = 120
     restartPolicyType = "on_failure"
     restartPolicyMaxRetries = 5
     ```
   - Make sure both `app/main.py` and `main.py` have working health check endpoints

2. **Set up environment variables in Railway**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: A secure secret key for JWT tokens
   - `ENVIRONMENT`: Set to "production"
   - `BACKEND_CORS_ORIGINS`: Include your Vercel frontend URL (e.g., https://parseon.vercel.app)

3. **Deploy to Railway**
   - Connect your Git repository to Railway
   - Choose the PostgreSQL plugin to add a database
   - Set up the service to use the backend directory
   - If you encounter health check issues, check the "Troubleshooting" section below

## Database Setup for Railway

When deploying to Railway with PostgreSQL, Railway will automatically:
- Provision a PostgreSQL database
- Set the `DATABASE_URL` environment variable

No manual database setup is required, but you may need to run migrations. You can do this by:
1. Adding a "MIGRATE" environment variable with value "true"
2. The prestart.sh script will handle running migrations when this variable is set

## Post-Deployment Verification

1. **Check health endpoints**
   - Verify the backend is healthy by visiting: `https://your-backend.railway.app/health`
   - Expected response: `{"status":"healthy", ...}`

2. **Test the frontend-backend connection**
   - Navigate to your Vercel-deployed frontend
   - Fill out the assessment form and submit
   - Verify that the backend processes the request correctly

## Troubleshooting

1. **CORS Issues**
   - Ensure `BACKEND_CORS_ORIGINS` includes your frontend URL
   - Check that your frontend is using the correct backend URL

2. **Railway Health Check Failures**
   - If the health check is failing with "service unavailable" errors:
     - Check that both entry points (`main.py` and `app/main.py`) have `/health` endpoints
     - Verify the app is starting correctly by checking logs
     - Make sure the app is binding to the correct port (the `$PORT` environment variable set by Railway)
     - Try deploying with both `uvicorn app.main:app` and `uvicorn main:app` as start commands
     - Check if there are any errors in the startup logs
     - Ensure all required dependencies are in requirements.txt
     - Try increasing the healthcheck timeout in railway.toml

3. **Database Connection Issues**
   - Ensure Railway has set the `DATABASE_URL` environment variable
   - The prestart.sh script will wait for the database to be available
   - Check logs for connection errors

4. **Mock Data Fallback**
   - The frontend is designed to fallback to mock data if the backend is unavailable
   - Set `NEXT_PUBLIC_ENABLE_MOCK_API` to "false" when you want to require a working backend

5. **Entry Point Issues**
   - Railway may have different conventions for where to look for the app entry point
   - We've included both `main.py` and `app/main.py` as options
   - Check the logs to see which one is being used

## Maintenance

- Regularly update the OpenAI API key for security
- Monitor your Railway database for load and performance
- Consider periodic database backups 