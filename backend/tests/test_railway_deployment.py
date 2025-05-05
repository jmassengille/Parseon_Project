import pytest
import os
import sys
import logging
import requests
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
import importlib.util
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure we can import from the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialize variables
app = None
client = None


def setup_module():
    """Setup for the entire test module"""
    global app, client
    
    try:
        # Import the application
        from main import app as main_app
        app = main_app
        client = TestClient(app)
        logger.info("Successfully imported app from main.py")
    except ImportError:
        logger.warning("Could not import from main.py, trying app.main")
        try:
            from app.main import app as app_main
            app = app_main
            client = TestClient(app)
            logger.info("Successfully imported app from app.main")
        except ImportError:
            logger.error("Failed to import the FastAPI app")
            pytest.fail("Could not import the FastAPI application")


class TestRailwayDeployment:
    """Tests to verify the application is ready for Railway deployment"""

    def test_health_endpoint(self):
        """Test the health endpoint responds correctly"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        
        logger.info(f"Health check passed: {data}")

    def test_root_endpoint(self):
        """Test the root endpoint responds correctly"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
        
        logger.info(f"Root endpoint check passed: {data}")

    def test_docs_accessibility(self):
        """Test that the API docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        logger.info("API docs are accessible")

    def test_openapi_schema(self):
        """Test that the OpenAPI schema is accessible"""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "paths" in data
        assert "components" in data
        
        logger.info("OpenAPI schema is accessible")

    def test_cors_headers(self):
        """Test that CORS headers are properly set"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
        
        response = client.options("/health", headers=headers)
        assert response.status_code == 200
        
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
        
        logger.info("CORS headers are properly configured")

    def test_environment_variables(self):
        """Test critical environment variables are set"""
        # Check for required environment variables
        required_vars = ["ENVIRONMENT", "PORT"]
        optional_vars = ["OPENAI_API_KEY", "DATABASE_URL", "NEXT_PUBLIC_API_URL"]
        
        for var in required_vars:
            assert os.getenv(var) is not None, f"Required environment variable {var} is not set"
        
        for var in optional_vars:
            if os.getenv(var) is None:
                logger.warning(f"Optional environment variable {var} is not set")
        
        # Check if we're in production mode
        env = os.getenv("ENVIRONMENT", "")
        if env.lower() == "production":
            logger.info("Running in production mode")
            assert os.getenv("NEXT_PUBLIC_ENABLE_MOCK_API", "").lower() == "false", \
                "NEXT_PUBLIC_ENABLE_MOCK_API should be set to 'false' in production"
        
        logger.info("Environment variables check passed")

    def test_railway_configuration(self):
        """Test that the Railway configuration file exists and has required fields"""
        railway_toml_path = os.path.join(os.path.dirname(__file__), "..", "railway.toml")
        assert os.path.exists(railway_toml_path), "railway.toml file not found"
        
        # Check if railway.toml has basic content (we don't parse it, just check existence)
        with open(railway_toml_path, "r") as f:
            content = f.read()
            
        assert "[build]" in content, "railway.toml is missing [build] section"
        assert "[deploy]" in content, "railway.toml is missing [deploy] section"
        assert "healthcheckPath" in content, "railway.toml is missing healthcheckPath"
        
        logger.info("Railway configuration file check passed")

    def test_dependencies_installed(self):
        """Test that all required dependencies are installed"""
        required_modules = [
            "fastapi", "uvicorn", "pydantic", "requests", 
            "sqlalchemy", "pytest", "openai"
        ]
        
        for module in required_modules:
            try:
                importlib.import_module(module)
                logger.info(f"Module {module} is installed")
            except ImportError:
                logger.error(f"Required module {module} is not installed")
                pytest.fail(f"Required module {module} is not installed")
        
        logger.info("All required dependencies are installed")

    def test_prestart_script(self):
        """Test that the prestart script exists and is executable"""
        prestart_path = os.path.join(os.path.dirname(__file__), "..", "prestart.sh")
        assert os.path.exists(prestart_path), "prestart.sh file not found"
        
        # Check if the script is executable
        is_executable = os.access(prestart_path, os.X_OK)
        if not is_executable:
            logger.warning("prestart.sh is not executable - this will cause issues on deployment")
            logger.info("Setting prestart.sh as executable")
            os.chmod(prestart_path, 0o755)
        
        logger.info("Prestart script check passed")

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_openai_connectivity(self):
        """Test OpenAI API connectivity if credentials are available"""
        try:
            import openai
            # Check which version of OpenAI we're using
            if hasattr(openai, "__version__"):
                version = openai.__version__
                logger.info(f"Using OpenAI SDK version: {version}")
                
                # For OpenAI v1.0.0+
                if version.startswith(("1.", "2.")):
                    from openai import OpenAI
                    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    response = client.completions.create(
                        model="gpt-3.5-turbo-instruct",
                        prompt="Hello, this is a test from Parseon.",
                        max_tokens=5
                    )
                # For older versions
                else:
                    openai.api_key = os.getenv("OPENAI_API_KEY")
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt="Hello, this is a test from Parseon.",
                        max_tokens=5
                    )
                    
                logger.info("OpenAI API connection successful")
            else:
                logger.warning("Could not determine OpenAI SDK version")
        except Exception as e:
            logger.error(f"OpenAI API connection failed: {str(e)}")
            pytest.fail(f"OpenAI API connection failed: {str(e)}")


if __name__ == "__main__":
    # If run directly, execute the tests
    setup_module()
    test_instance = TestRailwayDeployment()
    
    # Run all tests and collect results
    test_methods = [m for m in dir(TestRailwayDeployment) if m.startswith('test_')]
    results = {"passed": [], "failed": []}
    
    for method in test_methods:
        test_name = method
        try:
            logger.info(f"Running test: {test_name}")
            getattr(test_instance, method)()
            results["passed"].append(test_name)
            logger.info(f"✅ {test_name} - PASSED")
        except Exception as e:
            results["failed"].append({"name": test_name, "error": str(e)})
            logger.error(f"❌ {test_name} - FAILED: {str(e)}")
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info(f"RAILWAY DEPLOYMENT READINESS TEST RESULTS")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 50)
    logger.info(f"✅ Tests Passed: {len(results['passed'])}/{len(test_methods)}")
    logger.info(f"❌ Tests Failed: {len(results['failed'])}/{len(test_methods)}")
    
    if results["failed"]:
        logger.info("\nFailed Tests:")
        for failed in results["failed"]:
            logger.info(f"❌ {failed['name']}: {failed['error']}")
            
    logger.info("\nSummary: " + ("✅ READY FOR DEPLOYMENT" if not results["failed"] else "❌ NOT READY FOR DEPLOYMENT"))
    logger.info("=" * 50) 