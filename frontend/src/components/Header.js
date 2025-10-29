import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Upload, Eye, Settings } from 'lucide-react';

const Header = () => {
  return (
    <header className="relative gradient-bg text-white shadow-lg">
      <div className="absolute inset-0 opacity-20 bg-grid" />
      <div className="relative container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center shadow-inner">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold leading-tight">Requirements Engineering System</h1>
              <p className="text-xs text-blue-100/90">AI-powered SRS generation</p>
            </div>
          </div>
          <nav className="flex space-x-6">
            <Link 
              to="/" 
              className="nav-underline hover:text-blue-200 transition-colors duration-200 flex items-center space-x-1"
            >
              <Settings className="h-4 w-4" />
              <span>Home</span>
            </Link>
            <Link 
              to="/input" 
              className="nav-underline hover:text-blue-200 transition-colors duration-200 flex items-center space-x-1"
            >
              <Upload className="h-4 w-4" />
              <span>Input</span>
            </Link>
            <Link 
              to="/results" 
              className="nav-underline hover:text-blue-200 transition-colors duration-200 flex items-center space-x-1"
            >
              <Eye className="h-4 w-4" />
              <span>Results</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
