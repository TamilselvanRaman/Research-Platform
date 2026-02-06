# Research Intelligence Platform

A scalable research intelligence platform that ingests, processes, and extracts insights from massive volumes of unstructured documents (PDFs, reports, research papers) using hybrid search (vector + keyword).

## Architecture

### Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (TypeScript)
- **Database**: PostgreSQL 15
- **Vector DB**: Qdrant
- **Search**: Elasticsearch
- **Task Queue**: Celery + Redis
- **Storage**: MinIO (S3-compatible)

### System Components

1. **Document Ingestion** - Upload and validate PDFs
2. **Processing Pipeline** - Parse, chunk, and embed documents
3. **Storage Layer** - PostgreSQL, Qdrant, Elasticsearch, MinIO
4. **Search Engine** - Hybrid vector + keyword search
5. **API Layer** - RESTful API with FastAPI
6. **Web UI** - Search interface and document viewer

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Start Infrastructure Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)
- Elasticsearch (port 9200)
- MinIO (port 9000, console 9001)

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

### 3. Start Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info
```

### 4. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Access the Application

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `QDRANT_URL` - Qdrant host
- `ELASTICSEARCH_URL` - Elasticsearch host
- `MINIO_ENDPOINT` - MinIO endpoint
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key

## Usage

### Upload Documents

1. Navigate to http://localhost:3000/upload
2. Drag and drop PDF files or click to select
3. Documents are processed asynchronously
4. Check processing status in the UI

### Search Documents

1. Go to http://localhost:3000
2. Enter search query
3. Apply filters (company, date range)
4. View results with relevance scores
5. Click to view full document

## API Endpoints

### Documents
- `POST /api/upload` - Upload document
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document details
- `GET /api/documents/{id}/download` - Download original

### Search
- `POST /api/search` - Hybrid search query
- `GET /api/search/filters` - Get available filters

### Health
- `GET /health` - Service health check
- `GET /health/services` - Check all dependent services

## Development

### Backend Testing

```bash
cd backend
pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

## Project Structure

```
research-platform/
├── backend/
│   ├── api/              # API route handlers
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── tasks/            # Celery tasks
│   ├── tests/            # Unit and integration tests
│   ├── alembic/          # Database migrations
│   ├── main.py           # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages (App Router)
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   ├── public/           # Static assets
│   └── package.json
├── docker-compose.yml    # Infrastructure services
├── .env.example          # Environment template
└── README.md
```

## Phase 1 MVP Features

✅ Document upload (PDF)  
✅ PDF text extraction  
✅ Fixed-size chunking (750 tokens)  
✅ Embedding generation (sentence-transformers)  
✅ Vector search (Qdrant)  
✅ Keyword search (Elasticsearch)  
✅ Hybrid search with scoring  
✅ Search UI with filters  
✅ Document viewer  

## Roadmap

### Phase 2 (Months 3-4)
- OCR for scanned documents
- User authentication
- Advanced filters and facets
- Batch upload
- Admin dashboard

### Phase 3 (Months 5-6)
- Entity extraction (companies, dates, metrics)
- Time-series analytics
- Document clustering
- LLM-powered summarization
- Saved queries and alerts

## Performance

**Current benchmarks** (1000 documents):
- Upload: ~2 seconds per document
- Processing: ~5 seconds per document
- Search latency: <1.5 seconds (p95)
- Embedding generation: ~100 documents/minute

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open a GitHub issue.
