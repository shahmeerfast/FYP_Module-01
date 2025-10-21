# Requirements Engineering System - Complete Setup

This repository contains a complete Requirements Engineering System with both Python backend and React.js frontend.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
python start_system.py
```
This script will:
- Check all dependencies
- Install frontend packages if needed
- Start both backend and frontend servers
- Open the application in your browser

### Option 2: Manual Setup

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements_api.txt

# Start the API server
python api_server.py
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## 📱 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## 🎯 Features

### Frontend (React.js)
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Multiple Input Methods**: Text input and file upload (text/audio)
- **Real-time Processing**: Live processing status and results
- **SRS Generation**: Automatic IEEE 830-compliant SRS document generation
- **Export Options**: Download SRS in HTML and JSON formats
- **Interactive Results**: Expandable sections for detailed requirement analysis

### Backend (Python Flask)
- **REST API**: Complete API for frontend integration
- **File Processing**: Support for text and audio files
- **Requirements Analysis**: AI-powered requirement processing
- **SRS Generation**: IEEE 830-compliant document generation
- **Database Integration**: Persistent storage of requirements

## 📁 Project Structure

```
├── frontend/                 # React.js frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.js           # Main app
│   │   └── index.js         # Entry point
│   ├── package.json         # Frontend dependencies
│   └── README.md           # Frontend documentation
├── api_server.py           # Flask API server
├── main_orchestrator.py    # Main processing orchestrator
├── srs_generator.py       # SRS document generator
├── requirements_api.txt    # Python API dependencies
├── start_system.py       # Automated startup script
└── README.md             # This file
```

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `POST /api/process-single` - Process single requirement
- `POST /api/process-batch` - Process multiple files
- `POST /api/generate-srs` - Generate SRS document
- `POST /api/download-srs/<format>` - Download SRS
- `GET /api/stats` - Get system statistics

## 💡 Usage

1. **Input Requirements**: 
   - Go to the Input page
   - Fill in project information (title, author, version)
   - Choose text input or file upload
   - Upload text files (.txt) or audio files (.wav, .mp3, .m4a, .flac)
   - Click "Process Requirements"

2. **View Results**:
   - Results are displayed automatically after processing
   - Expand sections to see detailed analysis
   - Download results as JSON

3. **Generate SRS**:
   - Click "Generate SRS" button
   - View the generated SRS document
   - Download in HTML or JSON format

## 🛠️ Technologies Used

### Frontend
- **React 18** - Frontend framework
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Dropzone** - File upload component
- **Lucide React** - Icon library

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Whisper** - Speech-to-text processing
- **spaCy** - Natural language processing
- **Transformers** - AI model integration

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**:
   - Backend (8000): Kill process using port 8000
   - Frontend (3000): Kill process using port 3000

2. **Missing dependencies**:
   - Run `pip install -r requirements_api.txt` for Python
   - Run `npm install` in frontend directory for Node.js

3. **CORS errors**:
   - Ensure backend is running on port 8000
   - Check that Flask-CORS is properly configured

### Getting Help

- Check the console output for error messages
- Ensure all dependencies are installed
- Verify that both servers are running
- Check network connectivity

## 📝 Development

### Adding New Features

1. **Frontend**: Add components in `frontend/src/components/`
2. **Backend**: Add API endpoints in `api_server.py`
3. **Processing**: Modify `main_orchestrator.py` for new processing logic

### Testing

- Frontend: `npm test` in frontend directory
- Backend: Test API endpoints using curl or Postman

## 📄 License

This project is part of the Requirements Engineering System for academic purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy Requirements Engineering! 🎉**
