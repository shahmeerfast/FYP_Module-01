import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Upload, Eye, Settings } from 'lucide-react';

const Header = () => {
  return (
    <header className="gradient-bg text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="h-8 w-8" />
            <h1 className="text-2xl font-bold">Requirements Engineering System</h1>
          </div>
          <nav className="flex space-x-6">
            <Link 
              to="/" 
              className="hover:text-blue-200 transition-colors duration-200 flex items-center space-x-1"
            >
              <Settings className="h-4 w-4" />
              <span>Home</span>
            </Link>
            <Link 
              to="/input" 
              className="hover:text-blue-200 transition-colors duration-200 flex items-center space-x-1"
            >
              <Upload className="h-4 w-4" />
              <span>Input Requirements</span>
            </Link>
            <Link 
              to="/results" 
              className="hover:text-blue-200 transition-colors duration-200 flex items-center space-x-1"
            >
              <Eye className="h-4 w-4" />
              <span>View Results</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
