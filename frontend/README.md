# Requirements Engineering System - React Frontend

A modern React.js frontend for the Requirements Engineering System that allows users to input requirements and generate IEEE 830-compliant Software Requirements Specification (SRS) documents.

## Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Multiple Input Methods**: Text input and file upload (text/audio)
- **Real-time Processing**: Live processing status and results
- **SRS Generation**: Automatic IEEE 830-compliant SRS document generation
- **Export Options**: Download SRS in HTML and JSON formats
- **Interactive Results**: Expandable sections for detailed requirement analysis

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python backend running on port 8000

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

### Backend Setup

Make sure the Python backend is running:

```bash
# Install API dependencies
pip install -r requirements_api.txt

# Start the API server
python api_server.py
```

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Header.js          # Navigation header
│   │   ├── Home.js            # Landing page
│   │   ├── RequirementsInput.js # Input form
│   │   ├── ResultsView.js     # Results display
│   │   └── SRSViewer.js       # SRS document viewer
│   ├── App.js                 # Main app component
│   ├── App.css               # App styles
│   ├── index.js              # Entry point
│   └── index.css             # Global styles
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## API Integration

The frontend communicates with the Python backend through these endpoints:

- `POST /api/process-single` - Process single text requirement
- `POST /api/process-batch` - Process multiple files
- `POST /api/generate-srs` - Generate SRS document
- `POST /api/download-srs/<format>` - Download SRS
- `GET /api/stats` - Get system statistics
- `GET /api/health` - Health check

## Usage

1. **Input Requirements**: 
   - Go to the Input page
   - Fill in project information
   - Choose text input or file upload
   - Click "Process Requirements"

2. **View Results**:
   - Results are displayed automatically after processing
   - Expand sections to see detailed analysis
   - Download results as JSON

3. **Generate SRS**:
   - Click "Generate SRS" button
   - View the generated SRS document
   - Download in HTML or JSON format

## Technologies Used

- **React 18** - Frontend framework
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Dropzone** - File upload component
- **Lucide React** - Icon library

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Customization

- Modify `tailwind.config.js` for theme customization
- Update API endpoints in components if backend URL changes
- Add new components in the `src/components/` directory

## Deployment

1. Build the production version:
```bash
npm run build
```

2. Serve the `build` folder with a web server or deploy to platforms like:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Heroku

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Requirements Engineering System for academic purposes.
