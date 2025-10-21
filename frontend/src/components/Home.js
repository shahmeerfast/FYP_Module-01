import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Upload, Eye, Download, Users, Zap } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <Upload className="h-8 w-8 text-blue-600" />,
      title: "Input Requirements",
      description: "Upload text files or audio recordings to input your requirements",
      link: "/input"
    },
    {
      icon: <FileText className="h-8 w-8 text-green-600" />,
      title: "Process Requirements",
      description: "AI-powered processing to extract and analyze requirements",
      link: "/results"
    },
    {
      icon: <Download className="h-8 w-8 text-purple-600" />,
      title: "Generate SRS",
      description: "Generate IEEE 830-compliant Software Requirements Specification",
      link: "/srs"
    }
  ];

  const stats = [
    { label: "Requirements Processed", value: "100+" },
    { label: "SRS Documents Generated", value: "50+" },
    { label: "Active Users", value: "25+" }
  ];

  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Requirements Engineering
          <span className="text-blue-600"> Made Simple</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your requirements into professional IEEE 830-compliant 
          Software Requirements Specification documents with AI-powered analysis.
        </p>
        <div className="flex justify-center space-x-4">
          <Link 
            to="/input"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200 flex items-center space-x-2"
          >
            <Upload className="h-5 w-5" />
            <span>Get Started</span>
          </Link>
          <Link 
            to="/results"
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-8 py-3 rounded-lg font-semibold transition-colors duration-200 flex items-center space-x-2"
          >
            <Eye className="h-5 w-5" />
            <span>View Results</span>
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Link
              key={index}
              to={feature.link}
              className="bg-white p-8 rounded-xl card-shadow hover:shadow-xl transition-shadow duration-200 group"
            >
              <div className="text-center">
                <div className="mb-4 flex justify-center group-hover:scale-110 transition-transform duration-200">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white py-16 rounded-xl card-shadow">
        <div className="grid md:grid-cols-3 gap-8 text-center">
          {stats.map((stat, index) => (
            <div key={index}>
              <div className="text-4xl font-bold text-blue-600 mb-2">
                {stat.value}
              </div>
              <div className="text-gray-600">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center py-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Get Started?
        </h2>
        <p className="text-gray-600 mb-8">
          Upload your requirements and generate professional SRS documents in minutes.
        </p>
        <Link 
          to="/input"
          className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200 inline-flex items-center space-x-2"
        >
          <Zap className="h-5 w-5" />
          <span>Start Processing</span>
        </Link>
      </div>
    </div>
  );
};

export default Home;
