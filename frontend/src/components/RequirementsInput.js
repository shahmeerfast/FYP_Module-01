import React, { useState, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Mic, X, CheckCircle, AlertCircle, MicIcon, Square, Play } from 'lucide-react';
import axios from 'axios';

const RequirementsInput = ({ onResultsGenerated, onSRSGenerated }) => {
  const [inputType, setInputType] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [projectInfo, setProjectInfo] = useState({
    title: '',
    author: '',
    version: '1.0'
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState([]);
  const [showHelp, setShowHelp] = useState(false);
  
  // Audio recording states
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);

  const onDrop = (acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Date.now() + Math.random(),
      status: 'pending'
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'audio/*': ['.wav', '.mp3', '.m4a', '.flac']
    },
    multiple: true
  });

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks = [];

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Microphone access denied. Please allow microphone access to record audio.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const clearRecording = () => {
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setRecordingTime(0);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Derived helpers
  const wordCount = (textInput || '').trim().split(/\s+/).filter(w => w.length > 0).length;
  const hasLetter = /[A-Za-z]/.test(textInput || '');
  const charCount = (textInput || '').length;
  const minWords = 50;
  const progressPct = Math.min(100, Math.round((wordCount / minWords) * 100));

  const templates = [
    {
      label: 'User Management',
      text: 'The system should allow users to register, log in, reset passwords, and update profiles. Administrators can manage user roles, permissions, and view audit logs. The platform must ensure strong security, including session management, rate limiting, and multi-factor authentication. Notifications should be sent for critical actions and profile changes. The system must scale to handle peak usage and maintain availability.'
    },
    {
      label: 'E-commerce',
      text: 'Users can browse products, search by keywords and filters, add items to cart, and checkout. Payments must be processed securely with receipts sent via email. Administrators can add, edit, and remove products, manage inventory, and review orders. The site should be responsive, accessible, and support promotional discounts and coupon codes.'
    },
    {
      label: 'Analytics Dashboard',
      text: 'The application provides interactive charts, filters, and export options for business KPIs. Users can create custom dashboards, schedule reports, and share insights with teams. Data must refresh periodically and maintain accuracy. Access control should restrict sensitive metrics to authorized roles.'
    }
  ];

  // Validation function for text input (numbers/special symbols allowed, but must include letters)
  const validateTextInput = (text) => {
    const errors = [];
    const trimmed = text || '';
    const wordCount = trimmed.trim().split(/\s+/).filter(word => word.length > 0).length;
    // Require at least one alphabetic character
    const hasLetter = /[A-Za-z]/.test(trimmed);
    if (!hasLetter) {
      errors.push('Text must include at least one alphabetic character (A-Z).');
    }
    if (wordCount < 50) {
      errors.push(`Minimum 50 words required (current: ${wordCount} words)`);
    }
    return errors;
  };

  // Handle text input change with validation
  const handleTextInputChange = (e) => {
    const newText = e.target.value;
    setTextInput(newText);
    
    if (newText.trim()) {
      const errors = validateTextInput(newText);
      setValidationErrors(errors);
    } else {
      setValidationErrors([]);
    }
  };

  const processRequirements = async () => {
    setIsProcessing(true);
    setError(null);
    setValidationErrors([]);

    try {
      // Validate text input before processing
      if (inputType === 'text' && textInput.trim()) {
        const errors = validateTextInput(textInput);
        if (errors.length > 0) {
          setError('Please fix validation errors before processing');
          setIsProcessing(false);
          return;
        }
      }

      let response;

      if (inputType === 'text' && textInput.trim()) {
        // Process text input
        response = await axios.post('http://localhost:8000/api/process-single', {
          type: 'text',
          content: textInput,
          project_info: projectInfo
        });
      } else if (inputType === 'audio' && audioBlob) {
        // Process audio recording
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('project_info', JSON.stringify(projectInfo));

        response = await axios.post('http://localhost:8000/api/process-audio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else if (uploadedFiles.length > 0) {
        // Process uploaded files
        const formData = new FormData();
        uploadedFiles.forEach(({ file }) => {
          formData.append('files', file);
        });
        formData.append('project_info', JSON.stringify(projectInfo));

        response = await axios.post('http://localhost:8000/api/process-batch', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        throw new Error('Please provide text input, record audio, or upload files');
      }

      setResults(response.data);
      onResultsGenerated(response.data);
      
      // Auto-generate SRS if results are successful
      if (response.data.status === 'completed') {
        generateSRS(response.data);
      }

    } catch (err) {
      // Handle validation errors from backend
      if (err.response?.data?.validation_errors) {
        const validationData = err.response.data.validation_errors;
        
        if (Array.isArray(validationData) && validationData.length > 0) {
          // Check if it's file validation errors (has 'file' and 'errors' properties)
          if (validationData[0].file && validationData[0].errors) {
            // Multiple file validation errors
            const errorMessages = validationData.map(item => 
              `${item.file}: ${item.errors.join(', ')}`
            );
            setError('Validation failed for uploaded files');
            setValidationErrors(errorMessages);
          } else {
            // Single audio validation errors (array of strings)
            setError(err.response.data.error || 'Audio content validation failed');
            setValidationErrors(validationData);
          }
        } else if (typeof validationData === 'string') {
          // Single error message
          setError(err.response.data.error || 'Validation failed');
          setValidationErrors([validationData]);
        }
      } else {
        setError(err.response?.data?.error || err.message || 'An error occurred');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const generateSRS = async (resultsData) => {
    try {
      // Handle different result formats
      let requirementsArray;
      
      if (Array.isArray(resultsData)) {
        // Already an array
        requirementsArray = resultsData;
      } else if (resultsData.results && Array.isArray(resultsData.results)) {
        // Batch result with nested results array (from file upload)
        requirementsArray = resultsData.results;
      } else if (resultsData.status) {
        // Single result object (from text input)
        requirementsArray = [resultsData];
      } else {
        requirementsArray = [resultsData];
      }
      
      const response = await axios.post('http://localhost:8000/api/generate-srs', {
        results: requirementsArray,
        project_info: projectInfo
      });
      
      onSRSGenerated(response.data);
    } catch (err) {
      console.error('SRS generation failed:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto animate-fade-in">
      {/* Decorative gradient background */}
      <div className="relative rounded-2xl overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50" aria-hidden="true"></div>
        <div className="relative bg-white/70 backdrop-blur rounded-2xl card-shadow p-8">
          <h2 className="text-3xl md:text-4xl font-extrabold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
            Input Requirements
          </h2>

        {/* Project Information */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Project Information</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Title
              </label>
              <input
                type="text"
                value={projectInfo.title}
                onChange={(e) => setProjectInfo(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:border-gray-300 transition"
                placeholder="Enter project title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Author
              </label>
              <input
                type="text"
                value={projectInfo.author}
                onChange={(e) => setProjectInfo(prev => ({ ...prev, author: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:border-gray-300 transition"
                placeholder="Enter author name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Version
              </label>
              <input
                type="text"
                value={projectInfo.version}
                onChange={(e) => setProjectInfo(prev => ({ ...prev, version: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:border-gray-300 transition"
                placeholder="1.0"
              />
            </div>
          </div>
        </div>

        {/* Input Type Selection */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Input Method</h3>
          <div className="flex flex-wrap gap-3 mb-6">
            <button
              onClick={() => setInputType('text')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 shadow-sm ${
                inputType === 'text' 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white scale-[1.02]' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Text Input</span>
            </button>
            <button
              onClick={() => setInputType('audio')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 shadow-sm ${
                inputType === 'audio' 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white scale-[1.02]' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Mic className="h-4 w-4" />
              <span>Audio Recording</span>
            </button>
            <button
              onClick={() => setInputType('file')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 shadow-sm ${
                inputType === 'file' 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white scale-[1.02]' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>File Upload</span>
            </button>
          </div>

          {/* Text Input */}
          {inputType === 'text' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Requirements Text
              </label>
              <textarea
                value={textInput}
                onChange={handleTextInputChange}
                rows={8}
                className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  validationErrors.length > 0 ? 'border-red-300 bg-red-50' : 'border-gray-200 hover:border-gray-300'
                }`}
                placeholder="Enter your requirements here..."
              />

              {/* Progress bar */}
              <div className="mt-2 h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${progressPct >= 100 ? 'bg-green-500' : 'bg-blue-500'} transition-all duration-300`}
                  style={{ width: `${progressPct}%` }}
                />
              </div>

              {/* Live counters and badges */}
              <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full border ${
                  hasLetter ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'
                }`}>
                  {hasLetter ? 'Letters detected' : 'Add at least one letter'}
                </span>
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full border ${
                  wordCount >= minWords ? 'bg-green-50 text-green-700 border-green-200' : 'bg-yellow-50 text-yellow-700 border-yellow-200'
                }`}>
                  {wordCount} / {minWords} words
                </span>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full border bg-gray-50 text-gray-700 border-gray-200">
                  {charCount} characters
                </span>
              </div>
              
              {/* Validation Guidelines */
              }
              <div className="mt-2 text-sm text-gray-600">
                <p className="font-medium mb-1">Requirements:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>Minimum 50 words required</li>
                  <li>Numbers and symbols allowed, but include at least one letter</li>
                </ul>
              </div>

              {/* Quick templates */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-700">Quick templates</p>
                  <button
                    type="button"
                    onClick={() => setShowHelp(!showHelp)}
                    className="text-xs text-blue-600 hover:text-blue-700"
                  >
                    {showHelp ? 'Hide tips' : 'Show tips'}
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {templates.map((t) => (
                    <button
                      key={t.label}
                      type="button"
                      onClick={() => setTextInput(prev => (prev?.trim() ? `${prev.trim()}\n\n${t.text}` : t.text))}
                      className="px-3 py-1.5 text-sm rounded-full border bg-white hover:bg-blue-50 text-gray-700 hover:text-blue-700 border-gray-200 hover:border-blue-200 transition"
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {showHelp && (
                  <div className="mt-3 p-3 rounded-lg bg-blue-50 border border-blue-100 text-xs text-blue-800">
                    Aim for clear, complete sentences. Mention actors (users/admins), actions, constraints (security/performance), and any integrations. Avoid ambiguous terms like "fast" or "user-friendly" without specifics.
                  </div>
                )}
              </div>

              {/* Validation Errors */}
              {validationErrors.length > 0 && (
                <div className="mt-3 space-y-2">
                  {validationErrors.map((error, index) => (
                    <div key={index} className="flex items-start space-x-2 text-sm text-red-600">
                      <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                      <span>{error}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Audio Recording */}
          {inputType === 'audio' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Audio Recording
              </label>
              
              {/* Validation Guidelines */}
              <div className="mb-4 text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                <p className="font-medium mb-1">Recording Requirements:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>Minimum 50 words required</li>
                  <li>Speak clearly and at a moderate pace</li>
                </ul>
              </div>
              
              {!audioBlob ? (
                <div className="text-center p-8 border-2 border-dashed border-gray-300 rounded-lg">
                  <Mic className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg text-gray-600 mb-4">
                    {isRecording ? `Recording... ${formatTime(recordingTime)}` : 'Click to start recording'}
                  </p>
                  <div className="flex justify-center space-x-4">
                    {!isRecording ? (
                      <button
                        onClick={startRecording}
                        className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors duration-200"
                      >
                        <Mic className="h-5 w-5" />
                        <span>Start Recording</span>
                      </button>
                    ) : (
                      <button
                        onClick={stopRecording}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors duration-200"
                      >
                        <Square className="h-5 w-5" />
                        <span>Stop Recording</span>
                      </button>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-4">
                    Record your requirements by speaking into your microphone
                  </p>
                </div>
              ) : (
                <div className="bg-green-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <Mic className="h-6 w-6 text-green-600" />
                      <div>
                        <p className="font-medium text-green-900">Recording Complete</p>
                        <p className="text-sm text-green-700">Duration: {formatTime(recordingTime)}</p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      {audioUrl && (
                        <audio controls className="mr-2">
                          <source src={audioUrl} type="audio/wav" />
                          Your browser does not support the audio element.
                        </audio>
                      )}
                      <button
                        onClick={clearRecording}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-green-700">
                    Your audio recording is ready for processing. Click "Process Requirements" to analyze it.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* File Upload */}
          {inputType === 'file' && (
            <div>
              {/* Validation Guidelines */}
              <div className="mb-4 text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                <p className="font-medium mb-1">File Content Requirements:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>Minimum 50 words required per file</li>
                  <li>Supported formats: .txt, .wav, .mp3, .m4a, .flac</li>
                </ul>
              </div>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
                  isDragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-lg text-blue-600">Drop the files here...</p>
                ) : (
                  <div>
                    <p className="text-lg text-gray-600 mb-2">
                      Drag & drop files here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports: .txt, .wav, .mp3, .m4a, .flac
                    </p>
                  </div>
                )}
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Uploaded Files:</h4>
                  <div className="space-y-2">
                    {uploadedFiles.map(({ file, id, status }) => (
                      <div key={id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {file.type.startsWith('audio/') ? (
                            <Mic className="h-4 w-4 text-red-500" />
                          ) : (
                            <FileText className="h-4 w-4 text-blue-500" />
                          )}
                          <span className="text-sm font-medium">{file.name}</span>
                          <span className="text-xs text-gray-500">
                            ({(file.size / 1024).toFixed(1)} KB)
                          </span>
                        </div>
                        <button
                          onClick={() => removeFile(id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-red-700 font-semibold">{error}</span>
            </div>
            {validationErrors.length > 0 && (
              <div className="mt-3 ml-7 space-y-2">
                {validationErrors.map((err, index) => (
                  <div key={index} className="text-sm text-red-600">
                    • {err}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Process Button */}
        <div className="text-center">
          <button
            onClick={processRequirements}
            disabled={isProcessing || (!textInput.trim() && uploadedFiles.length === 0 && !audioBlob) || (inputType === 'text' && validationErrors.length > 0)}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-200 flex items-center space-x-2 mx-auto shadow-md hover:shadow-lg"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <CheckCircle className="h-5 w-5" />
                <span>Process Requirements</span>
              </>
            )}
          </button>
        </div>

        {/* Results Preview */}
        {results && (
          <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <h3 className="text-lg font-semibold text-green-800">Processing Complete!</h3>
            </div>
            <p className="text-green-700">
              Requirements processed successfully. SRS document has been generated.
            </p>
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default RequirementsInput;
