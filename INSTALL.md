# MultiToolAPI - Simple Installation Guide

## 🚀 Quick Start (No Docker Required)

### Step 1: Prerequisites
- Python 3.8 or higher
- No additional databases or services required

### Step 2: Setup
```bash
# Run the automated setup script
python setup.py
```

This will:
- Install all required Python packages
- Create necessary directories
- Set up SQLite database
- Create configuration files
- Generate a simple start script

### Step 3: Configure API Keys
Edit the `.env` file and add your API keys:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional but recommended
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### Step 4: Start the Application
```bash
python start_simple.py
```

### Step 5: Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Setup Status**: http://localhost:8000/setup-status

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Directories
```bash
mkdir -p data/chroma_db uploads logs data/sqlite
```

### 3. Configure Environment
```bash
cp env.example .env
# Edit .env with your API keys
```

### 4. Start the Application
```bash
uvicorn app.main_simple:app --reload
```

## 📋 API Keys Setup

### Gemini AI (Required)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### Google APIs (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Places API
   - Maps API
3. Create API keys for each service
4. Add them to your `.env` file

## 🧪 Test the Installation

Run the example script to test everything:

```bash
python example_usage.py
```

This will:
- Create a test client
- Upload sample data
- Start a scraping job
- Query the RAG system
- Generate solutions
- Show analysis results

## 🗂️ Project Structure

```
MultiToolAPI/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core configuration
│   ├── models/               # Database models
│   ├── services/             # Business logic services
│   ├── main_simple.py       # Simple FastAPI app
│   └── main.py              # Full FastAPI app
├── data/
│   ├── chroma_db/           # Vector database
│   └── sqlite/              # SQLite database
├── uploads/                  # File uploads
├── setup.py                 # Setup script
├── start_simple.py          # Simple start script
├── example_usage.py         # Usage example
└── requirements.txt         # Dependencies
```

## 🔍 Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Make sure you've added your API keys to the `.env` file
   - Check the setup status at http://localhost:8000/setup-status

2. **Database Issues**
   - The SQLite database is created automatically
   - If you have issues, delete `data/sqlite/multitoolapi.db` and restart

3. **Port Already in Use**
   - Change the port in `start_simple.py` or kill the process using port 8000

4. **Missing Dependencies**
   - Run `pip install -r requirements.txt` again
   - Make sure you're using Python 3.8+

### Getting Help

- Check the API documentation at http://localhost:8000/docs
- Run the example script to test functionality
- Check the logs for error messages

## 🎯 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Run Examples**: Try `python example_usage.py`
3. **Add Your Data**: Upload client documents and scrape websites
4. **Generate Solutions**: Use the AI-powered analysis features

## 🔄 Updating

To update the system:
```bash
git pull
pip install -r requirements.txt
python start_simple.py
```

## 🗑️ Uninstalling

To remove the system:
```bash
# Stop the application (Ctrl+C)
# Delete the project directory
rm -rf MultiToolAPI/
```
