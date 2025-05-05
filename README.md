# Parseon - AI Security Assessment Tool

Parseon is an AI security assessment tool focused on detecting and preventing security vulnerabilities in AI-integrated applications. It uses a sophisticated analysis approach that combines advanced LLM analysis with embedding-based validation against known AI security patterns and vulnerabilities.

## Features

- **Dynamic AI Security Analysis**: Analyzes AI components, prompts, and model interactions
- **AI-Specific Security Patterns**: Detects prompt injection, model security boundary issues, and more
- **Automated Security Validation**: Validates findings against known security patterns
- **Comprehensive Security Scoring**: Provides detailed security scores across multiple categories

## Architecture

The project consists of two main components:

1. **Frontend**: Next.js application with a modern UI for submitting assessments and viewing results
2. **Backend**: FastAPI service that performs the security analysis using AI models

## Deployment

### Frontend (Vercel)

The frontend is configured for deployment on Vercel:

```bash
cd frontend
npm install
npm run build
```

### Backend (Railway)

The backend is configured for deployment on Railway:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Railway configuration is provided in `railway.toml`.

## Environment Setup

- Project runs in WSL (Windows Subsystem for Linux)
- Python environment: Use `python3` command instead of `python`
- Virtual Environment: Activate with `source ~/projects/parseon_env/bin/activate`
- Dependencies: All required packages listed in backend/requirements.txt

## Common Commands

- Activate environment: `source ~/projects/parseon_env/bin/activate`
- Run tests: `python3 -m pytest tests/`
- Install dependencies: `pip3 install -r backend/requirements.txt`

Note: Always activate the parseon environment with `source ~/projects/parseon_env/bin/activate` before running any commands.

## License

This project is for portfolio demonstration purposes. 