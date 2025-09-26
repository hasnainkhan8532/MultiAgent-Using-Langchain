# MultiToolAPI - Intelligent Client Analysis and Solution Generation System

A comprehensive API system that combines web scraping, RAG (Retrieval Augmented Generation), Gemini AI, and Google APIs to provide intelligent analysis and solution generation for clients.

## Features

### 🔍 Web Scraping
- **Multiple Strategies**: Requests, Selenium, Playwright
- **Auto-Detection**: Automatically selects the best scraping method
- **Comprehensive Data Extraction**: Text, images, links, forms, tables, scripts
- **Background Processing**: Asynchronous scraping jobs

### 🧠 RAG System
- **LangChain Integration**: Advanced document processing and retrieval
- **ChromaDB Vector Store**: Efficient similarity search
- **Document Chunking**: Intelligent text splitting for optimal retrieval
- **Multi-Source Support**: Scraped data, uploaded files, manual notes

### 🤖 Gemini AI Integration
- **Intelligent Analysis**: Comprehensive client data analysis
- **Solution Generation**: AI-powered recommendations and strategies
- **Marketing Strategy**: Targeted marketing recommendations
- **Technical Analysis**: Website performance and SEO insights
- **Content Suggestions**: AI-generated content ideas

### 🗺️ Google APIs Integration
- **Places API**: Business location analysis
- **Maps API**: Geocoding and location insights
- **Competition Analysis**: Nearby business intelligence
- **Location Insights**: Market analysis and recommendations

### 📊 Client Management
- **Comprehensive Profiles**: Detailed client information
- **Data Organization**: Structured data storage and retrieval
- **File Upload Support**: PDF, DOCX, Excel, and text files
- **Progress Tracking**: Analysis and solution status monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Scraping  │    │   RAG System    │    │   Gemini AI     │
│                 │    │                 │    │                 │
│ • Requests      │───▶│ • LangChain     │───▶│ • Analysis      │
│ • Selenium      │    │ • ChromaDB      │    │ • Solutions     │
│ • Playwright    │    │ • Embeddings    │    │ • Strategies    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Google APIs   │
                    │                 │
                    │ • Places API    │
                    │ • Maps API      │
                    │ • Location Data │
                    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- No additional databases required (uses SQLite)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MultiToolAPI
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure your API keys**
   ```bash
   # Edit the .env file and add your API keys
   nano .env
   ```

4. **Start the application**
   ```bash
   python start_simple.py
   ```

### Manual Setup (Alternative)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create directories**
   ```bash
   mkdir -p data/chroma_db uploads logs data/sqlite
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Clients
- `POST /api/v1/clients/` - Create a new client
- `GET /api/v1/clients/` - List all clients
- `GET /api/v1/clients/{client_id}` - Get client details
- `PUT /api/v1/clients/{client_id}` - Update client
- `DELETE /api/v1/clients/{client_id}` - Delete client
- `POST /api/v1/clients/{client_id}/data` - Upload client data

### Web Scraping
- `POST /api/v1/scraping/start` - Start scraping job
- `GET /api/v1/scraping/jobs/{client_id}` - Get scraping jobs
- `GET /api/v1/scraping/jobs/{client_id}/{job_id}` - Get job details
- `POST /api/v1/scraping/reprocess/{job_id}` - Reprocess data

### RAG System
- `POST /api/v1/rag/query` - Query the RAG system
- `POST /api/v1/rag/search` - Search documents
- `POST /api/v1/rag/documents` - Add document
- `GET /api/v1/rag/documents/{client_id}` - Get client documents
- `POST /api/v1/rag/setup` - Setup RAG system

### Solutions
- `POST /api/v1/solutions/generate` - Generate solutions
- `GET /api/v1/solutions/{client_id}` - Get client solutions
- `POST /api/v1/solutions/feedback` - Submit feedback
- `POST /api/v1/solutions/sessions` - Create analysis session

### Analysis
- `POST /api/v1/analysis/comprehensive` - Start comprehensive analysis
- `GET /api/v1/analysis/marketing/{client_id}` - Get marketing analysis
- `GET /api/v1/analysis/technical/{client_id}` - Get technical analysis
- `GET /api/v1/analysis/content/{client_id}` - Get content suggestions
- `GET /api/v1/analysis/location/{client_id}` - Get location analysis

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/multitoolapi
REDIS_URL=redis://localhost:6379

# Google APIs
GOOGLE_API_KEY=your_google_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Vector Database
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Security
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Scraping
SCRAPING_DELAY=1
MAX_CONCURRENT_REQUESTS=5
USER_AGENT=MultiToolAPI/1.0

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIRECTORY=./uploads
```

## Usage Examples

### 1. Create a Client and Upload Data

```python
import requests

# Create client
client_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Example Corp",
    "website": "https://example.com",
    "industry": "Technology"
}

response = requests.post("http://localhost:8000/api/v1/clients/", json=client_data)
client_id = response.json()["client_id"]

# Upload client data
with open("client_document.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "data_type": "document",
        "title": "Company Overview"
    }
    requests.post(f"http://localhost:8000/api/v1/clients/{client_id}/data", 
                  files=files, data=data)
```

### 2. Scrape Website and Generate Analysis

```python
# Start scraping
scraping_data = {
    "client_id": client_id,
    "url": "https://example.com",
    "strategy": "auto"
}
requests.post("http://localhost:8000/api/v1/scraping/start", json=scraping_data)

# Generate comprehensive analysis
analysis_data = {
    "client_id": client_id,
    "analysis_type": "comprehensive",
    "include_google_data": True,
    "requirements": "Improve online presence and marketing"
}
requests.post("http://localhost:8000/api/v1/analysis/comprehensive", json=analysis_data)
```

### 3. Query RAG System

```python
# Query the knowledge base
query_data = {
    "client_id": client_id,
    "query": "What are the main challenges for this business?",
    "k": 5
}
response = requests.post("http://localhost:8000/api/v1/rag/query", json=query_data)
answer = response.json()["answer"]
```

## Development

### Project Structure

```
MultiToolAPI/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core configuration
│   ├── models/               # Database models
│   ├── services/             # Business logic services
│   └── main.py              # FastAPI application
├── data/                    # Data storage
├── uploads/                 # File uploads
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── README.md              # This file
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.

## Roadmap

- [ ] Advanced analytics dashboard
- [ ] Real-time notifications
- [ ] Multi-language support
- [ ] Advanced AI model integration
- [ ] API rate limiting and caching
- [ ] Advanced security features
- [ ] Mobile application
- [ ] Integration with more third-party services
