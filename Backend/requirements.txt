# FastAPI and server dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.0.3

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1

# Vector database support (pgvector)
pgvector==0.2.4

# Redis and Celery
redis==5.0.1
celery==5.3.4

# PDF processing
pypdf==3.17.1
pdfplumber==0.10.3
pytesseract==0.3.10

# AI/ML
google-generativeai==0.3.1
langchain==0.0.340
langchain-google-genai==0.0.6

# Utilities
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.25.2

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
isort==5.12.0
flake8==6.1.0