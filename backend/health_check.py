#!/usr/bin/env python3
"""
Railway Deployment Health Check Script for Parseon

This script performs various health checks to ensure the Parseon backend
is ready for deployment to Railway. It can be run directly before deployment
or as part of CI/CD pipeline.

Usage:
    python health_check.py [--host HOST] [--port PORT] [--retries NUM] [--timeout SECONDS] [--skip-health] [--check-openai]

Example:
    python health_check.py --host localhost --port 8000 --retries 5 --timeout 2
"""

import os
import sys
import time
import logging
import argparse
import importlib.util
from typing import Dict, List, Optional, Any
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Parseon Railway Deployment Health Check")
    parser.add_argument("--host", default="localhost", help="Host to check (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Port to check (default: 8000)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts (default: 3)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--wait", type=int, default=2, help="Wait time between retries in seconds (default: 2)")
    parser.add_argument("--check-openai", action="store_true", help="Test OpenAI API connectivity")
    parser.add_argument("--skip-health", action="store_true", help="Skip health endpoint check (useful during prestart)")
    return parser.parse_args()


def check_health_endpoint(base_url: str, retries: int = 3, timeout: int = 5, wait: int = 2) -> Dict[str, Any]:
    """Check the health endpoint of the API"""
    endpoint = f"{base_url}/health"
    
    for attempt in range(retries):
        try:
            logger.info(f"Checking health endpoint ({attempt+1}/{retries}): {endpoint}")
            response = requests.get(endpoint, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check passed: {data}")
                return {"status": "success", "data": data}
            else:
                logger.warning(f"Health check returned status code {response.status_code}: {response.text}")
        except RequestException as e:
            logger.warning(f"Health check attempt {attempt+1} failed: {str(e)}")
        
        if attempt < retries - 1:
            logger.info(f"Waiting {wait} seconds before next attempt...")
            time.sleep(wait)
    
    return {"status": "failed", "error": "Health check failed after multiple attempts"}


def check_railway_config() -> Dict[str, Any]:
    """Check that railway.toml exists and has required configurations"""
    try:
        railway_path = os.path.join(os.path.dirname(__file__), "railway.toml")
        
        if not os.path.exists(railway_path):
            return {"status": "failed", "error": "railway.toml file not found"}
        
        with open(railway_path, "r") as f:
            content = f.read()
        
        required_sections = ["[build]", "[deploy]", "[service]"]
        required_configs = ["healthcheckPath", "startCommand"]
        
        missing_sections = [s for s in required_sections if s not in content]
        missing_configs = [c for c in required_configs if c not in content]
        
        if missing_sections or missing_configs:
            return {
                "status": "failed", 
                "error": "Missing required configurations in railway.toml",
                "missing_sections": missing_sections,
                "missing_configs": missing_configs
            }
            
        return {"status": "success", "message": "Railway configuration is valid"}
    except Exception as e:
        return {"status": "failed", "error": f"Failed to check railway.toml: {str(e)}"}


def check_dependencies() -> Dict[str, Any]:
    """Check that all required dependencies are installed"""
    required_modules = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy", 
        "requests", "pytest", "openai"
    ]
    
    missing_modules = []
    installed_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            installed_modules.append(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        return {
            "status": "failed",
            "error": f"Missing required dependencies: {', '.join(missing_modules)}",
            "installed": installed_modules,
            "missing": missing_modules
        }
    
    return {
        "status": "success", 
        "message": "All required dependencies are installed",
        "installed": installed_modules
    }


def check_environment_variables() -> Dict[str, Any]:
    """Check that required environment variables are set"""
    required_vars = ["ENVIRONMENT"]
    # PORT is conditionally required - we'll check if it's passed via command line
    optional_vars = ["OPENAI_API_KEY", "DATABASE_URL", "NEXT_PUBLIC_API_URL", "PORT"]
    
    missing_required = [var for var in required_vars if os.getenv(var) is None]
    missing_optional = [var for var in optional_vars if os.getenv(var) is None]
    
    # Check for production configuration
    env = os.getenv("ENVIRONMENT", "").lower()
    mock_api = os.getenv("NEXT_PUBLIC_ENABLE_MOCK_API", "").lower()
    
    warnings = []
    if env == "production" and mock_api != "false":
        warnings.append("NEXT_PUBLIC_ENABLE_MOCK_API should be set to 'false' in production")
    
    # Add warning about PORT if missing but not as a failure condition
    if "PORT" in missing_optional and env == "production":
        warnings.append("PORT environment variable not set. This is required for Railway deployment but optional for this script.")
    
    if missing_required:
        return {
            "status": "failed",
            "error": f"Missing required environment variables: {', '.join(missing_required)}",
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "warnings": warnings
        }
    
    return {
        "status": "success",
        "message": "All required environment variables are set",
        "missing_optional": missing_optional,
        "warnings": warnings
    }


def check_prestart_script() -> Dict[str, Any]:
    """Check that prestart.sh exists and is executable"""
    prestart_path = os.path.join(os.path.dirname(__file__), "prestart.sh")
    
    if not os.path.exists(prestart_path):
        return {"status": "failed", "error": "prestart.sh file not found"}
    
    is_executable = os.access(prestart_path, os.X_OK)
    if not is_executable:
        try:
            os.chmod(prestart_path, 0o755)
            return {
                "status": "success", 
                "message": "prestart.sh exists and is now executable (fixed permissions)"
            }
        except Exception as e:
            return {
                "status": "warning",
                "error": f"prestart.sh exists but is not executable: {str(e)}"
            }
    
    return {"status": "success", "message": "prestart.sh exists and is executable"}


def check_openai_api() -> Dict[str, Any]:
    """Test connection to OpenAI API if credentials are available"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"status": "skipped", "message": "OPENAI_API_KEY not set, skipping check"}
    
    try:
        import openai
        # Check which version of OpenAI we're using
        if hasattr(openai, "__version__"):
            version = openai.__version__
            
            # For OpenAI v1.0.0+
            if version.startswith(("1.", "2.")):
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt="Hello, this is a test from Parseon.",
                    max_tokens=5
                )
            # For older versions
            else:
                openai.api_key = api_key
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt="Hello, this is a test from Parseon.",
                    max_tokens=5
                )
                
            return {
                "status": "success", 
                "message": f"OpenAI API connection successful (SDK version: {version})"
            }
        else:
            return {"status": "warning", "message": "Could not determine OpenAI SDK version"}
    except ImportError:
        return {"status": "failed", "error": "OpenAI module not installed"}
    except Exception as e:
        return {"status": "failed", "error": f"OpenAI API connection failed: {str(e)}"}


def main():
    """Main function to run all health checks"""
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    logger.info("=" * 60)
    logger.info("PARSEON RAILWAY DEPLOYMENT HEALTH CHECK")
    logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Checking API at: {base_url}")
    logger.info("=" * 60)
    
    # Run all checks
    checks = {
        "dependencies": check_dependencies(),
        "environment_variables": check_environment_variables(),
        "railway_config": check_railway_config(),
        "prestart_script": check_prestart_script(),
    }
    
    # Check API health if available and not skipped
    if not args.skip_health:
        checks["health_endpoint"] = check_health_endpoint(
            base_url, 
            retries=args.retries, 
            timeout=args.timeout,
            wait=args.wait
        )
    else:
        logger.info("Skipping health endpoint check as requested")
        checks["health_endpoint"] = {"status": "skipped", "message": "Health endpoint check skipped"}
    
    # Check OpenAI API connectivity if requested
    if args.check_openai:
        checks["openai_api"] = check_openai_api()
    
    # Process results
    failed_checks = [name for name, result in checks.items() if result.get("status") == "failed"]
    warning_checks = [name for name, result in checks.items() if result.get("status") == "warning"]
    successful_checks = [name for name, result in checks.items() if result.get("status") == "success"]
    skipped_checks = [name for name, result in checks.items() if result.get("status") == "skipped"]
    
    # Print results
    logger.info("\nCHECK RESULTS:")
    logger.info("=" * 60)
    
    for name, result in checks.items():
        status = result.get("status", "unknown")
        icon = {
            "success": "✅",
            "failed": "❌",
            "warning": "⚠️",
            "skipped": "⏭️",
            "unknown": "❓"
        }.get(status, "❓")
        
        message = result.get("message") or result.get("error") or "No details available"
        logger.info(f"{icon} {name}: {status.upper()} - {message}")
    
    # Summary
    logger.info("\nSUMMARY:")
    logger.info("=" * 60)
    logger.info(f"✅ Passed: {len(successful_checks)}")
    logger.info(f"⚠️ Warnings: {len(warning_checks)}")
    logger.info(f"❌ Failed: {len(failed_checks)}")
    logger.info(f"⏭️ Skipped: {len(skipped_checks)}")
    
    if failed_checks:
        logger.error("\nDEPLOYMENT BLOCKER: The following checks failed:")
        for check in failed_checks:
            logger.error(f"❌ {check}: {checks[check].get('error', 'Unknown error')}")
        logger.info("\n❌ RESULT: NOT READY FOR DEPLOYMENT TO RAILWAY")
        return 1
    elif warning_checks:
        logger.warning("\nDEPLOYMENT WARNINGS: The following checks have warnings:")
        for check in warning_checks:
            logger.warning(f"⚠️ {check}: {checks[check].get('message', 'No details')}")
        logger.info("\n⚠️ RESULT: READY FOR DEPLOYMENT WITH WARNINGS")
        return 0
    else:
        logger.info("\n✅ RESULT: READY FOR DEPLOYMENT TO RAILWAY")
        return 0


if __name__ == "__main__":
    sys.exit(main()) 