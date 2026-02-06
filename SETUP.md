# Research Intelligence Platform - Quick Setup Guide

## Prerequisites

Ensure you have the following installed:
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup

```bash
cd "s:\Project\intenship\Research Platform"
```

### 2. Start Infrastructure Services

```bash
# Start all Docker services
docker-compose up -d

# Wait 30 seconds for services to be healthy
# Check status
docker-compose ps
```

You should see 5 services running:
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ Qdrant (port 6333)
- ✅ Elasticsearch (port 9200)
- ✅ MinIO (port 9000)

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (this may take 2-3 minutes)
pip install -r requirements.txt

# Copy environment file
cp ..\.env.example .env

# Start FastAPI server
python main.py
```

API will be available at: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### 4. Start Celery Worker (New Terminal)

```bash
cd backend
venv\Scripts\activate
celery -A tasks.celery_app worker --loglevel=info --pool=solo
```

### 5. Set Up Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Web UI will be available at: **http://localhost:3000**

---

## ✅ Verify Installation

### Check Service Health

Visit: http://localhost:8000/health/services

You should see all services as "healthy":
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "qdrant": "healthy",
    "elasticsearch": "healthy",
    "minio": "healthy"
  }
}
```

### Test Upload

1. Go to http://localhost:3000/upload
2. Upload a PDF file
3. Check processing status on http://localhost:3000/documents
4. After processing completes (~10-30 seconds), search for content at http://localhost:3000

---

## 🛠️ Troubleshooting

### Docker Services Not Starting

```bash
# Check Docker logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Backend Errors

**"ModuleNotFoundError"**
```bash
# Ensure venv is activated
pip install -r requirements.txt
```

**"Connection refused" errors**
```bash
# Wait for Docker services to be fully ready
docker-compose ps  # All should show "healthy"
```

### Frontend Errors

**"Cannot find module"**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**"API connection error"**
- Ensure backend is running on port 8000
- Check `.env` has correct `NEXT_PUBLIC_API_URL=http://localhost:8000`

### Celery Worker Not Processing

```bash
# Check Redis is running
docker-compose ps redis

# Restart worker with verbose logging
celery -A tasks.celery_app worker --loglevel=debug --pool=solo
```

---

## 📂 Project Structure

```
research-platform/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── tasks/            # Celery tasks
│   ├── main.py           # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   ├── lib/              # API client
│   └── package.json
└── docker-compose.yml    # Infrastructure
```

---

## 🎯 Next Steps

1. **Upload Test Documents**
   - Use the upload page to add PDFs
   - Monitor processing in the documents page

2. **Try Search**
   - Search for keywords from your documents
   - Apply company/type filters
   - Note relevance scores

3. **Explore API**
   - Visit http://localhost:8000/docs
   - Try API endpoints directly

4. **Monitor Services**
   - Check health endpoint regularly
   - Watch Celery worker logs for processing

---

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://research_user:research_pass@localhost:5432/research_platform

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Chunking
CHUNK_SIZE=750
CHUNK_OVERLAP=100
```

---

## 📊 Performance Tips

1. **First document takes longer** (~2 minutes) - Loading ML model
2. **Subsequent documents are faster** (~10-30 seconds each)
3. **Search is fast** (<1 second for most queries)
4. **GPU acceleration** - If you have CUDA GPU, embeddings will be much faster

---

##  Stopping Services

```bash
# Stop frontend (Ctrl+C)
# Stop backend (Ctrl+C)
# Stop Celery worker (Ctrl+C)

# Stop Docker services
docker-compose down

# To remove all data
docker-compose down -v
```

---

## 📞 Need Help?

- Check logs in terminal windows
- Visit API docs at `/docs`
- Check Docker service logs: `docker-compose logs [service-name]`

**Happy Searching! 🔍**
