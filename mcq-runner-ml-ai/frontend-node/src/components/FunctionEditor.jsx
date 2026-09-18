import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { PlayCircle, Check, X, AlertCircle, Lightbulb } from 'lucide-react';
import toast from 'react-hot-toast';

/**
 * FunctionEditor Component
 * Main editor for writing function definitions with real-time validation
 */
export default function FunctionEditor({ 
  scenario, 
  onSubmit, 
  onValidate,
  initialCode = '' 
}) {
  const [code, setCode] = useState(initialCode);
  const [validationResults, setValidationResults] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [showHints, setShowHints] = useState(false);
  const [availableHints, setAvailableHints] = useState([]);
  const [timeElapsed, setTimeElapsed] = useState(0);

  // Timer for hint availability
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Update available hints based on time
  useEffect(() => {
    if (scenario?.hints) {
      const available = scenario.hints.filter(
        hint => timeElapsed >= hint.available_after
      );
      setAvailableHints(available);
    }
  }, [timeElapsed, scenario]);

  // Get starter template based on provider
  const getStarterTemplate = () => {
    if (scenario.provider === 'openai') {
      return JSON.stringify({
        name: "",
        description: "",
        parameters: {
          type: "object",
          properties: {},
          required: []
        }
      }, null, 2);
    } else if (scenario.provider === 'claude') {
      return JSON.stringify({
        name: "",
        description: "",
        input_schema: {
          type: "object",
          properties: {},
          required: []
        }
      }, null, 2);
    }
  };

  // Validate the code
  const handleValidate = async () => {
    setIsValidating(true);
    
    try {
      // Parse JSON first
      const parsed = JSON.parse(code);
      
      // Send to backend for validation
      const results = await onValidate(parsed, scenario);
      
      setValidationResults(results);
      
      if (results.isValid) {
        toast.success('Validation passed! ✅');
      } else {
        toast.error(`Failed ${results.failedTests.length} test(s)`);
      }
    } catch (error) {
      if (error instanceof SyntaxError) {
        toast.error('Invalid JSON syntax');
        setValidationResults({
          isValid: false,
          error: 'JSON Syntax Error: ' + error.message
        });
      } else {
        toast.error('Validation error: ' + error.message);
      }
    } finally {
      setIsValidating(false);
    }
  };

  // Submit the solution
  const handleSubmit = async () => {
    try {
      const parsed = JSON.parse(code);
      await onSubmit(parsed, scenario);
      toast.success('Solution submitted!');
    } catch (error) {
      toast.error('Please fix errors before submitting');
    }
  };

  // Load starter template
  const loadTemplate = () => {
    setCode(getStarterTemplate());
    toast.success('Template loaded');
  };

  // Format JSON
  const formatCode = () => {
    try {
      const parsed = JSON.parse(code);
      setCode(JSON.stringify(parsed, null, 2));
      toast.success('Code formatted');
    } catch (error) {
      toast.error('Invalid JSON - cannot format');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gray-800 px-4 py-3 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold">{scenario.title}</h3>
            <p className="text-gray-400 text-sm">
              {scenario.provider === 'openai' ? 'OpenAI' : 'Anthropic Claude'} Format
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Timer */}
            <div className="text-sm text-gray-400 px-3 py-1 bg-gray-700 rounded">
              {Math.floor(timeElapsed / 60)}:{(timeElapsed % 60).toString().padStart(2, '0')}
            </div>
            
            {/* Hints Button */}
            {availableHints.length > 0 && (
              <button
                onClick={() => setShowHints(!showHints)}
                className="flex items-center gap-2 px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-sm transition"
              >
                <Lightbulb size={16} />
                {availableHints.length} Hint{availableHints.length > 1 ? 's' : ''}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Hints Panel */}
      {showHints && availableHints.length > 0 && (
        <div className="bg-yellow-900 bg-opacity-20 border-b border-yellow-700 p-4">
          <div className="space-y-2">
            {availableHints.map((hint, index) => (
              <div key={index} className="flex items-start gap-2 text-yellow-200 text-sm">
                <Lightbulb size={16} className="mt-1 flex-shrink-0" />
                <p>{hint.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Toolbar */}
      <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center gap-2">
        <button
          onClick={loadTemplate}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition"
        >
          Load Template
        </button>
        
        <button
          onClick={formatCode}
          className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded transition"
        >
          Format JSON
        </button>
        
        <div className="flex-1"></div>
        
        <button
          onClick={handleValidate}
          disabled={isValidating}
          className="flex items-center gap-2 px-4 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-sm rounded transition"
        >
          <PlayCircle size={16} />
          {isValidating ? 'Validating...' : 'Validate'}
        </button>
        
        <button
          onClick={handleSubmit}
          className="flex items-center gap-2 px-4 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition"
        >
          Submit
        </button>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          defaultLanguage="json"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            rulers: [],
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            formatOnPaste: true,
            formatOnType: true
          }}
        />
      </div>

      {/* Validation Results */}
      {validationResults && (
        <div className="bg-gray-800 border-t border-gray-700 p-4 max-h-48 overflow-y-auto">
          <div className="space-y-2">
            {validationResults.error && (
              <div className="flex items-start gap-2 text-red-400 text-sm">
                <X size={16} className="mt-1 flex-shrink-0" />
                <p>{validationResults.error}</p>
              </div>
            )}
            
            {validationResults.testResults && validationResults.testResults.map((test, index) => (
              <div
                key={index}
                className={`flex items-start gap-2 text-sm ${
                  test.passed ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {test.passed ? (
                  <Check size={16} className="mt-1 flex-shrink-0" />
                ) : (
                  <X size={16} className="mt-1 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className="font-medium">{test.name}</p>
                  {test.message && (
                    <p className="text-gray-400 text-xs mt-1">{test.message}</p>
                  )}
                </div>
                <span className="text-gray-500">{test.points}pts</span>
              </div>
            ))}
            
            {validationResults.isValid && (
              <div className="mt-4 p-3 bg-green-900 bg-opacity-20 border border-green-700 rounded">
                <p className="text-green-400 font-medium">
                  ✅ All tests passed! Score: {validationResults.score}/{validationResults.maxScore}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
