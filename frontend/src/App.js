import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './components/Home';
import RequirementsInput from './components/RequirementsInput';
import SRSViewer from './components/SRSViewer';
import ResultsView from './components/ResultsView';
import './App.css';

function App() {
  const [currentResults, setCurrentResults] = useState(null);
  const [srsData, setSrsData] = useState(null);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route 
              path="/input" 
              element={
                <RequirementsInput 
                  onResultsGenerated={setCurrentResults}
                  onSRSGenerated={setSrsData}
                />
              } 
            />
            <Route 
              path="/results" 
              element={
                <ResultsView 
                  results={currentResults}
                  onGenerateSRS={setSrsData}
                />
              } 
            />
            <Route 
              path="/srs" 
              element={<SRSViewer srsData={srsData} />} 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
