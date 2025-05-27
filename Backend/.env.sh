# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=AKTA - Proposal Archive API
VERSION=1.0.0

# Database Configuration (matches docker-compose)
POSTGRES_SERVER=postgres
POSTGRES_USER=akta_user
POSTGRES_PASSWORD=akta_password
POSTGRES_DB=akta_db
POSTGRES_PORT=5432

# Redis Configuration  
REDIS_URL=redis://redis:6379/0

# AI Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-pro

# Security
SECRET_KEY=development_secret_key_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# File Upload
MAX_FILE_SIZE=52428800
UPLOAD_DIR=./uploads

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# Search Configuration
EMBEDDING_DIMENSION=768
MAX_SEARCH_RESULTS=100
DEFAULT_SEARCH_RESULTS=20