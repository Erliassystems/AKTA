## 5. Technical Architecture

### 5.1 System Components

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│                  │     │                  │     │                  │
│  React + Vite    │────▶│  FastAPI         │────▶│  PostgreSQL      │
│  Frontend        │     │  Backend         │     │  + pgvector      │
│                  │     │                  │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                │                           │
                                ▼                           ▼
                         ┌──────────────────┐     ┌──────────────────┐
                         │                  │     │                  │
                         │  Google Gemini   │     │  Redis Cache     │
                         │  API             │     │                  │
                         │                  │     │                  │
                         └──────────────────┘     └──────────────────┘
```

### 5.2 Technology Stack

#### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 16 with pgvector extension
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **PDF Processing**: pdfplumber, pytesseract
- **AI/ML**: Google Gemini API (gemini-pro), langchain

#### Frontend
- **Build Tool**: Vite 5.x
- **Framework**: React 18.x
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **API Client**: React Query (TanStack Query)
- **Routing**: React Router v6
- **Development**: Vite HMR, ESLint, Prettier

#### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose (development), Kubernetes (production)
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana

### 5.3 Google Gemini Integration

#### Embedding Generation
- **Model**: `models/embedding-001` for text embeddings
- **Dimension**: 768 (adjust pgvector accordingly)
- **Batch Processing**: Support for up to 100 texts per request

#### Text Analysis
- **Model**: `gemini-pro` for proposal extraction and analysis
- **Features**:
  - Proposal identification from PDFs
  - Metadata extraction
  - Summary generation
  - Tag suggestion

#### API Configuration
```python
# config/gemini.py
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

# For embeddings
embedding_model = genai.GenerativeModel('models/embedding-001')

# For text analysis
generation_model = genai.GenerativeModel('gemini-pro')

# Safety settings for political content
safety_settings = [
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]
```

### 5.4 Frontend Architecture (Vite + React)

#### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── search/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   └── FilterPanel.tsx
│   │   ├── proposal/
│   │   │   ├── ProposalCard.tsx
│   │   │   └── ProposalDetail.tsx
│   │   └── common/
│   │       ├── Layout.tsx
│   │       └── LoadingSpinner.tsx
│   ├── hooks/
│   │   ├── useSearch.ts
│   │   └── useProposal.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── search.service.ts
│   ├── store/
│   │   └── searchStore.ts
│   ├── types/
│   │   └── proposal.types.ts
│   ├── App.tsx
│   └── main.tsx
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

#### Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@tanstack/react-query', 'zustand'],
        },
      },
    },
  },
})
```

### 5.5 Development Environment

#### Docker Compose Configuration
```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: akta
      POSTGRES_USER: akta_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://akta_user:${DB_PASSWORD}@postgres/akta
      REDIS_URL: redis://redis:6379
      GOOGLE_API_KEY: ${GEMINI_API_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
  
  frontend:
    build: ./frontend
    environment:
      VITE_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
```

### 5.6 API Integration Patterns

#### React Query Configuration
```typescript
// src/services/api.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
})

// src/hooks/useSearch.ts
export const useSearch = (query: string, filters: SearchFilters) => {
  return useQuery({
    queryKey: ['search', query, filters],
    queryFn: () => searchService.search(query, filters),
    enabled: query.length > 0,
    staleTime: 1000 * 60 * 2, // 2 minutes
  })
}
```

### 5.7 Performance Optimizations

#### Frontend Optimizations
- **Code Splitting**: Lazy load routes and heavy components
- **Bundle Optimization**: Separate vendor chunks
- **Image Optimization**: Use WebP with fallbacks
- **Caching Strategy**: Service worker for offline access

#### Backend Optimizations
- **Connection Pooling**: PostgreSQL and Redis connection pools
- **Query Optimization**: Prepared statements and indexes
- **Caching Layers**:
  - Redis for frequently accessed proposals
  - In-memory cache for embeddings
  - CDN for static assets

#### Gemini API Optimizations
- **Batch Processing**: Group embedding requests
- **Rate Limiting**: Respect API quotas (60 requests/minute)
- **Fallback Strategy**: Cached responses for common queries
- **Cost Management**: 
  - Use `gemini-pro` for complex tasks only
  - Cache embeddings aggressively
  - Implement request queuing